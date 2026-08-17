# Rust Agent 工程化

这篇连接 Rust 语言能力与 [Agent 面试题库](../../Agent面试题库/README.md)。目标不是用 Rust 重写所有 Python 框架，而是理解什么时候需要自己掌控 Agent Runtime、工具执行、资源边界和可恢复性，并用 Rust 的类型、所有权与并发模型把这些约束变成代码。

可运行实践提炼为 [Agent 实践与项目表达题](../../Agent面试题库/12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md)。它覆盖有限状态循环、Tool Registry、预算、重复调用检测、取消和 Trace，以及真实 Provider、Async、MCP、沙箱与持久化的演进边界。

## 1. Rust 在 Agent 系统中的位置

适合优先使用 Rust 的部分：

- Coding Agent 的 CLI、文件系统与进程执行器。
- 需要严格资源上限、低内存和高并发的 Agent Gateway。
- Tool/MCP Server、协议适配器和结构化数据边界。
- 沙箱控制面、权限检查、审计和长期运行的 Agent Harness。
- 需要编译为单一二进制、跨平台交付或嵌入其他系统的组件。

不必优先使用 Rust 的部分：Prompt 快速实验、模型行为探索、某个 Provider 新能力的首日验证，以及高度依赖 Python 数据/模型生态的流程。合理架构可以是 Python 验证 Agent 行为，Rust 承担稳定 Runtime 或高风险执行边界；也可以在需求稳定后逐步迁移。

## 2. 先学什么

### 必修语言底座

```text
01 基础语法
→ 02 所有权/借用/生命周期
→ 03 Struct/Enum/Trait/泛型
→ 05 Result/Option/错误
→ 06 模块与测试
→ 07 Cargo 与项目组织
→ 10 Serde/配置/日志
→ 11 并发与 Async
→ 12 Tokio
```

### 按需专题

- 文件、Shell 和网络工具：补 [09_文件系统、进程与网络IO](./09_文件系统、进程与网络IO.md)。
- Agent API 或 Gateway：补 [13_Web服务与数据库](./13_Web服务与数据库.md)。
- 性能诊断：补 [14_Rust性能模型与适用边界](./14_Rust性能模型与适用边界.md)。
- 只有扩展宿主、WASM/原生库边界确有需要时再学宏、`unsafe` 与 FFI。

## 3. 架构映射

| Agent 问题 | Rust 设计 |
|---|---|
| 模型可能返回多种结果 | `enum ModelOutput { Final, ToolCall, ... }` 并穷尽匹配 |
| Provider 可以替换 | 小型 `Model` Trait；Provider DTO 留在 Adapter 内 |
| 工具输入不可信 | Serde DTO → Schema 校验 → 领域类型转换 |
| 工具集合动态注册 | `HashMap<String, Arc<dyn Tool + Send + Sync>>` |
| 任务跨线程执行 | 在边界证明 `Send + Sync + 'static` |
| 共享运行状态 | 优先消息传递/单所有者；必要时 `Arc` + 明确同步策略 |
| 长任务可能中断 | 事件日志 + Checkpoint + 可重放状态机 |
| 外部动作不可撤销 | 幂等键、准备/提交状态、补偿与人工接管 |
| 无限循环和成本失控 | 步数、时间、Token、工具调用与重复调用上限 |

类型系统可以阻止许多非法状态，但不能证明 Prompt 正确、模型可靠、权限合理或外部副作用已经回滚。这些仍需要威胁模型、Eval、故障测试和运行证据。

## 4. Provider 边界

Provider Adapter 只负责：认证、请求/响应 DTO、流式事件解析、错误分类、用量与请求 ID。核心 Runtime 依赖自己的稳定类型，不让某个 SDK 类型穿透 Agent Loop。

```text
Provider JSON/SSE
  → Provider Adapter
  → ModelOutput / Usage / ProviderError
  → Agent Runtime
```

错误至少区分：认证/权限、限流、瞬时网络、Provider 5xx、无效响应、Context 超限和调用方取消。重试必须同时满足“错误可重试、请求语义安全、总预算仍有余量”。流中断时不能假设模型端没有产生用量或工具调用。

当前主流官方 Agent SDK 的高层抽象主要面向 Python/TypeScript；Rust 实现应把 Provider/API 和 Runtime 分层，避免把社区框架的当前 API 当成长期领域模型。需要快速接入时可以评估 Rig 等 Rust 社区框架，但用项目 Eval、协议覆盖、发布节奏和维护风险决定是否采用。

## 5. Tool Contract 与注册表

每个 Tool 明确：稳定名称、用途、参数 Schema、返回 Schema、权限、副作用、超时、幂等与错误语义。建议把解析分成三层：

```text
模型参数 JSON
→ Serde 解析（形状正确）
→ 业务校验（值与权限正确）
→ 执行计划/领域命令
```

不要让模型直接获得任意 Shell、路径或数据库句柄。工具执行器在确定性代码中完成路径规范化、Allowlist、工作目录隔离、环境变量过滤、输出上限、超时和审计。

动态工具可以使用 Trait Object；编译期固定、性能敏感的内部路径可以用泛型。选择标准是部署和扩展边界，不是偏爱某种语法。

## 6. Agent Loop 是有限状态机

最小状态：

```text
Ready
  → CallingModel
  → ExecutingTool
  → CallingModel
  → Finished | Failed | Cancelled | AwaitingApproval
```

每次循环记录 Step、输入摘要、Provider 请求 ID、模型输出类型、Tool、耗时、用量与状态转换。必须具有：

- 最大 Step、时间、Token/费用和 Tool 调用次数。
- 相同 Tool + 参数的重复检测。
- 无效 Tool、无效参数和 Tool 失败的明确回填策略。
- 最终输出、暂停审批、取消和失败的不同终态。
- 进程崩溃后可判断哪些动作已经发生。

