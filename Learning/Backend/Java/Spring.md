# Spring

Spring 技术栈包含容器、Web 框架、应用装配、数据访问和微服务组件。它们共享 Spring 生态，但解决的问题不同，不再放在同一条连续正文中。

## 文档地图

| 文档 | 负责的问题 | 主要内容 |
| --- | --- | --- |
| [Spring 核心](Spring核心.md) | 对象如何创建、组装和增强 | IoC、DI、Bean、AOP、事务、扩展点 |
| [Spring Web 与 Boot](SpringWeb与Boot.md) | HTTP 应用如何接入和启动 | Spring MVC、参数绑定、异常处理、自动配置、Starter |
| [Java 数据访问](Java数据访问.md) | Java 服务如何安全访问关系数据库 | JDBC、连接池、MyBatis、JPA、事务边界 |
| [Spring Cloud](SpringCloud.md) | 多服务如何发现、通信和治理 | 注册配置、OpenFeign、Gateway、负载均衡与容错 |

## 建议顺序

1. 先学 Spring 核心，理解容器、代理和事务。
2. 再学 Spring Web 与 Boot，完成一个可测试的 HTTP 服务。
3. 接着学 Java 数据访问，把 SQL、连接池和事务接入应用。
4. 只有进入多服务场景后再学习 Spring Cloud。

## 边界

- Java 语言、反射和动态代理基础放 [Java](Java.md)。
- SQL 和数据库实现放 [Data](../Data/README.md)。
- 通用分布式与可靠性方法放 [Architecture](../Architecture/README.md)。
- 构建、容器和上线放 [Delivery](../Delivery/README.md)。

## 最小验收

- 能解释 Bean 从定义到可用对象经历了什么。
- 能说明声明式事务为什么依赖代理，以及哪些调用方式会失效。
- 能从 HTTP 请求追踪到 Controller、Service、Repository 和数据库。
- 能区分 Spring Boot 自动装配与 Spring Framework 本身。
- 能把数据一致性边界落实为事务、唯一约束和幂等处理。
- 能判断单体应用什么时候不需要引入 Spring Cloud。
