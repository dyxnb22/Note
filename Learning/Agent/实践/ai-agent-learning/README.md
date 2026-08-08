# ai-agent-learning 实践课程

这是 `Learning/Agent` 的可运行实验区：理论笔记讲概念与边界，代码负责运行、修改和验证。完整顺序以 [LEARNING_PATH](./agent-learning-projects/LEARNING_PATH.md) 为准。

## 主路线

| 阶段 | 入口 | 对应理论 |
|---|---|---|
| 00 | [最小 Agent Loop 练习（可选）](./agent-learning-projects/00_agent_mental_model/README.md) | [LLM 调用](../../01_LLM调用基础.md) · [Tool Calling](../../02_Tool%20Calling.md) · [Agent 架构](../../03_Agent架构与设计.md) |
| 01–02 | [Python 工程与 HTTP API](./agent-learning-projects/01_python_project_template/README.md) | [Python 工程化补充](../../../Python/04_Python%20Agent工程化补充.md)、[LLM 调用基础](../../01_LLM调用基础.md) |
| 03–05 | [SDK、Tool Calling、Agent Loop](./agent-learning-projects/03_openai_cli_chat/README.md) | [LLM 调用基础](../../01_LLM调用基础.md)、[Tool Calling](../../02_Tool%20Calling.md)、[Agent 架构](../../03_Agent架构与设计.md) |
| 06 | [FastAPI Agent Service](./agent-learning-projects/06_fastapi_agent_service/README.md) | [Agent 架构](../../03_Agent架构与设计.md)、[部署与生产化](../../12_部署与生产化.md) |
| 07–09 | [LangGraph、Tool、Memory](./agent-learning-projects/07_langgraph_basic_workflow/README.md) | [Workflow](../../Workflow与编排.md)、[LangGraph](../../LangGraph.md)、[Memory](../../Memory与状态管理.md) |
| 10 | [基础 RAG Agent](./agent-learning-projects/10_rag_agent_basic/README.md) | [RAG](../../RAG.md)、[知识系统](../../知识系统.md) |
| 11–12 | [MCP Server](./agent-learning-projects/11_mcp_server/README.md)、[Claude API](./agent-learning-projects/12_claude_api_agent/README.md) | [MCP](../../MCP与工具协议.md)、[LLM 调用基础](../../01_LLM调用基础.md) |
| 进阶 | [LangGraph 专项实验](./langgraph-advanced/README.md) | StateGraph、Checkpoint、HITL、MCP、Eval |
| 综合 | [DevPilot](./DevPilot/README.md) | 架构、安全、Eval、项目表达 |

## 怎么用

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r agent-learning-projects/07_langgraph_basic_workflow/requirements.txt
python agent-learning-projects/07_langgraph_basic_workflow/main.py
```

理论主线与实践 `03–05` 交替进行：读到 Provider、Tool 和 Loop 时就运行对应项目，不必先把四篇正文全部读完。00 号是可选的无 API 预热；`01–02` 只补 Python/HTTP，`06` 只在需要服务化时进入。需要模型的项目先复制 `.env.example`，不要提交真实密钥。每完成一个项目，只记录：输入与入口、状态/工具轨迹、一次失败边界、你的修改及验证结果。

`langgraph-advanced/` 用于机制对照，`DevPilot/` 用于综合练习；二者完成主路线后再选，不要把同一机制重复实现多遍。代码是教学快照，模型名、依赖、权限和本地存储都要按当前环境复核。
