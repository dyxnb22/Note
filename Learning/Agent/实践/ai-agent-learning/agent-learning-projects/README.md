# Agent Learning Projects

13 个（编号 00–12）从一次模型调用、Tool Calling、Agent Loop、Python 工程、HTTP、SDK、FastAPI、LangGraph、RAG 到 MCP 的递进实验。00 是可选的无 API 预热；按 [LEARNING_PATH](./LEARNING_PATH.md) 学习，本页只保留目录索引。

## 项目

| 编号 | 目录 | 主题 |
|---|---|---|
| 00 | `00_agent_mental_model` | 最小 Agent Loop（无 API，可选） |
| 01 | `01_python_project_template` | Python 工程模板 |
| 02 | `02_http_api_client` | HTTP/API 调用 |
| 03 | `03_openai_cli_chat` | SDK 多轮对话 |
| 04 | `04_tool_calling_agent` | Tool Calling |
| 05 | `05_simple_agent_loop` | 手写 Agent Loop |
| 06 | `06_fastapi_agent_service` | FastAPI 服务 |
| 07 | `07_langgraph_basic_workflow` | LangGraph 工作流 |
| 08 | `08_langgraph_tool_agent` | LangGraph Tool Agent |
| 09 | `09_langgraph_memory_agent` | Memory Agent |
| 10 | `10_rag_agent_basic` | 本地 Markdown RAG |
| 11 | `11_mcp_server` | MCP Server |
| 12 | `12_claude_api_agent` | Claude API Agent |

## 运行约定

每个目录按自己的 README 和 `requirements.txt` 运行。先运行，再修改，再验证；不要把真实 API Key 写入代码或提交 `.env`。默认示例面向 Python 3.11+，具体模型、依赖和 Provider 配置以项目当前文件为准。

同级的 `langgraph-advanced/` 是框架专项实验，`DevPilot/` 是综合项目；它们不替代这条主路线。
