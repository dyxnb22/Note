# Agent 架构与设计

本文只回答三件事：Agent 与普通调用/Workflow 的边界、常见运行时模式，以及如何把动态决策放进可控的工程系统。工具合同见 [Tool Calling](./02_Tool%20Calling.md)，Context 见 [Context 工程](./04_Context工程.md)，编排 API 见 [LangGraph](./LangGraph.md)。

> **前提与完成标准**：先完成 [LLM 调用基础](./01_LLM调用基础.md) 和 [Tool Calling](./02_Tool%20Calling.md)；[00 号无 API 练习](./实践/ai-agent-learning/agent-learning-projects/00_agent_mental_model/README.md) 可作为短练习。读完能画出任务状态转移并明确每一种停止原因，不能只说“让模型自己循环”。

## 0. 先把 Agent 看成状态机

这里先给出工程定义：**Agent 是围绕目标运行的有限循环**——读取当前事实，让模型提出下一步，校验并执行动作，把结果写回状态，然后继续或停止。模型负责提出候选动作，应用负责事实、权限和成功判定。

```text
running
  ├─ 模型文本 + 成功证据 → succeeded
  ├─ tool_call → executing_tool → tool_result → running
  ├─ 需要人工 → waiting_human → approved → running
  │                         └→ rejected/expired → stopped
  ├─ 取消/失败/无进展 → stopped 或 failed
  └─ 超过步数、Token、费用或时间 → stopped(budget_exhausted)
```

`while` 只是实现形式；真正重要的是每轮状态转移可解释、可持久化、可取消并且有硬上限。

## 1. Agent 的工程定义

| 范式 | 路径 | 适合场景 |
|---|---|---|
| 单次调用 | Input → LLM → Output | 问答、摘要、提取 |
| Chain | 固定的 LLM → LLM → LLM | 固定多步骤处理 |
| Workflow | 固定图结构，节点可含 LLM | 可预测的业务流程 |
| Agent | 根据状态循环决定下一步 | 路径不确定、需要工具与反馈 |

学习 Coding Agent 时，用四个维度判断：

1. 围绕目标持续推进，而不是只生成一次文本；
2. 能调用工具、API、数据库、浏览器或执行环境；
3. 能读取中间结果，并据此调整下一步；
4. 至少一部分路径由模型根据当前状态决定。

这是工程上的连续谱，不是绝对分类：步骤稳定时优先普通代码或 Workflow，只有动态性带来净收益时才引入 Agent。

## 2. Agent Loop

```text
目标 → 读取状态/外部事实 → 模型决定下一步
     → 校验/授权/执行工具 → 回填结果 → 继续或结束
```

```text
while budget.allows():
    response = model.decide(context)
    record(response)

    if response.text is not None and not response.tool_calls:
        if success_evidence_exists(state):
            return succeeded(response.text)
        return stopped("final_without_success_evidence")

    for call in response.tool_calls:
        result = executor.validate_authorize_execute(call)
        record(call, result)
        append_tool_result(result)

    if no_progress or cancelled:
        return stopped(reason)

return stopped("budget_exhausted")
```

不可变约束：模型只能提出动作；执行器负责参数校验、授权、超时、幂等和错误归一化；每次状态转移可由 Trace 解释；没有成功证据不能只凭模型文字宣布完成。

不要把几个相近概念混成一个“上下文对象”：

| 概念 | 负责什么 | 是否直接发给模型 |
|---|---|---|
| State | 任务当前的结构化事实、进度、审批和产出引用 | 只有被 Context 选择的部分 |
| Context | 本轮根据目标和预算装配出的模型输入 | 是，按 Provider 适配 |
| ModelResult | Provider 响应归一化后的文本、工具调用、usage 和请求 ID | 否，先更新 State 或决定下一步 |
| Trace | 事件、决策、耗时、错误和安全审计 | 否，主要用于观测、Replay 和复盘 |

因此，模型说“完成了”只是一个 `ModelResult`；只有 State 中的验证结果或外部事实满足成功条件，任务才应进入 `succeeded`。

## 3. 模式选择

| 模式 | 结构 | 适合 | 主要代价 |
|---|---|---|---|
| ReAct | 想 → 做 → 看的线性循环 | 默认的工具型任务 | 长任务可能迷路 |
| Plan-and-Execute | 先拆计划，再执行/重规划 | 多步骤、可检查的清单 | 计划会过时 |
| Router | 分类后进入专门路径 | 多领域、多能力系统 | 路由错误与维护成本 |
| Reflection | 草稿 → 评审 → 修改 | 有程序化验收的高质量输出 | 调用和延迟增加，必须限轮 |
| Multi-Agent | 多个专长 Agent 协作 | 可并行且边界清楚的复杂任务 | 协调、通信和错误传播 |
| ToT/GoT/Reflexion | 分支搜索、聚合或失败反思 | 需要比较方案或可验证推理 | 成本、延迟、调试显著增加 |

选择顺序：先用 Workflow；确有动态路径时从 ReAct 开始；复杂度再上升才考虑计划、反思或多 Agent，并用 Eval 证明收益。简单问题不要强制长计划；可以用小模型/规则做 `simple → ReAct`、`complex → deeper planning` 的路由，并设置时间和步数预算。

## 4. 自主性、审批与状态

