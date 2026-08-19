# Go

本目录现在保留 Go 的面试入口和实践入口。语言、Runtime、并发、网络、数据库、测试、性能与项目实战知识已经合并进 [Go 面试题库](./面试题库/README.md)。

## 进入方式

- 面试与系统化复习：先读 [Go 面试题库](./面试题库/README.md)。
- 可运行项目：进入 [Go 实践](./实践/README.md) 和 [go-backend-service](./实践/go-backend-service/README.md)。

## Go 题库覆盖

- 语言与 Runtime：值语义、slice/map/interface、错误、逃逸、GMP、GC 和构建。
- 并发与内存模型：Goroutine、Channel、Context、同步、背压、Race 和泄漏。
- 网络与后端：HTTP/RPC、数据库、Redis、Kafka、幂等、观测、发布和恢复。
- 编码与系统设计：算法、Worker Pool、限流、任务队列、订单服务和项目深挖。

实践目录下的项目和测试保持独立，不作为题库页面处理。

## 实践验收

题库负责可迁移的知识和问答；实践目录负责可运行证据。建议按以下顺序把题库内容落到实验中：

- 用小程序验证 slice 扩容共享、interface 携带 nil 指针、逃逸分析和方法集。
- 用 `go test`、Race Detector、Benchmark、pprof 和 trace 验证 Worker Pool、取消、背压、泄漏与性能结论。
- 用 [go-backend-service](./实践/go-backend-service/README.md) 验证 HTTP、领域服务、存储替换、测试和优雅关闭；项目代码、测试和配置不与题库混写。
- 复习时对每个结论补一句“如何实验或观测”，避免把 Runtime 微基准当成生产性能证明。
