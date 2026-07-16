# Backend

这里放传统后端开发内容，重点是服务、数据库、中间件和系统设计。

## 目录

- `Java`：语言、集合、并发、JVM、Spring；补充 [Tomcat](/Users/diaoyuxuan/Documents/Notes/Learning/Backend/Java/Tomcat.md) 和 [正则表达式](/Users/diaoyuxuan/Documents/Notes/Learning/Backend/Java/正则表达式.md)
- `Go`：并发服务、Context、HTTP、性能与测试
- `Rust`：所有权、并发安全、异步服务与性能模型
- `Data`：数据库、缓存、消息队列
- `Architecture`：分布式、系统设计
- `Delivery`：Git、Linux、Docker、部署上线

补充：[调试与问题定位](./Java/调试与问题定位.md)。

系统设计新增主线：

- [DDD 与领域建模](./Architecture/DDD与领域建模.md)
- [可靠性与一致性](./Architecture/可靠性与一致性.md)
- [任务、消息与补偿](./Architecture/任务、消息与补偿.md)
- [网关、接口治理与 SDK](./Architecture/网关、接口治理与SDK.md)
- [组件化与中间件设计](./Architecture/组件化与中间件设计.md)
- [场景方案库](./Architecture/场景方案库.md)

## 建议使用原则

- 写业务代码时碰到的语言和框架问题，放 `Java`
- Go 与 Rust 的语言/服务工程笔记分别放对应子目录
- 存储、缓存、MQ 相关内容，放 `Data`
- 架构层面的总结，放 `Architecture`
- 运维、环境、交付流程，放 `Delivery`
