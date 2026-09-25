
# Spring Web 与 Boot

Spring MVC 负责 HTTP 请求处理，Spring Boot 负责应用装配、默认配置和启动体验。两者经常一起使用，但不是同一个概念。

## Spring MVC 的请求链路是什么？

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

## Filter、Interceptor 与 AOP 应该如何区分？

| 机制 | 所在层 | 适合处理 |
| --- | --- | --- |
| Filter | Servlet 容器 | 编码、CORS、请求包装、通用安全头 |
| Interceptor | Spring MVC | 用户上下文、接口权限、Controller 前后逻辑 |
| AOP | Spring Bean 方法 | Service 事务、审计、指标和横切逻辑 |

不要在三层重复实现同一套鉴权或日志逻辑。先根据需要访问的上下文和拦截边界选择位置。

## Spring Web 接口合同应该包含哪些边界？

- **使用请求 DTO 和响应 DTO**，不直接暴露持久化实体。
- 对外部输入做类型、格式、范围和业务约束校验。
- 统一错误结构，但保留可定位的错误码和 TraceId。
- 分页、排序和过滤字段使用白名单。
- 上传文件同时限制大小、类型、文件名和存储位置。
- 对幂等写接口定义幂等键、重复请求响应和过期策略。

全局异常处理应把“可预期业务错误”和“未知系统错误”分开；未知错误对外隐藏堆栈，对内记录完整上下文。

## Spring Boot 解决什么问题，它和 Spring Framework 有什么区别？

Spring Boot 不替代 Spring Framework。它主要提供：

- Starter 依赖集合。
- 自动配置。
- 外部化配置。
- 内嵌 Web 容器。
- Actuator 等生产能力。
- 统一的启动与打包方式。

## @SpringBootApplication 组合了哪些注解？

`@SpringBootApplication` 是一个组合注解，核心由三部分组成：

```java
@SpringBootApplication
// 等价于：
@SpringBootConfiguration  // 本质是 @Configuration，标记配置类
@EnableAutoConfiguration  // 开启自动配置（核心）
@ComponentScan            // 扫描当前包及子包下的 @Component 等注解
```

| 注解 | 作用 | 说明 |
| --- | --- | --- |
| `@SpringBootConfiguration` | 标记为配置类 | 本质就是 `@Configuration`，Spring Boot 加了一层语义 |
| `@EnableAutoConfiguration` | 开启自动配置 | 根据 classpath、已有 Bean 和配置属性，**条件化地**注册组件 |
| `@ComponentScan` | 包扫描 | 扫描当前包及其子包下的 `@Component`、`@Service`、`@Repository` 等 |

**笔试考点：** 自动配置的重点在 `@EnableAutoConfiguration`，它通过 `spring.factories`（或 Spring Boot 2.7+ 的 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`）加载候选配置类，再用 `@Conditional` 系列注解决定是否生效。

自动配置通常根据 classpath、已有 Bean、配置属性和运行环境决定是否注册组件。自己的 Bean 覆盖默认组件时，要确认条件注解和加载顺序。

## Spring Boot 配置应该如何管理和排障？

配置应按环境外置，密钥不进入仓库。**配置属性优先绑定到类型明确的对象，并在启动时校验必要字段**。需要动态刷新时，要判断哪些 Bean 可以安全更新，避免同一请求读取到前后不一致的配置。

常见配置优先级较多，排障时先确认配置来源、激活 Profile 和最终绑定结果，不要只看某一个 `application.yml`。

## 一个可维护的 Spring Boot Starter 应该如何设计？

一个可维护的 Starter 通常包含：

- 明确的配置属性和默认值。
- 条件化自动配置。
- 用户可覆盖的默认 Bean。
- 启动失败时清晰的诊断信息。
- 独立测试验证“有依赖/无依赖、有配置/无配置”的组合。

Starter 负责装配通用能力，不应偷偷承载业务流程。

## Spring AI 是什么？Java 后端岗需要掌握到什么程度？

Spring AI 把大模型调用接入 Spring 生态：`ChatClient`/`ChatModel` 屏蔽厂商 API 差异，`Advisor` 组织拦截链（日志、重试、记忆），配合结构化输出、Function Calling、向量库集成和流式响应。

面试掌握到“会用 + 讲清边界”即可：

- 核心链路：Prompt → Model → 响应结构化；流式输出走 SSE（`Flux<String>`），要处理客户端断开与取消。
- LLM 输出不可信：结构化校验、超时/重试、token 与成本观测必须由应用层兜底。
- RAG、Tool Calling、MCP 的原理与工程化是独立专题，深入见 Agent 题库：[生产工程与系统设计](../Agent面试题库/09_工程化与系统设计/生产工程与系统设计.md)、[Tool Calling 与 MCP](../Agent面试题库/04_Tool与协议/Tool%20Calling与MCP.md)、[RAG 与检索](../Agent面试题库/06_RAG与知识库/RAG与检索.md)。

与 LangChain4j 的差异主要是生态位置：Spring AI 深度整合 Boot 自动装配与可观测性，LangChain4j 更中立、可脱离 Spring 使用。选型先看现有技术栈，不要为了框架换框架。

## 怎么用 AI 辅助编程？生成的代码怎么把关？

2026 年 Java 岗的常规问题。答“用什么工具”不如答“工作流和把关标准”：

- **分层使用**：生成样板代码、写测试、解释陌生代码、重构草案；核心业务逻辑与数据模型自己主导。
- **上下文管理**：给足项目约定（依赖版本、规范），避免模型用过时 API；大仓库用检索定位，不要整包贴入。
- **把关标准**：AI 生成代码等同外部贡献——编译与测试、边界条件、并发与事务语义、注入/越权等安全项照常 Review，不因“AI 写的”降低标准。
- **知道边界**：模型会幻觉不存在的 API、带出训练数据里的旧版本写法，版本以依赖清单为准验证。

常见追问是“上下文污染”：无关或错误信息留进会话，导致后续输出变差。应对是拆小任务、及时清理会话，把确认过的事实写进项目文档而不是依赖聊天历史。

## 如何验收一个 Spring Web 应用？

- 参数错误能否返回稳定的 4xx 合同？
- 未知异常是否带 TraceId 且不泄露内部信息？
- 超时、取消和客户端断开能否向下游传播？
- 健康检查是否区分存活和就绪？
- 接口、配置和自动装配是否有测试覆盖？
- Actuator 等管理端点是否与业务入口隔离并受保护？
