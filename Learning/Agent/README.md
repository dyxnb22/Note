# AI Agent 工程知识库

新入口先看[学习路线图](./00_学习路线图.md)，它负责阶段、练习和验收；本页只负责文档地图。

三个主题目录的整体关系见：[Python → AI → Agent 学习地图](../00_Navigation/AI-Python-Agent学习地图.md)。

代码块约定：`python` 表示语法完整的实现片段；`text` 表示协议示意、局部片段或省略上下文的伪代码。完整可运行示例以 `实践/` 中的项目为准。

模型、SDK、协议与价格会变化；运行示例或做技术选型前先查 [版本与来源](./版本与来源.md)。

## 学习主线

本目录默认以 **Coding Agent / Agent Harness** 为主线。不要把所有主题理解成一条必须按顺序完成的流水线，而是分成四个相互连接的方向：

```text
核心循环：LLM/API → Tool Calling → Agent Loop → State
编码 Agent：文件/终端 → 权限/沙箱 → Context → 验证 → Session/Resume
知识 Agent：RAG → Citation → Memory → 权限感知检索
生产化：Eval → Trace → Cost → Rate Limit → Deployment
```

最小必修路径是：

`Python 工程化 → Python Agent 工程化前置 → LLM 调用 → Tool Calling → Agent Loop → Context → 权限与验证 → Eval`

其中 Python 前置内容集中在上级目录的 [Python Agent 工程化补充](../Python/04_Python%20Agent工程化补充.md)：它连接 Python 的 Pydantic、asyncio、类型系统、重试和测试与本目录的 Agent Runtime。已有 Python 基础时不必重复通读全部语法，直接从该页开始即可。

RAG、Memory、Workflow、MCP、Multi-Agent 和 Computer Use 按项目目标选修；它们不是所有 Agent 的共同前置条件。

## 文档分组

| 组别 | 文档 |
|---|---|
| 核心 | [LLM 调用基础](./01_LLM调用基础.md)、[Agent 架构与设计](./03_Agent架构与设计.md)、[Tool Calling](./02_Tool%20Calling.md)、[Context 工程](./04_Context工程.md)、[代码 Agent 基础设施](./05_代码%20Agent%20基础设施.md) |
| 产品与协同 | [Agent 产品与人机协同](./Agent产品与人机协同.md)、[项目表达与面试](./项目表达与面试.md) |
| 知识与流程 | [RAG](./RAG.md)、[知识系统](./知识系统.md)、[Memory 与状态管理](./Memory与状态管理.md)、[Workflow 与编排](./Workflow与编排.md)、[LangGraph](./LangGraph.md)、[多 Agent 协作的边界与模式](./多Agent协作的边界与模式.md)、[MCP 与工具协议](./MCP与工具协议.md) |
| 可靠性与治理 | [Agent Eval 实验方法](./09_Agent%20Eval实验方法.md)、[Eval 与测试体系](./10_Eval与测试体系.md)、[Agent 安全与威胁建模](./07_Agent安全与威胁建模.md)、[Agent 身份与数据治理](./Agent身份与数据治理.md)、[Durable Execution 与分布式可靠性](./06_Durable%20Execution与分布式可靠性.md)、[可观测性与调试](./11_可观测性与调试.md) |
| 生产化 | [安全与可控性](./08_安全与可控性.md)、[成本与性能工程](./成本与性能工程.md)、[部署与生产化](./12_部署与生产化.md)、[Agent 运维与事故响应](./Agent运维与事故响应.md)、[版本与来源](./版本与来源.md) |
| 扩展 | [推理模型与 Extended Thinking](./推理模型与Extended%20Thinking.md)、[模型行为与工具调用训练](./模型行为与工具调用训练.md)、[Computer Use 与 GUI Agent](./Computer%20Use与GUI%20Agent.md) |
| 输出 | [AI 项目表达与面试](./项目表达与面试.md)、[Career 通用项目表达](../Career/项目表达.md) |

## 交叉主题的职责边界

