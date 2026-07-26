# Backend

这里放传统后端开发内容，重点是服务、数据库、中间件和系统设计。

## 目录

- [Java](Java/README.md)：语言、集合、并发、JVM、Spring 与工程工具
- [Go](Go/README.md)：并发服务、Context、HTTP、性能与测试
- `Rust`：所有权、并发安全、异步服务与性能模型
- [Data](Data/README.md)：数据库、缓存、消息队列
- [Architecture](Architecture/README.md)：分布式、系统设计
- [Delivery](Delivery/README.md)：Git、Linux、Docker、部署上线
- [后端测试体系](Testing.md)：单元、集成、契约、端到端、性能与韧性测试
- [软件工程与演进式架构](SoftwareEngineering.md)：需求、模块、重构、Review、ADR、技术债和遗留系统迁移

补充：[调试与问题定位](./Java/调试与问题定位.md)。

系统设计新增主线：

- [02_DDD与领域建模](./Architecture/02_DDD与领域建模.md)
- [04_可靠性与一致性](./Architecture/04_可靠性与一致性.md)
- [05_任务、消息与补偿](./Architecture/05_任务、消息与补偿.md)
- [06_网关、接口治理与SDK](./Architecture/06_网关、接口治理与SDK.md)
- [07_组件化与中间件设计](./Architecture/07_组件化与中间件设计.md)
- [08_场景方案库](./Architecture/08_场景方案库.md)
- [09_API与事件契约](./Architecture/09_API与事件契约.md)

跨组件基础补充：

- [数据库系统原理](./Data/数据库系统原理.md)：数据库产品之上的共同原理
- [生产系统工程](./Delivery/07_生产系统工程.md)：性能、容量、可观测性、SLO 和事故响应
- [数据工程与流处理](./Data/数据工程与流处理.md)：CDC、仓库/湖仓、批流、编排与治理
- [云原生与 IaC](./Delivery/08_云原生与IaC.md)：Terraform、GitOps、IAM、网络、多集群与成本

## 建议使用原则

- 写业务代码时碰到的语言和框架问题，放 `Java`
- Go 与 Rust 的语言/服务工程笔记分别放对应子目录
- 存储、缓存、MQ 相关内容，放 `Data`
- 架构层面的总结，放 `Architecture`
- 运维、环境、交付流程，放 `Delivery`
