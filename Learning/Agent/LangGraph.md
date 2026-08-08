# LangGraph

LangGraph 是把 State、Node、Edge、循环、并行、Checkpoint 和人工中断表达成图的框架。它不是 Agent 原理的起点，也不会自动解决权限、评测或生产可靠性。

> **学习位置**：先完成 `01–06` 和 [Workflow 与编排](./Workflow与编排.md)，再用本文把通用机制映射到框架 API。
>
> **职责边界**：本文只保留 LangGraph 的核心对象、常见控制流、状态恢复、流式和版本验证；通用 Loop 见 `03`，Durable Execution 见 `06`，多 Agent 选型见 [多 Agent 协作](./多Agent协作的边界与模式.md)。

## 1. 通用机制到 LangGraph 的映射

| 通用机制 | LangGraph 表达 | 需要自己负责 |
|---|---|---|
| 任务状态 | State / TypedDict / Pydantic | schema 版本、敏感字段和迁移 |
| 确定性动作 | Node | 超时、权限、幂等、错误 |
| 路由 | Edge / conditional edge | 只允许合法目标，防止任意跳转 |
| 恢复点 | Checkpointer + thread_id | 持久化、租约、重复副作用 |
| 人工介入 | interrupt / resume | 审批绑定、过期、撤销 |
| 事件流 | stream | 用户可见事件、脱敏和最终状态 |
| 动态并行 | Send / reducer | fan-out 上限、合并冲突和成本 |

如果一张图只是 A → B → C，普通函数或 Workflow 可能更简单。

## 2. State：图的唯一事实来源

State 应只保存任务需要的结构化事实，不把整个 Provider 响应或所有私有数据都塞进去：

```python
from typing import Annotated, TypedDict
import operator


class State(TypedDict):
    task: str
    status: str
    messages: list[dict]
    tool_results: Annotated[list[dict], operator.add]
    error: str | None
```

并行节点更新同一字段时需要 reducer；没有明确合并规则的字段不要让多个节点同时写。状态 Schema、Checkpoint 版本和迁移策略应进入部署回归。

## 3. Node、Edge 和最小图

Node 接收 State，返回局部更新；Edge 只负责迁移。业务权限和工具执行不要隐藏在路由函数中。

```python
from langgraph.graph import END, START, StateGraph


def draft(state: State) -> dict:
    # Node 只产生建议；真实写操作仍需独立工具授权。
    return {"status": "drafted", "messages": [{"role": "assistant", "content": "draft"}]}


def route(state: State) -> str:
    if state["error"]:
        return "failed"
    return "succeeded"


builder = StateGraph(State)
builder.add_node("draft", draft)
builder.add_node("failed", lambda state: {"status": "failed"})
builder.add_node("succeeded", lambda state: {"status": "succeeded"})
builder.add_edge(START, "draft")
builder.add_conditional_edges(
    "draft",
    route,
    {"failed": "failed", "succeeded": "succeeded"},  # 路由目标用显式 allowlist 固定。
)
builder.add_edge("failed", END)
builder.add_edge("succeeded", END)
graph = builder.compile()
```

节点要可单测；边要覆盖每个状态分支；循环必须设置 recursion/step 上限和停止原因。

## 4. Tool Agent

ToolNode 或框架提供的 Tool 执行器只解决编排便利，不替代 [Tool Calling](./02_Tool%20Calling.md) 的 schema、授权、超时、幂等和结果脱敏。典型结构：

```text
START → call_model
          ├─ 无 tool call → END
          └─ 有 tool call → execute_tools → call_model
```

工具返回错误时应回到模型或进入确定性失败分支；工具调用次数、并发和结果大小由应用配置控制。

## 5. Checkpoint、thread 和恢复

Checkpoint 保存 State 快照，`thread_id` 通常把多次调用关联到同一任务。开发可用内存存储；生产必须使用持久化存储，并考虑：

- State Schema 版本和向前/向后兼容；
- Worker 崩溃、Queue 重投和 Lease 过期；
- 已经提交的外部副作用；
- 取消、人工等待和恢复后的重复执行；
- Trace 和审计事件的关联。

恢复不是“从上一个 Node 重新跑就行”。恢复前要根据操作 Journal 或外部查询确认副作用事实，详见 [Durable Execution](./06_Durable%20Execution与分布式可靠性.md)。

