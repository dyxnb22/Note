from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class WorkflowState(TypedDict):
    user_input: str
    normalized_input: str
    answer: str


def receive_input(state: WorkflowState) -> dict:
    """Node 1：接收并清洗用户输入。

    LangGraph 叫 Graph，是因为它把流程表达成“节点 + 边”。
    每个节点只处理一小步，节点之间通过 State 传递数据。
    """
    return {"normalized_input": state["user_input"].strip()}


def generate_reply(state: WorkflowState) -> dict:
    """Node 2：基于 State 生成回复。"""
    text = state["normalized_input"]
    return {"answer": f"我收到了：{text}。这是 LangGraph 工作流生成的回复。"}


def build_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("receive_input", receive_input)
    graph.add_node("generate_reply", generate_reply)

    # Edge 决定节点执行顺序。普通函数调用也能串流程，
    # 但图结构更适合以后加入条件路由、工具、记忆和中断。
    graph.add_edge(START, "receive_input")
    graph.add_edge("receive_input", "generate_reply")
    graph.add_edge("generate_reply", END)
    return graph.compile()


def main() -> None:
    app = build_graph()
    result = app.invoke(
        {
            "user_input": "  第一次学习 LangGraph  ",
            "normalized_input": "",
            "answer": "",
        }
    )
    print(result["answer"])


if __name__ == "__main__":
    main()
