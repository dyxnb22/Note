# 权重衰减与 Dropout

## 权重衰减

L2 正则在损失中加入 `λ/2 ||w||²`，促使权重不过大，等价于更新时对权重做轻微收缩。PyTorch 中常通过 optimizer 的 `weight_decay` 设置；通常不对 bias 和归一化层参数施加强衰减。

## Dropout

训练时随机将部分隐藏单元置零，并对剩余输出缩放；这迫使网络不依赖某个特定单元。评估时 Dropout 关闭，使用完整网络，因此必须正确调用 `model.train()` 和 `model.eval()`。

## 如何选择

正则化是泛化工具，不是修复错误数据的工具。先从小的 weight decay 开始，根据验证曲线调整。现代 CNN/Transformer 中，数据增强、归一化、预训练和合理训练策略往往同样重要。

## 最小练习

固定模型与训练轮数，分别运行无正则、仅 weight decay、仅 Dropout、两者同时使用，比较训练—验证差距。

`#regularization #weight-decay #dropout`
