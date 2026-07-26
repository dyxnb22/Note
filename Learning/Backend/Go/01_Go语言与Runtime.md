# Go 语言与 Runtime

本篇深化 Go 的数据语义、接口、内存、调度器和 GC；工程总览见[Go 后端工程基础](Go后端工程基础.md)。

## 值、指针与方法集

Go 默认按值传递。Slice、Map、Channel 等值内部包含指向运行时结构的引用，但把它们传参仍是复制描述符。

- Array 长度属于类型。
- Slice 包含指针、长度和容量。
- Map 和 Channel 必须用 `make` 初始化后写入。
- Interface 值包含动态类型和值；“接口不为 nil、内部指针为 nil”是常见陷阱。

指针接收者和值接收者会影响方法集、复制和接口满足关系。选择应围绕语义一致性，而不是机械追求性能。

## Slice 与 Map

Slice 扩容可能分配新底层数组，因此不同切片是否共享数据取决于容量和追加过程。跨 API 返回 Slice 时要明确所有权，必要时复制。

Map 遍历顺序不保证稳定；普通 Map 不能在无同步情况下并发读写。结构体作为 Map Value 时无法直接修改其中字段，通常重新赋值或使用指针。

## Interface 与泛型

小接口由使用方定义，表达最小能力。不要为每个实现预先创建大接口。

泛型适合算法和容器复用；业务多态仍常由接口表达。约束应尽量精确，避免为了消除少量重复制造难理解的类型参数链。

## Defer、Panic 与 Recover

`defer` 在函数返回前按后进先出执行，适合释放资源。循环中累积大量 defer 可能延迟释放。

Panic 适合不可恢复的程序不变量或初始化错误，不适合普通业务分支。Recover 只在同一 Goroutine 的延迟函数中生效；恢复后仍要记录上下文并确认状态是否可继续使用。

## 逃逸与分配

编译器根据引用生命周期决定值在栈还是堆上。返回局部变量指针在 Go 中是安全的，但可能导致逃逸。

使用逃逸分析和 Benchmark 验证：

```text
go build -gcflags=-m ./...
go test -bench=. -benchmem ./...
```

减少逃逸不应牺牲清晰性；先定位高频分配热点。

## 调度器

Go Runtime 用 G、M、P 模型调度 Goroutine：

- G：Goroutine。
- M：操作系统线程。
- P：执行 Go 代码所需的调度资源。

阻塞系统调用、网络轮询、抢占和 Work Stealing 共同影响调度。Goroutine 很轻，但不是免费资源；无界创建仍会耗尽内存、连接和下游容量。

## GC

Go 使用并发垃圾回收，目标是在吞吐、CPU 和暂停之间平衡。分配速率过高会增加 GC 压力。

观察 Heap、Allocation Rate、GC CPU、Pause 和对象保留。`sync.Pool` 中对象随时可能被回收，不能存放业务状态或必须命中的缓存。

## 构建与二进制

理解：

- Module、Package 和 Internal。
- Build Tag 与目标平台。
- 静态/动态链接边界。
- `go:embed` 对制品大小和更新流程的影响。
- 版本信息和可复现构建。

## 最小实验

1. 验证 Slice 扩容前后的共享关系。
2. 复现 Interface 包含 nil 指针的判断。
3. 比较值接收者与指针接收者的方法集。
4. 使用逃逸分析和 Heap Profile 定位一次分配。
5. 调整分配方式并用 Benchmark 复测。

## 验收清单

- 能解释 Slice、Map、Interface 的运行时语义。
- 能用接口和泛型表达清晰边界。
- 能解释 G/M/P、逃逸和 GC 的基本作用。
- Runtime 性能结论有 Profile 和 Benchmark 支持。

## 来源与验证边界

语言语义以 Go Specification 为准，Runtime、GC 和编译器细节参考 Go 官方文档与源码说明。实现细节可能随版本变化，性能结论必须在项目锁定版本验证。

`#go #runtime #gc #interface #memory`
