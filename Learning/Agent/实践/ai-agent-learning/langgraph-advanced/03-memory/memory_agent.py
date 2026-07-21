"""
第 3 课：记忆机制 + Checkpointer

本课目标：
1. 理解 messages 如何作为短期记忆；
2. 理解 checkpointer 如何按 thread_id 保存状态；
3. 理解“同一个 thread_id 恢复历史，不同 thread_id 隔离历史”。

运行：
    python 03-memory/memory_agent.py
"""

from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class MemoryState(TypedDict):
    messages: Annotated[list[Any], add_messages]
    remembered_name: str


def _latest_user_text(state: MemoryState) -> str:
    message = state["messages"][-1]
    if isinstance(message, HumanMessage):
        return message.content
    if isinstance(message, dict):
        return str(message.get("content", ""))
    return str(getattr(message, "content", ""))


def memory_node(state: MemoryState) -> dict:
    """一个极简记忆节点：从用户输入中提取名字，并在后续问题中使用。"""
    text = _latest_user_text(state)

    # 先处理提问，再处理“我叫...”。
    # 因为“我叫什么名字”也包含“我叫”两个字，顺序反了会误判。
    if "我叫什么" in text:
        name = state.get("remembered_name", "")
        if name:
            answer = f"你叫{name}。这是从当前 thread_id 的历史状态里恢复出来的。"
        else:
            answer = "我还不知道你的名字。换一个 thread_id 时，历史记忆不会自动共享。"
        return {"messages": [AIMessage(content=answer)]}

    # 为了让学习重点放在 Checkpointer，这里用非常简单的规则提取名字。
    if "我叫" in text:
        name = text.split("我叫", 1)[1].split("，", 1)[0].split(",", 1)[0].strip(" 。")
        return {
            "remembered_name": name,
            "messages": [AIMessage(content=f"记住了，你叫{name}。")],
        }

    return {"messages": [AIMessage(content="我会把这轮消息保存到当前线程。")]}


def build_graph():
    graph = StateGraph(MemoryState)
    graph.add_node("memory", memory_node)
    graph.add_edge(START, "memory")
    graph.add_edge("memory", END)

    # MemorySaver 是内存版 checkpointer，适合教学和单进程 demo。
    # 生产环境可以换成 SQLite/Postgres checkpointer。
    return graph.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    app = build_graph()

    thread_a = {"configurable": {"thread_id": "user-a"}}
    thread_b = {"configurable": {"thread_id": "user-b"}}

    print("=== 第 3 课输出 ===")

    result = app.invoke(
        {
            "messages": [HumanMessage(content="我叫小明，记住这个名字。")],
            "remembered_name": "",
        },
        config=thread_a,
    )
    print("[user-a 第 1 轮]", result["messages"][-1].content)

    # 第二轮不需要手动传入 remembered_name。
    # LangGraph 会根据 thread_id 找到上一轮保存的状态。
    result = app.invoke(
        {"messages": [HumanMessage(content="我叫什么名字？")]},
        config=thread_a,
    )
    print("[user-a 第 2 轮]", result["messages"][-1].content)

    result = app.invoke(
        {
            "messages": [HumanMessage(content="我叫什么名字？")],
            "remembered_name": "",
        },
        config=thread_b,
    )
    print("[user-b 新线程]", result["messages"][-1].content)
