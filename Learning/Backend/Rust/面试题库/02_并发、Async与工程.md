# Rust 并发、Async 与工程

> 递进路径：先讲线程和 Future 的执行模型，再讲 Send/Sync、Pin、取消、背压和服务工程。

## Level 1｜线程、Channel 与 Send/Sync

### 1. Rust 线程和 async task 有什么区别？

答：线程是操作系统调度的执行单元，适合 CPU 并行和阻塞工作；async task 是 Future，由运行时在少量线程上调度，适合大量 I/O 等待。async 不会自动让 CPU 计算并行，长时间不 yield 的任务会阻塞同一 executor 上的其他任务。

### 2. Rust channel 的所有权语义是什么？

答：发送通常把值的所有权转移给接收方，避免双方同时修改同一对象；发送者全部释放后接收端能观察到关闭。无界 channel 可能让生产速度差异变成内存增长，有界 channel 才能形成背压；错误、取消和 receiver 退出都要有明确处理。

### 3. `Send` 和 `Sync` 在 async 代码中为什么经常出现？

答：如果任务可能在线程间被 executor 移动或被 `spawn`，Future 捕获的值通常需要满足相应的 Send 边界；共享引用跨线程则需要 Sync。`Rc`、非线程安全的 RefCell 等值可能导致编译错误，解决应先改变所有权/任务边界，而不是盲目 clone 或加 unsafe。

### 4. `Arc<Mutex<T>>` 的含义和边界是什么？

答：Arc 提供跨线程共享所有权，Mutex 保护内部可变数据；它能让多个任务安全访问同一资源，但不自动避免死锁、饥饿、长临界区和业务状态错误。锁的持有范围要尽量短，不要在同步锁内跨越不可控 `.await`，并明确锁中断/poison 的处理策略。

## Level 2｜Future、Async 和取消

### 5. `async fn` 返回什么？为什么 Future 是惰性的？

答：`async fn` 返回一个实现 Future 的状态机对象；调用函数通常只是构造 Future，必须被 runtime poll 才推进执行。`.await` 在 Future Pending 时让任务交还 executor，状态机会保存继续执行所需的数据。创建很多 Future 不等于已经发出了同样多的 I/O 请求。

### 6. executor、task、Future 和 `.await` 如何协作？

答：executor 负责 poll task，task 持有 Future 和调度状态；Future 返回 Pending 时注册唤醒条件，事件就绪后 executor 再次 poll；返回 Ready 时任务完成。面试时不要把 `.await` 描述成“开线程”，它更像在异步状态机上切换执行权。

### 7. Pin/Unpin 解决什么问题？

答：某些 Future 状态机内部可能包含指向自身字段的引用，移动它会使引用失效；Pin 通过类型约束保证值在需要时不再移动，Unpin 表示类型可以安全移动。Pin 不等于堆分配，也不等于异步本身；回答要结合自引用、poll 接口和实际 API 解释。

### 8. async 任务被 drop 或取消时会发生什么？

答：很多 Future 被 drop 后会停止本地推进，并依赖 RAII 清理资源；但已经提交到外部系统的写操作不能保证被撤销，取消可能发生在任意 `.await` 边界。设计取消安全时要考虑部分写入、锁、channel、临时文件、子进程和远端未知结果。

### 9. `timeout` 能保证操作没有发生吗？

答：不能。timeout 通常只结束当前等待并返回超时，远端请求可能已处理成功；本地 Future 是否被取消也要看库的语义。只读操作可重试，副作用操作应使用幂等键、查询状态、补偿或对账，不能把 timeout 直接等同于失败。

### 10. 为什么不应在 async 任务中直接做阻塞工作？

答：同步文件、进程、CPU 计算或阻塞网络会占住 executor 线程，使其他任务无法被 poll；应使用真正异步库、`spawn_blocking` 或专用线程池。spawn_blocking 也有容量和取消边界，必须限制并发并考虑任务已开始后不能强制终止。

