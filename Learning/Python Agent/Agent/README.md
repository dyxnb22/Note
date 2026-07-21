# AI Agent 工程知识库

新入口先看[学习路线图](./学习路线图.md)，它负责阶段、练习和验收；本页只负责文档地图。

## 学习主线

本目录默认以 **Coding Agent / Agent Harness** 为主线。不要把所有主题理解成一条必须按顺序完成的流水线，而是分成四个相互连接的方向：

```text
核心循环：LLM/API → Tool Calling → Agent Loop → State
编码 Agent：文件/终端 → 权限/沙箱 → Context → 验证 → Session/Resume
知识 Agent：RAG → Citation → Memory → 权限感知检索
生产化：Eval → Trace → Cost → Rate Limit → Deployment
```

最小必修路径是：

`LLM 调用 → Tool Calling → Agent Loop → Context → 权限与验证 → Eval`

RAG、Memory、Workflow、MCP、Multi-Agent 和 Computer Use 按项目目标选修；它们不是所有 Agent 的共同前置条件。

## 文档分组

| 组别 | 文档 |
|---|---|
| 核心 | [LLM 调用基础](./LLM调用基础.md)、[Agent 架构与设计](./Agent架构与设计.md)、[Tool Calling](./Tool%20Calling.md)、[Context 工程](./Context工程.md)、[代码 Agent 基础设施](./代码%20Agent%20基础设施.md) |
| 产品与协同 | [AI 应用产品设计](./AI应用产品设计.md)、[Agent 产品与人机协同](./Agent产品与人机协同.md)、[项目表达与面试](./项目表达与面试.md) |
| 知识与流程 | [RAG 与知识系统](./RAG与知识系统.md)、[Memory 与状态管理](./Memory与状态管理.md)、[Workflow 与 LangGraph](./Workflow与LangGraph.md)、[MCP 与工具协议](./MCP与工具协议.md) |
| 可靠性与治理 | [Agent Eval 实验方法](./Agent%20Eval实验方法.md)、[Eval 与测试体系](./Eval与测试体系.md)、[Agent 安全与威胁建模](./Agent安全与威胁建模.md)、[Agent 身份与数据治理](./Agent身份与数据治理.md)、[Durable Execution 与分布式可靠性](./Durable%20Execution与分布式可靠性.md)、[可观测性与调试](./可观测性与调试.md) |
| 生产化 | [安全与可控性](./安全与可控性.md)、[成本与性能工程](./成本与性能工程.md)、[部署与生产化](./部署与生产化.md)、[Agent 运维与事故响应](./Agent运维与事故响应.md) |
| 扩展 | [推理模型与 Extended Thinking](./推理模型与Extended%20Thinking.md)、[模型行为与工具调用训练](./模型行为与工具调用训练.md)、[Computer Use 与 GUI Agent](./Computer%20Use与GUI%20Agent.md) |
| 输出 | [AI 项目表达与面试](./项目表达与面试.md)、[Career 通用项目表达](../../Career/项目表达.md) |

## 按目标进入

- Coding Agent：`LLM 调用 → Tool Calling → Agent Loop → 文件/终端 → 权限/沙箱 → Context → 验证 → Session`。
- 可靠 Coding Agent：在上面补 `代码导航 → Eval → 威胁建模 → Durable Execution`。
- 知识型 Agent：`LLM 调用 → Context → RAG → Citation → Eval`。
- Workflow/业务 Agent：先掌握 `Tool Calling`，再按固定流程选择 Workflow，按开放任务选择 Agent。
- Agent 产品：`AI 应用产品设计 → Agent 产品与人机协同 → Eval/反馈闭环`。
- 企业 Agent：补 `身份与数据治理 → 威胁建模 → Durable Execution → 运维与事故响应`。
- 上生产：在最小循环之后就加入基础 `安全/预算/观测/Eval`，再补 `成本 → 部署`。
- 真实项目：看 [AI 案例](../../Case_Studies/AI/README.md)，重点核对工具权限、Session、执行边界和证据等级。

通用模型原理在 `Learning/AI`；本目录只保留调用、编排、治理和交付方法。
