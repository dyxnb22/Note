# Cassandra

> 定位：选型概览。本文用于理解宽列数据模型、分区、副本和读写路径；需要生产使用时，应继续补一致性级别实验、Compaction、Repair、Tombstone 和容量运维。

Cassandra 是面向高写入吞吐和水平扩展的分布式宽列数据库。它按查询设计数据模型，不追求关系数据库式的自由 JOIN 和全局事务。

## Cassandra 的数据模型是什么？

可以按以下层次理解：

```text
Keyspace → Table → Partition → Row/Clustering columns
```

- **Partition key** 决定数据落在哪个节点，是分布和查询路由的核心。
- **Clustering columns** 决定同一分区内的排序和范围查询。
- 一次查询通常必须带 partition key；否则可能退化为跨节点扫描。

建模顺序应从查询开始：先列出访问模式，再为每种高频查询设计表和主键，必要时接受数据冗余。要控制单个 Partition 的大小，避免热点分区和超大分区。

## 一致性 Hash、虚拟节点和副本怎么配合？

Cassandra 把节点映射到 Token Ring，数据 Key 根据分区键 Hash 后落到环上的位置，再由后续节点承担副本。虚拟节点把一台物理机拆成多个 Token，可以改善数据分布和扩缩容时的迁移均衡。

复制因子决定每个分区保存多少副本；协调节点根据一致性级别等待部分或全部副本确认。写入更偏向高可用和吞吐，读取时再通过版本、读修复或反熵同步收敛数据。

## Gossip 协议解决什么问题？

节点通过周期性地交换成员状态、Token 和版本信息，逐步传播集群拓扑和存活状态。Gossip 没有单点协调者，扩展性好，但状态传播需要时间；节点刚故障时，不同机器可能暂时看到不同的成员视图。

## Cassandra 的写入和读取路径是什么？

写入通常经过：协调节点定位副本 → 追加 CommitLog → 写入 MemTable → 按一致性级别返回确认 → MemTable 刷成 SSTable。CommitLog 用于故障恢复，SSTable 是不可变文件，后台 Compaction 负责合并、清理旧版本和墓碑。

读取通常检查 MemTable 和多个 SSTable，并结合 Bloom Filter、分区索引和摘要索引减少无效磁盘访问；多个版本可能需要合并，后台读修复帮助副本逐步一致。

## 什么时候适合使用 Cassandra？

适合：写入量大、数据按 Key 访问、需要多节点扩展和跨机房副本的场景，例如时间序列、事件流水和用户行为记录。

不适合：临时多条件查询、复杂 JOIN、强依赖跨分区事务或频繁修改主键的场景。应先验证查询模型、分区大小、热点分布、修复和 Compaction 成本，再决定是否引入。

## Query-first 建模

Cassandra 按查询建表，通常接受反规范化。Partition Key 决定数据落在哪些节点，Clustering Column 决定分区内排序和范围查询。

设计目标：

- 一次查询尽量命中少量分区。
- 分区大小有上限。
- 写入和读取分布均匀。
- 不依赖 `ALLOW FILTERING` 扫描大量数据。

## 一致性级别

读写可选择 ONE、QUORUM、ALL、LOCAL_QUORUM 等级。`R + W > RF` 只提供副本集合交集，仍需时间戳、冲突与故障假设。

跨数据中心通常使用 LOCAL_QUORUM 控制延迟，并明确远端副本恢复和容灾切换。

## Tombstone

删除和 TTL 会产生 Tombstone，在 Compaction 和 Grace Period 后才可安全清理。大量 Tombstone 会增加读取扫描和延迟。

若副本长时间未修复就过早清理 Tombstone，旧数据可能“复活”。TTL、Repair 和 `gc_grace` 必须共同设计。

## Compaction

- Size-tiered：适合写入密集，可能占用更多空间。
- Leveled：控制读放大，Compaction 写放大较高。
- Time-window：适合时间序列和 TTL 数据。

选择依赖读写模式、时间分布和删除策略，不能只按默认值。

## Repair 与运维

副本通过 Repair 比较并同步数据。监控：

- Repair 完成周期。
- Pending Compaction。
- Tombstone 和大分区。
- P99 读写延迟。
- 节点磁盘与流式迁移。
- Hinted Handoff 和一致性错误。

替换节点、扩容和跨机房操作前要估算 Streaming 带宽。

## Lightweight Transaction

LWT 使用 Paxos 提供条件更新，延迟和协调成本明显高于普通写。只用于真正需要 Compare-And-Set 的小范围不变量。

## 最小实验

设计一张按用户和月份分区的事件表，压测热点与大分区；制造节点离线、Tombstone 和 Repair 延迟，验证读取与恢复。

## 导航与关联

- [模块入口：Data](./README.md)
- 同一路线：[MongoDB](./MongoDB.md) · [大数据基础](./大数据基础.md)
