# DeepPathLab 与 Notes 的对应关系

## 项目定位

DeepPathLab 是一个项目制的深度学习实践仓库。每个模块都遵循：

`读理论 → 写自己的笔记 → 复现基线 → 从零实现 → 做实验 → 写报告`

它与 `Learning/AI/DeepLearning/` 的关系是：理论章节负责建立概念和训练直觉，DeepPathLab 负责把概念沉淀成可运行、可检查、可复盘的项目。

## 模块映射

| 理论章节 | DeepPathLab 实践模块 | 主要产出 |
|---|---|---|
| [微积分、自动微分与反向传播](../../DeepLearning/01_预备知识/微积分、自动微分与反向传播.md) | [01_preliminaries_autograd](./modules/01_preliminaries_autograd/README.md) | 最小自动微分引擎、梯度检查、实现报告 |
| [线性回归](../../DeepLearning/02_线性神经网络/线性回归：从零实现与简洁实现.md) / [Softmax 回归](../../DeepLearning/02_线性神经网络/Softmax回归与图像分类.md) | [02_linear_models](./modules/02_linear_models/README.md) | 线性回归、softmax 分类、基线对比、优化实验 |
| [多层感知机与激活函数](../../DeepLearning/03_多层感知机/多层感知机与激活函数.md) | [03_mlp](./modules/03_mlp/README.md) | MLP 训练器、激活函数/优化器对比、训练诊断 |
| [从全连接层到卷积](../../DeepLearning/05_卷积神经网络/从全连接层到卷积.md) / [LeNet](../../DeepLearning/05_卷积神经网络/LeNet与图像分类训练.md) | [04_cnn](./modules/04_cnn/README.md) | 卷积/池化实现、LeNet 基线、特征与错误分析 |

## 推荐学习顺序

1. 先读对应的 `Learning/AI/DeepLearning/` 理论文档。
2. 在模块 `notes.md` 中用自己的话补充理解，不复制教材原文。
3. 按 `reproduce/`、`from_scratch/`、`experiments/` 的顺序实现。
4. 把运行命令、指标、失败原因和结论记录到 `report.md`。
5. 一个模块完成后，再进入下一个模块；不要先铺开后续空模块。

## 当前状态

当前迁移的是项目原始骨架：四个模块的目录、任务队列、D2L 映射和报告模板已经就位，但实现代码、实验结果和报告结论尚未完成。优先级见 [TASKS.md](./TASKS.md)，应先完成 Module 01，再推进 Module 02–04。

## 迁移边界

已保留：项目说明、学习规则、D2L 映射、模块模板、脚本和四个模块目录。

未迁移：Git 历史、`.cursor/` 编辑器规则、`.DS_Store` 操作系统文件。原项目目录 `/Users/diaoyuxuan/DeepPathLab` 暂时保留，便于迁移后核对。
