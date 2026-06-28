# Workflow 与 LangGraph

这篇文档解决一个问题：**什么时候需要图式工作流编排，LangGraph 的核心概念是什么，如何构建可恢复、可监控的 AI 工作流**。

---

## 1. 为什么需要工作流编排

简单 Agent 可以自己写 while loop：

```python
while not done:
    response = llm.call(messages)
    if response.tool_calls:
        execute_tools(response.tool_calls)
    else:
        done = True
```

但当流程变复杂时，你会遇到：

| 问题 | 表现 |
|------|------|
| 状态散落在各处 | 全局变量、函数参数到处传 |
| 分支逻辑难维护 | 大量 if-else 嵌套 |
| 失败后无法恢复 | 崩了就得从头来 |
| 人工确认难以插入 | 没有自然的暂停点 |
| 调试困难 | 不知道执行到哪步出的问题 |
| 多 Agent 协作不清楚 | 谁管谁，数据怎么传 |

**LangGraph 用图来表达工作流**：

```
State → Node → Edge → Node → END
```

把它理解成"Agent 工作流引擎"。

---

## 2. 核心概念

### State（状态）

状态是整个图的数据中心，所有节点共享同一个 state：

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # add_messages 会自动追加而不是覆盖
    task_status: str
    tool_results: list[dict]
    step_count: int
    error_log: list[str]
