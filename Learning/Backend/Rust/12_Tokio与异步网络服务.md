# Tokio 与异步网络服务

## 1. Tokio 的组成

Tokio 主要提供：

- runtime：调度 async task。
- 异步 I/O：TCP、UDP、文件等能力的生态接口。
- task：轻量级并发任务。
- channel：任务间通信。
- time：sleep、interval、timeout。

只在确实需要异步 I/O 或大量并发等待时引入 runtime。异步代码不会自动解决线程安全、取消、背压或权限问题。

## 2. 启动 runtime

```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    run_server().await
}
```

宏会生成 runtime 和同步 `main`。需要精确控制线程数、关闭方式或嵌入已有 runtime 时，使用 `tokio::runtime::Builder` 手动构建。

## 3. 任务与所有权

```rust
let handle = tokio::spawn(async move {
    fetch().await
});

let result = handle.await??;
```

`spawn` 通常要求 Future 是 `Send + 'static`，因为任务可能在线程间调度并脱离当前栈帧。`move` 把捕获值带入任务。保存 `JoinHandle` 便于等待、取消和观察 panic；丢弃 handle 通常只是不再等待，不等于任务停止。

## 4. 异步 TCP

```rust
let listener = tokio::net::TcpListener::bind("127.0.0.1:8080").await?;
loop {
    let (stream, peer) = listener.accept().await?;
    tokio::spawn(async move {
        if let Err(error) = handle_connection(stream).await {
            tracing::warn!(%peer, %error, "connection failed");
        }
    });
}
```

生产服务还需要连接数上限、请求体上限、读写超时、优雅关闭和错误分类。每个连接创建任务意味着潜在资源消耗，不能无上限接受外部连接。

## 5. timeout、select 与取消

```rust
tokio::select! {
    result = operation() => handle_result(result),
    _ = tokio::time::sleep(Duration::from_secs(5)) => handle_timeout(),
    _ = shutdown.recv() => handle_shutdown(),
}
```

`select!` 中未完成分支通常会被 drop。被取消的 Future 必须能安全释放资源；如果外部副作用已经发送，取消本地 Future 不代表远端撤销。

超时应分层：连接建立、读取首字节、完整响应、数据库查询和整体请求可能需要不同预算。

## 6. channel 与背压

有界 channel：

```rust
let (tx, mut rx) = tokio::sync::mpsc::channel(100);
tx.send(job).await?;
```

当队列满时，发送者等待，这就是背压。无界 channel 要求你能证明消息量有上限，否则慢消费者会导致内存增长。关闭 channel 时要定义生产者退出、消费者 drain 和未处理任务的语义。

## 7. 同步锁与异步锁

`std::sync::Mutex` 在短临界区且不会跨 `.await` 时可以使用；跨 await 需要考虑异步锁或改用消息传递。异步锁不能消除死锁，锁顺序和临界区仍要设计。

绝不要持锁等待一个需要同一把锁的任务，也不要持锁执行数据库、网络和文件 I/O。

## 8. Web handler 的边界

基于 Axum、Actix 等框架时，handler 应负责：

1. 提取路径、查询、headers 和 body。
2. 校验输入并转换为内部类型。
3. 调用业务服务。
4. 把结果映射为 HTTP 状态和响应体。

复杂领域逻辑、数据库事务和外部调用编排应放在服务层；框架类型不应扩散到所有核心模块。

## 9. 优雅关闭

关闭流程通常是：停止接受新连接 → 通知任务 → 等待有限时间 → 取消剩余任务 → 关闭连接池和资源。每一步都应有超时，不能无限等待一个失控任务。

## 10. 观测与测试

使用 `tracing` span 关联请求、任务和外部调用，记录耗时、取消和错误。测试应覆盖：超时、取消、客户端断开、服务关闭、背压、连接数上限和响应体超限。

## 练习

实现一个有界并发的异步 TCP 服务：限制连接数，给每个请求设置超时，支持 shutdown channel，记录 request ID，并测试客户端提前断开和服务优雅退出。

`#rust #tokio #async #tcp #web-service #backpressure`
