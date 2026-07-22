# Agent 实践

这里集中放 `Learning/Agent` 的可运行代码。理论、边界和生产化判断仍维护在上级目录的章节笔记中，实践目录只保留代码、项目 README、配置示例和测试。

完整的 Python → AI → Agent 学习顺序和实践选择见：[学习地图](../../00_Navigation/AI-Python-Agent学习地图.md)。

## 两条实践路线

- [ai-agent-learning](./ai-agent-learning/README.md)：从 Python 工程、HTTP/API、Provider SDK、Tool Calling、Agent Loop 开始，逐步进入 FastAPI、LangGraph、Memory、RAG、MCP 和 DevPilot，适合作为入门主线。
- [learn-claude-code](./learn-claude-code/README.md)：s01–s20，重点学习 Agent Harness 的工具、权限、Hook、Context、Memory、Task、后台任务、团队、Worktree 和 MCP 机制。

## 选择建议

第一次系统学习 Agent：先完成 `ai-agent-learning/agent-learning-projects/01–09`，再按目标选择 RAG、MCP 或 LangGraph 专项。

已经能调用模型并写过基础 Agent：直接进入 `learn-claude-code/s01–s20`，或用 `ai-agent-learning/DevPilot` 做综合项目。

两套实践都属于教学代码。运行前检查依赖和 Provider 文档，涉及文件写入、外部命令、MCP Server 或真实模型时，先阅读对应理论章节的安全和验证要求。
