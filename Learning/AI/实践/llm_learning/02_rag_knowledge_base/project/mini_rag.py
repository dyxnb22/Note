#!/usr/bin/env python3
"""A dependency-free mini RAG system for local notes."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import urllib.request
from collections import Counter
from pathlib import Path


DOC_DIR = Path(__file__).with_name("docs")


def tokenize(text: str) -> list[str]:
    """Tokenize Chinese/English roughly enough for a teaching demo."""
    return re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9_]+", text.lower())


def split_text(text: str, size: int = 500, overlap: int = 80) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size])
        start += size - overlap
    return chunks


def load_chunks() -> list[dict[str, str]]:
    chunks: list[dict[str, str]] = []
    for path in sorted(DOC_DIR.glob("**/*")):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        for index, chunk in enumerate(split_text(path.read_text(encoding="utf-8"))):
            chunks.append({"source": f"{path.name}#{index}", "text": chunk})
    return chunks


def cosine(a: Counter[str], b: Counter[str]) -> float:
    common = set(a) & set(b)
    dot = sum(a[word] * b[word] for word in common)
    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))
    return dot / (norm_a * norm_b or 1)


def retrieve(question: str, chunks: list[dict[str, str]], top_k: int = 3) -> list[dict[str, str]]:
    question_vec = Counter(tokenize(question))
    scored = []
    for chunk in chunks:
        score = cosine(question_vec, Counter(tokenize(chunk["text"])))
        scored.append((score, chunk))
    return [chunk for score, chunk in sorted(scored, key=lambda item: item[0], reverse=True)[:top_k] if score > 0]


def call_llm(question: str, contexts: list[dict[str, str]]) -> str:
    context_text = "\n\n".join(f"[{item['source']}]\n{item['text']}" for item in contexts)
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        return "未配置 LLM_API_KEY，返回检索上下文：\n\n" + context_text

    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com").rstrip("/")
    model = os.environ["LLM_MODEL"]
    messages = [
        {"role": "system", "content": "Answer using only the provided context. Cite sources."},
        {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}"},
    ]
    payload = json.dumps({"model": model, "messages": messages, "temperature": 0.2}).encode()
    request = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode())["choices"][0]["message"]["content"]


def init_docs() -> None:
    DOC_DIR.mkdir(exist_ok=True)
    sample = DOC_DIR / "agent_notes.md"
    sample.write_text(
        "# Agent 学习笔记\n\n"
        "Agent 通常由模型、工具、记忆和控制循环组成。模型负责判断下一步，工具负责执行确定性动作。"
        "生产环境里，写文件、发邮件、下单等动作应该经过确认。\n\n"
        "RAG 适合给 Agent 提供外部知识。评测可以帮助判断 Prompt 或检索策略是否真的变好。\n",
        encoding="utf-8",
    )
    print(f"Created sample docs in {DOC_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="?", help="Question to ask the local knowledge base.")
    parser.add_argument("--init", action="store_true", help="Create sample documents.")
    args = parser.parse_args()

    if args.init:
        init_docs()
        return

    if not args.question:
        raise SystemExit("Please provide a question, or run with --init first.")

    chunks = load_chunks()
    if not chunks:
        raise SystemExit("No docs found. Run: python3 mini_rag.py --init")

    contexts = retrieve(args.question, chunks)
    print(call_llm(args.question, contexts))


if __name__ == "__main__":
    main()
