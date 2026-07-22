# Data

这里放后端开发里最常见的数据层和中间件能力。

## 这个目录解决什么问题

- 数据最终怎么存、怎么查、怎么保证一致性
- 高并发下缓存怎么顶住读流量
- 异步链路怎么解耦、削峰和保证可靠性
- 面试里 MySQL、Redis、MQ 这些高频题怎么讲得成体系

## 主题

- [SQL](SQL.md)：查询、聚合、JOIN、子查询、窗口函数与关系建模
- [MySQL](MySQL.md)：存储引擎、索引、事务、锁、日志与调优
- [PostgreSQL](PostgreSQL.md)：MVCC、VACUUM、WAL、扩展索引、复制与 MySQL 差异
- [Redis](Redis.md)：数据结构、缓存设计、持久化、高可用、集群
- [MongoDB](MongoDB.md)：文档模型、索引、复制、分片与聚合
- [Cassandra](Cassandra.md)：宽列模型、分区键、复制、Gossip 和读写路径
- [大数据基础](大数据基础.md)：HDFS、MapReduce、Hive、HBase、Spark、YARN
- [海量数据处理](海量数据处理.md)：海量数据下的分片、Top K、Bitmap、Bloom Filter 和外部处理
- [消息队列](消息队列.md)：异步、削峰、解耦、可靠性、顺序性、幂等
- [搜索与 Elasticsearch](搜索与Elasticsearch.md)：倒排索引、查询、分片与搜索工程边界

## 建议顺序

1. 先看 `SQL`，掌握关系模型和查询语言
2. 再看 `MySQL`，理解具体实现和性能机制
3. 然后看 `Redis`
4. 最后看 `消息队列`

## 学习层级

- 核心主线：`SQL`、`MySQL`、`Redis`、`消息队列`，内容覆盖原理、工程使用和排障。
- 关系数据库扩展：`PostgreSQL`，用于补齐另一套主流 MVCC、日志、索引和复制模型。
- 选型概览：`MongoDB`、`Cassandra`、`搜索与 Elasticsearch`、`大数据基础`、`海量数据处理`。这些文档当前用于建立边界和选型认知，不代表已经达到核心主线的深度。

## 边界

- 偏系统拆分、分布式一致性、服务治理放 `Architecture`
- 偏部署、上线、CI/CD、运维流程放 `Delivery`
- 偏 SQL、数据库、缓存、MQ 本身的原理和使用放这里
