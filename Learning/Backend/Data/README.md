# Data

这里放后端开发里最常见的数据层和中间件能力。

## 这个目录解决什么问题

- 数据最终怎么存、怎么查、怎么保证一致性
- 高并发下缓存怎么顶住读流量
- 异步链路怎么解耦、削峰和保证可靠性
- 面试里 MySQL、Redis、MQ 这些高频题怎么讲得成体系

## 主题

- [MySQL](../../../Learning/Backend/Data/MySQL.md)：关系型数据库、索引、事务、锁、日志、调优
- [Redis](../../../Learning/Backend/Data/Redis.md)：数据结构、缓存设计、持久化、高可用、集群
- [MongoDB](../../../Learning/Backend/Data/MongoDB.md)：文档模型、索引、复制、分片与聚合
- [大数据基础](../../../Learning/Backend/Data/大数据基础.md)：HDFS、MapReduce、Hive、HBase、Spark、YARN
- [消息队列](../../../Learning/Backend/Data/消息队列.md)：异步、削峰、解耦、可靠性、顺序性、幂等

## 建议顺序

1. 先看 `MySQL`
2. 再看 `Redis`
3. 最后看 `消息队列`

## 边界

- 偏系统拆分、分布式一致性、服务治理放 `Architecture`
- 偏部署、上线、CI/CD、运维流程放 `Delivery`
- 偏数据库、缓存、MQ 本身的原理和使用放这里
