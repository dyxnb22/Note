# Learning/AI

这个目录提供 AI 与模型原理的按需参考，不是进入 Agent 前必须全部完成的理论课程。它主要支撑三件事：

1. **读懂论文和技术博客**：理解模型行为和设计决策背后的原理
2. **解释 LLM 工作原理**：能在面试中清楚讲清 tokenization、generation、fine-tuning、alignment
3. **为应用工程提供判断依据**：理解模型能力边界，才能做出合理的系统设计决策

## 案例

项目专属结构和证据见 [AI 案例索引](../Case_Studies/AI/README.md)；通用模型原理仍以本目录正文为准。

## 与 Python / Agent 目录的边界

- 模型是什么、怎么工作、为什么这样设计 → 放这里
- Python 语言和服务工程 → 放 `Learning/Python/`
- 如何调用模型、构建 Agent、设计 RAG → 进入 [Agent 模块](../Agent/README.md)，知识点和面试问答按主题组织
- 训练数据、实验追踪、模型注册、模型服务与漂移 → 放 `ML系统与MLOps.md`
- 可运行的课程实验、样例输入和实验输出 → 放 `Learning/AI/实践/`
- 边界案例：context window 的原理（这里）vs 如何管理 context 窗口（Agent）

## 按目标选择入口

| 当前目标 | 先看 | 按需补充 |
|---|---|---|
| 准备模型面试 | [LLM 基础](./LLM基础.md)、[AI 面试题库](./面试题库/README.md) | 需要训练或 Transformer 细节时进入 [DeepLearning](./DeepLearning/README.md) |
| 做 Agent/RAG 项目 | [Agent 模块](../Agent/README.md) | 遇到模型机制问题再回到 LLM 基础；可运行实验见 [AI 实践](./实践/README.md) |
| 补模型理论 | [DeepLearning 路线](./DeepLearning/README.md) → [LLM 基础](./LLM基础.md) | 侧重理解，不要求手推所有公式 |
| 使用 AI 编程工具 | [AI 工具与编程助手](./AI工具与编程助手.md) | 其他模型理论按需补 |
| 部署模型服务 | [DeepLearning](./DeepLearning/README.md) / [LLM 基础](./LLM基础.md) | [ML 系统与 MLOps](./ML系统与MLOps.md) → [生产系统工程](../Delivery/07_生产系统工程.md) |

没有全员必读清单；从当前问题进入相应主题即可。

## 常见混淆边界

| 问题 | 答案 |
|------|------|
| context window 放哪里？ | 原理放这里（`LLM基础.md`）；如何在代码里管理刷 `Agent/02_Prompt与上下文/Prompt与Context Engineering.md` |
| tokenization 放哪里？ | 放这里；Context 的实际管理刷 `Agent/02_Prompt与上下文/Prompt与Context Engineering.md` |
| fine-tuning 放哪里？ | 原理（LoRA 数学、训练流程）放这里；模型行为训练的工程判断刷 [推理与模型行为](../Agent/10_模型与推理/03_推理与模型行为.md) |
| RAG 是理论还是工程？ | 检索与生成链路刷 [RAG 与检索](../Agent/06_RAG与知识库/RAG与检索.md)，来源、权限和版本治理刷 [知识摄取与 GraphRAG](../Agent/06_RAG与知识库/知识摄取与GraphRAG.md)；为什么 RAG 能减少幻觉的原理放 `LLM基础.md` |
