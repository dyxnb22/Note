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

## 无条件边
graph.add_edge("node_a", "node_b")

## 条件边（根据 state 动态决定下一个节点）
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

## 构建图
builder = StateGraph(AgentState)

## 添加节点
builder.add_node("call_llm", call_llm_node)
builder.add_node("execute_tools", execute_tools_node)

## 设置入口
builder.set_entry_point("call_llm")

## 添加边
builder.add_conditional_edges(
"call_llm",
should_continue,
{"execute_tools": "execute_tools", END: END},
)
builder.add_edge("execute_tools", "call_llm")  # 执行完工具，回到 LLM

## 编译（加 checkpointer 支持持久化）
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

## 运行
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
## 内存 Checkpointer（开发用，进程重启丢失）
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

## PostgreSQL Checkpointer（生产用）
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string("postgresql://...")

## SQLite Checkpointer（本地持久化）
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("./agent_state.db")

## 编译时传入
graph = builder.compile(checkpointer=checkpointer)
```

### 恢复执行

```python
## 同一个 thread_id = 同一个任务上下文
config = {"configurable": {"thread_id": "task-123"}}

## 查看当前状态
state = graph.get_state(config)
print(state.values)

## 从当前状态继续执行
result = graph.invoke(None, config=config)
```

---

## 5. Human-in-the-loop（中断与恢复）

```python
## 在某些节点前中断，等待人工确认
graph = builder.compile(
checkpointer=memory,
interrupt_before=["sensitive_action"],  # 在这个节点前暂停
)

## 第一次运行：执行到 sensitive_action 前暂停
config = {"configurable": {"thread_id": "task-456"}}
result = graph.invoke(initial_input, config=config)

## 此时 Agent 暂停，等待人工审核
current_state = graph.get_state(config)
print("待审核操作:", current_state.values["pending_action"])

## 人工审核后，可以选择：
## 1. 直接继续（同意）
graph.invoke(None, config=config)

## 2. 修改 state 后继续（修正）
graph.update_state(config, {"pending_action": modified_action})
graph.invoke(None, config=config)

## 3. 中止任务
## 不调用 invoke，让 thread 超时或显式标记失败
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
## 定义子图
research_builder = StateGraph(ResearchState)
research_builder.add_node("search", search_node)
research_builder.add_node("summarize", summarize_node)
research_builder.set_entry_point("search")
research_builder.add_edge("search", "summarize")
research_builder.add_edge("summarize", END)
research_graph = research_builder.compile()

## 在主图里使用子图
main_builder = StateGraph(MainState)
main_builder.add_node("research", research_graph)  # 子图作为节点
main_builder.add_node("write_report", write_node)
main_builder.set_entry_point("research")
main_builder.add_edge("research", "write_report")
```

---

## 8. 流式输出（Streaming）

```python
## 流式接收图的执行过程
for chunk in graph.stream(initial_input, config=config):
for node_name, node_output in chunk.items():
    print(f"节点 {node_name} 输出:", node_output)

## 流式接收 LLM token
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
## 设置递归限制
config = {
"configurable": {"thread_id": "task-123"},
"recursion_limit": 30,
}
```

---

## 10. 后台任务 + 通知注入模式

Agent 在处理用户请求的同时，需要运行耗时的后台工作（文件分析、远程 API 调用）：

```python
import threading
import queue

background_results: queue.Queue = queue.Queue()
background_lock = threading.Lock()

def spawn_background_task(task_fn: callable, *args):
    """在后台线程启动任务，完成后把结果放入队列"""
    def worker():
        try:
            result = task_fn(*args)
        except Exception as e:
            result = f"Error: {e}"
        background_results.put({
            "task_id": generate_id(),
            "result": result,
            "completed_at": datetime.utcnow().isoformat(),
        })
    threading.Thread(target=worker, daemon=True).start()

# 在 while True 顶部检查后台完成通知
while True:
    # 先消费所有已完成的后台任务
    while not background_results.empty():
        notification = background_results.get_nowait()
        messages.append({
            "role": "user",
            "content": f"<task_notification>{json.dumps(notification)}</task_notification>",
        })

    # 再做 LLM 调用
    response = client.messages.create(...)
