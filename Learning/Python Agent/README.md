# AI 应用工程知识库

这里承载从 Python 工程基础到 Agent、RAG、MCP 和生产交付的工程内容；模型原理回到 [`AI`](../AI/README.md)。

主入口：[Agent 工程目录](./Agent/README.md)。详细五阶段路线见[学习路线图](./Agent/学习路线图.md)，不在本页重复完整目录。

## 两条线

| 方向 | 入口 |
|---|---|
| Python 服务工程 | [Python](./Python/README.md)：语法、工程化、HTTP、FastAPI、排错 |
| AI 应用工程 | [Agent](./Agent/README.md)：模型调用、工具、上下文、RAG、工作流、安全、评测、部署 |

## 选择方式

- 已有 Python 基础：从 [LLM 调用基础](./Agent/LLM调用基础.md) 开始。
- 做 RAG：`LLM 调用 → Context → RAG → Eval`。
- 做 Agent：`LLM 调用 → Agent 架构 → Tool Calling → Memory/Workflow`。
- 上生产：补 `安全 → 观测 → 成本 → 部署`。
- 做完项目或准备面试：使用 [Career 项目表达](../Career/项目表达.md) 和 [AI 专项面试补充](./Agent/项目表达与面试.md)。
