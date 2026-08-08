# Workflow 与编排

这篇文章解决一个选择问题：**什么时候把任务写成确定性 Workflow，什么时候保留 Agent 的动态决策**。

> **学习位置**：完成 `01–06` 后阅读。它是编排专题，不是 Agent Loop 的前置。
>
> **职责边界**：本文讲与框架无关的状态图、分支、并行、人工节点和测试；Checkpoint/Queue/Lease/Resume 的可靠性见 [Durable Execution](./06_Durable%20Execution与分布式可靠性.md)，LangGraph API 见 [LangGraph](./LangGraph.md)。

## 1. Workflow、Agent 与普通代码

| 方案 | 路径由谁决定 | 适合 |
|---|---|---|
| 普通代码 | 开发者完全决定 | 规则明确、结果必须确定 |
| Workflow | 开发者定义图，节点可调用模型 | 流程稳定但有分支、并行、审批或恢复 |
| Agent | 模型在运行时选择下一步 | 路径不确定，需要根据反馈探索 |

生产系统常见的稳妥形态是“确定性 Workflow + 少量动态 Agent 节点”，而不是让模型控制全部流程。

## 2. 四个核心对象

- **State**：任务的结构化事实、进度、审批和产出；必须可序列化和版本化。
- **Node**：一个可测试的确定性动作或模型调用；输入输出边界明确。
- **Edge**：无条件、条件、循环、并行汇聚或人工等待的迁移。
- **Checkpoint**：状态快照或事件位置；恢复语义由 [Durable Execution](./06_Durable%20Execution与分布式可靠性.md) 定义。

先写状态和迁移，再写 Prompt。一个节点不应同时隐藏任意工具权限、不可控副作用和多种业务状态。

## 3. 从业务事实画图

```text
输入
  → 校验/澄清
  → 读取或检索
  → 模型决策/生成草稿
  → 审批（如果有副作用）
  → 执行
  → 验证
  → 成功 / 重试 / 人工接管 / 失败
```

每个节点都写清：输入事实、输出事实、允许工具、超时、失败类型、是否可重试、成功证据和下一状态。不要用一个“万能节点”包住所有业务逻辑。

## 4. 分支、循环、并行和人工节点

- **条件分支**：根据结构化 State 路由，不让模型返回任意节点名。
- **循环**：必须有目标、进度检测、最大次数和停止原因。
- **并行**：只有资源互不冲突、结果可合并且预算允许时使用；汇聚时处理部分失败。
- **人工节点**：保存待审批 State，明确谁批准、批准什么摘要、过期后怎么办。

```text
if validation.ok:
    publish
elif validation.retryable and attempts < limit:
    repair
elif needs_human:
    wait_for_approval
else:
    fail_with_evidence
```

## 5. 失败、取消和恢复

不要把所有错误都交给模型。先按确定性类别处理：参数错误、权限拒绝、依赖超时、状态冲突、预算耗尽、外部副作用未知。取消要区分：

- 尚未开始：直接标记 cancelled；
- 可中断步骤：在安全点停止并保存 State；
- 已提交副作用：先查询事实，再补偿或人工处理。

Queue、Lease、幂等、Outbox、Checkpoint 和迁移合同统一见 [Durable Execution](./06_Durable%20Execution与分布式可靠性.md)，本篇不复制实现。

## 6. Workflow 与 Agent 的组合边界

使用 Workflow 的信号：路径可列举、审批点固定、需要强审计、回归容易定义。使用 Agent 节点的信号：需要根据检索/工具结果动态选择下一步，且有验证器和预算。

先建立固定 Workflow 基线，再把一个节点替换成 Agent，比较成功率、错误类型、延迟、成本和人工接管率；没有净收益就保留确定性实现。

## 7. 观测与测试

每次迁移记录：`run_id`、State 版本、节点、输入摘要、输出摘要、工具调用、耗时、停止原因和副作用。质量/轨迹/安全评测见 [Agent Eval](./09_Agent%20Eval实验方法.md) 与 [Eval 与测试体系](./10_Eval与测试体系.md)，Trace 细节见 [可观测性](./11_可观测性与调试.md)。

测试至少覆盖：每条分支、循环上限、并行部分失败、审批拒绝、取消、恢复、旧 State 迁移和重复投递。

## 8. 何时进入 LangGraph

当需要条件边、循环、并行、Checkpoint、interrupt、stream 或子图时，才用 LangGraph 表达已经理解的状态机。先看本篇和 `06`，再看 [LangGraph](./LangGraph.md)；不要通过记 API 名称代替理解迁移合同。

## 9. 设计真实流程时检查

只有当前任务存在稳定步骤、固定审批或恢复需求时才画 Workflow。可以直接检查真实业务流程，不必为本文虚构一个完整代码修改流程：

1. 每个节点有输入、输出和成功证据；
2. 写操作前有审批，写操作后有验证；
3. 重启后能从安全边界恢复；
4. 每条路径都有 Trace 和可重复 Case；
5. 能解释为什么某一步是 Workflow，某一步才使用 Agent。

实践：[LangGraph Basic Workflow](./实践/ai-agent-learning/agent-learning-projects/07_langgraph_basic_workflow/README.md)。
