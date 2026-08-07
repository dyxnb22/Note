# Agent 架构与设计

这篇文档解决一个问题：**Agent 究竟是什么，有哪些架构模式，怎么设计一个可靠的 Agent 系统**。

不是概念科普，而是要能回答：什么时候用 Agent、什么时候不用、各种模式的权衡是什么。

> **职责边界**：本文讲 Agent 的工程定义、核心循环、状态和运行时模式；工具 schema/执行细节集中在 [Tool Calling](./02_Tool%20Calling.md)，通用编排见 [Workflow 与编排](./Workflow与编排.md)，LangGraph API 见 [LangGraph](./LangGraph.md)，上下文压缩集中在 [Context 工程](./04_Context工程.md)。

---

## 1. Agent 与其他范式的区别

### 四种范式对比

| 范式 | 结构 | 灵活性 | 可控性 | 适合场景 |
|------|------|--------|--------|---------|
| **单次 LLM 调用** | Input → LLM → Output | 低 | 高 | 问答、摘要、提取 |
| **链式调用（Chain）** | LLM → LLM → LLM | 中 | 高 | 固定多步骤处理 |
| **Workflow（图编排）** | 固定图结构，节点可含 LLM | 中 | 很高 | 业务流程自动化 |
| **Agent** | 循环：观察→规划→执行→观察 | 高 | 低 | 开放性任务、工具使用、自主探索 |

### Coding Agent 的实用判定维度

```
1. 目标导向：围绕任务推进，而不是只生成一次文本
2. 外部行动：能够调用工具、API、数据库、浏览器或其他执行环境
3. 状态与反馈：能读取中间结果，并据此修正下一步
4. 动态决策：至少有一部分路径由模型根据当前状态决定
```

这不是所有文献都统一采用的必要条件，而是本笔记学习 Coding Agent 时使用的工程定义。Agent 更适合被看成一个连续维度：从单次调用、固定 Workflow，到带工具和反馈的动态循环，边界取决于任务和系统设计。

---

## 2. Agent Loop 的完整结构

```
输入目标
   ↓
[感知 / Perception]
  - 读取当前状态
  - 读取工具执行结果
  - 读取外部信息（检索、数据库）
   ↓
[规划 / Planning]
  - LLM 基于当前状态推理下一步
  - 选择：调用工具 / 继续推理 / 请求人类确认 / 结束
   ↓
[执行 / Action]
  - 调用工具，获取结果
  - 更新状态
   ↓
[判断 / Termination]
  - 目标是否达成？
  - 是否遇到无法处理的失败？
  - 是否超过最大步数？
   ↓
完成 / 失败 / 请求人工介入
```

### Loop 合同（实现见 Tool Calling）

本文只保留循环的状态转移；Provider 消息格式、工具 schema、并发调用和错误归一化统一见 [Tool Calling](./02_Tool%20Calling.md)。

~~~text
while budget.allows():
    response = model.decide(context)

    record assistant response
    if response.final:
        return succeeded(response.final)

    for call in response.tool_calls:
        result = tool_executor.validate_authorize_execute(call)
        record tool result
        append result to context

    if no_progress or cancellation_requested:
        return stopped(reason)

return stopped(reason="budget_exhausted")
~~~

循环的不可变约束是：模型只能提出动作；执行器负责校验、授权、超时、幂等和错误归一化；每次状态转移都能在 Trace 中解释；没有确定性成功证据时不能报告任务完成。

## 3. 主流 Agent 范式

### ReAct（Reasoning + Acting）

最基础的 Agent 范式。模型交替输出 Thought（推理）和 Action（动作）：

```
Thought: 用户想知道今天北京天气，我需要调用天气 API
Action: call_weather(city="Beijing")
Observation: {"temp": 28, "condition": "Sunny"}
Thought: 已经获取到天气，可以回答了
Action: finish(answer="今天北京天气晴，气温 28°C")
```

**优点**：简单、透明、容易 debug
**缺点**：不做长期规划，容易在复杂任务中迷失

