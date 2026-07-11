# RNN 从零实现与框架实现

从零实现时，显式创建输入到隐藏、隐藏到隐藏、隐藏到输出的参数，手动维护 state；框架实现使用 `nn.RNN`。两者要共享相同的数据、loss 和训练策略，才可以公平比较。

序列 batch 的 state 必须按 batch 维对齐；如果 batch 之间连续读取文本，可以传递 detach 后的 state；如果每个 batch 独立，必须重置 state。`detach()` 防止反向图无限延长。

最小练习：用两种实现训练字符语言模型，并实现 temperature 采样生成一段文本；解释温度提高后为何更随机。

`#rnn #pytorch #text-generation`