```

**时序图**：

```
t=0s:  主 Agent 收到用户请求
t=0s:  spawn_background_task(analyze_codebase)
t=0s:  主 Agent 继续处理当前对话（用户感知不到后台工作在进行）
t=30s: 后台任务完成 → 结果放入 background_results 队列
t=35s: 下一次 while True 迭代 → 通知作为 user 消息注入 → 模型感知到完成
```

注意：通知是作为 `role: "user"` 消息注入，不是 `tool_result`——因为后台任务不是模型主动调用的工具。

---

## 11. Agent Teams：Mailbox 协议

多个 Agent 协作时，使用文件系统 mailbox 实现解耦通信：

```
.mailboxes/
├── lead.jsonl       ← Lead Agent 的收件箱
├── worker-1.jsonl   ← Worker-1 的收件箱
└── worker-2.jsonl   ← Worker-2 的收件箱
```

**JSONL 格式**（每行一条消息）：

```python
# worker 发送消息给 lead
def send_message(to: str, content: str):
    mailbox = Path(f".mailboxes/{to}.jsonl")
    mailbox.parent.mkdir(exist_ok=True)
    msg = {
        "from": AGENT_NAME,
        "timestamp": utc_now(),
        "content": content,
    }
    with open(mailbox, "a") as f:
        f.write(json.dumps(msg) + "\n")

# lead 读取（读取即删除，防止重复消费）
def read_inbox(agent_name: str) -> list[dict]:
    mailbox = Path(f".mailboxes/{agent_name}.jsonl")
    if not mailbox.exists():
        return []
    messages = [json.loads(line) for line in mailbox.read_text().splitlines() if line]
    mailbox.unlink()  # 读完即删
    return messages
```

**并行任务时序**：

```
Lead:     spawn worker-1（后台线程，分析 A 模块）
          spawn worker-2（后台线程，分析 B 模块）
          while True → check_inbox() → 等待两个 worker 完成

Worker-1: 分析 A 模块（4s）→ send_message("lead", "A 模块结果：...")
Worker-2: 分析 B 模块（3s）→ send_message("lead", "B 模块结果：...")

串行时间：4s + 3s = 7s
并行时间：max(4s, 3s) = 4s，节省 43%
```

**教学注意**：这是演示用的无锁 mailbox 实现，生产场景需要文件锁或 Redis。

---

## 12. 变更工作流的检查点与回滚

对于会产生真实副作用的 Agent 工作流（写文件、改数据库、推 PR），必须支持回滚或补偿操作：

```python
from dataclasses import dataclass, field

@dataclass
class WorkflowCheckpoint:
    """每个节点结束后保存的状态快照"""
    task_id: str
    node_name: str           # 当前完成的节点
    state: dict              # 序列化的工作流状态
    artifacts: dict          # 已产生的中间产物（文件路径、patch 等）
    saved_at: str

# 保存检查点示例
def run_workflow_node(node_fn, state, task_id: str, node_name: str):
    try:
        new_state = node_fn(state)
        # 节点成功 → 保存检查点
        save_checkpoint(WorkflowCheckpoint(
            task_id=task_id,
            node_name=node_name,
            state=new_state,
            artifacts=collect_artifacts(new_state),
            saved_at=utc_now(),
        ))
        return new_state
    except Exception as e:
        # 节点失败 → 可以从上一个检查点恢复
        last = load_last_checkpoint(task_id)
        if last:
            return resume_from(last)
        raise

# 从检查点恢复（人工审批中断后继续）
def resume_workflow(task_id: str):
    checkpoint = load_last_checkpoint(task_id)
    return run_workflow_from(checkpoint.node_name, checkpoint.state)
```

**设计原则**：变更操作要么有回滚机制，要么有补偿操作（audited compensation action）；检查点保存在审批暂停前，确保人工确认后能从中断处继续，而不是从头来。

---

## 13. 工作流节点注册表模式

替代大量 if-else 分支，用注册表统一管理工作流节点：

```python
from collections.abc import Callable, Awaitable

# 固定的节点执行顺序（修改需同步迁移 schema 和测试）
WORKFLOW_NODE_ORDER: tuple[str, ...] = (
    "classify_request",
    "collect_context",
    "retrieve_evidence",
    "analyze_risk",
    "plan_actions",
    "propose_output",
    "validate",
    "approval_gate",    # 高风险时暂停，等待人工审批
    "finalize",
)

