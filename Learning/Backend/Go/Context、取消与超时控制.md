# Context、取消与超时控制

`context.Context` 承载请求范围内的 deadline、取消信号与少量元数据。HTTP 入口传入的 context 应沿调用链向下传递；不要把它存进 struct，也不要用它代替可选业务参数。

下游 I/O 必须调用支持 context 的 API，例如 `QueryContext`、`NewRequestWithContext`。创建 `WithTimeout` 后总是 `defer cancel()` 释放计时器。超时不是重试理由；重试前判断操作是否幂等，并设置总预算。

`#go #context #timeout #cancellation`
