"""无外部依赖的最小 Agent Loop 练习。"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CallRequest:
    instructions: str
    user_input: str
    tool_names: list[str]
    tool_results: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ToolCall:
    call_id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ModelResult:
    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str = "unknown"
    usage: dict[str, int] | None = None
    request_id: str | None = None


class MockProvider:
    """返回固定的 Provider 原始格式，模拟外部 API。"""

    def complete(self, request: CallRequest) -> dict[str, Any]:
        if not request.tool_results:
            return {
                "request_id": "req_1",
                "kind": "tool_call",
                "call_id": "call_1",
                "name": "read_file",
                "arguments": {"path": "src/app.py"},
                "usage": {"input_tokens": 80, "output_tokens": 15},
            }

        content = request.tool_results[-1]
        if content.get("ok"):
            return {
                "request_id": "req_2",
                "kind": "text",
                "text": "我读取了 src/app.py。基于文件内容，可以继续分析其中的错误；本轮没有修改文件。",
                "usage": {"input_tokens": 120, "output_tokens": 25},
            }
        return {
            "request_id": "req_2",
            "kind": "text",
            "text": f"无法继续：工具返回 {content['error_code']}。",
            "usage": {"input_tokens": 100, "output_tokens": 15},
        }


def adapt(raw: dict[str, Any]) -> ModelResult:
    """把 Provider 原始响应翻译成 Agent 内部结果。"""
    if raw["kind"] == "tool_call":
        return ModelResult(
            tool_calls=[
                ToolCall(
                    call_id=raw["call_id"],
                    name=raw["name"],
                    arguments=raw["arguments"],
                )
            ],
            finish_reason="tool_call",
            usage=raw.get("usage"),
            request_id=raw.get("request_id"),
        )
    return ModelResult(
        text=raw.get("text"),
        finish_reason="completed",
        usage=raw.get("usage"),
        request_id=raw.get("request_id"),
    )


FILES = {"src/app.py": "def divide(a, b):\n    return a / b\n"}


def execute_tool(call: ToolCall) -> dict[str, Any]:
    """最小执行器：先检查工具名和路径，再读取内存文件。"""
    if call.name != "read_file":
        return {"call_id": call.call_id, "ok": False, "error_code": "unknown_tool"}

    path = call.arguments.get("path")
    if path not in FILES:
        return {"call_id": call.call_id, "ok": False, "error_code": "file_not_found"}

    return {"call_id": call.call_id, "ok": True, "value": FILES[path]}


def run() -> None:
    provider = MockProvider()
    request = CallRequest(
        instructions="你是只读代码分析助手，不得修改文件。",
        user_input="请分析 src/app.py 中的错误。",
        tool_names=["read_file"],
    )
    trace: list[dict[str, Any]] = []

    for step in range(1, 4):
        raw = provider.complete(request)
        result = adapt(raw)
        trace.append({"step": step, "request_id": result.request_id, "reason": result.finish_reason})
        print(f"\n第 {step} 轮: {trace[-1]}")

        if result.text is not None:
            print("最终文本:", result.text)
            print("Trace:", trace)
            return

        for call in result.tool_calls:
            print("模型提出 ToolCall:", call)
            tool_result = execute_tool(call)
            print("执行器返回 ToolResult:", tool_result)
            request.tool_results.append(tool_result)

    print("已停止: budget_exhausted")


if __name__ == "__main__":
    run()