# 节点 → 运行函数映射（编排器通过名字派发，不直接导入节点模块）
NODE_RUNNERS: dict[str, Callable[[WorkflowState], Awaitable[NodePatch]]] = {
    "classify_request":  classify.run,
    "collect_context":   collect.run,
    "retrieve_evidence": retrieve.run,
    "analyze_risk":      analyze.run,
    "plan_actions":      plan.run,
    "propose_output":    propose.run,
    "validate":          validate.run,
    "approval_gate":     approval.run,
    "finalize":          finalize.run,
}

class LocalOrchestrator:
    """按 WORKFLOW_NODE_ORDER 顺序执行节点，每步保存检查点"""

    async def run(self, state: WorkflowState) -> WorkflowState:
        for node_name in WORKFLOW_NODE_ORDER:
            runner = NODE_RUNNERS[node_name]
            patch = await runner(state)        # 节点返回增量 patch
            state = apply_patch(state, patch)  # 增量更新 state
            save_checkpoint(state, node_name)  # 每步存盘

            # approval_gate 可能返回 "waiting" 状态——挂起等待人工
            if state.status == "waiting_for_approval":
                return state  # 保存状态，等待人工恢复

        return state
```

**NodePatch 增量更新**：每个节点只返回它改变的部分，不返回完整 state——减少序列化开销，方便审计哪个节点改了什么：

```python
@dataclass
class NodePatch:
    """节点产出的增量更新"""
    node: str
    updates: dict          # 只包含变更字段
    artifacts: dict = field(default_factory=dict)  # 节点产生的中间产物

def apply_patch(state: WorkflowState, patch: NodePatch) -> WorkflowState:
    """把 patch 的字段合并到 state"""
    updated = asdict(state)
    updated.update(patch.updates)
    updated["completed_nodes"] = state.completed_nodes + [patch.node]
    return WorkflowState(**updated)
```

---

## 14. 任务依赖图（Task Dependency Graph）

复杂项目的任务有依赖关系，不能并行启动所有任务：

```python
from dataclasses import dataclass, field

@dataclass
class Task:
    id: str
    subject: str
    description: str
    status: str           # "pending" | "in_progress" | "completed"
    owner: str | None     # 认领者（多 Agent 场景）
    blockedBy: list[str]  # 依赖的 task id 列表

def can_start(task_id: str, tasks_dir: Path) -> bool:
    """检查所有前置依赖是否已完成"""
    task = load_task(task_id, tasks_dir)
    for dep_id in task.blockedBy:
        dep_path = tasks_dir / f"{dep_id}.json"
        if not dep_path.exists():
            return False  # 依赖任务不存在 = 阻塞
        dep = load_task(dep_id, tasks_dir)
        if dep.status != "completed":
            return False  # 依赖未完成 = 阻塞
    return True

def claim_task(task_id: str, owner: str, tasks_dir: Path) -> str:
    task = load_task(task_id, tasks_dir)
    if task.status != "pending":
        return f"Task {task_id} is {task.status}, cannot claim"
    if not can_start(task_id, tasks_dir):
        blocked_by = [d for d in task.blockedBy
                      if load_task(d, tasks_dir).status != "completed"]
        return f"Blocked by: {blocked_by}"
    task.owner = owner
    task.status = "in_progress"
    save_task(task, tasks_dir)
    return f"Claimed {task_id}"

def complete_task(task_id: str, tasks_dir: Path) -> str:
    task = load_task(task_id, tasks_dir)
    task.status = "completed"
    save_task(task, tasks_dir)
    # 报告哪些任务被解锁了
    all_tasks = list_tasks(tasks_dir)
    unblocked = [t.subject for t in all_tasks
                 if t.status == "pending" and can_start(t.id, tasks_dir)]
    msg = f"Completed {task_id}"
    if unblocked:
        msg += f"\nUnblocked: {', '.join(unblocked)}"
    return msg
```

**典型依赖图**：

```
[design_api]           ← 无依赖，可立即开始
     ↓
[implement_backend]    ← blockedBy: [design_api]
[implement_frontend]   ← blockedBy: [design_api]
     ↓              ↓
[integration_test]     ← blockedBy: [implement_backend, implement_frontend]
     ↓
