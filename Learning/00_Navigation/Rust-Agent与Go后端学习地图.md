---
type: map
status: mature
last_verified: 2026-07-30
---

# Rust Agent 与 Go 后端学习地图

这张地图服务两个明确目标：用 Go 建立可就业、可生产交付的后端能力；用 Rust 深入 Agent Runtime、工具执行器和可靠 Harness。它不复制语言正文，而是规定顺序、产物与验收。

## 1. 两条主线如何分工

```text
Go 后端主线
语言惯用法 → Runtime/并发 → HTTP/数据库 → 测试/性能 → 可靠交付
                                                        ↓
                                             生产系统共同能力
                                                        ↑
Rust Agent 支线                                       │
Rust 语言 → Async/Tokio → Agent Loop/Tool → 沙箱/恢复/Eval
              ↑
Python Agent 主线先验证模型行为与 Agent 机制
```

Go 负责业务服务、数据库、事务、接口、部署和生产排障；Rust 负责类型安全的 Agent Runtime、并发工具执行、文件/进程边界、长任务恢复与高可靠基础设施。两者共享 HTTP、超时、幂等、可观测性、测试和交付知识，不维护两套重复架构笔记。

## 2. Go 后端正式路线

### 阶段 G0：语言入口

阅读：

1. [Go 基础语法与惯用法](../Backend/Go/00_Go基础语法与惯用法.md)
2. [Go 后端工程基础](../Backend/Go/Go后端工程基础.md)

产物：文本统计 CLI、带超时 HTTP Client、内存 Todo Service。

验收：能解释零值、Slice、Interface nil、Error 链、Module 和 Package；测试覆盖错误、取消与资源释放。

### 阶段 G1：Runtime 与并发

阅读：

1. [Go 语言与 Runtime](../Backend/Go/01_Go语言与Runtime.md)
2. [Go 并发与内存模型](../Backend/Go/02_Go并发与内存模型.md)

产物：有界 Worker Pool；能主动制造并修复 Race 和 Goroutine 泄漏。

验收：每个 Goroutine 的所有者、退出、错误和上限明确；结论由 Race、Profile 和 Benchmark 支持。

### 阶段 G2：网络服务

阅读：[Go 网络服务工程](../Backend/Go/03_Go网络服务工程.md)。

实践：[go-backend-service](../Backend/Go/实践/go-backend-service/README.md) 阶段 0–3。

验收：订单 API 支持超时、幂等、PostgreSQL 事务、迁移、下游客户端和优雅关闭；重复与响应丢失不会产生重复事实。

### 阶段 G3：测试、性能与交付

阅读：

1. [Go 测试与性能诊断](../Backend/Go/04_Go测试与性能诊断.md)
2. [Go 后端项目实战](../Backend/Go/05_Go后端项目实战.md)
3. [后端测试体系](../Backend/Testing.md)
4. [生产系统工程](../Backend/Delivery/07_生产系统工程.md)

验收：Race、Fuzz、集成、故障、负载和关闭测试有固定入口；一次 Profile 能解释瓶颈；部署和回滚可重复。

## 3. Rust Agent 正式路线

### 阶段 R0：Agent 机制前置

先完成 [Agent 学习路线图](../Agent/00_学习路线图.md) 的阶段 0–1：LLM 调用、Tool Calling、有限 Agent Loop。优先用现有 Python 实践看清模型和协议行为，不要同时与借用检查器、Async 和 Provider 差异搏斗。

验收：已有一个具备参数校验、终止条件、错误回填和固定测试的最小 Agent。

### 阶段 R1：Rust 语言核心

按 [Rust README](../Backend/Rust/README.md) 完成 01–07；重点是所有权、借用、Enum、Trait、Result、模块和测试。

产物：CLI、文本处理库、带单元/集成测试的 Tool Registry。

验收：能解释值由谁拥有、Trait 为什么在该边界、错误在哪里增加语义。

### 阶段 R2：I/O 与 Async

阅读 Rust 09–12：文件/进程/网络、Serde/配置/日志、并发/Async 和 Tokio。

产物：有界并发 Tool Executor，支持超时、取消、输出限制和优雅关闭。

验收：没有阻塞 Async Worker；Channel 有界；Task、子进程和资源均有结束路径。

### 阶段 R3：Agent Runtime

阅读：[Rust Agent 工程化](../Backend/Rust/16_Rust%20Agent工程化.md)。

实践：[rust-agent-runtime](../Agent/实践/rust-agent-runtime/README.md) 阶段 A–B。

验收：Provider 与 Runtime 解耦；Agent Loop 有 Step/时间/费用/Tool 预算；流中断、限流、重复调用和取消有测试。

### 阶段 R4：可靠 Harness

继续实践阶段 C–D，并阅读 Agent 的 Context、代码基础设施、安全、Durable Execution、Eval 与观测主题。

验收：文件和进程工具无法越权；高风险动作需审批；进程中断后可恢复；幂等副作用不重复；固定任务集能比较版本升级。

## 4. 建议节奏

Go 是主线，Rust 是专项支线。没有固定周数要求，但同一时间只推进一个“实现难点”：

| 学习周期 | Go 主线 | Rust/Agent 支线 |
|---|---|---|
| 1 | G0 语言与小练习 | Python Agent 阶段 0–1 |
| 2 | G1 Runtime 与并发 | R1 Rust 核心 |
| 3 | G2 HTTP + 内存服务 | R2 I/O 与 Async |
| 4 | G2 PostgreSQL + 可靠性 | R3 确定性 Runtime |
| 5 | G3 测试、性能、交付 | R3 Provider Adapter |
| 6 | Go 项目故障与回滚演练 | R4 沙箱、恢复与 Eval |

如果时间不足，先完成 G0–G2 和 Agent 阶段 0–1；Rust R3–R4 在拥有真实 Agent 场景后继续。宏、`unsafe`、FFI、多 Agent 和 GUI Agent 都不是前置条件。

## 5. 共同能力只学一份

| 共同主题 | 主入口 | 在语言项目中验证 |
|---|---|---|
| HTTP、API、错误码 | Go 网络服务工程 / Agent LLM 调用 | Go Handler；Rust Provider Adapter |
| 数据库、事务、幂等 | Backend/Data 与可靠性 | Go 订单；Rust Checkpoint/事件表 |
| 超时、取消、背压 | Go 并发 / Rust Tokio | Worker Pool；Tool Executor |
| 测试与故障 | 后端测试体系 / Agent Eval | Race/Fuzz；Scripted Model/任务集 |
| 观测与 SLO | 生产系统工程 / Agent 可观测性 | HTTP RED；Run/Step/Tool Trace |
| 安全和权限 | Backend 应用安全 / Agent 安全 | API 鉴权；文件/Shell 沙箱 |

同一机制先在主文档理解，再在两种语言中验证差异；不要复制一篇“Go 幂等”和一篇“Rust 幂等”作为两套理论。

## 6. 完成证据

正式学习完成不以阅读勾选数判断，而以以下证据判断：

- Go：一个有状态、可测试、可部署、可诊断、可回滚的后端服务。
- Rust：一个可终止、可取消、权限受控、可恢复、可评测的 Agent Runtime/Harness。
- 每个项目记录版本、环境、运行命令、原始结果、失败路径和未完成边界。
- 能分别解释业务正确性、并发正确性、生产可靠性和 Agent 质量，避免用“测试通过”替代所有证明。

`#map #go #rust #backend #agent #learning-path`
