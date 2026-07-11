# 并发安全与 Async 基础

`Send` 表示值可在线程间移动，`Sync` 表示共享引用可跨线程使用；编译器会阻止不安全组合。线程适合 CPU 并行，async 适合大量 I/O 等待；async 不会让 CPU 计算自动并行。

`async fn` 返回 Future，只有被 runtime poll 才执行。不要在 async runtime worker 上执行阻塞 I/O 或长 CPU 计算；使用异步库、`spawn_blocking` 或专用线程池。取消通常发生在 Future 被 drop 时，资源操作应能安全中断。

`#rust #send-sync #async #concurrency`
