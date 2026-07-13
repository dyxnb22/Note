# 并发安全与 Async 基础

## 1. 线程与任务

线程是操作系统调度的执行单元，适合 CPU 并行和阻塞工作；async task 是由运行时调度的 Future，适合大量 I/O 等待。

async 不会让 CPU 计算自动并行。一个长时间不让出执行权的 CPU 循环会阻塞同一执行器上的其他任务。

## 2. `Send` 与 `Sync`

- `Send`：值可以安全地移动到另一个线程。
- `Sync`：对值的共享引用可以安全地在线程间共享；等价于 `&T: Send`。

`Rc<T>` 通常不是 `Send`/`Sync`；`Arc<T>` 只有在内部 `T` 也满足相应条件时才安全。编译器会检查这些 trait，但不会理解你的业务锁顺序。

## 3. 创建线程

```rust
use std::thread;

let handle = thread::spawn(|| {
    2 + 2
});

let result = handle.join().expect("worker panicked");
```

`move` 闭包把捕获值的所有权转移给线程。`join` 等待线程结束并获取返回值；不 `join` 可能导致主线程提前结束或忽略 panic。

## 4. Channel

channel 适合把所有权从一个执行单元转移给另一个：

```rust
let (sender, receiver) = std::sync::mpsc::channel();
sender.send(String::from("job")).unwrap();
let job = receiver.recv().unwrap();
```

发送者全部被释放后，接收端会看到关闭。channel 也可以作为背压边界：有界 channel 能限制内存增长，无界 channel 可能把生产速度差异变成内存问题。

## 5. Future 与 async

`async fn` 返回一个 Future。调用 async 函数不会立即执行函数体；Future 必须被 runtime poll 才会推进：

```rust
async fn fetch_value() -> Result<String, Error> {
    // 到达 .await 时可能让出执行权
    Ok(String::from("value"))
}
```

`.await` 等待一个 Future，并可能把当前任务交还给运行时。Future 通常是惰性的，不能把创建 Future 等同于完成工作。

## 6. 阻塞与非阻塞

不要在 async worker 上直接执行长时间阻塞的文件、进程或 CPU 操作。可以：

- 使用真正的异步库。
- 使用 `spawn_blocking` 把阻塞工作放到专门线程池。
- 使用同步 runtime 或专用线程。

`spawn_blocking` 也不是无限资源；应限制并发，并关注任务取消和线程池饱和。

## 7. 取消与超时

Future 被 drop 时，很多 async 操作会被取消，但取消不一定能撤销已经提交到外部系统的副作用。资源清理应依赖 RAII 和明确的状态设计。

超时应包住实际操作，并区分“等待超时”和“操作已经在外部完成但响应丢失”：

```rust
let result = tokio::time::timeout(Duration::from_secs(2), operation()).await;
```

取消安全要求：部分写入、锁、channel、临时文件和子进程在中断时仍处于可解释状态。

## 8. 共享状态与锁顺序

尽量减少共享可变状态。必须加锁时：

- 固定锁顺序，避免死锁。
- 缩小临界区。
- 不持锁跨越 `.await`，除非明确知道异步锁的语义和必要性。
- 统计锁竞争、等待时间和队列长度。

## 9. 并发测试

并发 bug 可能不稳定出现。测试应包含：关闭 channel、任务 panic、超时、取消、生产者过快、消费者退出和共享状态边界。不要只依赖 `sleep` 让竞态“碰巧发生”，使用 barrier、channel 和确定性时序控制。

## 练习

实现一个有界并发 worker pool：接收任务、限制并行数、传播第一个错误、等待剩余任务安全结束，并分别测试正常关闭、消费者失败、超时和取消。

`#rust #concurrency #send-sync #future #async #cancellation`
