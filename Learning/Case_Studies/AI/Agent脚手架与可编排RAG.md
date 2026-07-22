# Agent 脚手架与可编排 RAG

这类项目把模型、工具、上下文、工作流、会话和观测抽成可复用底座，再通过管理端配置具体 Agent。

## 三层结构

1. **模型与工具底座**：Spring AI、LangChain4j、Google ADK、MCP 和模型适配。
2. **执行脚手架**：Runner、Loop、Sequential、Parallel、Session、Plugin、Skills 和回调。
3. **业务配置**：Prompt、Advisor、知识库、工具组合、权限和场景流程。

Agent 不是一段 Prompt；它至少包含决策、执行、状态、停止条件和失败处理。

## RAG 链路

```text
文档/SQL/TXT/Word/Git
        ↓
解析 → 切分 → 向量化 → 召回 → 重排 → 上下文装配
        ↓
模型回答 → 引用/结构化输出 → 评估与反馈
```

PostgreSQL 可保存向量数据，Redis 适合标签、配置和快速状态；管理端维护模型、Client、MCP、Advisor、Prompt 等资源，应用代码与具体 Agent 配置解耦。

## 边界

- `Loop`、`Sequential`、`Parallel` 是控制结构；Runner 是执行边界；Plugin/Hook 承载治理和观测。
- Planning/FlowAgent 适合把复杂请求分解为规划、执行和汇总，但强状态、强权限业务仍应由领域代码控制。
- RAG 解决知识缺失和更新问题；不能替代权限校验、业务规则和结果验证。
- 动态配置必须有版本、发布、回滚、权限和审计，不应把所有逻辑藏在拖拉拽流程里。

相关：[Agent 架构与设计](../../Agent/Agent架构与设计.md)、[RAG](../../Agent/RAG.md)、[知识系统](../../Agent/知识系统.md)、[Workflow 与编排](../../Agent/Workflow与编排.md)、[LangGraph](../../Agent/LangGraph.md)。

来源：`xfg-planet/02-AI应用范式/Agent与工作流/AI-Agent脚手架-知识提炼.md`、`RAG与知识库/可编排Agent-知识提炼.md`。
