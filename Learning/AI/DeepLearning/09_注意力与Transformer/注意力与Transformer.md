# 注意力与Transformer

本章从查询、键和值的加权检索开始，逐步进入自注意力、多头机制、位置表示和 Transformer 结构。

## 注意力机制与注意力评分函数
注意力以 query 查询一组 key-value：先计算 query 和 key 的相关性，再 softmax 得到权重，最后对 value 加权求和。它解决的是“在当前步骤应从所有候选信息中取什么”的问题。

加性注意力用小网络打分；缩放点积注意力用 `QKᵀ/sqrt(d)`，便于矩阵并行计算。缩放项避免维度变大时点积方差过大，使 softmax 饱和。mask 用于屏蔽 padding 或未来位置，屏蔽值在 softmax 前设为极小数。

最小练习：对一个 query 和三个 key/value 手算 softmax 权重；改变一个 key 的相似度，观察输出如何变化。

## 多头注意力、自注意力与位置编码
多头注意力将 Q/K/V 投影到多个子空间，各头可学习不同关系，再拼接输出。自注意力令 query、key、value 来自同一序列，能直接连接任意两个位置，但计算量随序列长度平方增长。

注意力本身不感知顺序，因此需要位置编码。正弦位置编码提供固定相对规律；可学习位置嵌入更灵活；现代模型还常用旋转位置编码。因果 mask 保证语言模型位置 t 不看未来 token。

最小练习：解释 padding mask 和 causal mask 的差别，并为 4 个 token 写出因果 mask 的可见矩阵。

## Transformer 从结构到实现
标准 Transformer 编码器层由多头自注意力、残差连接、LayerNorm、前馈网络组成；解码器额外有 masked self-attention 与 encoder-decoder attention。LLM 常使用 decoder-only 架构，仅保留因果自注意力和前馈层。

实现时先确保 shape：常见 batch-first 输入为 `(N,T,D)`；attention mask 的维度必须能广播到注意力分数。Pre-LN（先 LayerNorm）在深层训练中通常更稳定。推理缓存 K/V，避免每生成一 token 重算全部历史。

最小练习：实现一个单头 masked self-attention，输入 `(2,5,16)`，验证输出 shape 不变，并验证未来位置权重为零。

## 学习与验证

- 运行对应最小代码，记录数据、随机种子、模型、优化器和指标。
- 每次只改变一个变量，对比训练曲线、验证指标、吞吐和显存。
- 把失败归因到数据、目标函数、优化、容量或系统资源，而不是只换模型。
- 能用自己的话解释本章各机制之间的因果关系，再进入下一章。

## 从零实现检查点

实现顺序：

1. 单头 `QKᵀ/sqrt(d)`。
2. Padding/Causal Mask。
3. Softmax 与 Dropout。
4. 多头 reshape/transpose。
5. 输出投影。
6. Residual + LayerNorm + FFN。
7. 多层堆叠和 LM Head。

每一步用 Shape、Mask 可见矩阵和与框架实现的数值对照验证。

## 残差与归一化

Pre-LN 把 LayerNorm 放在子层之前，深层训练通常更稳定；Post-LN 是原始结构。两者改变梯度路径和最终归一化位置，加载权重时不可混用。

FFN 对每个 Token 独立进行通道变换，通常包含升维、激活、降维。现代模型可能使用 SwiGLU 等门控变体。

## 复杂度与长序列

全注意力的分数矩阵随序列长度为 O(T²)，显存也可能成为瓶颈。FlashAttention 通过更好的内存访问和分块计算精确注意力，不是简单近似算法。

稀疏、滑窗、线性注意力和状态空间模型有不同能力边界，不能只按复杂度选型。

## 推理与 KV Cache

自回归生成时缓存历史 K/V，使每一步不重算全部历史层。Cache 占用随层数、序列、Batch 和 KV Head 增长；连续批处理、分页 Cache 和 GQA/MQA 用于改善吞吐与容量。

## 导航与关联

- 同一路线：[现代循环网络与 Seq2Seq](../08_现代循环网络与序列到序列/现代循环网络与Seq2Seq.md) · [优化与训练诊断](../10_优化与训练策略/优化与训练诊断.md)

`#attention #transformer #self-attention`
