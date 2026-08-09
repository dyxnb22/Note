# AI Agent 工程知识库

本页只做目录索引，不是阅读清单；主题依赖和分支选择看 [Agent 学习地图](./00_学习路线图.md)。

跨目录关系见 [Python → AI → Agent 学习地图](../00_Navigation/AI-Python-Agent学习地图.md)。模型、SDK、协议和价格变化时，先查 [版本与来源](./版本与来源.md)。

## 文档分组

| 方向 | 主文档 |
|---|---|
| 核心循环 | [LLM 调用](./01_LLM调用基础.md) · [Tool Calling](./02_Tool%20Calling.md) · [Agent 架构](./03_Agent架构与设计.md) · [Context](./04_Context工程.md) · [代码 Agent](./05_代码%20Agent%20基础设施.md) |
| 可靠性与上线 | [Durable Execution](./06_Durable%20Execution与分布式可靠性.md) · [威胁建模](./07_Agent安全与威胁建模.md) · [安全与可控性](./08_安全与可控性.md) · [Eval 实验](./09_Agent%20Eval实验方法.md) · [Eval 测试](./10_Eval与测试体系.md) · [可观测性](./11_可观测性与调试.md) · [部署](./12_部署与生产化.md) · [成本性能](./成本与性能工程.md) · [身份治理](./Agent身份与数据治理.md) · [运维](./Agent运维与事故响应.md) |
| 知识与流程 | [文档摄取](./文档摄取与解析.md) · [RAG](./RAG.md) · [检索系统](./检索系统工程.md) · [知识系统](./知识系统.md) · [GraphRAG](./GraphRAG与关系检索.md) · [Memory](./Memory与状态管理.md) · [Workflow](./Workflow与编排.md) · [LangGraph](./LangGraph.md) |
| 工具与协作 | [MCP](./MCP与工具协议.md) · [Skills](./Skills与渐进式披露.md) · [多 Agent](./多Agent协作的边界与模式.md) · [跨 Agent/A2A](./跨Agent协议与A2A.md) |
| 产品与扩展 | [产品与人机协同](./Agent产品与人机协同.md) · [框架选型](./Agent框架与平台选型.md) · [Computer Use](./Computer%20Use与GUI%20Agent.md) · [语音](./语音与实时对话Agent.md) · [推理服务](./推理服务速答.md) · [推理模型](./推理模型与Extended%20Thinking.md) · [模型行为训练](./模型行为与工具调用训练.md) |
| 输出与面试 | [项目表达](./项目表达与面试.md) · [面试目录](./面试/README.md) |

## 使用约定

- 一个主题只在一篇主文档维护完整解释；其他文章只说明边界并链接回去。
- `python` 代码块表示语法完整的实现片段，`text`/`pseudocode` 表示协议或局部示意；可运行代码进入 [实践](./实践/README.md)。
- 消息、工具和 Provider 示例可能是语义示意；真实字段以适配层和 [版本与来源](./版本与来源.md) 为准，不要把示例格式当成跨 Provider 合同。
- 第一次学习只走 `01/实践 03 → 02/实践 04 → 03/实践 05 → 04 Context`；已经掌握的章节可通过项目解释直接确认，不要求重读。
- 正文中的练习不是默认待办。可运行验证统一在实践项目完成；`learn-claude-code` 和 `rust-agent-runtime` 只作后续对照，不重复三遍。
- 第一遍不要求同时掌握所有 Provider。先用一个具体 API 跑通 03–05，再回头比较 Provider 差异；理论中的语义示例不等于可直接复制的 SDK 请求。
