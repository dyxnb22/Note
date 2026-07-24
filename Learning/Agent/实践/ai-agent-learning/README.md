# ai-agent-learning 实践课程

这里是从外部项目 `ai-agent-learning` 整理进 Notes 的可运行实践快照。

它补充 `Learning/Agent/` 的理论笔记：理论笔记负责概念、边界和生产化判断；这里负责运行代码、观察状态变化、修改练习和记录实验结果。源项目保留在原目录中，本目录不包含真实密钥、虚拟环境或运行缓存。

## 学习入口

| 阶段 | 实践目录 | 配套理论 |
|---|---|---|
| 01–02 | [Python 工程与 HTTP API](./agent-learning-projects/01_python_project_template/README.md) | [Python Agent 工程化补充](../../../Python/04_Python%20Agent工程化补充.md)、[LLM 调用基础](../../01_LLM调用基础.md) |
| 03–05 | [SDK、Tool Calling、Agent Loop](./agent-learning-projects/03_openai_cli_chat/README.md) | [LLM 调用基础](../../01_LLM调用基础.md)、[Tool Calling](../../02_Tool%20Calling.md)、[Agent 架构与设计](../../03_Agent架构与设计.md) |
| 06 | [FastAPI Agent Service](./agent-learning-projects/06_fastapi_agent_service/README.md) | [部署与生产化](../../12_部署与生产化.md) |
| 07–09 | [LangGraph、Tool、Memory](./agent-learning-projects/07_langgraph_basic_workflow/README.md) | [Workflow 与编排](../../Workflow与编排.md)、[LangGraph](../../LangGraph.md)、[Memory 与状态管理](../../Memory与状态管理.md) |
| 10 | [基础 RAG Agent](./agent-learning-projects/10_rag_agent_basic/README.md) | [RAG](../../RAG.md)、[知识系统](../../知识系统.md) |
| 11–12 | [MCP Server、Claude API](./agent-learning-projects/11_mcp_server/main.py) | [MCP 与工具协议](../../MCP与工具协议.md)、[LLM 调用基础](../../01_LLM调用基础.md) |
| 进阶 | [LangGraph 专项实验](./langgraph-advanced/README.md) | Tool、Workflow、Multi-Agent、Security、MCP、Eval |
| 综合项目 | [DevPilot](./DevPilot/README.md) | Agent 架构、代码 Agent 基础设施、安全、Eval、项目表达 |

完整课程顺序见 [Agent Learning Projects 学习路径](./agent-learning-projects/LEARNING_PATH.md)。

## 三条实践线

### 1. Agent Learning Projects：主学习路线

这是最适合从头学习的一组 12 个小项目。每个项目都有独立的 README、依赖、配置示例和练习，建议按 01 → 12 顺序完成，不要一开始跳到 LangGraph 或多 Agent。

### 2. LangGraph Advanced：框架专项对照

这里保留原项目根目录下的 `01-basics`～`07-eval`。它们和上面的 07–09、11 有主题交叉，但更集中展示 StateGraph、ToolNode、Checkpoint、Human-in-the-loop、MCP 和 Eval。完成主路线后，把它当作框架机制复习和对照实验。

### 3. DevPilot：综合项目

DevPilot 将 Router、Analyzer、Fixer、Approval、Reviewer 和 PR Creator 组合成一个 LangGraph 流程。当前版本只生成建议级 diff，不直接改文件，适合练习状态设计、人工审批、工具边界和可控的项目表达。

## 如何运行

```bash
# 在本 README 所在目录下执行
python3 -m venv .venv
source .venv/bin/activate
```

按项目安装自己的依赖。例如：

```bash
pip install -r agent-learning-projects/07_langgraph_basic_workflow/requirements.txt
python agent-learning-projects/07_langgraph_basic_workflow/main.py
```

LangGraph 专项实验：

```bash
pip install -r langgraph-advanced/requirements.txt
python langgraph-advanced/01-basics/hello_graph.py
```

需要调用模型的项目，再进入对应目录复制 `.env.example` 为 `.env` 并填写自己的配置。`.env` 已被本地忽略，禁止把真实密钥提交到 Notes。

## 练习记录建议

完成每章后至少记录四项：

1. 运行入口和输入；
2. State、messages 或工具轨迹发生了什么变化；
3. 一次失败或边界情况；
4. 你改动了什么，以及改动后如何验证。

实践代码是教学快照，不是生产框架。尤其要重新审视示例中的模型名、依赖最低版本、mock MCP、内存 Checkpointer、简化权限和本地文件存储。