### Plan-and-Execute

先生成完整计划，再逐步执行：

```
1. Planner LLM：把大目标分解成有序的子任务列表
2. Executor：逐个执行子任务
3. Replanner：如果某步失败，重新规划剩余步骤
```

**优点**：更适合需要长远规划的任务
**缺点**：初始计划可能不适应执行过程中发现的情况

### Router Agent

根据用户输入，把请求路由到不同的专门处理路径：

```
用户输入 → Router LLM（分类意图）
   ├── "代码问题" → Code Agent
   ├── "查询订单" → Order Agent
   ├── "投诉"     → Human Agent（人工介入）
   └── "其他"     → General Agent
```

**适合**：多领域客服、多能力系统、降低单个 Agent 复杂度。

### Reflection Agent

Agent 完成任务后，评估自己的输出，不满意就重来：

```
Task → Draft Answer → Critic LLM（评分 + 改进意见）→ 修改 → 再评估
```

**适合**：要求高质量输出的场景（代码生成、写作）
**注意**：成本高，可能陷入无限改进循环，必须设最大轮数。

### Multi-Agent

多个专门的 Agent 协作完成复杂任务：

```
Orchestrator Agent（协调者）
   ├── Research Agent（信息收集）
   ├── Analysis Agent（分析）
   ├── Writer Agent（写作）
   └── Reviewer Agent（审查）
```

**适合**：超出单个 context window 的长任务、需要并行处理的场景。
**注意**：协调开销大，错误会传播，不要轻易用——很多时候一个好的 ReAct Agent 已经够用。

### ToT / GoT / Reflexion（规划拓扑升级）

ReAct 是**线性**「想→做→看」。更重的范式改变的是推理拓扑，不是换个框架名：

| 范式 | 拓扑 | 适合 | 工程代价 |
|---|---|---|---|
| ReAct | 线性循环 | 绝大多数工具型任务 | 低，默认首选 |
| Plan-and-Execute | 先计划再执行 | 多步骤、可检查的清单任务 | 中；计划过时需重规划 |
| Tree-of-Thoughts (ToT) | 多分支搜索 + 评价剪枝 | 数学/逻辑/需比较多方案 | LLM 调用 × 分支数；延迟难控 |
| Graph-of-Thoughts (GoT) | 任意聚合/回边 | 多源信息综合 | 实现与调试更重 |
| Reflexion | 失败后写自然语言反思再试 | 可程序化验证的任务 | 需外存反思；防空转 |

**为什么生产默认仍是 ReAct**：成本与延迟可预期、轨迹好看、工具失败好恢复。ToT 在「买 A 还是 B」类对比题上可能更好，但用户第五秒就开始焦虑——要用 Eval 证明收益再上。

### 过度规划与 complexity router

症状：用户问天气，Agent 输出长篇计划再行动。根因常是 System Prompt 强制「先规划」。

解法：

1. **复杂度路由**：轻量分类器/小模型判定 simple → 直达 ReAct；complex → Plan-Execute 或更深搜索。
2. **时间/步数预算**：能一步完成禁止写计划。
3. **用户可见计划**：必须规划时展示短清单，而不是沉默思考。

模型路由见 [成本与性能工程](成本与性能工程.md)；框架选型见 [Agent 框架与平台选型](Agent框架与平台选型.md)。

---

## 4. 自主性与可控性的权衡

这是 Agent 设计中最核心的张力。

| 自主程度 | 人工介入点 | 适合场景 | 风险 |
|---------|-----------|---------|------|
| 全自动 | 无 | 低风险、可逆操作 | 无人监督，错误放大 |
| 半自动 | 关键决策节点 | 大多数生产场景 | 需要设计确认流程 |
| 辅助模式 | 每一步都人审 | 高风险操作（删数据、发邮件） | 效率低，但安全 |

### 为什么生产系统不做全自动 Agent

