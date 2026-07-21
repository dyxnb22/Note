# Agent Learning Projects

这是一套面向 Java 后端转 Python / AI Agent / LangGraph / RAG 的循序渐进示例项目集合。

它不是为了展示复杂成品，而是为了让你通过“阅读、运行、修改”逐步建立 Agent 工程直觉。

## 项目列表

```text
01_python_project_template      Python 工程化模板
02_http_api_client              HTTP/API 调用
03_openai_cli_chat              OpenAI CLI 多轮对话
04_tool_calling_agent           Tool Calling 基础
05_simple_agent_loop            手写 Agent Loop
06_fastapi_agent_service        FastAPI Agent 服务
07_langgraph_basic_workflow     LangGraph 基础工作流
08_langgraph_tool_agent         LangGraph Tool Agent
09_langgraph_memory_agent       LangGraph Memory Agent
10_rag_agent_basic              本地 Markdown RAG
11_mcp_server                  MCP Server
12_claude_api_agent            Claude API Agent
```

## 推荐方式

每个项目都独立运行。建议你不要一次性看完，而是按顺序做：

1. 先运行原始代码；
2. 读 README 和注释；
3. 完成 README 里的练习；
4. 用自己的话复述核心流程；
5. 再进入下一课。

## 环境

默认环境：

- macOS
- VS Code
- Python 3.11+
- ChatGPT Plus / Codex

每个项目都有自己的：

```text
README.md
requirements.txt
.env.example
.gitignore
main.py
```

## 安全提醒

不要把真实 API Key 写进代码，也不要提交 `.env`。

所有项目的 `.gitignore` 都包含：

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

## 和实践总目录其他项目的关系

实践总目录下的 `langgraph-advanced/` 和 `DevPilot/` 更偏 LangGraph 专项训练与综合项目。

这个 `agent-learning-projects` 目录更像完整教材：它从 Python 工程化、HTTP、OpenAI SDK 开始，再逐步进入 Tool Calling、Agent Loop、FastAPI、LangGraph 和 RAG。
