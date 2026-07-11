# Tokio 与异步网络服务

Tokio 提供 runtime、任务调度、异步 I/O、channel 和 time。基于 Axum/Actix 等框架的 handler 应传递 state、解析输入、调用服务、映射错误；避免在 handler 中写复杂领域逻辑。

所有外部调用设 timeout，并将 cancellation 传下去。连接池、并发限制、背压、优雅关闭是生产服务的基本组成。观测使用结构化日志和 tracing span，不能只在错误处 print。

`#rust #tokio #async #http-service`
