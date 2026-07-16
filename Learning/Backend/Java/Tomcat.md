# Tomcat

Tomcat 是 Java Servlet/JSP 容器，负责接收 HTTP 请求、定位 Web 应用并调用 Servlet。Spring Boot 常以内嵌 Tomcat 运行，但核心的连接器、线程池和请求链路仍适用。

## Tomcat 的核心层次是什么？

`Connector → Service → Engine → Host → Context → Wrapper/Servlet`。

- Connector 监听端口、解析协议并接收请求。
- Engine 根据虚拟主机分发，Host 表示一个域名，Context 表示一个 Web 应用。
- Context 根据 URL 映射到具体 Servlet，构造 request/response 并调用 `service`。

## BIO、NIO、NIO2 有什么区别？

- BIO：连接和线程绑定，模型简单，但连接数大时线程和阻塞成本高。
- NIO：基于 Selector 的多路复用，少量线程处理大量连接，Tomcat 常用。
- NIO2/AIO：由操作系统完成异步 I/O 后通知应用，实际收益取决于平台和工作负载。

## Tomcat 线程和连接参数怎么理解？

- `maxThreads`：处理请求的工作线程上限。
- `acceptCount`：工作线程满后，连接进入等待队列的上限，超过后可能拒绝连接。
- `connectionTimeout`：连接等待超时。

调优不能只增大 `maxThreads`：线程过多会导致上下文切换、内存和下游连接池耗尽。应结合 CPU、请求耗时、队列长度、数据库连接池和压测结果设置。

## Servlet 生命周期是什么？

容器加载并实例化 Servlet 后调用 `init`，每次请求调用 `service`（再分发到 `doGet`/`doPost`），应用卸载时调用 `destroy`。`load-on-startup` 可让 Servlet 在启动阶段初始化，否则可能在第一次请求时初始化。

## Tomcat 集群如何处理 Session？

常见方案是集中式 Session（Redis 等）、无状态 Token，或容器 Session 复制/粘性会话。Session 复制会带来网络和一致性成本；能无状态化时优先无状态，必须保留 Session 时使用集中存储并设置过期与故障策略。
