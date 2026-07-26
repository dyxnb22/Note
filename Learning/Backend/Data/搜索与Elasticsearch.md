# 搜索与 Elasticsearch

> 定位：选型概览。本文用于理解搜索与数据库的边界、倒排索引和分片；需要生产使用时，应继续补 Mapping 演进、Analyzer、相关性评估、集群恢复和容量实验。

## 搜索与数据库的边界

关系数据库擅长事务与精确查询；搜索引擎擅长全文检索、相关性排序、聚合和模糊匹配。不要因“查询慢”就同步复制整套数据到 ES；先明确检索需求、延迟、一致性和回源策略。

## 倒排索引

倒排索引从 term 指向包含它的文档及位置，因而能高效查词。analyzer 决定字符如何变 token；中文分词、同义词、停用词和词干处理会直接改变召回。mapping 一旦投入生产不宜随意改，字段应区分 `text`（分析、全文）与 `keyword`（精确过滤/聚合）。

## 查询与排序

先过滤（filter）再评分（query）：filter 可缓存且不影响相关性，query 产生 score。BM25 是常用词项相关性基础；排序还可能叠加业务权重、时间衰减和权限过滤。召回、排序、重排是不同阶段，指标也不同。

## 数据同步与运维

常用数据库变更日志/消息队列异步同步到 ES，接受最终一致；必须处理重复、乱序、重建索引和删除。使用 alias 实现零停机 reindex；监控写入拒绝、segment、堆内存、查询延迟和热点分片。

## Elasticsearch 写入和查询的核心流程是什么？

写入时，客户端请求先路由到目标索引的 primary shard；写入内存缓冲区并记录 translog，达到 refresh 条件后形成可搜索的 segment，再由 replica shard 复制。`refresh` 影响“能否被搜索”，`flush` 主要负责把事务日志整理到持久化结构，不能把两者混为一谈。

查询时，协调节点把请求转发到相关分片，各分片返回局部结果，协调节点再合并、排序和截取最终结果。分片数、字段 mapping、分词、查询类型和副本数量都会影响延迟与资源消耗。

## Elasticsearch 深分页怎么处理？

`from + size` 需要每个分片保留并排序较多数据，页码很深时成本高且受 `max_result_window` 限制。大批量遍历优先使用 `search_after`，并配合 PIT 固定查询视图；需要按桶遍历聚合时考虑 `composite aggregation`。不要用不断增大的 `from` 模拟批处理。

## 最小练习

为“文章搜索”设计 mapping、分词策略、按标题/正文加权的 query，以及数据库更新到索引的失败补偿方案。

## Mapping 与 Analyzer

`text` 字段经过 Analyzer 用于全文检索，`keyword` 保存完整值用于精确过滤、聚合和排序。日期、数字和布尔值应使用对应类型。

Analyzer 包含字符过滤、Tokenizer 和 Token Filter。索引时与查询时 Analyzer 可以不同，但必须用 `_analyze` 和真实查询验证。错误 Mapping 上线后通常需要新索引重建，不能期待原地改变所有历史字段语义。

## Lucene Segment

Shard 底层由多个不可变 Segment 组成。Refresh 让新 Segment 可搜索，Merge 后台合并 Segment 并清理删除标记。

- Refresh 太频繁增加小 Segment 和开销。
- Merge 消耗 CPU、磁盘和 I/O。
- Delete/Update 实际会标记旧文档并写新版本。
- Force Merge 不适合频繁写入的在线索引常规使用。

## 相关性与查询

区分：

- Query Context：计算相关性。
- Filter Context：是/否匹配，适合缓存。
- `must/should/filter/must_not` 的布尔语义。
- Match、Term、Phrase、Range 和 Multi-match。

搜索质量需要 Query 集、相关性标注、Recall/NDCG 和线上指标；不能只看某个示例排第一。

## 聚合

聚合会在各 Shard 计算局部结果再合并。高基数 Terms、深层嵌套和大范围 Cardinality 可能消耗大量内存。

字段用于聚合时优先 Keyword/Numeric Doc Values。Composite Aggregation 适合分页遍历桶。

## 分片与容量

Shard 过多增加 Heap、文件句柄和集群状态；过大则恢复、迁移和查询成本高。估算文档量、索引体积、写入率、保留期、查询并发和副本。

使用 Rollover、ILM 和冷热层管理时间序列数据。扩容不仅加节点，还要验证磁盘水位、Shard 均衡和恢复带宽。

## 数据同步

数据库到索引通常最终一致：

```text
数据库事务/Outbox → CDC/MQ → 索引消费者
→ 版本检查 → 写入 → 对账与重建
```

文档携带业务版本，拒绝旧事件覆盖新状态。保留全量重建和原子 Alias 切换能力。

## 集群故障

理解 Master-eligible、Data、Ingest 和 Coordinating 角色。脑裂防护和选主由当前集群协调机制负责；运维重点是多数派、Shard Allocation、磁盘水位和恢复。

故障演练：节点退出、磁盘满、热点 Shard、Mapping 冲突、重建切换和快照恢复。

## 安全与多租户

按索引/文档/字段控制访问，避免把权限过滤交给最终模型。多租户需要在共享索引、独立索引和独立集群之间权衡隔离、Shard 数和运维成本。

`#elasticsearch #search #inverted-index`