| 模式 | 适用 | 设计要求 |
|---|---|---|
| 全自动 | 低风险、可逆动作 | 硬预算、审计、失败回收 |
| 半自动 | 大多数生产任务 | 在关键副作用前进入 `waiting_human` |
| 辅助模式 | 删除、发信、付款等高风险动作 | 每步预览、审批和可追责记录 |

需要人工介入的典型条件：有真实副作用、处理敏感数据、模型/工具不确定、超过成本阈值，或策略要求人工审批。暂停时持久化待审批动作和当前状态；批准后恢复，拒绝则结束或改走安全路径。LangGraph 的 `interrupt`、`Command(resume=...)` 和持久化实现见 [LangGraph](./LangGraph.md)。

```python
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class AgentState:
    goal: str
    task_id: str
    status: Literal[
        "running", "waiting_human", "succeeded", "failed", "stopped", "cancelled"
    ] = "running"
    messages: list[dict] = field(default_factory=list)
    tool_calls_log: list[dict] = field(default_factory=list)
    step: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
```

状态至少要能序列化、审计、暂停、取消、恢复和回放；消息上下文与审计轨迹可以分开保存，避免把完整敏感原文无差别写入日志。

## 5. 终止与失败

所有 Agent 都要有硬上限：最大步数、Token、费用、墙钟时间和并发数。连续无进展、连续失败、取消、权限拒绝和恢复事实不明也应有明确停止原因。

| 失败 | 处理 |
|---|---|
| 工具参数错误 | 在执行边界校验，返回稳定错误码，让模型修正或结束 |
| 暂时不可用/超时 | 仅对幂等动作限次退避重试 |
| 有副作用且结果未知 | 先查询事实，不直接重做 |
| 权限/审批拒绝 | 停止或换安全路径，不靠模型自行绕过 |
| 无进展/预算耗尽 | 保存 Trace，返回可解释的 `stopped` 状态 |

常见反模式只有一句话：没有预算、把所有工具都暴露给模型、把异常直接抛出、依赖 Prompt 代替权限、把最终文字当成成功证据、没有记录中间状态。

## 6. Harness 边界

```text
Harness = Tools + Context + Observation + Permissions + State + Recovery
```

Harness 决定模型能看见什么、能执行什么、如何暂停恢复、如何验证结果。模型输出是提案，不是授权；能力提升不能替代工具合同、权限、状态、验证和可观测性。Coding Agent 的文件导航、Patch、验证、Worktree 见 [代码 Agent 基础设施](./05_代码%20Agent%20基础设施.md)。

## 7. 机制归属

| 机制 | 主文档 | 本篇只记住 |
|---|---|---|
| Tool schema、执行、并发、错误 | [Tool Calling](./02_Tool%20Calling.md) | 独立执行层不能被模型绕过 |
| Context、压缩、Skill | [Context 工程](./04_Context工程.md)、[Skills](./Skills与渐进式披露.md) | Context 不等于权限 |
| Checkpoint、Journal、Queue、Lease、Resume | [Durable Execution](./06_Durable%20Execution与分布式可靠性.md) | 恢复前先核实副作用 |
| 策略、沙箱、审批、脱敏 | [安全与可控性](./08_安全与可控性.md)、[威胁建模](./07_Agent安全与威胁建模.md) | 高风险动作需独立门禁 |
| 用户澄清、进度、接管 | [Agent 产品与人机协同](./Agent产品与人机协同.md) | 不确定且有副作用时先缩小歧义 |
| 多 Agent 拆分与仲裁 | [多 Agent 协作](./多Agent协作的边界与模式.md) | 先证明相对单 Agent/Workflow 的净收益 |
| 成本、延迟、循环预算 | [成本与性能工程](./成本与性能工程.md) | 每个循环都要能停止 |
| Trace、Replay、质量回归 | [可观测性](./11_可观测性与调试.md)、[Eval](./09_Agent%20Eval实验方法.md) | 正确答案不代表安全轨迹 |

## 8. 设计评审清单

实现前回答：

1. 任务为什么需要动态路径，Workflow 为什么不够？
2. 每个工具的输入、输出、权限、超时、幂等和失败语义是什么？
3. 状态如何序列化、暂停、取消、恢复、迁移和审计？
4. 哪些动作要预览、审批、补偿或人工接管？
5. 如何用确定性证据证明成功，并限制步数、Token、费用、时间和并发？
6. Provider、工具、环境或策略失败时如何降级，是否有 Trace、Replay、Eval 和基线？

如果答案只有“靠 Prompt 约束”，说明系统边界还没有建立。

## 9. 最小实践与验收

先实现一个窄任务的 ReAct 循环，再逐项接入 Tool、Context、权限、验证、Checkpoint、Trace 和 Eval；每次只增加一种机制，并记录它改善的指标与新增成本。

验收至少包括：

- 有限步数和明确停止原因；
- 工具参数校验、权限检查和高风险审批；
- 可审查的状态与工具 Trace；
- 写操作后的程序化验证；
- 失败、取消、恢复和人工接管路径；
- 可重复的成功、拒绝、边界和历史事故 Case。

实践选择见 [Agent 学习路线图](./00_学习路线图.md)：`ai-agent-learning` 走应用主线，`learn-claude-code` 拆 Harness，Rust Runtime 做跨语言对照。
