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
| [从全连接层到卷积](../../DeepLearning/05_卷积神经网络/卷积神经网络基础.md) / [LeNet](../../DeepLearning/05_卷积神经网络/卷积神经网络基础.md) | [04_cnn](./modules/04_cnn/README.md) | 卷积/池化实现、LeNet 基线、特征与错误分析 |

## 推荐学习顺序

1. 先读对应的 `Learning/AI/DeepLearning/` 理论文档。
2. 在模块 `notes.md` 中用自己的话补充理解，不复制教材原文。
3. 按 `reproduce/`、`from_scratch/`、`experiments/` 的顺序实现。
4. 把运行命令、指标、失败原因和结论记录到 `report.md`。
5. 一个模块完成后，再进入下一个模块；不要先铺开后续空模块。

## 当前状态

当前仅 Module 01 进入迭代：它保留完整工作布局，用来承载第一批笔记、代码、实验和报告。Module 02–04 已保留理论范围、实践目标和依赖关系，但只保留模块 README，不预先创建空的 `notes.md`、`reproduce/`、`from_scratch/`、`experiments/` 和 `report.md`。优先级见 [TASKS.md](./TASKS.md)，完成一个模块后再展开下一个。

## 迁移边界

已保留：项目说明、学习规则、D2L 映射、根级模块/报告模板、脚本、Module 01 完整工作区和 Module 02–04 范围卡。

未迁移：Git 历史、`.cursor/` 编辑器规则、`.DS_Store` 操作系统文件。原项目目录 `DeepPathLab` 已不在当前文件系统中；Notes 内的 DeepPathLab 是后续唯一维护入口。