## Level 3｜并发设计与工程化

### 11. 如何实现一个有界异步 Worker Pool？

答：使用有界 channel 发送任务，固定数量 task 消费；每项任务带 deadline 和取消信号，首个关键错误通过共享状态取消兄弟任务，关闭 sender 后等待所有 worker 结束。要处理 receiver 被 drop、任务 panic、生产者过快、超时、部分结果和资源释放。

### 12. 为什么不建议持有锁跨越 `.await`？

答：`.await` 可能长时间 Pending，持锁会让其他任务无法进入临界区；如果另一个任务需要这把锁才能推进当前 Future，还可能形成死锁。通常先在锁内读取/更新必要的小状态，再释放锁后执行 I/O；确有必要时使用异步锁并明确公平性、取消和锁竞争。

### 13. 如何让异步服务具备背压？

答：对入口请求、任务 channel、worker、连接池、spawn_blocking 和下游调用都设置有限容量；满载时选择等待、拒绝、降级或丢弃低优先级任务，并记录队列等待和拒绝指标。无界 channel、无界 `join_all` 和无限重试会把过载延迟转化成内存/成本事故。

### 14. Rust 的并发安全能否替代运行时测试？

答：不能。编译器能证明很多数据竞争和生命周期问题，但不能证明锁顺序、业务状态机、取消时的部分提交、死锁、活锁、资源饥饿和远端一致性。仍需单测、并发压力、超时/取消测试、日志/Trace 和故障注入。

### 15. Cargo、crate、module 和 feature 如何组织？

答：crate 是编译单元，module 组织可见性和命名，workspace 管理多个 crate；Cargo.toml 记录依赖、版本和 feature。公共库应控制暴露 API、错误类型和 feature 组合，应用要锁定依赖和工具链并保证构建可复现；模块边界优先服务所有权和测试边界。

### 16. Serde、配置和日志在 Rust 服务中如何设计？

答：Serde 负责协议/数据映射，边界层先反序列化并校验，再转成领域类型；配置启动时解析、校验和冻结，密钥不进入日志；日志/Trace 记录结构化事件、request/task ID 和错误上下文。序列化格式要定义版本、大小、未知字段、兼容和敏感数据策略。

### 17. unsafe 和 FFI 面试时应该怎么回答？

答：unsafe 不是“关闭所有检查”，而是允许执行者承担额外不变量，如裸指针、外部函数、未验证别名或初始化；安全封装应把 unsafe 缩小到最小块，并在安全 API 边界证明前置条件。FFI 还需处理 ABI、布局、所有权、线程、panic 跨边界和资源释放，不能只说性能更高。

## Level 4｜性能与验证

### 18. Rust 中 clone、借用和零拷贝如何取舍？

答：借用减少复制但增加生命周期和边界约束，clone 简化所有权并可能降低复杂度，零拷贝只有在数据规模/热点足够大时才值得。先用 profile 证明复制是瓶颈，再选择切片、Cow、Arc 或移动；不要为追求零拷贝让 API 难以维护或把数据生命周期绑定到临时缓冲区。

### 19. Rust 服务如何排查性能问题？

答：固定工具链、依赖和工作负载，区分 CPU、分配、锁、I/O、序列化和下游等待；使用 benchmark、采样 profile、allocation/heap、async trace 和请求指标定位。优化后复测吞吐、P95、内存、编译时间和错误率，不能用单一微基准代表线上服务。

### 20. 如何测试 async 代码的异常路径？

答：用可控 channel、barrier、fake clock、测试 server 和注入错误的依赖，覆盖任务正常完成、sender/receiver 关闭、panic、timeout、cancel、下游慢和重复副作用。断言任务已结束、资源已 drop、状态可恢复，避免用随机 sleep 制造“看起来并发”的测试。

### 21. Rust 服务如何优雅退出？

