# Go 后端工程基础

Go 的优势来自简单的组合模型、显式错误、低成本并发和成熟标准库。工程质量不取决于使用多少技巧，而取决于边界是否清楚：谁拥有资源、谁负责取消、错误在哪里增加语义、事务和 goroutine 在哪里结束。

## 1. 语言与数据语义

Go 用 package 组织代码，优先写短函数、零值可用的 struct 和清晰的数据流。日常最低检查是 `gofmt`、`go vet` 和 `go test`。

几个容易出错的语义：

- slice 是指针、长度和容量的描述符；`append` 可能换底层数组，因此要使用返回值。
- map 是引用式数据结构，不保证并发安全；并发访问需要同步或所有权隔离。
- struct 赋值默认复制值；包含 slice、map、pointer 时仍可能共享底层数据。
- pointer 用于表达共享可变状态、大对象或可选性，不应为了“性能”到处使用。
- 零值应尽量可用；构造函数主要负责强制不变量和依赖。

## 2. 接口、组合与错误

Go 通过 struct 嵌入、函数组合和接口满足实现复用。接口应由消费者定义，并保持最小：只需要 `Read` 就不要依赖一个完整客户端。

```go
type UserStore interface {
	FindByID(ctx context.Context, id string) (User, error)
}

type UserService struct {
	store UserStore
}
```

错误是返回值。使用 `%w` 保留错误链，用 `errors.Is` 和 `errors.As` 判断语义；不要比较错误字符串。只有调用方能够增加上下文、转换协议错误或执行恢复时才处理错误，否则继续返回。

```go
user, err := s.store.FindByID(ctx, id)
if err != nil {
	return User{}, fmt.Errorf("find user %q: %w", id, err)
}
```

普通业务失败不应使用 panic。进程入口或 goroutine 边界可以 recover 并记录，但 recover 不是忽略程序错误的手段。

## 3. Goroutine、Channel 与同步

goroutine 很轻，但并非免费。启动前必须回答：

1. 谁等待它结束？
2. 如何取消？
3. 错误传到哪里？
4. 最大并发是多少？

channel 适合传递所有权和协调阶段，mutex 适合保护共享状态。不要把 channel 当成所有并发问题的默认答案。

```go
func worker(ctx context.Context, jobs <-chan Job, results chan<- Result) error {
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case job, ok := <-jobs:
			if !ok {
				return nil
			}
			result, err := run(ctx, job)
			if err != nil {
				return err
			}
			select {
			case results <- result:
			case <-ctx.Done():
				return ctx.Err()
			}
		}
	}
}
```

常见模式包括 worker pool、fan-out/fan-in 和 pipeline。通常由发送方关闭 channel；接收方通过 `value, ok := <-ch` 判断结束。并发代码应运行 `go test -race ./...`。

## 4. Context、超时与取消

`context.Context` 承载请求范围的 deadline、取消信号和少量跨边界元数据。HTTP 入口的 context 应沿调用链传递：

- 不把 context 存入长期 struct；
- 不用 context 代替业务参数；
- 下游使用 `QueryContext`、`BeginTx`、`NewRequestWithContext` 等可取消 API；
- 创建 `WithTimeout` 或 `WithCancel` 后及时 `defer cancel()`。

单次调用超时、整个请求预算和重试预算是不同概念。超时不自动意味着可以重试；先确认错误是否瞬时、操作是否幂等，以及总预算是否仍有余量。

## 5. Modules 与项目组织

`go.mod` 定义模块路径和依赖，使用 `go mod tidy` 清理不再使用的依赖。业务公共接口尽量不暴露第三方库类型，否则依赖升级会扩散到调用者。

常见布局：

```text
cmd/api/             可执行入口与组装
internal/domain/     领域类型和规则
internal/service/    用例编排
internal/repository/ 存储接口与实现
internal/transport/  HTTP/RPC 适配
```

`pkg/` 只用于确实要被其他模块导入的公共库。依赖方向从 transport 到 service，再到由内层定义的 repository 接口；领域逻辑不依赖 HTTP 或数据库实现。

## 6. HTTP 服务

Handler 负责解析、认证、调用 service 和映射响应。业务规则放在 service/domain；日志、request ID、认证、恢复和限流适合中间件，但顺序会改变语义。

服务端至少设置 header/read/write/idle timeout，限制请求体大小，并使用稳定错误码。内部堆栈和敏感字段只进入受控日志，不直接返回客户端。

```go
server := &http.Server{
	Addr:              ":8080",
	Handler:           handler,
	ReadHeaderTimeout: 5 * time.Second,
	ReadTimeout:       15 * time.Second,
	WriteTimeout:      30 * time.Second,
	IdleTimeout:       60 * time.Second,
}
```

优雅关闭要先停止接收新连接，再在有限时间内等待在途请求；后台 worker 和数据库连接也要进入同一生命周期。

## 7. 数据库与事务

`database/sql.DB` 是连接池管理器，应在进程内复用，并设置最大连接、空闲连接和连接生命周期。所有 SQL 使用参数化查询。

事务应覆盖一个业务不变量，而不是笼统包住“所有操作”：

```go
func transfer(ctx context.Context, db *sql.DB, from, to string, amount int64) (err error) {
	tx, err := db.BeginTx(ctx, nil)
	if err != nil {
		return fmt.Errorf("begin transfer: %w", err)
	}
	defer func() {
		if err != nil {
			_ = tx.Rollback()
		}
	}()

	// 省略使用 tx 执行、检查余额和更新两个账户的参数化 SQL。
	if err = tx.Commit(); err != nil {
		return fmt.Errorf("commit transfer: %w", err)
	}
	return nil
}
```

外部 HTTP、消息发送和慢 I/O 不应放进长事务。读取 rows 后及时关闭并检查 `rows.Err()`。数据库事务无法原子覆盖外部系统，跨边界一致性应使用 outbox、幂等和补偿。

## 8. 测试、Benchmark 与 Profiling

表驱动测试适合输入—输出矩阵，使用 `t.Run` 标识子用例。时间、随机数、网络和数据库等副作用通过小接口或显式依赖隔离；不要为了测试制造庞大接口。

推荐检查：

```bash
gofmt -w .
go vet ./...
go test ./...
go test -race ./...
go test -bench=. -benchmem ./...
```

Benchmark 不把设置成本计入循环，用 `benchstat` 比较多次结果。CPU、heap、block 和 mutex profile 用于定位不同瓶颈；优化前后都要在相同负载下测量。

## 9. 内存与性能

逃逸表示值的生命周期或引用方式使其需要分配到堆，可用 `go build -gcflags=-m` 辅助理解。但性能优化顺序应是：指标与 profile → 找热点 → 最小改动 → benchmark 验证。

常见有效手段包括减少无意义分配和字符串转换、为已知规模的 slice 预分配容量、避免复制大对象。`sync.Pool` 只适合短生命周期、可安全重置且确有分配热点的对象，不能作为通用缓存。

## 验收清单

- 所有 goroutine 都有结束、取消和错误传播路径。
- 网络和数据库调用接受 context，并有明确超时。
- 错误保留因果链，不靠字符串判断。
- Handler、业务规则和存储职责分开。
- 事务不包含不可控外部调用。
- race、测试和静态检查通过；性能结论由 benchmark/profile 支持。

`#go #backend #concurrency #context #http #database #testing`
