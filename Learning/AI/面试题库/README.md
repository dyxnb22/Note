# AI 面试题库

这里集中维护模型原理、训练、推理和 AI 系统的问答题。每道题按“结论 → 机制 → 工程边界 → 追问/验证”组织；长篇原理仍以 `AI/LLM基础.md` 和 `AI/DeepLearning/` 为主文档。

## 推荐顺序

1. [[00_复习路线与答题模板]]
2. [[01_大模型基础]]
3. 遇到训练过程、数值稳定性或 Transformer 细节，回到 [DeepLearning](../DeepLearning/README.md)。
4. 遇到模型注册、推理服务、灰度、漂移和回滚，回到 [ML 系统与 MLOps](../ML系统与MLOps.md)。
5. 遇到 Provider、Tool、State、RAG 应用和 Agent Loop，进入 [Agent 面试题库](../../Agent面试题库/README.md)。

## 归属边界

- 模型是什么、怎么训练、怎么推理：AI。
- 模型如何被 Agent 调用、如何参与工具和工作流：Agent。
- Python 服务如何接入模型：Python 题库；模型行为和系统取舍再回到 AI/Agent。
- 可运行的模型实验和课程项目：`AI/实践/`，不在题库中复制代码。

## 答题标准

不要只背 Transformer、RAG、LoRA 等名词。每道题至少要能说明问题、核心机制、适用边界、质量/性能/成本影响和一种验证方式。
