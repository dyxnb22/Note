# Python 学习路径

这页只负责“先学什么、什么时候进入 Agent”；具体内容和场景索引见 [Python 工程基础](./README.md)。

## 推荐顺序

### 1. 语言基础

阅读 [Python 核心语法](./Python核心语法.md)。目标是能读懂变量、容器、函数、异常、文件/JSON、模块和 `async/await`，并完成几个小脚本。

### 2. 工程化

阅读 [Python 工程化](./Python工程化.md)。重点是虚拟环境、依赖、`pyproject.toml`、配置、日志、测试和项目入口。

### 3. 外部 API 与 Agent 前置

按项目需要阅读：

- [HTTP 与 API 调用](./HTTP与API调用.md)：`requests`/`httpx`、超时、重试和客户端封装；
- [Python Agent 工程化补充](./Python%20Agent工程化补充.md)：Pydantic、asyncio、类型边界、幂等、并发和测试。

### 4. 服务化与可维护性

- 需要 API 服务时：阅读 [FastAPI](./FastAPI.md)；
- 项目开始变复杂时：阅读 [Python 代码组织与设计模式](./Python代码组织与设计模式.md)；
- 遇到问题时：查 [错误与 Debug](./错误与Debug.md)。

## 进入 Agent

Python 基础和工程化完成后，进入 [AI Agent 工程知识库](../Agent/README.md)；完整路线见 [AI Agent 工程学习路线图](../Agent/学习路线图.md)。最小主线是：

`LLM 调用基础 → Tool Calling → Agent 架构与设计 → Context 工程 → 安全/验证 → Eval`

按目标再选择：

- 知识库问答：加 [RAG](../Agent/RAG.md) 和 [知识系统](../Agent/知识系统.md)；
- 固定流程或可恢复编排：先看 [Workflow 与编排](../Agent/Workflow与编排.md)，再按需使用 [LangGraph](../Agent/LangGraph.md)；
- 外部工具生态：加 [MCP 与工具协议](../Agent/MCP与工具协议.md)；
- API 交付：回到 [FastAPI](./FastAPI.md)，再看 Agent 的部署文档。

## 边界

- `Python/`：语言、标准库、项目工程、HTTP 和服务化；
- `Python Agent工程化补充.md`：只讲 Python 能力如何落到 Agent Runtime，不重复完整的 LLM 协议和 Agent 设计；
- `Agent/`：LLM、工具协议、Agent Loop、RAG、编排、治理、评测和生产交付。
