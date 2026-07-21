"""DevPilot Graph 组装。

流程：
START -> Router -> Analyzer -> Fixer -> Approval -> Reviewer -> PR Creator -> END
                                   └── 审批拒绝则直接 END
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agents import analyzer, approval_node, fixer, pr_creator, reviewer, router
from state import DevPilotState


def route_after_approval(state: DevPilotState) -> str:
    """审批通过进入 Reviewer；拒绝则结束。"""
    if state.get("approved"):
        return "reviewer"
    return END


def build_graph():
    graph = StateGraph(DevPilotState)

    graph.add_node("router", router)
    graph.add_node("analyzer", analyzer)
    graph.add_node("fixer", fixer)
    graph.add_node("approval", approval_node)
    graph.add_node("reviewer", reviewer)
    graph.add_node("pr_creator", pr_creator)

    graph.add_edge(START, "router")
    graph.add_edge("router", "analyzer")
    graph.add_edge("analyzer", "fixer")
    graph.add_edge("fixer", "approval")
    graph.add_conditional_edges("approval", route_after_approval)
    graph.add_edge("reviewer", "pr_creator")
    graph.add_edge("pr_creator", END)

    # MVP 使用内存 checkpointer，避免 SQLite 依赖影响学习。
    return graph.compile(checkpointer=MemorySaver())
