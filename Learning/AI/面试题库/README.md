# AI 面试题库

这里集中维护模型原理、训练、推理和 AI 系统的问答题。每道题按“结论 → 机制 → 工程边界 → 追问/验证”组织；长篇原理仍以 `AI/LLM基础.md` 和 `AI/DeepLearning/` 为主文档。

## 阅读入口

先读 [[01_大模型基础]]；遇到训练过程、数值稳定性或 Transformer 细节，再回到 [DeepLearning](../DeepLearning/README.md)。模型注册、推理服务、灰度、漂移和回滚见 [ML 系统与 MLOps](../ML系统与MLOps.md)。Provider、Tool、State、RAG 应用和 Agent Loop 见 [Agent 模块](../../Agent/README.md)。

## 归属边界

- 模型是什么、怎么训练、怎么推理：AI。
- 模型如何被 Agent 调用、如何参与工具和工作流：Agent。
- Python 服务如何接入模型：Python 学习路线；模型行为和系统取舍再回到 AI/Agent。
- 可运行的模型实验和课程项目：`AI/实践/`，不在题库中复制代码。

## 答题标准

答题时先说明要解决什么问题，再按“输入/状态 → 机制 → 输出”讲清因果链；随后补充适用边界和质量、性能、成本上的代价，最后给出验证办法，如数值检查、离线评测、消融、压测或线上灰度。不要只罗列 Transformer、RAG、LoRA 等名词。