不要用“模型通常会停”作为终止条件，也不要把所有错误文本原样回填模型；错误需要稳定代码、可公开信息和内部诊断三层表达。

## 7. Async、并发、背压与取消

真实 Runtime 通常使用 Tokio，但并发不是默认越多越好：

- Provider 请求、Tool 调用和后台任务分别设置 `Semaphore` 上限。
- 使用有界 Channel 传递事件，慢消费者必须产生背压或明确丢弃策略。
- 给连接、首字节、完整响应、Tool 和整个 Run 设置分层预算。
- `select!` 取消分支会 Drop 未完成 Future；逐个核对取消安全。
- 阻塞进程、文件或 CPU 工作放到受限线程池/进程，不占住 Async Worker。
- 保存并等待 `JoinHandle`；丢弃 Handle 不代表任务已经停止。

取消只能停止本地等待，不能自动撤销已经发送的邮件、数据库提交或 Shell 写入。高风险工具使用两阶段流程：先生成计划和 Diff，审批后带幂等键提交，再验证实际结果。

## 8. Context、Memory 与持久化

当前 Run 的消息、工具结果和预算属于 Session State；跨 Session 的偏好或知识属于 Memory。不要把二者混成无限增长的 `Vec<Message>`。

Checkpoint 至少保存：

- Session/Run/Step ID 与状态机版本。
- 已确认的消息和结构化 Tool 结果。
- 已消耗的预算、模型和 Prompt/Tool 版本。
- 待审批动作与已提交副作用的幂等键。
- 恢复位置、失败分类和最后一次 Trace 关联 ID。

恢复前先校验 Schema 和版本；无法安全迁移时拒绝恢复，不要静默丢字段。日志不是业务状态，Trace 丢失不能改变执行正确性。

## 9. 安全执行边界

Coding Agent 的工具面至少分级：只读、工作区写入、进程执行、网络访问、凭据使用和外部系统写入。默认最小权限，并把策略放在 Tool Executor，而不是只写在 Prompt 中。

文件工具：规范化路径后再检查是否位于工作区；处理符号链接和 TOCTOU。Shell 工具：使用参数数组而非拼接命令，限制 cwd、环境、网络、时间、输出和子进程。Provider/网页/MCP 返回内容全部视为不可信数据，不能升级系统指令或权限。

## 10. Eval、测试与观测

测试分层：

- 单元：状态转换、预算、重复检测、Schema 与错误映射。
- 脚本模型：固定模型输出，验证 Tool 顺序、取消和恢复。
- Provider 契约：固定响应 Fixture 与流式边界。
- 沙箱集成：真实文件/进程，但使用临时工作区和最小权限。
- 任务 Eval：固定仓库、任务和评分器，记录成功率、步骤、成本和副作用。

Trace 需要能回答失败来自模型、Context、Tool、权限、Provider 还是基础设施。不要把含密钥、完整 Prompt 或用户敏感数据的调试输出默认写入日志。

## 11. 四阶段实践路线

| 阶段 | 产物 | 验收 |
|---|---|---|
| A. 确定性 Runtime | 当前无依赖基线 | Tool 调用、终止、预算、重复、取消测试通过 |
| B. Async Provider | Tokio + HTTP/SSE Adapter | 超时、流中断、限流和取消有契约测试 |
| C. Coding Tools | 文件、Patch、受限进程、审批 | 路径逃逸、超时、输出爆炸和危险动作被拦截 |
| D. Durable Harness | Checkpoint、Resume、Trace、Eval | 进程中断后恢复；副作用不重复；固定任务集回归 |

阶段 B 开始前先完成 Python Agent 主线中的 LLM 调用、Tool Calling 与 Agent Loop，以区分“Agent 机制问题”和“Rust 实现问题”。阶段 D 完成后再评估 MCP、多 Agent、GUI 或复杂 Workflow。

## 12. 最终验收

- [ ] 核心 Runtime 不依赖具体 Provider SDK 类型。
- [ ] 所有 Run 都有确定终态和多维预算。
- [ ] Tool 参数、权限、副作用和错误合同可测试。
- [ ] Async 任务、Channel、子进程和连接均有数量与生命周期上限。
- [ ] Checkpoint 可以安全恢复或明确拒绝，不重复外部副作用。
- [ ] 固定 Eval 能比较模型、Prompt、Tool 或 Runtime 版本升级。
- [ ] Trace 可定位问题，但不承担唯一业务事实。

## 来源与版本边界

- [The Rust Programming Language](https://doc.rust-lang.org/book/)：语言、所有权、Trait、错误、并发和项目基础。
- [Asynchronous Programming in Rust](https://rust-lang.github.io/async-book/)：Future、Runtime、取消和 Async 生态；官方标注部分内容仍在重写，具体 API 以所用 Runtime 文档为准。
- [Tokio 文档](https://docs.rs/tokio/latest/tokio/)：Runtime、Task、Channel、Time 和 I/O。
- [OpenAI Agents SDK（Python）](https://openai.github.io/openai-agents-python/)与 [TypeScript](https://openai.github.io/openai-agents-js/)：用于对照当前高层 Agent Runtime 能力，不作为 Rust API 契约。
- [Rig](https://docs.rig.rs/)：Rust 社区 Agent 框架示例；采用前锁定版本并通过自己的 Eval 与故障测试。

本文验证环境为 Rust 1.97、Cargo 1.97、Edition 2024；Crate API 和 Provider 协议属于易变信息，升级时必须重新验证。

`#rust #agent #runtime #tool-calling #tokio #sandbox #durable-execution`
