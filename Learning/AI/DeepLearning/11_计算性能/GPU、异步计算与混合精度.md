# GPU、异步计算与混合精度

GPU 擅长大规模并行张量运算，但 CPU 向 GPU 传输、频繁小算子和同步读取会成为瓶颈。CUDA 操作通常异步提交；测时前需要同步，否则只测到提交开销。

混合精度以 FP16/BF16 执行多数矩阵运算，必要处保留 FP32。FP16 范围较小，常需 loss scaling；BF16 范围更接近 FP32，现代硬件上更稳。使用 `torch.autocast` 和 GradScaler，先验证数值一致性再追求速度。

`#gpu #mixed-precision #performance`
