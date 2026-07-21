from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class MemoryState(TypedDict):
    messages: Annotated[list[Any], add_messages]
    memory: dict[str, str]


def memory_agent(state: MemoryState) -> dict:
    """一个最小记忆 Agent。

    messages 是对话历史，适合保存“说过什么”。
    memory 是提取后的结构化信息，适合保存“应该记住什么”。
    """
    text = state["messages"][-1].content
    memory = dict(state.get("memory", {}))

    if "我叫什么" in text:
        name = memory.get("name")
        answer = f"你叫 {name}。" if name else "我还不知道你的名字。"
        return {"messages": [AIMessage(content=answer)], "memory": memory}

    if "我叫" in text:
        name = text.split("我叫", 1)[1].strip(" 。")
        memory["name"] = name
        return {"messages": [AIMessage(content=f"我记住了，你叫 {name}。")], "memory": memory}

    return {"messages": [AIMessage(content="我会记住重要信息。")], "memory": memory}


def build_graph():
    graph = StateGraph(MemoryState)
    graph.add_node("memory_agent", memory_agent)
    graph.add_edge(START, "memory_agent")
    graph.add_edge("memory_agent", END)

    # Checkpointer 根据 thread_id 保存状态。它让多轮调用共享同一份 State。
    return graph.compile(checkpointer=MemorySaver())


def main() -> None:
    app = build_graph()
    config = {"configurable": {"thread_id": "student-001"}}

    first = app.invoke(
        {"messages": [HumanMessage(content="我叫 Tom")], "memory": {}},
        config=config,
    )
    print(first["messages"][-1].content)

    second = app.invoke(
        {"messages": [HumanMessage(content="我叫什么？")]},
        config=config,
    )
    print(second["messages"][-1].content)


if __name__ == "__main__":
    main()
