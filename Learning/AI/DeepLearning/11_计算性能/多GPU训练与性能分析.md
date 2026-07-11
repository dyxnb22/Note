# 多 GPU 训练与性能分析

数据并行让每张 GPU 持有模型副本、处理不同 batch，再同步梯度；PyTorch 优先使用 DistributedDataParallel。有效 batch size 变大后通常需重新调学习率和 warmup，不能假设单卡配置直接可用。

性能分析先区分数据加载、前向、反向、优化器、通信和显存限制。吞吐量以 samples/s 或 tokens/s 衡量，不能只看单 step 时间。多卡加速低于线性是常态，原因包括通信、负载不均和小 batch。

`#ddp #multi-gpu #profiling`
