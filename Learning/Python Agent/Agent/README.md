# AI Agent 工程知识库

新入口先看[学习路线图](./学习路线图.md)，它负责阶段、练习和验收；本页只负责文档地图。

## 主链路

`LLM 调用 → Agent 架构 → Tool Calling → Context → RAG → Memory/Workflow → MCP → Eval → 观测/安全 → 成本/部署`

## 文档分组

| 组别 | 文档 |
|---|---|
| 核心 | [LLM 调用基础](./LLM调用基础.md)、[Agent 架构与设计](./Agent架构与设计.md)、[Tool Calling](./Tool%20Calling.md)、[Context 工程](./Context工程.md) |
| 知识与流程 | [RAG 与知识系统](./RAG与知识系统.md)、[Memory 与状态管理](./Memory与状态管理.md)、[Workflow 与 LangGraph](./Workflow与LangGraph.md)、[MCP 与工具协议](./MCP与工具协议.md) |
| 生产化 | [Eval 与测试体系](./Eval与测试体系.md)、[可观测性与调试](./可观测性与调试.md)、[安全与可控性](./安全与可控性.md)、[成本与性能工程](./成本与性能工程.md)、[部署与生产化](./部署与生产化.md) |
| 扩展 | [推理模型与 Extended Thinking](./推理模型与Extended%20Thinking.md)、[Computer Use 与 GUI Agent](./Computer%20Use与GUI%20Agent.md) |
| 输出 | [AI 项目表达与面试](./项目表达与面试.md)、[Career 通用项目表达](../../Career/项目表达.md) |

## 按目标进入

- RAG：`LLM 调用 → Context → RAG → Eval`。
- Agent：`LLM 调用 → Agent 架构 → Tool Calling → Memory/Workflow`。
- 上生产：补 `安全 → 观测 → 成本 → 部署`。
- 真实项目：看 [AI 案例](../../Case_Studies/AI/README.md)，重点核对工具权限、Session、执行边界和证据等级。

通用模型原理在 `Learning/AI`；本目录只保留调用、编排、治理和交付方法。