1. **错误成本高**：自动发邮件、改数据库、触发外部付费 API——出错影响真实用户
2. **可观测性差**：LLM 推理不透明，出了问题很难追因
3. **边界难以定义**：告诉模型"不要删数据"，但模型可能用间接方式绕过
4. **合规要求**：很多场景需要人工审批记录

**实际经验**：先从 Human-in-the-loop 开始，逐步观察失败模式，再有选择地自动化低风险步骤。

---

## 5. Human-in-the-loop 设计模式

Human-in-the-loop 的典型触发条件：
- 操作涉及真实副作用（发邮件、写数据库、调用外部付费 API）
- Agent 的置信度低（模型自己表达不确定）
- 超过预设成本阈值
- 处理敏感数据或个人信息

实现上，通用 Agent 只需要把任务置为 `waiting_human`，持久化待审批动作和当前状态，收到决定后再恢复；LangGraph 的 `interrupt`、`Command(resume=...)` 和持久化 Checkpoint 见 [LangGraph](./LangGraph.md)。本文不再复制框架 API。

---

## 6. 终止条件设计

Agent 最容易出现的问题：无法正确终止。

```python
class TerminationCondition:
    def __init__(self, max_steps=20, max_cost_usd=1.0, max_tokens=100_000):
        self.max_steps = max_steps
        self.max_cost = max_cost_usd
        self.max_tokens = max_tokens

    def should_stop(self, state) -> tuple[bool, str]:
        if state.step >= self.max_steps:
            return True, f"超过最大步数 {self.max_steps}"
        if state.total_cost_usd > self.max_cost:
            return True, f"超过成本上限 ${self.max_cost}"
        if state.total_tokens > self.max_tokens:
            return True, "超过 token 限制"
        if state.consecutive_errors >= 3:
            return True, "连续失败 3 次，中止"
        return False, ""
```

**原则**：任何生产 Agent 都必须有最大步数、最大成本的硬性上限。

---

## 7. 状态设计

好的状态设计是 Agent 可维护的关键：

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal

class AgentState(BaseModel):
    goal: str
    task_id: str
    # 每个任务必须拥有独立的消息容器，不能共享可变默认值。
    messages: list[dict] = Field(default_factory=list)
    step: int = 0
    # 显式状态便于暂停、恢复、人工接管和回放。
    status: Literal["running", "waiting_human", "done", "failed"] = "running"
    # 工具轨迹用于审计和定位失败，不等同于给模型看的完整上下文。
    tool_calls_log: list[dict] = Field(default_factory=list)
    final_answer: Optional[str] = None
    error_message: Optional[str] = None
    # 预算是运行时硬边界，不能只依赖模型“自觉停止”。
    total_tokens: int = 0
    total_cost_usd: float = 0.0
