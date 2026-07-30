# Go

本目录面向后端工程，重点是组合、显式错误、并发生命周期、HTTP、数据库和性能验证。

- [00_Go基础语法与惯用法](./00_Go基础语法与惯用法.md)：从其他语言迁移到 Go 的正式入口，覆盖语法、数据语义、接口、错误、Module 与惯用法。
- [Go 后端工程基础](./Go后端工程基础.md)：从语言语义到并发、Context、服务、事务、测试和性能的完整主线。
- [01_Go语言与Runtime](./01_Go语言与Runtime.md)：对象语义、接口、逃逸、调度器和 GC。
- [02_Go并发与内存模型](./02_Go并发与内存模型.md)：Goroutine 生命周期、Channel、Context、同步与 Race。
- [03_Go网络服务工程](./03_Go网络服务工程.md)：HTTP/gRPC、客户端、数据库、观测与优雅退出。
- [04_Go测试与性能诊断](./04_Go测试与性能诊断.md)：单元/集成/Fuzz、Benchmark、pprof 和生产诊断。
- [05_Go后端项目实战](./05_Go后端项目实战.md)：订单服务的持久化、可靠性、观测、性能与交付闭环。
- [Go 实践](./实践/README.md)：实践维护规则与项目入口；当前从 [go-backend-service](./实践/go-backend-service/README.md) 阶段 0 基线开始。

`Go后端工程基础.md` 保留为快速总览；专项文档负责可独立学习、实验和验收的深度内容。

## 正式学习顺序

```text
00 基础与惯用法
→ 工程基础总览
→ 01 Runtime
→ 02 并发与内存模型
→ 03 网络服务
→ 04 测试与性能
→ 05 项目实战
```

希望同时推进 Rust Agent 时，使用 [Rust Agent 与 Go 后端学习地图](../../00_Navigation/Rust-Agent与Go后端学习地图.md)，不要并行维护重复的可靠性和交付理论。

`#go #backend #index`
