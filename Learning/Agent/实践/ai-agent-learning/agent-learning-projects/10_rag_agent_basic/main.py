import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
load_dotenv(BASE_DIR / ".env")


def load_markdown_files() -> list[tuple[str, str]]:
    """读取本地 Markdown 文档。"""
    documents = []
    for path in DOCS_DIR.glob("*.md"):
        documents.append((path.name, path.read_text(encoding="utf-8")))
    return documents


def chunk_text(text: str, chunk_size: int = 180) -> list[str]:
    """把长文档切成 chunk。

    chunk 是 RAG 的基本单位。切太大，检索不精确；切太小，又容易丢上下文。
    这里优先按段落切分，比硬切字符更适合初学者观察结果。
    """
    paragraphs = [item.strip() for item in text.split("\n\n") if item.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(current) + len(paragraph) <= chunk_size:
            current = f"{current}\n\n{paragraph}".strip()
        else:
            if current:
                chunks.append(current)
            current = paragraph
    if current:
        chunks.append(current)
    return chunks


def build_chunks() -> list[dict[str, str]]:
    chunks = []
    for filename, text in load_markdown_files():
        for index, chunk in enumerate(chunk_text(text)):
            chunks.append({"source": filename, "id": f"{filename}-{index}", "text": chunk})
    return chunks


def retrieve(question: str, chunks: list[dict[str, str]], top_k: int = 3) -> list[dict[str, str]]:
    """用简单关键词匹配做 retrieval。

    生产 RAG 常用 embedding + 向量数据库。这里先不用复杂组件，
    因为你需要先理解 retrieval 的位置和作用。
    """
    keywords = [word.lower() for word in question.replace("？", " ").split() if word]
    scored = []
    for chunk in chunks:
        text = chunk["text"].lower()
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]] or chunks[:top_k]


def answer_without_llm(question: str, contexts: list[dict[str, str]]) -> str:
    context_text = "\n\n".join(item["text"] for item in contexts)
    return (
        "这是基于本地检索结果的回答草稿：\n"
        f"问题：{question}\n\n"
        f"相关上下文：\n{context_text}"
    )


def answer_with_openai(question: str, contexts: list[dict[str, str]]) -> str:
    """Context Injection：把检索到的 chunk 塞进 prompt。"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    context_text = "\n\n".join(
        f"[{item['source']}]\n{item['text']}" for item in contexts
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "只能根据给定上下文回答，不要编造。"},
            {"role": "user", "content": f"上下文：\n{context_text}\n\n问题：{question}"},
        ],
    )
    return response.choices[0].message.content or ""


def main() -> None:
    chunks = build_chunks()
    question = input("请输入问题：").strip() or "什么是 RAG？"
    contexts = retrieve(question, chunks)

    # 默认不调用 OpenAI，方便无 API Key 时也能学习 RAG 流程。
    if os.getenv("USE_OPENAI", "false").lower() == "true":
        answer = answer_with_openai(question, contexts)
    else:
        answer = answer_without_llm(question, contexts)

    print(answer)


if __name__ == "__main__":
    main()
