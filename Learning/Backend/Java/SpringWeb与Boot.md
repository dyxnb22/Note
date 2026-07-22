# Spring Web 与 Spring Boot

Spring MVC 负责 HTTP 请求处理，Spring Boot 负责应用装配、默认配置和启动体验。两者经常一起使用，但不是同一个概念。

## Spring MVC 请求链路

```text
客户端
→ Filter
→ DispatcherServlet
→ HandlerMapping 查找处理器
→ HandlerAdapter 调用 Controller
→ 参数解析与校验
→ Service
→ 返回值处理/消息转换
→ ExceptionHandler（发生异常时）
→ Interceptor afterCompletion
→ Filter 返回
```

`HandlerMapping` 负责“找到谁”，`HandlerAdapter` 负责“怎么调用”。`DispatcherServlet` 通过这层抽象兼容不同处理器模型。

## Filter、Interceptor 与 AOP

| 机制 | 所在层 | 适合处理 |
| --- | --- | --- |
| Filter | Servlet 容器 | 编码、CORS、请求包装、通用安全头 |
| Interceptor | Spring MVC | 用户上下文、接口权限、Controller 前后逻辑 |
| AOP | Spring Bean 方法 | Service 事务、审计、指标和横切逻辑 |

不要在三层重复实现同一套鉴权或日志逻辑。先根据需要访问的上下文和拦截边界选择位置。

## 接口合同

- 使用请求 DTO 和响应 DTO，不直接暴露持久化实体。
- 对外部输入做类型、格式、范围和业务约束校验。
- 统一错误结构，但保留可定位的错误码和 TraceId。
- 分页、排序和过滤字段使用白名单。
- 上传文件同时限制大小、类型、文件名和存储位置。
- 对幂等写接口定义幂等键、重复请求响应和过期策略。

全局异常处理应把“可预期业务错误”和“未知系统错误”分开；未知错误对外隐藏堆栈，对内记录完整上下文。

## Spring Boot 的职责

Spring Boot 不替代 Spring Framework。它主要提供：

- Starter 依赖集合。
- 自动配置。
- 外部化配置。
- 内嵌 Web 容器。
- Actuator 等生产能力。
- 统一的启动与打包方式。

自动配置通常根据 classpath、已有 Bean、配置属性和运行环境决定是否注册组件。自己的 Bean 覆盖默认组件时，要确认条件注解和加载顺序。

## 配置管理

配置应按环境外置，密钥不进入仓库。配置属性优先绑定到类型明确的对象，并在启动时校验必要字段。需要动态刷新时，要判断哪些 Bean 可以安全更新，避免同一请求读取到前后不一致的配置。

常见配置优先级较多，排障时先确认配置来源、激活 Profile 和最终绑定结果，不要只看某一个 `application.yml`。

## Starter 设计

一个可维护的 Starter 通常包含：

- 明确的配置属性和默认值。
- 条件化自动配置。
- 用户可覆盖的默认 Bean。
- 启动失败时清晰的诊断信息。
- 独立测试验证“有依赖/无依赖、有配置/无配置”的组合。

Starter 负责装配通用能力，不应偷偷承载业务流程。

## Web 应用验收

- 参数错误能否返回稳定的 4xx 合同？
- 未知异常是否带 TraceId 且不泄露内部信息？
- 超时、取消和客户端断开能否向下游传播？
- 健康检查是否区分存活和就绪？
- 接口、配置和自动装配是否有测试覆盖？
- Actuator 等管理端点是否与业务入口隔离并受保护？
