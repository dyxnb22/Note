# LangGraph 专项实验

这里保留 `ai-agent-learning` 根目录下的 LangGraph 进阶示例，按“图基础 → 工具 → 记忆 → 多 Agent → 生产控制 → MCP → Eval”组织。

| 目录 | 重点 | 配套理论 |
|---|---|---|
| `01-basics` | State、Node、Edge、条件路由 | [Workflow 与 LangGraph](../../../Workflow与LangGraph.md) |
| `02-tools` | Tool、ToolNode、ReAct 闭环 | [Tool Calling](../../../Tool%20Calling.md) |
| `03-memory` | MemorySaver、thread_id、状态恢复 | [Memory 与状态管理](../../../Memory与状态管理.md) |
| `04-multi-agent` | 子图、共享 State、职责拆分 | [多 Agent 协作的边界与模式](../../../多Agent协作的边界与模式.md) |
| `05-production` | interrupt、resume、流式事件 | [安全与可控性](../../../安全与可控性.md)、[部署与生产化](../../../部署与生产化.md) |
| `06-mcp` | MCP Server / Client、工具复用 | [MCP 与工具协议](../../../MCP与工具协议.md) |
| `07-eval` | 轨迹检查、规则评估、LLM-as-Judge | [Eval 与测试体系](../../../Eval与测试体系.md) |

## 运行

```bash
cd "/Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Agent/实践/ai-agent-learning"
python3 -m venv .venv
source .venv/bin/activate
pip install -r langgraph-advanced/requirements.txt
python langgraph-advanced/01-basics/hello_graph.py
```

`01-basics`、`04-multi-agent` 等示例主要用于理解图机制；涉及模型或外部服务的实验，先阅读代码中的配置说明。`06-mcp` 提供 Mock 模式，完整模式需要额外安装 MCP 依赖。

这些例子和 `agent-learning-projects/07`～`12` 有意存在少量交叉：前者用于拆解 LangGraph 机制，后者用于完整的渐进式项目练习。不要把两套内容当成两门独立课程重复通读。
