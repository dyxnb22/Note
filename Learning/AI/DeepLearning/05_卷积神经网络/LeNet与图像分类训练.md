# LeNet 与图像分类训练

LeNet 将卷积、激活、池化与全连接分类头串成早期 CNN：前部抽取局部空间特征，后部完成分类。它适合用来理解完整 CNN，不应作为现代视觉任务的强基线。

训练时先打印每层输出 shape，尤其注意展平前的维度。若训练慢，检查数据是否搬到 GPU；若准确率低，先确认像素归一化、标签和 eval 模式，再调整宽度、学习率和轮数。

最小练习：在 Fashion-MNIST 上训练 LeNet，比较有无归一化以及不同学习率的影响。

## 配套实践

- [DeepPath Lab Module 04：Convolutional Neural Networks](../../实践/DeepPathLab/modules/04_cnn/README.md)：完成 LeNet 风格图像分类基线、可视化诊断和错误分析。

`#lenet #cnn #image-classification`
