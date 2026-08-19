# Go 面试题库

这是一份 Go 后端面试题库，专门训练语言语义、Runtime、并发、网络、数据库、性能和系统设计的面试表达。

## 推荐顺序

1. [[00_复习路线与答题模板]]、[[00_主题速答卡]]
2. [[01_语言与Runtime]]：值/指针、slice/map/interface、defer、逃逸、GMP 和 GC。
3. [[02_并发与内存模型]]：Goroutine、Channel、Context、同步、背压、Race 和泄漏。
4. [[03_网络与后端]]：HTTP、数据库、Redis、Kafka、幂等、观测和发布。
5. [[04_编码题与系统设计]]：算法、Worker Pool、限流、任务队列和订单服务。

## 覆盖范围

- 语言与 Runtime：值语义、slice/map/interface、错误、逃逸、GMP、GC 和构建。
- 并发：Goroutine、Channel、Context、同步、内存模型、背压、Race 和泄漏。
- 后端：HTTP/RPC、数据库、Redis、Kafka、幂等、观测、发布和恢复。
- 表达：算法、Worker Pool、限流、任务队列、订单服务和项目深挖。

## 答题边界

- Go 语言语义、编译器/runtime 实现、框架和部署约束要分开说。
- Channel 不是万能共享内存，Goroutine 不是免费资源；每个并发题都要讲生命周期和背压。