[deploy]               ← blockedBy: [integration_test]
```

---

## 15. `Send` API — 动态并行 Fan-out

当你需要把同一个节点并行执行多次（每次输入不同），用 `Send`：

```python
from langgraph.types import Send
from typing import TypedDict, Annotated
import operator

class OverallState(TypedDict):
    documents: list[str]
    summaries: Annotated[list[str], operator.add]  # fan-in：所有并行结果合并

class DocState(TypedDict):
    document: str

# 每个文档单独走 summarize_node
def summarize_node(state: DocState) -> dict:
    summary = llm.invoke(f"总结：{state['document']}")
    return {"summaries": [summary.content]}

# fan-out：为每个 document 发一个 Send
def fan_out(state: OverallState) -> list[Send]:
    return [
        Send("summarize_node", {"document": doc})
        for doc in state["documents"]
    ]

builder = StateGraph(OverallState)
builder.add_node("summarize_node", summarize_node)
builder.add_conditional_edges("__start__", fan_out, ["summarize_node"])
builder.add_edge("summarize_node", "__end__")
graph = builder.compile()

# 输入 5 个文档 → 5 个 summarize_node 并行执行 → summaries 列表合并
result = graph.invoke({"documents": ["doc1...", "doc2...", "doc3..."]})
print(result["summaries"])  # 3 个摘要
```

**适合场景**：
- Map-Reduce（并行处理大量文档 / 代码文件）
- 多路并发检索（同时查多个数据源）
- 批量分类、批量评分

**与普通并行节点的区别**：普通 `add_edge` 是在图结构里固定并行；`Send` 是运行时动态决定并行实例数量，输入不同。

---

## 16. `Command` 对象 — 在节点内部路由

传统做法：路由逻辑写在 `add_conditional_edges` 的函数里（节点外）。

2025 年新做法：用 `Command` 在节点内部同时更新 state 和决定下一步：

```python
from langgraph.types import Command

def review_node(state: AgentState) -> Command:
    result = llm.invoke(state["messages"])
    decision = parse_decision(result.content)

    if decision == "approve":
        return Command(
            update={"status": "approved", "messages": [result]},
            goto="execute_node",     # 路由到下一个节点
        )
    elif decision == "reject":
        return Command(
            update={"status": "rejected", "reason": result.content},
            goto="__end__",
        )
    else:
        return Command(
            update={"messages": [result]},
            goto="review_node",      # 循环回自身（需要更多信息）
        )

builder = StateGraph(AgentState)
builder.add_node("review_node", review_node)
builder.add_node("execute_node", execute_node)
builder.set_entry_point("review_node")
# 注意：不需要 add_conditional_edges，路由逻辑已在节点里
graph = builder.compile()
```

**`Command` vs `add_conditional_edges` 对比**：

| | `add_conditional_edges` | `Command` |
|-|------------------------|-----------|
| 路由逻辑位置 | 图结构定义时（节点外）| 节点函数内 |
| 可读性 | 全局视图清晰 | 逻辑内聚，节点自含 |
| 适合场景 | 固定分支结构 | 逻辑依赖复杂计算结果的动态路由 |
| 同时更新 state | 需要分开写 | 一步完成（`update` + `goto`）|

**在 Multi-agent 里跨图路由**：

```python
# Command 可以路由到另一个子图
return Command(
    update={"task": task_description},
    goto=Send("worker_graph", {"task": task_description}),
)
```

---

## 17. `interrupt()` — 新版 Human-in-the-loop

旧版（编译时静态）：`compile(interrupt_before=["node_name"])`
——在图编译时就固定了哪些节点前中断，灵活性差。

新版（运行时动态）：在节点内部调用 `interrupt()`，可以根据运行时条件决定是否中断：

```python
from langgraph.types import interrupt

def approval_node(state: AgentState) -> dict:
    proposed_action = state["proposed_action"]

    # 只有高风险操作才中断等待审批
    if state["risk_level"] == "high":
        human_decision = interrupt({
            "question": "是否执行以下操作？",
            "action": proposed_action,
            "estimated_impact": state["impact_assessment"],
        })
        # interrupt() 会暂停执行，等待人工通过 graph.invoke() 传入决定
        # human_decision 是人工传入的值
        if human_decision["approved"] is False:
            return {"status": "rejected", "reason": human_decision.get("reason")}

    # 低风险直接执行，不中断
    return {"status": "approved"}

