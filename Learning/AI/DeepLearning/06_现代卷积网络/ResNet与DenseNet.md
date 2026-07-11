# ResNet 与 DenseNet

ResNet 学习残差 `F(x)+x`，捷径路径让梯度更容易传播，使深网络可训练。维度不一致时，捷径用 1×1 卷积投影；一致时优先 identity shortcut。

DenseNet 将每层特征与后续层拼接，鼓励特征复用，但会增加内存和通道管理复杂度。两者都说明：优秀架构不仅要有表达力，还要让优化器能有效训练。

最小练习：实现 basic residual block，打印主分支和捷径分支 shape；解释何时需要 downsample。

`#resnet #densenet #residual-learning`
