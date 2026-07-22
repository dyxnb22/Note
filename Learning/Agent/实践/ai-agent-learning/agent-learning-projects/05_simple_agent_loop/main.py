import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def get_weather(city: str) -> dict[str, str]:
    return {"city": city, "temperature": "26°C", "condition": "Cloudy"}


def calculate(expression: str) -> dict[str, str]:
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {"expression": expression, "result": str(result)}
    except Exception as exc:
        return {"error": str(exc)}


def get_current_time() -> dict[str, str]:
    return {"current_time": datetime.now().isoformat(timespec="seconds")}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询城市天气",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算简单数学表达式",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前时间",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def run_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "get_weather":
        return get_weather(args["city"])
    if name == "calculate":
        return calculate(args["expression"])
    if name == "get_current_time":
        return get_current_time()
    return {"error": f"unknown tool: {name}"}


def main() -> None:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.environ["OPENAI_MODEL"]

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "你是一个会使用工具解决问题的 Agent。"}
    ]

    print("Simple Agent Loop. 输入 exit 退出。")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        messages.append({"role": "user", "content": user_input})

        # Agent Loop 和普通 ChatBot 的区别：
        # ChatBot 通常一次回答；Agent 会在“思考、行动、观察”之间循环。
        for _ in range(3):
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
            )
            assistant_message = response.choices[0].message
            messages.append(assistant_message.model_dump(exclude_none=True))

            if not assistant_message.tool_calls:
                print("AI:", assistant_message.content)
                break

            for tool_call in assistant_message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                observation = run_tool(tool_call.function.name, args)
                # Observation 是工具执行后的结果。模型下一轮会基于 Observation 继续推理。
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(observation, ensure_ascii=False),
                    }
                )
        else:
            print("AI: 达到最大循环次数，已停止。")


if __name__ == "__main__":
    main()
