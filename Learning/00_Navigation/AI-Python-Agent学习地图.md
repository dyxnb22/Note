# Python、AI 与 Agent 的边界地图

本页只解决三个目录的分工和起点选择，不复制各自目录，也不记录个人学习进度。

## 三层关系

```text
Python：语言、工程、HTTP、异步和服务基础
   ↓ 只补项目缺少的能力
AI：模型、训练、表示和 LLM 原理
   ↓ 只在需要理解模型行为时进入
Agent：模型调用、工具、状态、编排、治理和交付
```

实践代码属于对应主题的验证材料，不再形成第四套理论：

- [Python](../Python/README.md)：语言与通用工程问题。
- [AI](../AI/README.md)：模型为什么这样工作、如何训练。
- [Agent 面试题库](../Agent面试题库/README.md)：如何调用模型并构建可控系统。

## 根据当前目标选择起点

| 当前目标 | 从哪里开始 | 不需要先做什么 |
|---|---|---|
| 做 Agent 应用 | Agent 面试题库 | 不先通读 Python、深度学习和全部 LLM 原理 |
| Python 基础不足 | Python 问题地图 | 不默认重做已经会的语法练习 |
| 理解 LLM 行为 | [LLM 基础](../AI/LLM基础.md) 的相关章节 | 不为了 Agent 调用先完成整套模型训练 |
| 自己训练模型 | [DeepLearning](../AI/DeepLearning/README.md) | 不并行展开 Agent、RAG 和全部应用分支 |
| 把模型做成服务 | [ML 系统与 MLOps](../AI/ML系统与MLOps.md) | 不在概念页重复实现部署练习 |

遇到概念阻塞时才向上一层补课。例如看不懂异步取消回到 Python；看不懂 token、生成或训练回到 AI；工具、State、Context 和恢复问题留在 Agent。

## 实践如何选择

- Agent 入门默认刷 [Agent 实践与项目表达题](../Agent面试题库/12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md)。
- 深度学习只选择与当前模型目标对应的 [DeepPath Lab](../AI/实践/DeepPathLab/README.md) 模块。
- LLM 研究、微调或评测按需使用 [llm_learning](../AI/实践/llm_learning/README.md)，不与 Agent 主线重复通读。
- Python 基础练习只在语法和工程基础确实阻塞项目时使用。

同一个机制选择一条主要实践；其他实现用于对照，不形成新的待办。

## 维护边界

- Python 正文不解释模型和 Agent Loop。
- AI 正文不维护 Provider 调用、工具执行和应用编排。
- Agent 正文不重复 Python 语法、神经网络训练和模型架构推导。
- 跨目录关系只在本页维护；具体主题顺序回到各自唯一入口。
