"""
第 4 课：多 Agent 协作

本课目标：
1. 理解一个 Agent 可以是一个子图；
2. 理解父图可以把子图当成普通节点；
3. 理解多 Agent 的核心是职责拆分，而不是简单堆数量。

运行：
    python 04-multi-agent/multi_agent.py
"""

from typing import Annotated, Any, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class TeamState(TypedDict):
    messages: Annotated[list[Any], add_messages]
    analysis: str
    plan: str
    final_answer: str


def _latest_user_text(state: TeamState) -> str:
    message = state["messages"][-1]
    if isinstance(message, HumanMessage):
        return message.content
    if isinstance(message, dict):
        return str(message.get("content", ""))
    return str(getattr(message, "content", ""))


# ---------------------------------------------------------------------------
# 子图 1：Analyzer Agent
# ---------------------------------------------------------------------------


def analyze_requirement(state: TeamState) -> dict:
    """Analyzer 只负责拆解问题，不负责制定执行计划。"""
    task = _latest_user_text(state)
    analysis = "\n".join(
        [
            f"需求：{task}",
            "关键点 1：需要明确 Agent 要解决的具体任务。",
            "关键点 2：需要设计 State，避免状态字段混乱。",
            "关键点 3：需要决定哪些能力做成工具，哪些留给模型判断。",
        ]
    )
    return {"analysis": analysis}


def build_analyzer():
    graph = StateGraph(TeamState)
    graph.add_node("analyze_requirement", analyze_requirement)
    graph.add_edge(START, "analyze_requirement")
    graph.add_edge("analyze_requirement", END)
    return graph.compile()


# ---------------------------------------------------------------------------
# 子图 2：Planner Agent
# ---------------------------------------------------------------------------


def make_plan(state: TeamState) -> dict:
    """Planner 只基于 analysis 生成步骤计划。"""
    plan = "\n".join(
        [
            "建议计划：",
            "1. 先做最小可运行图，验证状态流转。",
            "2. 再加入工具调用，形成 ReAct 闭环。",
            "3. 然后加入记忆、人工审批和错误处理。",
            "4. 最后把这些能力合成一个可展示的项目。",
        ]
    )
    return {"plan": plan}


def build_planner():
    graph = StateGraph(TeamState)
    graph.add_node("make_plan", make_plan)
    graph.add_edge(START, "make_plan")
    graph.add_edge("make_plan", END)
    return graph.compile()


# ---------------------------------------------------------------------------
# 父图：Team Supervisor
# ---------------------------------------------------------------------------


def write_final_answer(state: TeamState) -> dict:
    """Supervisor 汇总多个 Agent 的结果，形成最终答复。"""
    final_answer = f"{state['analysis']}\n\n{state['plan']}"
    return {"final_answer": final_answer}


def build_team():
    graph = StateGraph(TeamState)

    # 子图可以直接作为节点挂到父图上。
    graph.add_node("analyzer", build_analyzer())
    graph.add_node("planner", build_planner())
    graph.add_node("final_writer", write_final_answer)

    graph.add_edge(START, "analyzer")
    graph.add_edge("analyzer", "planner")
    graph.add_edge("planner", "final_writer")
    graph.add_edge("final_writer", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_team()

    result = app.invoke(
        {
            "messages": [HumanMessage(content="我想在项目里引入 AI Agent。")],
            "analysis": "",
            "plan": "",
            "final_answer": "",
        }
    )

    print("=== 第 4 课输出 ===")
    print(result["final_answer"])