## 6. Human-in-the-loop

静态 `interrupt_before/after` 适合固定断点；动态 `interrupt(payload)` 适合根据 State 决定是否等待。恢复时传入的决定只是一种输入，节点仍需重新校验权限、审批摘要和 State 版本。

```python
from langgraph.types import Command, interrupt


def approve_publish(state: State) -> dict:
    decision = interrupt({
        "action": "publish",
        "summary": state["task"],
    })
    if decision != "approve":
        return {"status": "rejected"}
    # 恢复后重新执行权限检查，不能把 interrupt 的结果当作永久授权。
    return {"status": "approved"}


# graph.invoke(Command(resume="approve"), config={"configurable": {"thread_id": "t1"}})
```

中断前的副作用必须已经完成、可查询或幂等；否则恢复会产生重复写入。

## 7. Streaming 和用户事件

框架可以流出 State 更新、Node 事件和 LLM token。对用户只暴露稳定事件：`tool_requested`、`tool_completed`、`approval_required`、`validation_failed` 等；完整输入输出进入脱敏 Trace。答案 token 与进度事件分通道，前端不要把内部 Node 名称当作稳定产品协议。

## 8. 并行、子图和动态路由

| 能力 | 用途 | 先解决的问题 |
|---|---|---|
| Subgraph | 把可复用流程封装为节点 | 输入/输出和权限边界 |
| Send | 运行时 fan-out，例如逐文档处理 | 并行上限、结果 reducer、部分失败 |
| Command | 节点同时更新 State 和路由 | 路由可测试、目标 allowlist |
| Functional API | 用函数/任务表达轻量流程 | 与图式 State/Checkpoint 的迁移 |

这些 API 不改变通用原则：并行写操作需资源隔离，动态路由不能跳过授权，循环需要硬上限。

## 9. Multi-Agent 不等于多几个节点

Supervisor、worker、handoff、子图和共享 State 只是表达方式。是否拆分要依据任务边界、上下文隔离、并行收益和故障传播做实验；完整选型见 [多 Agent 协作的边界与模式](./多Agent协作的边界与模式.md)。

## 10. 常见错误

| 错误 | 后果 | 修正 |
|---|---|---|
| 用框架 API 代替状态设计 | 图能跑但无法恢复 | 先写 State/迁移合同 |
| 全部内容放进 State | 泄露、膨胀、迁移困难 | 只保存结构化事实和引用 ID |
| 依赖内存 Checkpointer 上生产 | 重启丢任务 | 持久化 + Schema 迁移 |
| interrupt 前做不可逆副作用 | 恢复重复执行 | 先审批，副作用节点幂等 |
| 并行节点共同覆盖字段 | 结果不确定 | reducer 或拆分字段 |
| 无限循环依赖模型停止 | 卡死和成本失控 | recursion/预算/stuck 检测 |

## 11. 版本验证和最小 Smoke Test

LangGraph API、Checkpointer、stream 事件和 Provider 集成会变化。升级时至少验证：

1. 图能编译，入口和结束路径存在；
2. 工具 call/result 能正确配对；
3. `thread_id` 能保存和恢复 State；
4. interrupt/resume 不重复副作用；
5. stream 事件能映射到产品合同；
6. 关键 Eval、权限和成本指标无退化。

实践按顺序阅读：[07 基础 Workflow](./实践/ai-agent-learning/agent-learning-projects/07_langgraph_basic_workflow/README.md)、[08 Tool Agent](./实践/ai-agent-learning/agent-learning-projects/08_langgraph_tool_agent/README.md)、[09 Memory Agent](./实践/ai-agent-learning/agent-learning-projects/09_langgraph_memory_agent/README.md)，再看 [LangGraph Advanced](./实践/ai-agent-learning/langgraph-advanced/README.md) 和 [DevPilot](./实践/ai-agent-learning/DevPilot/README.md)。

## 12. 开始使用框架前检查

能用 LangGraph 实现一个有限循环，并说明：

- State、Node、Edge、Reducer 和 Checkpoint 各自负责什么；
- 工具、审批、取消、恢复和外部副作用如何处理；
- 哪些逻辑应留在普通代码/Workflow，不应交给模型；
- 如何用 Trace、Eval 和版本化 Smoke Test 证明升级安全。
