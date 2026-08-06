# Softmax 回归与图像分类

## 从回归到分类

多分类模型先对每个类别输出 logits：`z=XW+b`。Softmax 将 logits 变成和为 1 的概率：`exp(z_i)/sum(exp(z_j))`。训练时应把 logits 直接传给 `CrossEntropyLoss`，它内部完成稳定的 log-softmax，手动先 softmax 容易数值不稳。

## 标签与形状

对 `N` 个样本、`C` 类：模型输出 shape 为 `(N,C)`，标签是类别索引 shape `(N,)`，dtype 为 `torch.long`。不要把标签错误做成 `(N,C)` one-hot 后仍交给默认 CrossEntropyLoss。

## 图像分类流水线

Fashion-MNIST 等数据集的图像先转 tensor，必要时归一化；使用 DataLoader 分 batch；训练时最小化交叉熵；评估时比较 `argmax(logits, dim=1)` 与标签。准确率容易理解，却会掩盖类别不平衡和置信度问题。

## 数值稳定性

直接计算 `exp(1000)` 会溢出。稳定 softmax 会先减去每行最大值，概率不变。实际项目优先使用框架提供的 fused loss。

## 最小练习

在 Fashion-MNIST 上实现 softmax 回归，随机展示预测正确和错误的图片各 6 张，并观察最容易混淆的类别。

## 配套实践

- [DeepPath Lab Module 02：Linear Models](../../实践/DeepPathLab/modules/02_linear_models/README.md)：在回归基础上补充 softmax 分类和优化行为实验。

`#softmax #classification #fashion-mnist`
