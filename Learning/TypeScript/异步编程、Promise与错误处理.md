# 异步编程、Promise 与错误处理

`async/await` 是 Promise 语法糖；任何 await 都可能 reject，因此边界处要捕获、分类和映射错误。并行独立任务用 `Promise.all`，但任一失败会整体 reject；需要汇总结果时用 `Promise.allSettled`。

超时和取消不是 Promise 内建语义，使用 `AbortController` 并让底层 fetch/库支持 signal。避免吞掉 catch；错误要附加操作上下文，向客户端返回安全的稳定码。

`#typescript #async #promise #error-handling`
