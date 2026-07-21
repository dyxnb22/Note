"""
第 5 课：生产化最小闭环

本课目标：
1. 理解关键动作前为什么需要人工审批；
2. 理解 interrupt 如何暂停图执行；
3. 理解 Command(resume=...) 如何恢复图执行；
4. 理解 stream 如何观察每一步事件。

运行：
    python 05-production/production.py
"""

from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt


class ProductionState(TypedDict):
    messages: Annotated[list[Any], add_messages]
    proposed_action: str
    approved: bool


def propose_action(state: ProductionState) -> dict:
    """生成一个待审批动作。真实项目里这里可能是写文件、发 PR、执行命令等。"""
    return {
        "proposed_action": "为当前项目生成一份学习计划报告",
        "messages": [AIMessage(content="我准备生成学习计划报告，需要人工确认。")],
    }


def approval_gate(state: ProductionState) -> dict:
    """人工审批节点：执行到这里会暂停，等待外部传入 approve/reject。"""
    decision = interrupt(
        {
            "question": "是否批准执行 proposed_action？",
            "proposed_action": state["proposed_action"],
        }
    )

    approved = bool(decision.get("approved")) if isinstance(decision, dict) else False
    return {"approved": approved}


def execute_action(state: ProductionState) -> dict:
    """根据审批结果决定是否执行。"""
    if state["approved"]:
        content = f"已执行：{state['proposed_action']}"
    else:
        content = "审批未通过，已停止执行。"
    return {"messages": [AIMessage(content=content)]}


def build_graph():
    graph = StateGraph(ProductionState)

    graph.add_node("propose", propose_action)
    graph.add_node("approval", approval_gate)
    graph.add_node("execute", execute_action)

    graph.add_edge(START, "propose")
    graph.add_edge("propose", "approval")
    graph.add_edge("approval", "execute")
    graph.add_edge("execute", END)

    return graph.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    app = build_graph()
    config = {"configurable": {"thread_id": "production-demo"}}

    print("=== 第 5 课：第一次执行，直到 interrupt 暂停 ===")
    for event in app.stream(
        {
            "messages": [HumanMessage(content="请准备一个需要审批的动作。")],
            "proposed_action": "",
            "approved": False,
        },
        config=config,
    ):
        print(event)

    print("\n=== 恢复执行：模拟人工批准 ===")
    for event in app.stream(Command(resume={"approved": True}), config=config):
        print(event)
