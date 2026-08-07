# Agent 主题速答

本页只做面试复习索引，不重复主文档。先按 [学习范围与面试题型](./学习范围与面试题型.md) 选择主题，再回到对应正文；若内容冲突，以正文和当前 Provider/框架文档为准。

## 高频题与答题抓手

| 主题 | 高频问题 | 回答必须覆盖 |
|---|---|---|
| LLM 调用 | Service、流式、结构化输出 | 统一边界；SSE/断线/取消；schema 校验不等于业务可信 |
| Tool Calling | 谁执行代码、失败怎么办、Schema 作用 | 模型只产出意图；宿主执行；超时/错误/幂等/权限 |
| Agent 架构 | Agent 与 Workflow、ReAct、HITL | 固定路径优先 Workflow；动态决策才用 Agent；风险动作人工确认 |
| Context | Prompt 与 Context、长上下文、注入 | 组装/裁剪/来源分层；检索与摘要；工具层权限兜底 |
| 安全 | Prompt Injection、Tool Misuse | 外部内容不是指令；最小权限；参数校验、沙箱、审计 |
| Durable | 长任务、重试、恢复 | 持久状态、checkpoint、租约；副作用幂等；恢复先核实事实 |
| Eval | Harness、Offline/Online、CI 回归 | 数据集、执行器、指标、报告；离线门禁+线上监控 |
| 可观测性 | AI 指标、生产排障 | trace、token/cost、工具轨迹、检索质量、输出质量 |
| LangGraph | State、Checkpoint、HITL、Send、Command | 状态机与控制流；持久化恢复；动态 fan-out；节点副作用幂等 |
| MCP | MCP 与直接 Tool Calling | 跨进程能力合同与复用；认证、权限、版本、供应链仍由系统治理 |
| Memory | 会话、长期记忆、任务状态 | 生命周期、来源、时间戳、权限；相关检索而非全量历史 |
| 成本/性能 | 成本与延迟优化 | 先测 token、命中率、TTFT/TPOT；再缓存、路由、压缩、并行 |

## 通用答题骨架

先给定义，再说适用边界；然后给最小执行流程；最后补失败、权限、可观测性和验证方式。涉及具体 API、价格或框架行为时，明确版本和 Provider，不把经验值说成固定规则。

## 正文入口

[LLM 调用](../01_LLM调用基础.md) · [Tool Calling](../02_Tool%20Calling.md) · [Agent 架构](../03_Agent架构与设计.md) · [Context](../04_Context工程.md) · [安全](../07_Agent安全与威胁建模.md) · [Durable](../06_Durable%20Execution与分布式可靠性.md) · [Eval](../09_Agent%20Eval实验方法.md) · [可观测性](../11_可观测性与调试.md) · [LangGraph](../LangGraph.md) · [MCP](../MCP与工具协议.md) · [Memory](../Memory与状态管理.md) · [成本](../成本与性能工程.md)
