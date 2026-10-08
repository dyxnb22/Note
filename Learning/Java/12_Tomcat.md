Tomcat 是 Java Servlet/JSP 容器，负责接收 HTTP 请求、定位 Web 应用并调用 Servlet。Spring Boot 常以内嵌 Tomcat 运行，但核心的连接器、线程池和请求链路仍适用。

# Tomcat 的核心层次是什么？

`Connector → Service → Engine → Host → Context → Wrapper/Servlet`。

- Connector 监听端口、解析协议并接收请求。
- Engine 根据虚拟主机分发，Host 表示一个域名，Context 表示一个 Web 应用。
- Context 根据 URL 映射到具体 Servlet，构造 request/response 并调用 `service`。

# BIO、NIO、NIO2 有什么区别？

三种模型的完整对比（同步/异步、阻塞/非阻塞、Selector 的角色）见 [IO 与网络编程](02_IO与网络编程.md)。Tomcat 侧的差异点：模型由连接器实现——8.5 起 BIO 连接器移除，默认 NIO 连接器，poller 线程多路复用事件、工作线程池处理请求；NIO2 连接器提供异步模式，实际收益取决于平台和工作负载，通常不构成选型理由。连接器的实际容量上限落在下一题的线程与队列参数上。

# Tomcat 线程和连接参数怎么理解？

- `maxThreads`：处理请求的工作线程上限。
- `acceptCount`：工作线程满后，连接进入等待队列的上限，超过后可能拒绝连接。
- `connectionTimeout`：连接等待超时。

调优不能只增大 `maxThreads`：线程过多会导致上下文切换、内存和下游连接池耗尽。应结合 CPU、请求耗时、队列长度、数据库连接池和压测结果设置。

# Servlet 生命周期是什么？

容器加载并实例化 Servlet 后调用 `init`，每次请求调用 `service`（再分发到 `doGet`/`doPost`），应用卸载时调用 `destroy`。`load-on-startup` 可让 Servlet 在启动阶段初始化，否则可能在第一次请求时初始化。

# Tomcat 的类加载器有什么特点？

Tomcat 通常为每个 Web 应用创建独立的 `WebappClassLoader`：

- `Common` 类加载器加载容器和多个 Web 应用共享的类，通常对应 `$CATALINA_BASE/lib`。
- `WebappClassLoader` 加载当前应用的 `WEB-INF/classes` 和 `WEB-INF/lib`，使不同应用可以使用不同版本的依赖。
- Web 应用类默认具有一定的子优先特征，但 Java/Jakarta 等核心 API 会优先委托父加载器；可通过 `delegate` 配置改变委托顺序。

应用停止或热部署后，只有该类加载器不再被线程、静态变量、缓存等引用时，相关类元数据才可能卸载。因此不要把应用专属依赖随意放进共享目录，并注意线程池、ThreadLocal 和 JDBC 驱动造成的 ClassLoader 泄漏。

# Tomcat 集群如何处理 Session？

常见方案是集中式 Session（Redis 等）、无状态 Token，或容器 Session 复制/粘性会话。Session 复制会带来网络和一致性成本；能无状态化时优先无状态，必须保留 Session 时使用集中存储并设置过期与故障策略。
