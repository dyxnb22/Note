"""
第 1 课：最小可运行 LangGraph

本课目标：
1. 理解 State、Node、Edge 的关系；
2. 理解普通边和条件边；
3. 不依赖 LLM，先把“流程图会流转”这件事学明白。

运行：
    python 01-basics/hello_graph.py
"""

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


# ---------------------------------------------------------------------------
# 1. 定义 State
# ---------------------------------------------------------------------------
# State 是整个图里流动的数据。每个节点都能读取 State，并返回“要更新的字段”。
# TypedDict 的好处是：字段结构清楚，IDE 和类型检查也更友好。


class LessonState(TypedDict):
    user_input: str
    intent: str
    answer: str


# ---------------------------------------------------------------------------
# 2. 定义节点
# ---------------------------------------------------------------------------
# 节点就是普通 Python 函数。签名通常是：
#     node(state) -> dict
# 返回的 dict 会被 LangGraph 合并回 State。


def classify_intent(state: LessonState) -> dict:
    """根据用户输入做一个非常简单的意图分类。"""
    text = state["user_input"].lower()

    if "langgraph" in text or "agent" in text:
        intent = "agent_question"
    else:
        intent = "general_question"

    return {"intent": intent}


def answer_agent_question(state: LessonState) -> dict:
    """回答 Agent 相关问题。"""
    return {
        "answer": (
            "LangGraph 可以把 Agent 拆成状态、节点和边，"
            "让复杂流程变得可观察、可控制。"
        )
    }


def answer_general_question(state: LessonState) -> dict:
    """回答普通问题。"""
    return {"answer": "这是一个普通问题。下一课我们会加入工具调用。"}


# ---------------------------------------------------------------------------
# 3. 定义路由函数
# ---------------------------------------------------------------------------
# 条件边会调用路由函数。路由函数只负责返回“下一站节点名”。


def route_by_intent(state: LessonState) -> Literal["agent_answer", "general_answer"]:
    if state["intent"] == "agent_question":
        return "agent_answer"
    return "general_answer"


# ---------------------------------------------------------------------------
# 4. 组装 Graph
# ---------------------------------------------------------------------------


def build_graph():
    graph = StateGraph(LessonState)

    graph.add_node("classify", classify_intent)
    graph.add_node("agent_answer", answer_agent_question)
    graph.add_node("general_answer", answer_general_question)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", route_by_intent)
    graph.add_edge("agent_answer", END)
    graph.add_edge("general_answer", END)

    return graph.compile()


# ---------------------------------------------------------------------------
# 5. 运行示例
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    app = build_graph()

    result = app.invoke(
        {
            "user_input": "什么是 LangGraph Agent？",
            "intent": "",
            "answer": "",
        }
    )

    print("=== 第 1 课输出 ===")
    print("意图:", result["intent"])
    print("回答:", result["answer"])
