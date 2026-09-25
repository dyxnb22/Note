# ClickHouse

> 定位：选型概览。本文用于理解列式 OLAP 的存储模型、MergeTree 读写路径、集群扩展和 OLTP/OLAP 分工；需要生产使用时，应继续补容量规划、ZooKeeper/Keeper 运维和查询调优实验。

ClickHouse 是面向大规模分析查询的列式 OLAP 数据库，以高扫描吞吐和低聚合延迟著称，适合事件、日志和时序类数据；它不追求 OLTP 式的点查和强事务。

## 列式存储为什么适合分析？

按列组织数据后，一次聚合查询只读涉及的列，I/O 大幅下降；同列数据类型一致，压缩率远高于行存，进一步减少磁盘和网络开销；向量化执行按批处理列数据，充分利用 CPU 流水线和 SIMD。

代价是行级随机读和整行取出变慢，所以它天然偏重"少量列、大量行"的聚合场景，而不是"取整行、按主键点查"的事务场景。

## MergeTree 引擎是怎么工作的？

写入按批生成不可变的 part 文件，后台把小 part 不断合并成大 part：

```text
INSERT → 内存排序 → 生成 part → 后台 Merge → 逐渐合并成大 part
```

- **ORDER BY 主键**：part 内数据按主键有序，主键索引是稀疏索引（每 granule 一条），定位后顺序扫描一段数据，不是 B+ 树式的逐行定位。
- **分区（PARTITION BY）**：通常按时间分区，查询时按分区裁剪掉无关数据；分区也是 TTL 和数据生命周期管理（DROP PARTITION）的抓手。
- **表引擎族**：ReplacingMergeTree/CollapsingMergeTree 用后台合并去重或对消记录，SummingMergeTree 预聚合——它们都是"最终生效"，不是即时更新的事务语义。
- **物化视图**：写入时同步或异步触发聚合到目标表，用预聚合换查询延迟。

**工程含义**：小批量高频写入会生成大量小 part，合并压力剧增（too many parts），要按大批次、低频率写入；幂等和去重要靠业务键 + ReplacingMergeTree/Collapsing 语义设计，不能用"先查再改"的 OLTP 思路。

## 为什么它不适合 OLTP？

- 事务能力弱，没有跨表的多语句强事务和回滚语义。
- 点查/更新走"读整段 + 重写 part"的路径，高并发小事务的延迟和吞吐都不可接受。
- 数据可见性和去重依赖后台合并，是最终一致的；主键查询是范围扫描，不是低延迟键值查找。

因此典型架构是：事务事实（账户、任务状态、幂等记录）留在 MySQL/PostgreSQL，事件流水异步批量进 ClickHouse 做分析，两侧用 CDC 或批量抽取衔接。

## 集群怎么复制和扩展？

- **Replicated\*MergeTree + ClickHouse Keeper（ZooKeeper）**：同分片多副本，副本间同步插入日志，保证副本一致；Keeper 只管元数据协调，不承载数据。
- **分片（Shard）+ Distributed 表**：按分片键把数据水平拆到多个分片，Distributed 表做透明路由和跨分片聚合。
- 扩容涉及分片重平衡和数据搬迁，通常按时间分区设计降低迁移粒度。

## 什么时候适合使用 ClickHouse？

适合：事件/日志/Trace/时序数据的大规模聚合与下钻、准实时报表和监控看板、用户行为漏斗分析、需要秒级响应的 OLAP ad-hoc 查询。

不适合：高频单行更新、强事务、按主键点查的业务事实存储——这些回到 MySQL/PostgreSQL；文档/宽列和全文检索场景分别看 MongoDB、Cassandra 与搜索与 Elasticsearch。
