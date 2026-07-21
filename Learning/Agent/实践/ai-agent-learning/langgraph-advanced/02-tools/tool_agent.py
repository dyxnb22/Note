"""
第 2 课：工具调用 + 最小 ReAct 循环

本课目标：
1. 理解 Tool 是普通函数；
2. 理解 Agent 先“决定调用工具”，再由 ToolNode 执行工具；
3. 理解 ReAct 的最小闭环：决策 -> 行动 -> 观察 -> 回答。

为了让你本地直接跑通，本课不用真实 LLM，而是用规则模拟“模型决定调用哪个工具”。
真实 LLM 接入时，planner 节点可以替换成 llm.bind_tools(tools).invoke(...)。

运行：
    python 02-tools/tool_agent.py
"""

from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


# ---------------------------------------------------------------------------
# 1. 定义工具
# ---------------------------------------------------------------------------
# @tool 会把普通函数包装成 LangChain/LangGraph 能识别的工具。
# docstring 很重要：真实 LLM 会靠它理解什么时候应该调用这个工具。


@tool
def calculator(expression: str) -> str:
    """计算一个简单数学表达式，例如 '2 + 3 * 4'。"""
    # 学习项目里用 eval 是为了让例子短小；生产环境要换成安全表达式解析器。
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as exc:
        return f"计算失败: {exc}"


@tool
def get_weather(city: str) -> str:
    """查询城市天气。支持北京、上海、深圳。"""
    data = {
        "北京": "晴，25°C",
        "上海": "多云，22°C",
        "深圳": "小雨，28°C",
    }
    return data.get(city, f"暂时没有 {city} 的天气数据")


TOOLS = [calculator, get_weather]


# ---------------------------------------------------------------------------
# 2. 定义 State
# ---------------------------------------------------------------------------
# add_messages 是消息列表的 reducer：新消息会追加，而不是覆盖旧消息。


class ToolLessonState(TypedDict):
    messages: Annotated[list[Any], add_messages]


def _latest_user_text(state: ToolLessonState) -> str:
    """兼容 HumanMessage 和 dict 两种输入形式。"""
    message = state["messages"][-1]
    if isinstance(message, HumanMessage):
        return message.content
    if isinstance(message, dict):
        return str(message.get("content", ""))
    return str(getattr(message, "content", ""))


# ---------------------------------------------------------------------------
# 3. Planner 节点：决定要不要调用工具
# ---------------------------------------------------------------------------
# 真实 Agent 中，这一步通常由 LLM 完成。
# 这里用规则模拟，方便你专注理解 ToolNode 的工作方式。


def planner(state: ToolLessonState) -> dict:
    user_text = _latest_user_text(state)
    tool_calls = []

    if "天气" in user_text:
        if "北京" in user_text:
            tool_calls.append(
                {
                    "name": "get_weather",
                    "args": {"city": "北京"},
                    "id": "call_weather_beijing",
                }
            )
        if "上海" in user_text:
            tool_calls.append(
                {
                    "name": "get_weather",
                    "args": {"city": "上海"},
                    "id": "call_weather_shanghai",
                }
            )

    if "温差" in user_text:
        tool_calls.append(
            {
                "name": "calculator",
                "args": {"expression": "25 - 22"},
                "id": "call_temperature_gap",
            }
        )

    if not tool_calls:
        return {"messages": [AIMessage(content="这个问题不需要调用工具，我可以直接回答。")]}

    # AIMessage 的 tool_calls 字段表示“我想调用这些工具”。
    # 注意：这里还没有真正执行工具，执行发生在 ToolNode。
    return {"messages": [AIMessage(content="", tool_calls=tool_calls)]}


def should_use_tools(state: ToolLessonState) -> str:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return END


# ---------------------------------------------------------------------------
# 4. Responder 节点：读取工具结果，生成最终回答
# ---------------------------------------------------------------------------


def responder(state: ToolLessonState) -> dict:
    tool_results = [
        message
        for message in state["messages"]
        if isinstance(message, ToolMessage)
    ]

    if not tool_results:
        return {"messages": [AIMessage(content="没有工具结果可总结。")]}

    lines = ["工具执行结果："]
    for result in tool_results:
        lines.append(f"- {result.name}: {result.content}")

    lines.append("结论：北京 25°C，上海 22°C，温差 3°C。")
    return {"messages": [AIMessage(content="\n".join(lines))]}


# ---------------------------------------------------------------------------
# 5. 组装 Graph
# ---------------------------------------------------------------------------


def build_graph():
    graph = StateGraph(ToolLessonState)

    graph.add_node("planner", planner)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_node("responder", responder)

    graph.add_edge(START, "planner")
    graph.add_conditional_edges("planner", should_use_tools)
    graph.add_edge("tools", "responder")
    graph.add_edge("responder", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    result = app.invoke(
        {
            "messages": [
                HumanMessage(content="北京和上海今天天气怎么样？温差是多少？")
            ]
        }
    )

    print("=== 第 2 课输出 ===")
    for message in result["messages"]:
        role = message.type if hasattr(message, "type") else "unknown"
        content = getattr(message, "content", "")
        if content:
            print(f"[{role}] {content}")
