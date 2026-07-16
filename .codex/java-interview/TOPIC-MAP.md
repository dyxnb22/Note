# Java 面试资料主题映射

这是一份初始映射，处理具体资料时可以补充目标章节，但不改变“已有文档优先”的原则。

| 原始资料主题 | Learning 目标文档 | 默认处理方式 |
|---|---|---|
| 计算机组成 | `Learning/CS/计算机组成.md` | 仅在确认没有对应内容后新建 |
| 操作系统、Linux | `Learning/CS/OS.md` | 合并到已有章节 |
| TCP/IP、HTTP、HTTPS、DNS | `Learning/CS/Network.md` | 合并到已有章节 |
| Git | `Learning/Backend/Delivery/Git.md` | 合并到已有章节 |
| 数据结构总览 | `Learning/CS/数据结构.md` | 合并到已有章节 |
| 数组、链表、栈、队列、树、图、哈希 | `Learning/CS/算法/` 或 `Learning/CS/数据结构.md` | 按已有文件归并 |
| Java 基础、面向对象、异常、泛型、反射 | `Learning/Backend/Java/Java.md` | 合并到已有章节 |
| Java 集合 | `Learning/Backend/Java/Java集合.md` | 合并到已有章节 |
| JVM、类加载、GC、调优 | `Learning/Backend/Java/JVM.md` | 合并到已有章节 |
| 并发、多线程、锁、AQS、线程池 | `Learning/Backend/Java/JUC.md` | 合并到已有章节 |
| Spring、Spring Boot、MyBatis、Spring Cloud | `Learning/Backend/Java/Spring.md` | 合并到已有章节 |
| MySQL、索引、事务、MVCC、锁、调优 | `Learning/Backend/Data/MySQL.md` | 合并到已有章节 |
| Redis 数据结构、缓存、持久化、集群、分布式锁 | `Learning/Backend/Data/Redis.md` | 合并到已有章节 |
| Kafka、RabbitMQ、RocketMQ、ActiveMQ | `Learning/Backend/Data/消息队列.md` | 合并到已有章节 |
| Elasticsearch | `Learning/Backend/Data/搜索与Elasticsearch.md` | 合并或按规模扩充 |
| 分布式理论、RPC、ZooKeeper、分布式 ID | `Learning/Backend/Architecture/分布式.md` | 合并到已有章节 |
| 限流、熔断、降级、容灾、治理 | `Learning/Backend/Architecture/高可用与服务治理.md` | 合并到已有章节 |
| 秒杀、短链、Feed、订单、排行榜等系统设计 | `Learning/Backend/Architecture/系统设计.md` | 合并到已有章节 |
| Netty、NIO、Tomcat、Nginx | `Learning/CS/Network.md` 或新增专题文档 | 先判断是否达到独立主题规模 |
| Dubbo 深入内容 | `Learning/Backend/Architecture/分布式.md` 或新增 RPC 文档 | 先去重再决定 |
| Kubernetes | `Learning/Backend/Delivery/Docker.md` 或新增 Kubernetes 文档 | 只保留后端面试相关内容 |
| MongoDB、正则、性能优化 | 对应 Data、Java 或新增专题文档 | 作为补漏阶段处理 |
| 大厂面经 | 映射回以上主题文档 | 不按公司重复建立题库 |
| 项目表达、面试准备 | `Learning/Writing_and_Expression/03_Workplace_Communication/面试中的项目表达框架.md` | 只补充新的回答方法 |

## 处理标记

- `SKIP`：已有内容充分或没有面试价值。
- `MERGE`：已有主题中补充新的重点、追问、场景或易错点。
- `REVISE`：已有内容存在明显错误、过时或表述不适合面试。
- `CREATE`：Learning 中确实没有对应主题，且内容规模足以独立成文。
