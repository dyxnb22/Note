from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


@tool
def get_weather(city: str) -> str:
    """查询城市天气。支持香港、北京、上海。"""
    data = {"香港": "多云，26°C", "北京": "晴，24°C", "上海": "小雨，22°C"}
    return data.get(city, f"没有 {city} 的天气数据")


@tool
def calculator(expression: str) -> str:
    """计算简单数学表达式，例如 '26 - 22'。"""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as exc:
        return f"计算失败: {exc}"


TOOLS = [get_weather, calculator]


class AgentState(TypedDict):
    messages: Annotated[list[Any], add_messages]


def planner(state: AgentState) -> dict:
    """模拟 LLM 判断是否需要工具。

    真实项目中，这里会替换成 llm.bind_tools(TOOLS).invoke(messages)。
    Tool Node 负责执行工具，Conditional Edge 负责判断下一步走工具还是结束。
    """
    user_text = state["messages"][-1].content
    tool_calls = []

    if "香港" in user_text and "天气" in user_text:
        tool_calls.append(
            {"name": "get_weather", "args": {"city": "香港"}, "id": "weather_hk"}
        )
    if "上海" in user_text and "天气" in user_text:
        tool_calls.append(
            {"name": "get_weather", "args": {"city": "上海"}, "id": "weather_sh"}
        )
    if "温差" in user_text:
        tool_calls.append(
            {"name": "calculator", "args": {"expression": "26 - 22"}, "id": "gap"}
        )

    if tool_calls:
        return {"messages": [AIMessage(content="", tool_calls=tool_calls)]}
    return {"messages": [AIMessage(content="这个问题不需要工具。")]}


def route_after_planner(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


def final_answer(state: AgentState) -> dict:
    observations = [m for m in state["messages"] if isinstance(m, ToolMessage)]
    lines = ["工具观察结果："]
    for item in observations:
        lines.append(f"- {item.name}: {item.content}")
    lines.append("最终答案：香港 26°C，上海 22°C，温差 4°C。")
    return {"messages": [AIMessage(content="\n".join(lines))]}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("planner", planner)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_node("final_answer", final_answer)
    graph.add_edge(START, "planner")
    graph.add_conditional_edges("planner", route_after_planner)
    graph.add_edge("tools", "final_answer")
    graph.add_edge("final_answer", END)
    return graph.compile()


def main() -> None:
    app = build_graph()
    result = app.invoke(
        {"messages": [HumanMessage(content="香港和上海天气怎么样？温差是多少？")]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
