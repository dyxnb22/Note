# Spring 生产机制与排障

本篇把 Spring 容器、Web、事务、数据访问、安全与生产排障连接起来。基础定义见[Spring 核心](Spring核心.md)、[Spring Web 与 Boot](SpringWeb与Boot.md)和[Java 数据访问](Java数据访问.md)。

## 1. 启动与刷新流程

应用启动大致经历环境准备、配置加载、ApplicationContext 创建、BeanDefinition 注册、后处理器执行、单例创建、Web Server 启动和就绪事件。

排查启动慢或失败时按阶段记录：

- 配置与条件装配。
- Classpath 扫描。
- Bean 创建与外部连接。
- 数据库迁移。
- Web Server 与健康检查。

不要在 Bean 构造器中执行不可控长网络调用。

## 2. Bean 生命周期

典型链路包含实例化、属性注入、Aware 回调、BeanPostProcessor 前后处理、初始化和销毁。

AOP 代理常由 BeanPostProcessor 创建，因此：

- 构造阶段不应依赖最终代理行为。
- 直接 `new` 的对象不受容器增强。
- `this` 自调用绕过代理。
- `final`、可见性和代理方式会影响可增强方法。

## 3. 自动配置

Spring Boot 自动配置依赖 Classpath、属性和缺失 Bean 等条件。排查时查看：

- 哪个条件匹配或未匹配。
- 用户 Bean 是否覆盖默认 Bean。
- 配置属性是否绑定成功。
- 多个 Starter 是否重复注册能力。

Starter 提供可覆盖的安全默认值，不把业务流程藏在自动配置中。

## 4. MVC 请求链路

```text
容器线程 → Filter → DispatcherServlet
→ HandlerMapping → Interceptor → Controller
→ 参数解析/校验 → Service → 返回值处理
→ 异常解析 → Response
```

Filter 适合协议和容器层能力，Interceptor 适合 MVC 上下文，AOP 适合方法级横切。认证、Trace 和错误处理的顺序需要集成测试。

## 5. 异步与线程池

`@Async` 同样依赖代理；自调用可能不生效。必须显式配置线程池、队列、拒绝策略、线程命名和上下文传播。

无界队列会隐藏过载。MDC、SecurityContext 和 Trace 上下文不会天然安全传播到任意线程，需要受控装配并清理。

## 6. 声明式事务

事务拦截器围绕代理方法开启、提交或回滚事务。重点理解：

- 传播行为决定加入、挂起还是新建事务。
- 隔离级别最终由数据库支持。
- 默认回滚规则不一定覆盖所有受检异常。
- 异步方法不继承调用线程事务。
- 事务内远程调用会延长锁与连接占用。

`REQUIRES_NEW` 会额外占用连接，外层事务并发较高时可能耗尽连接池。

## 7. ORM 与批处理

JPA Persistence Context 会缓存受管实体；大量处理需分批 Flush/Clear。N+1、隐式懒加载和过度级联常导致不可控 SQL。

MyBatis 仍需关注动态 SQL、安全参数绑定、批执行、返回行数和事务边界。所有 ORM 优化都应看真实 SQL 与执行计划。

## 8. Spring Security

安全链路区分：

- Authentication：建立主体。
- SecurityContext：保存当前请求身份。
- Authorization：方法或资源级决策。
- CSRF、CORS 和 Session 策略。
- 密码编码、Token 验证和注销。

URL 放行不能替代资源级授权。异步、消息和定时任务需要显式建立工作负载身份。

## 9. 连接池

连接池大小由数据库容量、实例数、事务时间和并发共同决定。监控：

- Active、Idle、Pending。
- 获取连接等待时间。
- 连接寿命和验证失败。
- 慢事务与泄漏。

连接池耗尽是症状，可能来自慢 SQL、锁等待、网络、事务过长或连接未释放。

## 10. Actuator 与可观测性

区分 liveness 与 readiness；管理端点应独立保护。统一 Metrics、Trace 和日志中的应用名、版本、环境和请求上下文。

高基数业务 ID 放日志或 Trace，不作为普通指标标签。

## 11. 线程与 GC 联合排障

排查高延迟：

1. 确认请求率、错误和延迟。
2. 查看 Web 线程池、数据库池和下游等待。
3. 获取线程栈判断 RUNNABLE、BLOCKED、WAITING。
4. 查看 CPU、GC、Heap 和锁。
5. 对照最近发布和配置。

单次线程 Dump 可能误判，应在问题窗口多次采样。

## 12. 最小演练

- 复现事务自调用失效。
- 构造 N+1 和连接池耗尽并用指标定位。
- 构造线程池无界队列造成的尾延迟。
- 为 Security 方法授权写集成测试。
- 模拟 SIGTERM，验证就绪摘除和请求排空。

## 验收清单

- 能画出启动、Bean 和 MVC 请求链路。
- 能解释代理导致的事务与异步失效。
- 数据访问以 SQL、连接池和执行计划为证据。
- 安全覆盖 URL、方法和资源三个层次。
- 线程、连接池、GC 和 Trace 可以联合定位问题。

## 来源与验证边界

机制以项目使用版本的 Spring Framework、Spring Boot、Spring Security 和数据访问官方文档为准；代理、自动配置和默认值可能随版本变化，必须用最小集成测试验证。

`#java #spring #transaction #security #troubleshooting`
