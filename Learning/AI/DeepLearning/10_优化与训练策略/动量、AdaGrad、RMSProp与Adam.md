# 动量、AdaGrad、RMSProp 与 Adam

动量累计梯度的指数滑动平均，减少狭长峡谷中的来回震荡。AdaGrad 为频繁出现的参数降低有效学习率，但长期可能衰减过度；RMSProp 用窗口平均缓解该问题；Adam 结合一阶动量和二阶尺度校正，是常用默认起点。

优化器不是魔法。Adam 仍要调学习率和 weight decay；AdamW 将权重衰减与自适应更新解耦，实践中常更符合正则化意图。比较优化器时固定模型、数据、训练预算和学习率搜索范围。

`#momentum #adam #optimizer`
