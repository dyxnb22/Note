# GoogLeNet 与 BatchNorm

Inception 模块并行使用不同尺度卷积和池化，再在通道维拼接，让网络自行选择合适感受野；1×1 卷积常用于降维，控制计算量。

BatchNorm 在训练时用 batch 统计量标准化激活，再学习缩放与偏移；推理时使用运行均值/方差。因此小 batch、train/eval 状态混用会导致问题。BN 常允许更大学习率，但不是“任何网络都必需”的开关。

最小练习：在一个 CNN 中加入/移除 BatchNorm，比较收敛速度并说明 train 与 eval 输出为何不同。

`#googlenet #inception #batchnorm`