| 主题 | 主要文档 | 另一篇文档的职责 |
|---|---|---|
| Eval | [Agent Eval 实验方法](./09_Agent%20Eval实验方法.md) | 任务、轨迹、Replay 和发布门禁；[Eval 与测试体系](./10_Eval与测试体系.md) 负责通用 Harness、数据集、指标实现和 CI |
| 安全 | [Agent 安全与威胁建模](./07_Agent安全与威胁建模.md) | 信任边界、资产和攻击面；[安全与可控性](./08_安全与可控性.md) 负责防御代码、策略、沙箱和恢复模式 |
| 运行时 | [Agent 架构与设计](./03_Agent架构与设计.md) | Agent Loop、状态和运行时机制；[Tool Calling](./02_Tool%20Calling.md) 负责工具合同/执行，[Workflow 与编排](./Workflow与编排.md) 负责通用编排，[LangGraph](./LangGraph.md) 负责框架实现 |
| RAG / 知识 | [RAG](./RAG.md) | 切分、检索、排序、生成和评测；[知识系统](./知识系统.md) 负责来源、版本、权限、引用和删除治理 |
| Context / Memory | [Context 工程](./04_Context工程.md) | 当前请求的上下文构造与压缩；[Memory 与状态管理](./Memory与状态管理.md) 负责跨轮次持久化、召回和生命周期 |
| 可靠性 | [Durable Execution 与分布式可靠性](./06_Durable%20Execution与分布式可靠性.md) | 与框架无关的状态机、Checkpoint、Queue、Lease、Resume 原语；Workflow 文档只讲其在 LangGraph 中的落地 |
| 部署 | [部署与生产化](./12_部署与生产化.md) | 只负责模型/Prompt/工具/索引版本、Eval 门禁、状态恢复和 LLM 预算；通用 Docker、CI/CD、健康检查和发布流程见 [Backend Delivery](../Backend/Delivery/README.md) |

## 按目标进入

- Coding Agent：`LLM 调用 → Tool Calling → Agent Loop → 文件/终端 → 权限/沙箱 → Context → 验证 → Session`。
- 可靠 Coding Agent：在上面补 `代码导航 → Eval → 威胁建模 → Durable Execution`。
- 知识型 Agent：`LLM 调用 → Context → RAG → Citation → Eval`。
- Workflow/业务 Agent：先掌握 `Tool Calling`，再按固定流程选择 Workflow，按开放任务选择 Agent。
- Agent 产品：`Agent 产品与人机协同 → Eval/反馈闭环`。
- 企业 Agent：补 `身份与数据治理 → 威胁建模 → Durable Execution → 运维与事故响应`。
- 上生产：在最小循环之后就加入基础 `安全/预算/观测/Eval`，再补 `成本 → 部署`。
- 真实项目：看 [AI 案例](../Case_Studies/AI/README.md)，重点核对工具权限、Session、执行边界和证据等级。

通用模型原理在 `Learning/AI`；本目录只保留调用、编排、治理和交付方法。

## learn-claude-code 实践入口

本目录的概念可以用 `learn-claude-code` 的 `s01-s20` 逐章验证：先跑 `s01_agent_loop` 和 `s02_tool_use`，再做权限/Hook（s03-s04）、Context/Memory（s07-s10）、任务与后台（s12-s14）、团队与 Worktree（s15-s18），最后做 MCP 和综合 Harness（s19-s20）。复制到本目录的实践代码位于 [学习实践/learn-claude-code](./实践/learn-claude-code/README.md)，每个章节的 `code.py` 都是独立实验入口。

项目代码适合实验和对照，不是生产框架。尤其是文件 mailbox、单进程 cron、mock MCP、简化权限和教学版压缩阈值，阅读时要同时标记“机制不变量”和“为了教学而省略的生产约束”。

## ai-agent-learning 实践入口

[ai-agent-learning 实践课程](./实践/ai-agent-learning/README.md)提供另一条更适合从零开始的 SDK-first 路线：Python 工程与 HTTP API → OpenAI/Claude API → Tool Calling → 手写 Agent Loop → FastAPI → LangGraph → Memory → RAG → MCP。完成这条主线后，再用其中的 [LangGraph 专项实验](./实践/ai-agent-learning/langgraph-advanced/README.md)和 [DevPilot 综合项目](./实践/ai-agent-learning/DevPilot/README.md)做框架机制与工程闭环练习。

两套实践的职责不同：`ai-agent-learning` 负责建立 Agent 应用开发基础，`learn-claude-code` 负责深入 Agent Harness 的 Context、权限、任务、恢复、团队和 MCP 机制。主题重叠时优先选择一套完成，不要重复抄写两套课程说明。
