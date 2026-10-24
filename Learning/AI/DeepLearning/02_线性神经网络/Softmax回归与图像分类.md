# Softmax 回归与图像分类

多分类模型先为每个类别计算一个分数，称为 logit。线性模型输出 `z = XW + b`；分数本身不必为正，也不必相加为 1。Softmax 再把同一样本的分数转换为概率：`pᵢ = exp(zᵢ) / Σ exp(zⱼ)`。

## 类别之间比较的是相对分数

给所有 logits 加上相同常数，分子和分母会同时乘上同一因子，所以概率保持不变。利用这一性质，计算前减去最大 logit，就能避免直接计算 `exp(1000)` 这样的溢出值。

例如 logits 为 `[1000, 1001]`，减去最大值后为 `[-1, 0]`，第二类概率约为 0.7311。若真实标签是第二类，交叉熵为 `-log(p₁)`，约 0.3133：模型给正确类别的概率越小，这项损失越大。

```python
from math import exp, log, isclose

logits = [1000.0, 1001.0]
target = 1
maximum = max(logits)
shifted = [value - maximum for value in logits]
denominator = sum(exp(value) for value in shifted)
probabilities = [exp(value) / denominator for value in shifted]
cross_entropy = log(denominator) - shifted[target]

assert isclose(sum(probabilities), 1.0)
assert isclose(probabilities[1], 0.7310585786300049)
assert isclose(cross_entropy, 0.31326168751822286)
```

损失直接使用平移后的 log-sum-exp 计算，避免先得到一个可能下溢到 0 的概率，再对它取对数。

## 标签决定损失怎样解释目标

对 N 个样本、C 个类别，模型输出通常为 `(N, C)`。常见标签是 `(N,)` 的类别索引，在 PyTorch 中使用整数类型 `torch.long`；每个样本只指定一个正确类别。

概率标签则用与输出相同的 `(N, C)` 形状和浮点类型，表示一个目标分布；one-hot 是它的特殊情况，混合标签也可以使用这种形式。概率目标需要满足非负、每行和为 1 等约束。`CrossEntropyLoss` 支持这两种目标形式，不能把 one-hot 一概视为非法输入。[PyTorch 2.9 CrossEntropyLoss](https://docs.pytorch.org/docs/2.9/generated/torch.nn.CrossEntropyLoss.html)

框架损失接收原始 logits，并在内部完成相应的稳定计算。如果先做 softmax，再把概率当成 logits 输入，就改变了原先的目标函数。

## 图像分类连接表示与评估

图像先转换成数值张量，再按批次进入模型。使用全连接线性分类器时，还要把通道、高度和宽度整理成特征维；每层形状要与标签中的样本数一致。

预测类别可以取 `argmax(logits)`，因为 softmax 保留大小顺序。准确率观察最终类别，交叉熵还区分预测有多确信：同样预测正确，0.51 和 0.99 的概率会产生不同损失。类别比例、错误分布和置信度因此需要一起分析，不能只依赖一个总准确率。
