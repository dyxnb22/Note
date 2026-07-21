from datetime import datetime


def run_agent(message: str) -> str:
    """一个假的 Agent Service。

    真实项目中，这里可以调用 OpenAI、Tool Calling 或 LangGraph。
    先把 Agent 包成函数，后面接 FastAPI 会很自然。
    """
    if "天气" in message:
        return "香港今天多云，26°C。"
    if "时间" in message:
        return f"当前时间是 {datetime.now().isoformat(timespec='seconds')}"
    return f"收到你的问题：{message}"