答：停止接收新请求/任务，广播 cancellation，关闭 channel sender，等待 worker 和在途请求在 deadline 内结束，再关闭数据库、HTTP client 和其他资源。外部副作用必须记录状态，超时退出后可由持久化任务和租约恢复；不能靠 runtime 直接 drop 所有 task 就认为业务已安全停止。

### 22. Rust 的 module、可见性和公开 API 如何共同维护不变量？

答：模块组织命名空间，默认私有；`pub(crate)`、`pub(super)` 和 `pub` 逐级扩大可见性。公开类型可以用私有字段和构造函数保证非法状态无法直接创建，测试优先通过公开行为验证，而不是为了方便把内部实现全部 `pub` 出去。

### 23. Cargo workspace、lockfile、feature 和 Edition 如何影响交付？

答：workspace 统一多个 crate 的依赖与构建，lockfile 固定解析结果，feature 控制可选能力，Edition 影响语言和库的兼容规则；CI 应锁定 Rust 工具链并运行 check/test/fmt/clippy。依赖升级、feature 组合和跨平台构建都需要回归，不能只在本机 `cargo run` 通过就认为可发布。

### 24. Rust 的单元测试、集成测试和文档测试分别验证什么？

答：单元测试适合模块内部状态和纯函数，集成测试通过 library crate 的公开 API 验证边界，文档测试验证示例仍可编译运行。测试应覆盖正常、错误、取消、资源释放和协议兼容；断言稳定错误分类和行为，不要把内部字符串或布局当长期合同。

### 25. Serde 的外部 DTO 为什么不应直接等同于领域类型？

答：外部 JSON/配置 schema 可能包含别名、缺省、未知字段和不可信值；先反序列化成 DTO，再做范围/权限/状态校验并转换成领域类型，可以把协议变化和业务不变量隔离。版本字段、未知字段策略、迁移失败和日志脱敏都要明确，序列化成功不代表业务输入合法。

### 26. Tokio 中 `JoinHandle`、`select!` 和取消如何组合？

答：`JoinHandle` 表示任务的观察/等待句柄，保存它并 await 才能知道任务是否完成或 panic；`select!` 可在 I/O、取消和超时之间竞争，但被 drop 的 Future 是否安全取消要逐个确认。关闭时广播取消、停止生产、等待 handles，再释放连接和临时资源，不能丢掉 handle 后假设任务已停止。

### 27. Axum、Hyper 和 Tokio 在一个 Rust Web 服务中如何分层？

答：Tokio 提供 executor、定时器和异步 I/O，Hyper 负责 HTTP 连接/协议基础，Axum 在其上组织路由、提取器、中间件和响应；业务层不应依赖具体 handler 的请求类型。入口要限制请求体/连接/并发，阻塞文件或 CPU 工作放到受控 blocking pool，关闭时停止接收、取消任务、等待句柄并释放连接池。

### 28. Tokio、Libuv 和 io-uring 的选择应该如何回答？

答：先从 workload、平台、生态、可观测性和维护能力出发；Tokio 适合 Rust 生态中的通用异步运行时，Libuv 适合跨语言/跨平台事件循环边界，io-uring 可能在 Linux 高性能 I/O 场景有收益但带来内核、驱动和兼容成本。不要用“更底层所以更快”下结论，必须用同一 workload、版本、内核和失败模型 benchmark/压测。

### 29. Rust Web 服务的 take-home 作业如何体现工程能力？

答：README 要写清运行、测试、架构决策、已知不足和若有更多时间的改进；代码要有 DTO/领域/存储边界、错误合同、输入限制和端点测试。评审时说明哪些地方选择简单内存实现、哪些地方预留持久化/并发扩展，以及如何用测试和指标证明，而不是堆砌框架。

## 验证边界

- Future、Pin、Send/Sync 和 Tokio 行为必须用锁定的 Rust Edition、Tokio 版本和最小可运行实验验证。
