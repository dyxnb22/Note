# 测试、 Benchmark 与 Profiling

表驱动测试适合覆盖输入—输出矩阵；使用 `t.Run` 命名子用例。测试应隔离时间、随机数、网络和数据库等副作用，必要时通过小接口注入 fake。并发代码要跑 race detector。

Benchmark 使用 `go test -bench`，避免将设置成本计入循环；用 `benchstat` 比较多次结果。CPU/heap profile 用 pprof 找热点，先测量再优化，优化后重测防止幻觉。

`#go #testing #benchmark #pprof`