# 动态恢复示例
graph = builder.compile(checkpointer=checkpointer)  # 必须有 checkpointer
config = {"configurable": {"thread_id": "task-789"}}

# 第一次运行：遇到 interrupt() 暂停
result = graph.invoke(initial_state, config=config)
# result 包含 interrupt 的内容（问题和动作描述）

# 人工审核后，传入决定继续
result = graph.invoke(
    Command(resume={"approved": True, "comment": "LGTM"}),
    config=config,
)
```

**新版 vs 旧版对比**：

| | `interrupt_before` | `interrupt()` |
|-|-------------------|---------------|
| 设置时机 | 编译时固定 | 运行时动态 |
| 条件中断 | 不支持（总是中断）| 支持（if risk_level == "high"）|
| 传递上下文给审核者 | 只能看 state | 可以传结构化问题 |
| 接收人工输入 | `update_state` + `invoke(None)` | `Command(resume=...)` |

---

## 18. Multi-agent Supervisor 模式

Orchestrator-Worker 是 LangGraph 中最常见的多 Agent 架构：

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent

# 定义专业 Worker Agent
research_agent = create_react_agent(
    model=llm,
    tools=[web_search, read_file],
    state_modifier="你是研究专员，负责信息收集。",
)

coder_agent = create_react_agent(
    model=llm,
    tools=[write_file, run_bash],
    state_modifier="你是开发工程师，负责代码实现。",
)

# Supervisor 节点：决定派给谁
def supervisor_node(state: SupervisorState) -> Command:
    response = llm.invoke([
        SystemMessage("你是 supervisor，根据任务分配给合适的 worker。"
                      "可以选择：research_agent / coder_agent / FINISH"),
        *state["messages"],
    ])

    decision = parse_routing(response.content)

    if decision == "FINISH":
        return Command(goto=END)
    return Command(goto=decision)  # 路由到对应 worker

# 构建 Supervisor 图
class SupervisorState(TypedDict):
    messages: Annotated[list, add_messages]

builder = StateGraph(SupervisorState)
builder.add_node("supervisor", supervisor_node)
builder.add_node("research_agent", research_agent)
builder.add_node("coder_agent", coder_agent)

builder.set_entry_point("supervisor")
# worker 完成后回到 supervisor 做下一步决策
builder.add_edge("research_agent", "supervisor")
builder.add_edge("coder_agent", "supervisor")

graph = builder.compile(checkpointer=MemorySaver())
```

**执行流程**：

```
用户输入
    ↓
Supervisor（分析任务）
    ├─→ research_agent（搜索信息）→ Supervisor
    ├─→ coder_agent（写代码）→ Supervisor
    └─→ END（任务完成）
```

**关键设计原则**：
- Supervisor 只做路由决策，不直接执行任务
- 每个 Worker 有专属工具集和 system prompt
- Worker 完成后总是回到 Supervisor，由 Supervisor 决定下一步
- Supervisor 可以多次派同一个 Worker（迭代改进）

### 18.1 何时值得引入多 Agent

多 Agent 不是能力叠加器。只有在任务可分解、子任务相对独立、并行收益超过协调成本，或确实需要不同工具/权限隔离时，才值得引入；否则单 Agent 加明确 Workflow 通常更稳定、更便宜。

常见模式包括 manager-worker、planner-executor、reviewer 和同类候选的 swarm。每个 Agent 都应有输入契约、输出 schema、预算、工具白名单和终止条件。

共享状态时默认传递压缩后的显式产物，不共享无限对话历史。写操作必须串行化或使用事务/幂等键；子 Agent 不继承父 Agent 的全部权限。协调者还要处理超时、重复、冲突、低质量结果和递归派生。

评估多 Agent 是否值得保留时，至少和单 Agent/单 Workflow 比较端到端质量、成本、延迟和失败率；如果没有可量化提升，就删掉协作层。

---

## 19. 时间旅行（Time Travel）

LangGraph 的 Checkpoint 不只是为了容错——还可以回到任意历史状态重新执行：