```

状态应该可序列化（Pydantic），方便：持久化到数据库、断点续传、审计和调试。

---

## 8. 常见设计错误

| 错误 | 问题 | 正确做法 |
|------|------|---------|
| 没有最大步数限制 | Agent 可能无限循环 | 强制设置 max_steps |
| 工具失败直接抛异常 | 一个工具失败整个 Agent 崩溃 | catch 异常，把错误作为 tool result 返回给模型 |
| 把所有工具都给 Agent | 模型选择困难，容易误用 | 按任务范围限制可用工具 |
| 不记录中间状态 | 出错后无法 debug | 每一步都 log state |
| system prompt 太简单 | 模型对任务边界不清楚 | 明确写出能做什么、不能做什么、何时请求人工 |
| 不处理工具幂等性 | 重试时副作用重复 | 工具要标注是否幂等 |

---

## 9. Harness 的边界

Harness 不是模型本身，而是包围模型的确定性系统：

~~~text
Harness = Tools + Context + Observation + Permissions + State + Recovery
~~~

它决定模型能观察什么、能执行什么、遇到失败如何恢复。模型能力提升不能替代工具合同、权限、状态、验证和可观测性。对 Coding Agent 来说，工程重点通常在 Harness；但每一项机制都应有独立的状态、预算和审计边界。

---

## 10. 工程机制的唯一归属

本篇只保留架构判断，不再复制各专题的实现代码：

| 机制 | 唯一主文档 | 本篇只需要记住 |
|---|---|---|
| Tool schema、路由、执行、并发和错误归一化 | [Tool Calling](./02_Tool%20Calling.md) | 模型输出工具调用仍要经过独立执行层 |
| Context、压缩、Skill 和 Prompt 组装 | [Context 工程](./04_Context工程.md)、[Skills与渐进式披露](./Skills与渐进式披露.md) | Context 是运行时输入，不等于权限 |
| 文件导航、Patch、验证和 Worktree | [代码 Agent 基础设施](./05_代码%20Agent%20基础设施.md) | 写入后必须有可审查变更和确定性验证 |
| Checkpoint、Journal、Queue、Lease、Cron 和 Resume | [Durable Execution 与分布式可靠性](./06_Durable%20Execution与分布式可靠性.md) | 恢复前先判断副作用是否已经发生 |
| 威胁模型、策略、沙箱、审批和脱敏 | [Agent 安全与威胁建模](./07_Agent安全与威胁建模.md)、[安全与可控性](./08_安全与可控性.md) | 模型输出是提案，不是执行授权 |
| 澄清、进度、接管和用户审批体验 | [Agent 产品与人机协同](./Agent产品与人机协同.md) | 不确定且有副作用时先缩小歧义 |
| 多 Agent 的拆分、通信、仲裁和评测 | [多 Agent 协作的边界与模式](./多Agent协作的边界与模式.md) | 先证明相对单 Agent/Workflow 的净收益 |
| 成本、延迟、预算和卡死循环 | [成本与性能工程](./成本与性能工程.md) | 每个循环都要有硬上限和停止原因 |
| Trace、Replay、质量回归和发布门槛 | [可观测性与调试](./11_可观测性与调试.md)、[Agent Eval实验方法](./09_Agent%20Eval实验方法.md) | 最终答案正确不代表轨迹安全或可解释 |

Hook 是跨切面扩展点，权限 Hook 的生产实现归 [安全与可控性](./08_安全与可控性.md)；学习版入口在 [learn-claude-code 实践](./实践/learn-claude-code/README.md)。不要在本篇再维护一套 Hook、Subagent、Worktree 或验证器代码。

---

## 11. 设计评审清单

设计一个 Agent 前，至少回答：

1. 任务是否真的需要动态路径？如果步骤稳定，优先普通代码或 Workflow。
2. 每个工具的输入、输出、权限、超时、幂等性和失败语义是什么？
3. 模型可以观察哪些事实，哪些内容必须标记为不可信数据？
4. 状态如何序列化、暂停、取消、恢复和迁移？
5. 哪些动作需要预览、审批、补偿或人工接管？
6. 任务如何确定性地证明成功，而不是只看模型的最终文字？
7. 最大步数、Token、费用、墙钟时间和并发上限分别是什么？
8. 发生 Provider、工具、环境或策略故障时，如何降级并留下 Trace？
9. 是否有单 Agent 或 Workflow 基线，以及能证明复杂度收益的 Eval？

如果其中任一问题只能回答“靠 Prompt 约束”，说明系统边界还没有建立。

---

## 12. 最小实践与验收

先实现一个窄任务的 ReAct 循环，再逐项接入 Tool、Context、权限、验证、Checkpoint、Trace 和 Eval。每次只增加一种机制，并记录它改善了哪个指标、增加了多少成本。

最小验收不要求一次实现所有专题，但必须具备：

- 有限步数和明确停止原因；
- 工具参数校验与权限检查；
- 可审查的状态和工具 Trace；
- 写操作后的程序化验证；
- 失败、取消和人工接管路径；
- 一组可重复的成功、拒绝、边界和历史事故 Case。

实践选择见 [Agent 学习路线图](./00_学习路线图.md)；ai-agent-learning 适合应用开发主线，learn-claude-code 适合 Harness 机制拆解，Rust Runtime 适合跨语言对照。
