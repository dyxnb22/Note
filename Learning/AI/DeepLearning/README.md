# 动手学深度学习路线

本目录以李沐《动手学深度学习》（D2L）的章节逻辑组织：先能写出训练循环，再理解模型为何有效，最后进入视觉、自然语言处理和 Transformer。每篇都应完成“读概念 → 运行最小代码 → 改一个变量 → 记录结果”四步。

## 学习顺序

`00_环境与工具` → `01_预备知识` → `02_线性神经网络` → `03_多层感知机` → `04_深度学习计算` → `05_卷积神经网络` → `06_现代卷积网络` → `07/08_循环网络` → `09_注意力与Transformer` → `10/11_优化与性能` → `12_视觉` → `13_NLP`。

## 与其他目录的边界

- 这里学习模型训练、表示、架构和实验；`../LLM基础.md` 解释现代 LLM 的工作全链路。
- 这里的 NLP 止于理解 BERT/Transformer；RAG、Agent、评测和部署在 `Learning/Agent/`。
- 默认采用 PyTorch。每个实验记录数据集、随机种子、指标、超参数和失败原因。

## 配套实践

- [深度学习到 LLM 学习文档](../实践/llm_learning/00_deep_learning_for_llm/学习文档.md) 与 [tiny next-token model](../实践/llm_learning/00_deep_learning_for_llm/project/tiny_next_token_model.py)：把 token、logits、softmax、loss 和梯度下降串起来。
- [Transformer 学习文档](../实践/llm_learning/00_transformer_foundation/学习文档.md) 与 [self-attention demo](../实践/llm_learning/00_transformer_foundation/project/self_attention_demo.py)：运行最小 Q/K/V 注意力实验。
- [DeepPath Lab 对应关系](../实践/DeepPathLab/与%20Notes%20的对应关系.md)：把本目录的理论章节落到 01–04 四个项目模块，统一记录实现、实验和报告。

这些实验是概念桥接，不替代本目录的 PyTorch/D2L 系统学习。

## 完成标准

能不用复制粘贴地实现线性回归、MLP、CNN、RNN/Seq2Seq、注意力和 Transformer 的训练骨架；能解释 loss 曲线异常、过拟合和显存不足的原因。

`#deep-learning #d2l #pytorch #index`
