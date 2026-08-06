# Agent 框架与平台选型

本文回答面试高频题：**LangGraph / AutoGen / CrewAI / 轻量 SDK / 低代码平台各自适合什么，什么时候不用框架**。具体图 API 见 [LangGraph](LangGraph.md)；多 Agent 边界见 [多 Agent 协作的边界与模式](多Agent协作的边界与模式.md)。

## 1. 一张对比表

| 形态 | 代表 | 设计哲学 | 适合 | 不适合 |
|---|---|---|---|---|
| 显式状态图 | LangGraph | 把循环、分支、持久化建成一等公民 | 生产工作流、HITL、可恢复长任务 | 一次性脚本、无状态问答 |
| 对话式多 Agent | AutoGen 类 | Agent 互相发消息协作 | 研究原型、开放式辩论 | 强审计、严格状态机、成本敏感线上 |
| 角色编排 DSL | CrewAI 类 | 角色+任务快速拼装 | Demo、内部工具、短流程 | 深定制、细粒度权限与恢复 |
| 轻量循环 | OpenAI Agents / Anthropic Tool Use / 自写 Loop | 最少抽象，模型+工具 | 工具 ≤ 十来个、流程简单 | 复杂并行汇聚、跨会话 Time Travel |
| 低代码 | Dify、扣子(Coze)、百炼工作流等 | 可视化编排、产品化托管 | 业务方自助、快速试点 | 强定制 Harness、代码级沙箱、深度评测门禁 |

没有「最好框架」，只有「控制力 / 速度 / 运维成本」三角。

## 2. 从 LangChain Agent 到 LangGraph 的思维转变

- **从前**：线性 Chain 或隐藏循环的「Agent Executor」，状态靠消息列表硬撑。
- **之后**：显式 Node/Edge/State；循环与分支是图结构，不是 prompt 里的愿望。
- **生产含义**：Checkpoint、中断恢复、并行 reducer、按节点观测，都依赖显式图。

任务是固定 A→B→C 时，Chain 或普通代码即可；出现「调工具→看结果→再决定」的环，再上图。

## 3. 轻量 vs 重量：什么时候不需要框架

```text
单轮工具 / 结构化抽取
  → 直接 SDK + schema 校验

3–10 工具、有限步 Agent Loop、无复杂 HITL
  → 自写 Loop 或轻量 SDK

需要分支/循环/并行汇聚/持久化/审批/多角色
  → LangGraph 或等价状态机

跨团队可视化、非工程同学改流程
  → 低代码（接受能力上限）
```

框架的成本是：升级破坏、抽象泄漏、调试多一层。评测「是否值得采用」看：状态模型是否清晰、失败可否恢复、能否接入现有观测与权限、团队能否读懂源码级行为。

## 3.1 选型评分卡（注释版）

框架选型应以待解决的工程约束评分，不按社区热度直接下注。

```python
def score_option(option, requirements):
    scores = {}
    for requirement, weight in requirements.items():
        # 每项评分必须附证据：最小 Demo、故障测试或团队维护经验。
        scores[requirement] = option.evidence_based_score(requirement) * weight
    return sum(scores.values()), scores


requirements = {
    "durable_resume": 3,
    "human_approval": 2,
    "tool_policy_boundary": 3,
    "trace_export": 2,
    "team_operability": 2,
}
```

评分卡不能替代 PoC：至少用一个真实业务流程验证状态恢复、权限、评测、升级和故障排查，否则“支持某能力”只是文档声明。

## 4. 低代码平台怎么答（尤其字节生态）

面试常问「怎么看扣子 / Dify」。稳妥立场：

1. **承认价值**：降低试错成本、适合标准客服/FAQ/简单编排、运营可改流程图。
2. **说清边界**：复杂权限、自定义沙箱、细粒度 Eval、与内部中台深度集成时，代码 Agent / 图编排更可控。
3. **不要贬低具体竞品**：尤其面试公司自有的低代码产品；强调「场景分层」而非「低代码无用」。
4. **混合现实**：试点用低代码验证需求 → 稳定核心路径沉淀为代码与评测门禁。

Coding Agent（Claude Code / Codex 类）与低代码工作流也不同：前者是**带仓库工具的 Harness**，后者是**可视化业务流程**。对比维度：工具深度、上下文工程、权限模型、是否面向开发者。

## 5. 选型口述模板（约 60 秒）

> 我先看任务有没有环和审批。没有就 SDK 或轻量 Loop。有环、要恢复和并行，用显式状态图（我们用 LangGraph：State+Reducer+Checkpointer）。多 Agent 只在子任务可隔离且能量化收益时上。业务试点可以用低代码，但权限、评测和危险工具最终要收到代码与策略引擎里。

## 导航与关联

- [LangGraph](LangGraph.md) · [Agent 架构与设计](03_Agent架构与设计.md) · [Skills与渐进式披露](Skills与渐进式披露.md) · [跨Agent协议与A2A](跨Agent协议与A2A.md)

`#agent #langgraph #framework #coze #dify #interview`