```python
# 获取某个 thread 的所有历史 checkpoint
config = {"configurable": {"thread_id": "task-123"}}
history = list(graph.get_state_history(config))

# history 是按时间倒序的 snapshot 列表
for snapshot in history:
    print(f"节点: {snapshot.next}")
    print(f"时间: {snapshot.created_at}")
    print(f"步骤: {snapshot.metadata.get('step')}")
    print("---")

# 选择某个历史 checkpoint（比如第 3 步）
target_snapshot = history[-3]  # 倒数第 3 个（最早的那端）

# 从这个 checkpoint 继续执行（会分叉出新的执行路径）
result = graph.invoke(None, config=target_snapshot.config)
```

**实际调试场景**：

```python
# 场景：Agent 在第 8 步做了错误决策，想从第 5 步重试

history = list(graph.get_state_history(config))

# 找到第 5 步的 snapshot
step5 = next(s for s in history if s.metadata.get("step") == 5)

# 修改第 5 步的 state（注入修正信息）
graph.update_state(
    step5.config,
    {"messages": [HumanMessage("注意：请优先考虑方案B")]},
)

# 从第 5 步重新执行（走不同的路径）
result = graph.invoke(None, config=step5.config)
```

**时间旅行的工程价值**：
- **调试**：快速定位哪一步出了问题，不用重跑整个流程
- **A/B 测试**：从同一个 checkpoint 分叉，对比不同 prompt / 参数的效果
- **审计**：重现历史执行过程，验证 Agent 行为

---

## 20. Functional API（轻量写法）

2025 年 LangGraph 新增 Functional API，比 StateGraph 更轻量，适合简单流程：

```python
from langgraph.func import entrypoint, task

# @task：定义可以并行执行的异步任务
@task
def summarize(document: str) -> str:
    return llm.invoke(f"总结：{document}").content

@task
def classify(document: str) -> str:
    return llm.invoke(f"分类：{document}").content

# @entrypoint：定义整个工作流的入口
@entrypoint(checkpointer=MemorySaver())
def process_docs(documents: list[str]) -> dict:
    # 并行提交所有任务（返回 Future）
    summary_futs = [summarize(doc) for doc in documents]
    classify_futs = [classify(doc) for doc in documents]

    # .result() 等待完成（自动并行）
    summaries = [f.result() for f in summary_futs]
    categories = [f.result() for f in classify_futs]

    return {"summaries": summaries, "categories": categories}

# 调用方式和 StateGraph 相同
config = {"configurable": {"thread_id": "run-1"}}
result = process_docs.invoke(["文档1...", "文档2...", "文档3..."], config=config)
```

**Functional API vs StateGraph**：

| | StateGraph | Functional API |
|-|-----------|----------------|
| 适合场景 | 复杂图结构、条件路由 | 简单顺序/并行流程 |
| 学习曲线 | 较陡（需要理解图概念）| 低（普通函数写法）|
| 可视化 | 完整图结构 | 有限 |
| Checkpoint | 节点级别 | 任务级别 |
| HITL | `interrupt_before` / `interrupt()` | `interrupt()` |

**选择原则**：有复杂条件路由或需要完整图可视化 → StateGraph；简单 Map-Reduce 或线性流程 → Functional API。

---

## learn-claude-code 对照：从团队通信到自治认领

s15-s18 展示了 LangGraph 之外的另一种 Harness 协作实现：

- **Agent Teams（s15）**：用文件系统 inbox/mailbox 传递消息，Lead 和 teammate 通过显式消息协作；读取、删除、重试和并发写入都需要定义语义。
- **Team Protocols（s16）**：shutdown、plan approval 等操作采用 request/response 状态机，不能把一条自然语言消息当成可靠协议。
- **Autonomous Agents（s17）**：队友空闲时扫描未认领任务并尝试原子 claim；自治不是“无限自主”，仍需工作轮次、空闲超时、身份重新注入和 shutdown 信号。
- **Worktree Isolation（s18）**：任务、Agent 身份和工作目录绑定，工具执行时切换到对应 cwd，完成后明确 keep/remove，避免并行修改互相污染。

这套文件邮箱和线程模型是教学实现；在生产系统中应替换为带锁/事务的任务存储、可靠消息、租约和可审计生命周期。对应实验：[s15_agent_teams/code.py](./实践/learn-claude-code/s15_agent_teams/code.py)、[s16_team_protocols/code.py](./实践/learn-claude-code/s16_team_protocols/code.py)、[s17_autonomous_agents/code.py](./实践/learn-claude-code/s17_autonomous_agents/code.py)、[s18_worktree_isolation/code.py](./实践/learn-claude-code/s18_worktree_isolation/code.py)，工作目录细节另见 [代码 Agent 基础设施](./代码%20Agent%20基础设施.md)。

