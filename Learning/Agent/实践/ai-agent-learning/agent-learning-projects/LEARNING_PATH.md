# Agent 学习路径

> 本页只维护实践顺序、阶段目标和统一验收；单个项目的运行命令、目录和练习以各项目 README 或入口代码为准。课程总说明见 [实践课程 README](../README.md)。

## 课程结构

| 阶段 | 项目 | 主要产物 | 配套理论 |
|---|---|---|---|
| 01 | [Python Project Template](./01_python_project_template/README.md) | 配置、日志、依赖和 CLI 骨架 | [Python Agent 工程化补充](../../../../Python/04_Python%20Agent工程化补充.md) |
| 02 | [HTTP API Client](./02_http_api_client/README.md) | 同步/异步 HTTP、超时和错误处理 | [LLM 调用基础](../../../01_LLM调用基础.md) |
| 03 | [OpenAI CLI Chat](./03_openai_cli_chat/README.md) | 多轮 messages 和 Provider 调用 | [LLM 调用基础](../../../01_LLM调用基础.md) |
| 04 | [Tool Calling Agent](./04_tool_calling_agent/README.md) | schema → tool call → tool result | [Tool Calling](../../../02_Tool%20Calling.md) |
| 05 | [Simple Agent Loop](./05_simple_agent_loop/README.md) | 不依赖框架的有限 Agent Loop | [Agent 架构与设计](../../../03_Agent架构与设计.md) |
| 06 | [FastAPI Agent Service](./06_fastapi_agent_service/README.md) | Agent 服务化和请求边界 | [Agent 架构与设计](../../../03_Agent架构与设计.md) · [部署与生产化](../../../12_部署与生产化.md) |
| 07 | [LangGraph Basic Workflow](./07_langgraph_basic_workflow/README.md) | State、Node、Edge 和 Graph | [Workflow 与编排](../../../Workflow与编排.md) |
| 08 | [LangGraph Tool Agent](./08_langgraph_tool_agent/README.md) | 图中的工具节点和条件边 | [LangGraph](../../../LangGraph.md) |
| 09 | [LangGraph Memory Agent](./09_langgraph_memory_agent/README.md) | State、thread_id 和 Checkpoint | [Memory 与状态管理](../../../Memory与状态管理.md) |
| 10 | [RAG Agent Basic](./10_rag_agent_basic/README.md) | 文档、chunk、检索和 Context 注入 | [RAG](../../../RAG.md) |
| 11 | [MCP Server](./11_mcp_server/main.py) | Tool、Resource、Prompt 的协议服务 | [MCP 与工具协议](../../../MCP与工具协议.md) |
| 12 | [Claude API Agent](./12_claude_api_agent/main.py) | 原生 API、Streaming、Tool Use 和缓存 | [LLM 调用基础](../../../01_LLM调用基础.md) |

## 推荐顺序与分支

### 01–06：应用工程主线

完成 01–02 的 Python/HTTP 前置，再完成 03–05 的 LLM、Tool Calling 和 Agent Loop，最后用 06 把 CLI 变成服务。到这里应能写出一个有配置、超时、日志、工具合同和终止条件的最小 Agent。

### 07–09：框架与状态分支

07–08 用同一类任务对比普通函数、Workflow 和 Tool Agent；09 再加入持久化状态。不要把 LangGraph 当成 Agent 的前置条件，先理解状态转移，再用框架表达它。

### 10：知识分支

10 只是最小 RAG 实验，用来观察 chunk、检索和 Context 注入的关系。生产级摄取、权限、引用、混合检索和评测分别进入 [文档摄取与解析](../../../文档摄取与解析.md)、[检索系统工程](../../../检索系统工程.md)、[知识系统](../../../知识系统.md) 和 [Agent Eval 实验方法](../../../09_Agent%20Eval实验方法.md)。

### 11–12：协议与 Provider 对照

11 用于理解跨宿主工具协议，12 用于对照另一套 Provider 的原生调用形状。它们是扩展和对照实验，不应替代 03–05 的核心机制学习。

## 每个项目的统一验收

完成一个项目后，至少记录：

1. 运行入口、配置和依赖版本；
2. State、messages 或工具轨迹发生了什么变化；
3. 一个成功 Case 和一个失败/边界 Case；
4. 你修改了什么，以及如何验证；
5. 如果项目引入了新抽象，它相对上一项目解决了什么问题、增加了什么成本。

不要只记录“能跑”。对 Agent 项目尤其要记录工具调用、停止原因、上下文大小、错误路径和是否产生副作用。

## 统一运行约定

每个项目独立安装依赖并使用自己的环境；真实模型项目从对应的 .env.example 创建 .env，不要把密钥写入代码或笔记。11、12 没有独立 README，运行命令和依赖以各目录中的 main.py、requirements.txt 为准。

教学项目中的 Mock Provider、内存 Checkpointer、关键词检索和本地文件存储是为了观察机制，不是生产实现。完成主线后，再用 [实践 README](../README.md) 中的 LangGraph Advanced 或 DevPilot 做综合练习。
