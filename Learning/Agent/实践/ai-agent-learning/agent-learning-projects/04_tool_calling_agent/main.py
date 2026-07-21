import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def get_weather(city: str) -> dict[str, str]:
    """天气查询工具。这里用 mock 数据，重点是学习 Tool Calling 流程。"""
    data = {
        "香港": {"temperature": "26°C", "condition": "Cloudy"},
        "北京": {"temperature": "24°C", "condition": "Sunny"},
        "上海": {"temperature": "22°C", "condition": "Rainy"},
    }
    weather = data.get(city, {"temperature": "unknown", "condition": "unknown"})
    return {"city": city, **weather} # **weather 叫做 字典解包


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名，例如 香港"}
                },
                "required": ["city"],
            },
        },
    }
]


def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Python 程序负责真正执行工具函数。LLM 本身不会执行代码。"""
    if name == "get_weather":
        return get_weather(city=arguments["city"])
    return {"error": f"unknown tool: {name}"}


def main() -> None:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "你是一个会在需要时调用工具的助手。"},
        {"role": "user", "content": "香港天气怎么样？"},
    ]

    first = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
    )
    assistant_message = first.choices[0].message
    messages.append(assistant_message.model_dump(exclude_none=True))

    # 模型只是决定“要调用哪个工具 + 参数是什么”。
    # tool_calls 不为空时，我们读取参数并在 Python 里执行函数。
    for tool_call in assistant_message.tool_calls or []:
        args = json.loads(tool_call.function.arguments)
        result = execute_tool(tool_call.function.name, args)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            }
        )

    final = client.chat.completions.create(model=model, messages=messages)
    print(final.choices[0].message.content)


if __name__ == "__main__":
    main()