## ai-agent-learning 配套实践

- [07 LangGraph Basic Workflow](./实践/ai-agent-learning/agent-learning-projects/07_langgraph_basic_workflow/README.md)：从 State、Node、Edge、compile、invoke 开始。
- [08 LangGraph Tool Agent](./实践/ai-agent-learning/agent-learning-projects/08_langgraph_tool_agent/README.md)：练习 ToolNode 和条件边。
- [09 LangGraph Memory Agent](./实践/ai-agent-learning/agent-learning-projects/09_langgraph_memory_agent/README.md)：练习 Checkpointer 与 `thread_id`。
- [LangGraph Advanced](./实践/ai-agent-learning/langgraph-advanced/README.md)：补充多 Agent、人工审批、MCP 和 Eval 对照实验。

建议先完成 07–09，再阅读本篇的持久化、Human-in-the-loop、子图、流式和动态并行章节。

## 附录：面试高频

**Q：LangGraph 和 LangChain 的区别是什么？**

> LangChain 提供的是线性链（Chain），步骤固定从 A 到 B 到 C。LangGraph 用图结构，支持条件路由、循环、分支、并行节点，可以表达任意复杂的 Agent 工作流。LangGraph 是在 LangChain 基础上专门为 Agent 场景设计的编排框架。如果任务是固定线性步骤，LangChain 够用；如果有条件分支、循环、需要 checkpoint，用 LangGraph。

**Q：什么是 Checkpoint，为什么重要？**

> Checkpoint 是在图执行过程中保存 state 快照的机制。重要性：一是容错——程序崩了可以从上次状态恢复，不用从头来；二是 Human-in-the-loop——在关键节点暂停，等待人工确认后继续；三是调试——可以回到任意历史状态检查问题。生产环境必须用持久化 Checkpointer（PostgreSQL/SQLite），开发环境可以用 MemorySaver。

**Q：如何实现 Human-in-the-loop？**

> 有两种方式。旧版：编译时 `compile(interrupt_before=["node_name"])` 静态指定中断节点，暂停后通过 `update_state` + `invoke(None)` 继续。新版（推荐）：在节点内部调用 `interrupt(payload)` 动态中断，支持条件中断（只有高风险操作才暂停），人工通过 `Command(resume=...)` 传入决定继续。新版更灵活，可以把审核上下文（操作描述、风险等级）结构化传给审核者。

**Q：`Send` API 解决什么问题？**

> `Send` 解决动态并行的问题。普通图结构是静态的（编译时固定节点数量），但 Map-Reduce 场景下需要"根据输入数据量动态创建并行执行实例"——比如 10 个文档就并行 10 个 summarize_node。`Send` 在 conditional_edges 函数里返回 `[Send("node", input1), Send("node", input2), ...]`，运行时动态 fan-out，结果通过 Annotated + `operator.add` 自动 fan-in 合并。

**Q：`Command` 对象和 `add_conditional_edges` 有什么区别？**

> 两者都能做路由，区别在于逻辑位置。`add_conditional_edges` 是在图构建时定义路由函数，路由逻辑和节点逻辑分离，全局结构清晰。`Command` 是在节点函数内部同时返回 state 更新和路由决定，适合路由逻辑依赖复杂计算结果的场景（不需要把中间结果放进 state 再读出来做判断）。实际项目里两者混用：固定分支用 `add_conditional_edges`，复杂动态路由用 `Command`。

**Q：什么是时间旅行（Time Travel），有什么工程价值？**

> LangGraph 的 Checkpoint 记录了每一步的完整 state 快照。Time Travel 是指用 `get_state_history()` 获取所有历史 checkpoint，然后选择某个历史节点用 `invoke(None, config=snapshot.config)` 从那里重新执行，会分叉出新的执行路径。工程价值：调试时快速定位出错步骤（不用重跑全程）；A/B 测试从同一 checkpoint 分叉对比不同策略；审计时重现历史执行过程验证 Agent 行为。
