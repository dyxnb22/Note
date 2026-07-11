# PyTorch 环境、张量与 Notebook

## 目标

在开始模型前，先建立可重复的实验环境，并把张量、设备和形状当作一等公民。深度学习中许多“模型错误”实际是环境、dtype、device 或 shape 错误。

## 最小环境

建议每个项目独立虚拟环境，固定 Python、PyTorch 与 CUDA 版本，并保存 `requirements.txt` 或锁文件。启动时记录：`torch.__version__`、`torch.cuda.is_available()`、GPU 名称和随机种子。CPU 足够完成前六章的小实验；训练视觉模型时再使用 GPU。

```python
import random, numpy as np, torch
seed = 42
random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
x = torch.randn(2, 3, device=device)  # shape=(batch, feature)
```

## 张量心智模型

Tensor 是带有形状、数据类型和设备信息的多维数组。首先确认三件事：

- `shape`：每个轴代表什么；约定 batch 通常位于第 0 维。
- `dtype`：模型输入一般为 `float32`；类别标签通常为 `long`。
- `device`：参与同一计算的张量与模型必须在同一设备。

常用操作是索引、切片、reshape、broadcast、矩阵乘法和沿指定维度聚合。`reshape` 只在元素数一致时改变视图；`view` 要求内存连续；不确定时优先 `reshape`。对图像，PyTorch 通常用 `(N, C, H, W)`，而非 `(N, H, W, C)`。

## Notebook 使用边界

Notebook 适合探索、画图和逐步验证；正式实验应把数据、模型、训练、评估拆进 `.py` 文件，并将 Notebook 仅作为入口。避免依赖隐藏的运行顺序：Restart 后 Run All 必须仍可运行。

## 排错清单

1. 打印输入、输出、标签的 `shape/dtype/device`。
2. 先用 10 个样本训练到近乎 100% 准确率，验证训练循环。
3. 固定随机种子，保存第一轮 loss 作为基线。
4. 出现 NaN 时依次检查学习率、数据范围、除零、log(0) 和混合精度。

## 最小练习

创建一个 `(4, 3)` 张量，分别完成按行求和、矩阵乘法、移动到 GPU（如可用）和将其 reshape 为 `(2, 6)`；解释每一步的 shape。

`#pytorch #tensor #notebook #deep-learning`
