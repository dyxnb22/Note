# 编码器—解码器与 Seq2Seq

Seq2Seq 用 encoder 将源序列编码为状态，用 decoder 条件生成目标序列。翻译、摘要等输入输出长度不同的任务可用此范式。

朴素 Seq2Seq 把整句压成固定向量，长句容易形成信息瓶颈；注意力机制允许 decoder 每一步选择关注的 encoder states，随后成为 Transformer 的核心思路。训练常用 teacher forcing，评估应使用真实的自回归生成。

最小练习：画出机器翻译中 source、encoder state、decoder input、target 的时间关系；说明训练和推理输入有何不同。

`#encoder-decoder #seq2seq #machine-translation`
