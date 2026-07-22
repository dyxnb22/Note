import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def main() -> None:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.environ["OPENAI_MODEL"]

    # messages 是对话上下文。
    # system 定义助手行为，user 是用户输入，assistant 是模型历史回答。
    messages = [
        {"role": "system", "content": "你是一个耐心的 Python 和 Agent 学习助手。"}
    ]

    print("OpenAI CLI Chat. 输入 exit 退出。")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break
        if not user_input:
            continue

        # 多轮对话必须保存历史 messages，否则模型只知道当前这一句话。
        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
            answer = response.choices[0].message.content or ""
        except OpenAIError as exc:
            print("OpenAI API error:", exc)
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": answer})
        print("AI:", answer)


if __name__ == "__main__":
    main()
