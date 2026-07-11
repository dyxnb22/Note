# Transformer 从结构到实现

标准 Transformer 编码器层由多头自注意力、残差连接、LayerNorm、前馈网络组成；解码器额外有 masked self-attention 与 encoder-decoder attention。LLM 常使用 decoder-only 架构，仅保留因果自注意力和前馈层。

实现时先确保 shape：常见 batch-first 输入为 `(N,T,D)`；attention mask 的维度必须能广播到注意力分数。Pre-LN（先 LayerNorm）在深层训练中通常更稳定。推理缓存 K/V，避免每生成一 token 重算全部历史。

最小练习：实现一个单头 masked self-attention，输入 `(2,5,16)`，验证输出 shape 不变，并验证未来位置权重为零。

`#transformer #layernorm #kv-cache`
