# Cassandra：查询决定分区，一致性决定等待

Cassandra 的宽列模型围绕分区访问与多副本组织。学习时先确定一次查询必须读哪些键，再推导分区、状态大小、确认和后台整理，而不是把它当成能任意 JOIN 的关系库。本章以 Cassandra 5.0 的核心机制为背景。

## 从用户事件查询建表

“某租户某用户某月的事件，按时间倒序”可以设计成：

```sql
CREATE TABLE events_by_user_month (
    tenant_id text,
    user_id text,
    bucket text,
    occurred_at timestamp,
    event_id text,
    payload text,
    PRIMARY KEY ((tenant_id, user_id, bucket), occurred_at, event_id)
) WITH CLUSTERING ORDER BY (occurred_at DESC, event_id DESC);

SELECT occurred_at, event_id, payload
FROM events_by_user_month
WHERE tenant_id = 't1' AND user_id = 'u1' AND bucket = '2026-10'
  AND occurred_at >= '2026-10-22T00:00:00Z'
LIMIT 100;
```

括号里的组合是 Partition Key，确定分区及相应副本集合；后两列是 Clustering Columns，定义分区内次序。bucket 的月份规则由应用统一生成，数据库不会自动校验事件时间属于该月。

普通 INSERT 具有 upsert 语义，不是关系库式的“主键重复必报错”。跨用户搜索或跨月汇总需要额外表、有限分区合并或分析路径，不能靠 ALLOW FILTERING 消除扫描成本。

## 时间桶不自动保证小分区

若一个用户每月有一百万条事件、每条约 500 字节，仅原始内容已约 500 MB，尚未计算编码、索引与版本开销。月份不再是合适的小桶，应结合峰值选择更细时间或确定分片规则。

拆桶会增加查询扇出，多张反规范化表也增加写入与修复。要明确同一事实的更新、删除和对账来源，不能把“按查询建表”理解为冗余永远没有一致性代价。

## Token、副本与故障域

分区键经分区器映射到 Token，节点拥有 Token 范围；虚拟节点使一台物理机承担多个范围，但同一热分区仍由相应固定副本承受。

NetworkTopologyStrategy 还按数据中心、机架等策略放副本，不能简化为“环上随后几台机器就是副本”。协调节点组织请求，复制因子定义每个相关范围的副本数量，Gossip 等成员信息传播也不等同于业务写入的共识协议。

## 写入路径与确认

副本把修改写入 CommitLog 与 Memtable，后续刷成不可变 SSTable。确认等多少副本，与这些副本是否已把日志同步到稳定存储是两条独立轴。

periodic 日志模式可能在对应 fsync 前确认，batch 等策略有不同等待条件；不能只因“先写 CommitLog”就宣称任何崩溃都不丢确认写入。内存表刷盘后，相应恢复日志才逐步释放。[存储引擎与同步策略](https://cassandra.apache.org/doc/stable/cassandra/architecture/storage-engine.html)

读取合并 Memtable、缓存和有关 SSTable 中的版本。Bloom Filter 用于减少不必要访问，有旧版本与删除标记时仍需协调；读修复及反熵 Repair 也有不同触发、范围和版本配置，不是一条必然后台执行的万能修复线。

## Quorum 提供交集而非全部业务语义

RF=3 时，QUORUM 通常要求 2 个相应副本响应；一个副本不可用仍可能成功，只有一个可达就无法满足该级别。LOCAL_QUORUM 按本地数据中心的相关副本计算，不能直接当成跨中心所有写入已完成。

R+W>RF 在固定集合内提供交集，还需处理版本、并发写、时间戳、成员和失败条件。普通写的冲突选择不能凭较大墙上时钟就证明符合业务发生顺序，时钟与无条件更新都可能让旧业务事实占上风。

### LWT 的条件边界

需要相应范围的 Compare-And-Set 时，可用 IF NOT EXISTS 或 IF 条件的 LWT，相关 Paxos 协调与 SERIAL/LOCAL_SERIAL 有独立语义和成本。条件操作不等于跨任意分区的一般事务，旁路无条件写也可能绕过应用不变量。

BATCH 同样不能仅凭名字被理解成通用跨分区隔离事务。应按原子性、隔离范围与失败恢复逐项检查，而非寻找一个“事务开关”。

## 删除、TTL 与数据复活

删除或过期以 Tombstone 参与版本合并。达到 gc_grace_seconds 不等于立即物理清理，还需合适的 Compaction 与重叠数据条件；大量墓碑会增加读取工作。

若某副本离线期间没收到删除，其他副本又过早清掉删除证据，旧值可能在恢复同步时重新出现。Repair 周期、离线窗口、保留与压缩策略必须一起设计，不能只调小 grace 降磁盘。

## Compaction 的资源交换

Size-tiered 在大小相近文件间合并，Leveled 约束层内重叠，Time-window 利用时间分布；它们在读放大、写放大、额外空间与过期清理上有不同交换。5.0 引入的 UCS 还提供统一的调整路径，应结合版本和负载评估。[UCS](https://cassandra.apache.org/doc/stable/cassandra/managing/operating/compaction/ucs.html)

合并不只在空闲时免费发生。写入高峰、Repair、Streaming 与 Compaction 会竞争磁盘和带宽，磁盘接近满时还可能缺少生成新文件的空间。

## 维护围绕可恢复副本展开

观察分区大小、墓碑扫描、读写尾延迟、待合并量、Repair 完成范围、Hint 积压与一致性错误，并把它们对应到具体查询。扩容和替换节点要测量范围迁移与剩余恢复能力，而非只看机器已经加入集群。

Cassandra 适合查询可预先设计、按分区扩展的事件与宽列负载；自由关联、跨资源约束或长期忽略修复的运行方式，会让原本的吞吐优势被查询和维护成本抵消。
