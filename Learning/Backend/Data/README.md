# Data

这里放后端开发里最常见的数据层和中间件能力。

## 这个目录解决什么问题

- 数据最终怎么存、怎么查、怎么保证一致性
- 高并发下缓存怎么顶住读流量
- 异步链路怎么解耦、削峰和保证可靠性
- 面试里 MySQL、Redis、MQ 这些高频题怎么讲得成体系

## 主题

- [数据库系统原理](数据库系统原理.md)：关系模型、存储页、索引、优化器、事务、WAL、复制与恢复
- [SQL](SQL.md)：查询、聚合、JOIN、子查询、窗口函数与关系建模
- [MySQL](MySQL.md)：存储引擎、索引、事务、锁、日志与调优
- [PostgreSQL](PostgreSQL.md)：MVCC、VACUUM、WAL、扩展索引、复制与 MySQL 差异
- [PostgreSQL 实践路线](PostgreSQL/README.md)：迁移、查询计划、连接池、锁、恢复、高可用和容量演练
- [Redis](Redis.md)：数据结构、缓存设计、持久化、高可用、集群
- [MongoDB](MongoDB.md)：文档模型、索引、复制、分片与聚合
- [Cassandra](Cassandra.md)：宽列模型、分区键、复制、Gossip 和读写路径
- [大数据基础](大数据基础.md)：HDFS、MapReduce、Hive、HBase、Spark、YARN
- [数据工程与流处理](数据工程与流处理.md)：CDC、仓库/湖仓、批流计算、事件时间、编排、质量与血缘
- [海量数据处理](海量数据处理.md)：海量数据下的分片、Top K、Bitmap、Bloom Filter 和外部处理
- [消息队列](消息队列.md)：异步、削峰、解耦、可靠性、顺序性、幂等
- [搜索与 Elasticsearch](搜索与Elasticsearch.md)：倒排索引、查询、分片与搜索工程边界
- [检索系统工程](../../Agent面试题库/06_RAG与知识库/RAG与检索.md)：向量数据库、ANN/HNSW、混合检索、索引更新和检索评测

## 建议顺序

1. 先看 [数据库系统原理](./数据库系统原理.md)，建立数据模型、索引、事务和恢复框架
2. 再看 [SQL](./SQL.md)，掌握关系查询语言
3. 然后用 [MySQL](./MySQL.md) 或 [PostgreSQL](./PostgreSQL.md) 对照具体实现
4. 再看 [Redis](./Redis.md)
5. 最后看 [消息队列](./消息队列.md)
6. 需要分析与实时数据链路时进入 [数据工程与流处理](./数据工程与流处理.md)
7. 需要把 PostgreSQL 接入服务并做故障验证时进入 [PostgreSQL 实践路线](./PostgreSQL/README.md)

## 学习层级

- 核心主线：[数据库系统原理](./数据库系统原理.md)、[SQL](./SQL.md)、`MySQL/PostgreSQL`、[Redis](./Redis.md)、[消息队列](./消息队列.md)，内容覆盖原理、工程使用和排障。
- 关系数据库扩展：[PostgreSQL](./PostgreSQL.md)，用于补齐另一套主流 MVCC、日志、索引和复制模型。
- 专项系统：[MongoDB](./MongoDB.md)、[Cassandra](./Cassandra.md)、`搜索与 Elasticsearch` 已覆盖建模、索引/存储、扩展、容量和故障恢复。
- 数据平台：[大数据基础](./大数据基础.md) 用于组件地图，[数据工程与流处理](./数据工程与流处理.md) 负责 CDC、批流、仓库/湖仓、编排和治理主线。
- [海量数据处理](./海量数据处理.md) 负责算法型场景；向量索引和混合检索以 Agent 题库下的 [检索系统工程题](../../Agent面试题库/06_RAG与知识库/RAG与检索.md) 为唯一主文档。

## 边界

- 偏系统拆分、分布式一致性、服务治理放 `Architecture`
- 偏部署、上线、CI/CD、运维流程放 `Delivery`
- 偏 SQL、数据库、缓存、MQ 本身的原理和使用放这里