```

**设计原则**：
- State 要可序列化（方便 checkpoint）
- 只放需要在节点间传递的数据
- 用 `Annotated` + reducer 控制字段如何更新（追加 vs 覆盖）

### Node（节点）

节点是函数，接受 state，返回对 state 的更新：

```python
def call_llm_node(state: AgentState) -> dict:
    """调用 LLM，返回下一个 message"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=state["messages"],
        tools=tools,
    )
    return {
        "messages": [response.choices[0].message],
        "step_count": state["step_count"] + 1,
    }

def execute_tools_node(state: AgentState) -> dict:
    """执行工具调用"""
    last_message = state["messages"][-1]
    tool_results = []
    
    for tool_call in last_message.tool_calls:
        result = tool_registry.execute(
            tool_call.function.name,
            json.loads(tool_call.function.arguments),
        )
        tool_results.append({
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        })
    
    return {
        "messages": [{"role": "tool", **r} for r in tool_results],
        "tool_results": state["tool_results"] + tool_results,
    }
```

### Edge（边）

边控制节点之间的跳转：

```python
from langgraph.graph import StateGraph, END

# 无条件边
graph.add_edge("node_a", "node_b")

# 条件边（根据 state 动态决定下一个节点）
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "execute_tools"
    return END  # 没有工具调用 = 结束

graph.add_conditional_edges(
    "call_llm",
    should_continue,
    {
        "execute_tools": "execute_tools",
        END: END,
    }
)
```

---

## 3. 构建完整 Agent Graph

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# 构建图
builder = StateGraph(AgentState)

# 添加节点
builder.add_node("call_llm", call_llm_node)
builder.add_node("execute_tools", execute_tools_node)

# 设置入口
builder.set_entry_point("call_llm")

# 添加边
builder.add_conditional_edges(
    "call_llm",
    should_continue,
    {"execute_tools": "execute_tools", END: END},
)
builder.add_edge("execute_tools", "call_llm")  # 执行完工具，回到 LLM

# 编译（加 checkpointer 支持持久化）
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# 运行
config = {"configurable": {"thread_id": "task-123"}}
result = graph.invoke(
    {"messages": [{"role": "user", "content": "帮我查一下订单 #456 的状态"}]},
    config=config,
)
```

---

## 4. Checkpoint 与状态持久化

Checkpoint 让 Agent 可以：
- 断点续传（程序崩了从上次状态继续）
- 时间旅行调试（回到任意历史状态）
- 并发运行多个任务（每个任务独立的 thread_id）

```python
# 内存 Checkpointer（开发用，进程重启丢失）
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

# PostgreSQL Checkpointer（生产用）
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string("postgresql://...")

# SQLite Checkpointer（本地持久化）
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("./agent_state.db")

# 编译时传入
graph = builder.compile(checkpointer=checkpointer)
```

### 恢复执行

```python
# 同一个 thread_id = 同一个任务上下文
config = {"configurable": {"thread_id": "task-123"}}

# 查看当前状态
state = graph.get_state(config)
print(state.values)

# 从当前状态继续执行
result = graph.invoke(None, config=config)
```

---

## 5. Human-in-the-loop（中断与恢复）

```python
# 在某些节点前中断，等待人工确认
graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["sensitive_action"],  # 在这个节点前暂停
)

# 第一次运行：执行到 sensitive_action 前暂停
config = {"configurable": {"thread_id": "task-456"}}
result = graph.invoke(initial_input, config=config)

# 此时 Agent 暂停，等待人工审核
current_state = graph.get_state(config)
print("待审核操作:", current_state.values["pending_action"])

# 人工审核后，可以选择：
# 1. 直接继续（同意）
graph.invoke(None, config=config)

# 2. 修改 state 后继续（修正）
graph.update_state(config, {"pending_action": modified_action})
graph.invoke(None, config=config)

# 3. 中止任务
# 不调用 invoke，让 thread 超时或显式标记失败
```

---

## 6. 条件路由与分支

```python
def route_by_intent(state: AgentState) -> str:
    """根据用户意图路由到不同处理路径"""
    intent = state.get("classified_intent", "unknown")
    
    routing = {
        "order_query": "order_agent",
        "complaint": "complaint_handler",
        "technical": "tech_support",
        "unknown": "clarification",
    }
    return routing.get(intent, "clarification")

builder.add_conditional_edges(
    "intent_classifier",
    route_by_intent,
    {
        "order_agent": "order_agent",
        "complaint_handler": "complaint_handler",
        "tech_support": "tech_support",
        "clarification": "clarification",
    }
)
```

---

## 7. 子图（Subgraph）

复杂工作流可以把一部分逻辑封装成子图，提高可维护性：

```python
# 定义子图
research_builder = StateGraph(ResearchState)
research_builder.add_node("search", search_node)
research_builder.add_node("summarize", summarize_node)
research_builder.set_entry_point("search")
research_builder.add_edge("search", "summarize")
research_builder.add_edge("summarize", END)
research_graph = research_builder.compile()

# 在主图里使用子图
main_builder = StateGraph(MainState)
main_builder.add_node("research", research_graph)  # 子图作为节点
main_builder.add_node("write_report", write_node)
main_builder.set_entry_point("research")
main_builder.add_edge("research", "write_report")
```

---

## 8. 流式输出（Streaming）

```python
# 流式接收图的执行过程
for chunk in graph.stream(initial_input, config=config):
    for node_name, node_output in chunk.items():
        print(f"节点 {node_name} 输出:", node_output)

# 流式接收 LLM token
for chunk in graph.stream(
    initial_input,
    config=config,
    stream_mode="messages",  # 流式 LLM token
):
    for message, metadata in chunk:
        if hasattr(message, "content") and message.content:
            print(message.content, end="", flush=True)
```

---

## 9. 常见模式与最佳实践

| 实践 | 原因 |
|------|------|
| State 用 TypedDict 或 Pydantic | 类型安全，IDE 有补全，减少运行时错误 |
| 每个节点只做一件事 | 单一职责，方便测试和替换 |
| 生产环境用持久化 Checkpointer | MemorySaver 进程重启后丢失 |
| 设置 recursion_limit | 防止无限循环，默认 25 |
| 在节点里记录日志 | 方便 debug，知道每步做了什么 |

```python
# 设置递归限制
config = {
    "configurable": {"thread_id": "task-123"},
    "recursion_limit": 30,
}
```

---

## 10. 面试高频

**Q：LangGraph 和 LangChain 的区别是什么？**

> LangChain 提供的是线性链（Chain），步骤固定从 A 到 B 到 C。LangGraph 用图结构，支持条件路由、循环、分支、并行节点，可以表达任意复杂的 Agent 工作流。LangGraph 是在 LangChain 基础上专门为 Agent 场景设计的编排框架。如果任务是固定线性步骤，LangChain 够用；如果有条件分支、循环、需要 checkpoint，用 LangGraph。

**Q：什么是 Checkpoint，为什么重要？**

> Checkpoint 是在图执行过程中保存 state 快照的机制。重要性：一是容错——程序崩了可以从上次状态恢复，不用从头来；二是 Human-in-the-loop——在关键节点暂停，等待人工确认后继续；三是调试——可以回到任意历史状态检查问题。生产环境必须用持久化 Checkpointer（PostgreSQL/SQLite），开发环境可以用 MemorySaver。

**Q：如何实现 Human-in-the-loop？**

> 使用 `interrupt_before` 在特定节点前暂停图执行。图暂停后，当前 state 保存在 checkpointer 里，人工可以查看 state、决定是否继续或修改 state。同意后调用 `graph.invoke(None, config)` 继续；需要修改则先 `graph.update_state()` 再继续。这个模式特别适合涉及真实副作用（发邮件、写数据库）的操作——人工确认后再真正执行。
