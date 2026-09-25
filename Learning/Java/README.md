# Java 后端

本目录是 Java 后端路线入口；具体知识统一按"题目 → 答案 → 追问/验证"组织。

版本基线（2026-07-30）：JDK 25 已于 2025-09-16 GA；LTS 支持期限由具体发行商定义。现有项目仍应按框架兼容性选择 17、21 或 25，不要只为追新升级。版本状态以 [OpenJDK 发布页](https://openjdk.org/projects/jdk/) 和目标发行商支持策略为准。

## 进入方式

- 面试与系统化复习：从 [[01_语言与运行时]] 开始，按推荐顺序阅读。
- 语言、JVM、集合、并发、Spring、Tomcat、数据访问和日志问题，都在本目录按问答形式组织。
- 数据库与缓存见 [Data](../Data/README.md)，分布式与系统设计见 [Architecture](../Architecture/README.md)，部署交付见 [Delivery](../Delivery/README.md)，测试体系见 [Testing](../Testing.md)。

## 页面目录

| 页面 | 覆盖 |
|---|---|
| [01_语言与运行时](./01_语言与运行时.md) | 语言基础、对象模型与运行时机制 |
| [02_IO与网络编程](./02_IO与网络编程.md) | IO/NIO、Socket 与网络编程 |
| [03_集合与容器](./03_集合与容器.md) | 集合框架、HashMap 实现与并发容器 |
| [04_JVM](./04_JVM.md) | 内存区域、类加载、GC 与调优 |
| [05_并发与JUC](./05_并发与JUC.md) | 线程、锁、AQS、并发工具与线程池 |
| [06_设计模式](./06_设计模式.md) | 常用模式与工程化使用 |
| [07_Java数据访问](./07_Java数据访问.md) | JDBC、MyBatis 与数据访问层 |
| [08_Spring核心](./08_Spring核心.md) | IoC、AOP、事务与 Bean 生命周期 |
| [09_SpringWeb与Boot](./09_SpringWeb与Boot.md) | Spring MVC、Boot 自动配置与启动 |
| [10_SpringCloud](./10_SpringCloud.md) | 注册配置、网关与分布式组件 |
| [11_Spring生产机制与排障](./11_Spring生产机制与排障.md) | 循环依赖、启动排障与生产问题 |
| [12_Tomcat](./12_Tomcat.md) | 连接器、容器与线程模型 |
| [13_正则表达式](./13_正则表达式.md) | 语法要点与工程实践 |
| [14_调试与问题定位](./14_调试与问题定位.md) | 排查路径、日志与工具 |
| [15_Maven](./15_Maven.md) | 构建生命周期与依赖管理 |
| [16_Java日志与可观测性](./16_Java日志与可观测性.md) | SLF4J/Logback、MDC 与异步日志 |

## Java 的边界

- Java 特有的语言、Runtime、JVM、Spring、Maven/Gradle 和 Java 客户端放本目录。
- 数据库本身、消息系统、分布式一致性和生产交付方法不复制到 Java，使用公共后端正文。
- Java 实践项目出现后，放入本目录的 `实践/`；可迁移结论再回链到公共能力或案例目录。
