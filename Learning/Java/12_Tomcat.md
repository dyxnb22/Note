# 12 Tomcat：从连接到 Servlet 调用

Tomcat 把网络连接上的 HTTP 数据转换为 Servlet 请求，再把结果写回连接。连接、请求、工作线程与 Web 应用是不同层次：一个长连接可承载多次请求，等待下一次请求的连接也不必一直占用业务线程。本章按 Tomcat 10.1 的平台线程与 NIO 连接器说明。

## 容器层次与请求路径

一个 Service 组合多个 Connector 和一个 Engine；Engine 下包含 Host，Host 下包含 Web 应用 Context，Context 通过 Wrapper 管理具体 Servlet。Service 表达组件组合，不是业务请求必须逐级调用的一段处理代码。

```text
Service
  ├─ Connector：端口、协议与连接处理
  └─ Engine → Host → Context → Wrapper → Servlet
```

连接器完成协议处理后，请求沿容器管线与映射进入目标应用，再调用 Servlet.service。应用过滤器与 Servlet 承担相应处理；Spring MVC 的 DispatcherServlet 是其中一种 Servlet，不会替代容器的连接管理。

## I/O 就绪与业务执行是两件事

NIO 连接器用多路复用管理连接事件，工作线程执行协议处理与同步 Servlet 业务。NIO2 的异步 I/O 接口改变等待网络完成的方式，但不自动把阻塞的数据库、文件或 RPC 调用变成异步业务。

Servlet 异步处理还需要应用显式建立异步生命周期并最终完成响应。它与选择 NIO/NIO2 连接器不是同一个开关。I/O 模型的基础见[I/O 与网络编程](02_IO与网络编程.md)。

## 线程、连接与队列参数

| 参数 | 限制或等待的对象 | 判断边界 |
|---|---|---|
| maxThreads | Connector 内部执行器的平台工作线程 | 使用外部 Executor 时需看其配置，不能只改此值 |
| maxConnections | 连接器接收并处理的连接数 | 不等于同时执行业务的线程数 |
| acceptCount | 连接数达到上限后，操作系统连接等待队列的请求容量 | 实际行为还受操作系统影响，不是通用业务任务队列长度 |
| connectionTimeout | 接收连接后等待请求行等相应读阶段的超时 | 不覆盖任意业务方法的总执行时长 |
| keepAliveTimeout | 持久连接等待下一次请求的空闲时间 | 与单次业务处理超时不同 |

工作线程耗尽时，已接受请求可在执行侧等待；达到 maxConnections 后，新连接又可能停在操作系统队列。观察到“排队”时，先确定是哪一层，才能知道要调整线程、连接还是下游容量。[Tomcat HTTP Connector](https://tomcat.apache.org/tomcat-10.1-doc/config/http.html)

例如数据库池只有 20 个连接，单纯把工作线程从 100 增到 500，可能增加等待数据库的线程与内存，未必提高完成速率。应同时测量连接数、工作线程活跃数、队列、请求时长、数据库等待和拒绝情况，给各层设置匹配的上限。

## Servlet 的创建、服务与销毁

容器实例化 Servlet 后调用 init，请求到来时调用 service，卸载时调用 destroy。load-on-startup 可以提前初始化，否则可能在首次使用时创建。多个请求可能并发进入同一个 Servlet 实例，因此请求特有数据应保存在局部变量或明确的请求作用域，不应直接写入共享字段。

应用停止时还要结束自己创建的线程与任务；destroy 是生命周期回调，不能保证强制终止或进程崩溃时仍能完成所有外部动作。

## Web 应用的类加载隔离

每个 Web 应用通常有独立的 WebappClassLoader，加载 WEB-INF/classes 与 WEB-INF/lib；Common 加载器提供容器和应用共享的类。应用加载器有子优先规则，但 Java/Jakarta 等核心 API 存在委派例外，可配置的 delegate 也会影响选择。

隔离允许两个应用使用不同依赖版本，随意把应用专属库放进共享目录会改变这个边界。卸载后，旧线程、ThreadLocal、驱动注册与全局缓存若仍引用应用类加载器，类元数据就可能继续存活；类加载与卸载机制见[JVM](04_JVM.md)。

## 多实例与 Session 状态

若 Session 只在实例 A 内存，后续请求到 B 可能找不到同一状态。粘性路由减少跨实例访问，却仍面对节点故障；Session 复制与共享存储分别引入复制流量或外部存储依赖，需要设计过期与故障行为。

自包含 Token 可以减少每次会话读取，但即时撤销、权限变化和密钥轮换仍需机制支持。选择依据是状态与失效要求，不能仅把“无状态”当成所有服务更优的答案。
