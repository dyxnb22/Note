# 搜索与 Elasticsearch：从词项到可恢复索引

搜索引擎把文本转换成可检索结构，再按相关性与过滤条件返回结果。作为数据库事实的派生索引，它需要明确分词、版本、可见性、权限与重建方式。以下 REST 示例采用 Elasticsearch 8.x 的常见语法。

## 倒排索引与字段语义

倒排结构把词项连到包含它的文档和相应信息。Analyzer 的字符处理、分词与 Token Filter 改变索引词项，搜索时必须使用兼容语义；中文、同义词与停用词应以实际查询验证。

创建演示索引使用 PUT /course_articles_v1，正文为：

```json
{
  "mappings": {
    "properties": {
      "article_id": {"type": "keyword"},
      "tenant_id": {"type": "keyword"},
      "status": {"type": "keyword"},
      "title": {"type": "text", "analyzer": "standard"},
      "updated_at": {"type": "date"}
    }
  }
}
```

text 面向分析和全文匹配，keyword 面向完整值的筛选、排序和聚合，数值与日期也应按对应类型建模。许多字段类型或分析规则不能原地重解释全部历史数据，需要新索引重建，不是修改 Mapping 就已迁移完成。

## 写入确认、复制与搜索可见性

用 PUT /course_articles_v1/_doc/a1?refresh=wait_for 写入：

```json
{
  "article_id": "a1",
  "tenant_id": "t1",
  "status": "published",
  "title": "Database transaction boundaries",
  "updated_at": "2026-10-22T09:00:00Z"
}
```

主分片执行写入并将操作复制给相应副本，按协议与配置确认。复制不必等到先生成可搜索 Segment 才发生；把“主分片 refresh 后再复制副本”画成固定写入链是错误的。[写入与复制](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/docs-replication.html)

Refresh 使相应新内容进入搜索视图，不等于完成所有持久化；translog 的同步策略与 Lucene 提交影响恢复。Flush 建立相应持久提交并滚动 translog，不是“让搜索立刻看见”的同义词。副本各自也有搜索可见性阶段。[刷新](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/near-real-time.html)、[Translog](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/index-modules-translog.html)

wait_for 等待相应刷新，不等于每次都强制立即刷新。按 ID 读取与 Search 还有不同实时性约定，因此“写成功但没搜到”要先判断访问路径，而不是直接认定写入丢失。

## Query、Filter 与相关性

对 GET /course_articles_v1/_search 发送：

```json
{
  "query": {
    "bool": {
      "must": [{"match": {"title": "database"}}],
      "filter": [
        {"term": {"tenant_id": "t1"}},
        {"term": {"status": "published"}}
      ]
    }
  },
  "sort": [{"_score": "desc"}, {"article_id": "asc"}],
  "size": 20
}
```

Query Context 计算相应相关性，Filter Context 表达是否匹配并可能按策略缓存。这是语义区别，不是所有请求必定“先执行 filter 再执行 query”的时间线。match 分析文本，term 匹配词项或完整 keyword 值，不能随意互换。

BM25、字段加权、时间与业务信号共同影响排序，should 是否必须满足也要显式设计。查询集、相关性标注、Recall/NDCG 与线上反馈用于评估质量，单个例子第一名不构成正确性证据。

租户过滤在这里表达查询范围；若调用方还能任意改 DSL 或直连索引，它并不是完整授权边界。数据访问必须由相应服务和权限机制约束。

## 分片查询与聚合

协调节点把查询分发到相关分片，收集局部候选后合并。分片越多，局部工作与结果传输也越多；副本能帮助相应读负载，不会把一个主分片的写入自动切成多个主分片。

聚合通常依赖 Keyword/Numeric 的 Doc Values。Terms 的分布式候选与分片大小会影响精度，Cardinality 通常为近似值，高基数与深嵌套还会消耗内存；需要分页遍历桶时可考虑 Composite，而不是把 size 无限调大。

## 深分页、游标与稳定视图

from+size 需要各分片提供更大的候选集合，深页成本高且受结果窗口限制。search_after 根据上一页最后一行的完整 sort 值继续，要求相同查询和稳定的补充排序键。

只换成 search_after 不会固定变化中的索引。需要稳定遍历时配合 PIT，并使用响应提供的完整排序数组与相应新 PIT ID，管理存活期并完成后关闭；它也不是任意跳页的索引。[分页与 PIT](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/paginate-search-results.html)

## 数据同步与删除

```text
数据库事实与 Outbox/CDC → 事件消费者
→ 对应业务版本与删除判断 → 索引写入 → 对账
```

旧事件不能覆盖新状态，相同版本的重试也要有内容等价的约定。外部版本、乐观并发等机制各有条件，不能只带一个 updated_at 就证明乱序已处理；删除墓碑的保留与历史重放窗口同样需要设计。

搜索通常允许派生数据延迟，关键状态可按合同回源确认。Change Log 的位置、索引消费进度与数据库提交是不同事实，不能用请求成功率代替同步完整性。

## Alias 切换与重建

Alias 能原子更新逻辑名称的索引指向，但不会替重建过程补齐并发变更。可靠流程需要固定基线、持续捕获增量、重建并追平到明确边界，再切换读写和处理残留事件。

若只启动 Reindex，结束后立刻切 Alias，构建期间的更新或删除可能未被正确交接。校验还应覆盖数量、版本、抽样内容、权限与排序，旧索引保留需与回滚和成本窗口一致。

## Segment、容量与恢复

更新与删除会留下旧版本或删除标记，后台 Merge 整理 Segment，并消耗 CPU、磁盘与 I/O。频繁 Refresh 会增加小 Segment，Force Merge 也不是活跃索引日常提速按钮。

分片太多放大元数据与调度，太大增加迁移和恢复时间。按写入率、体积、保留、查询并发、磁盘余量与恢复带宽估算，Rollover/ILM 与冷热层只是具体执行手段。

Master-eligible、Data、Ingest、Coordinating 各有职责，选主看相应投票配置，不是所有数据节点随便选多数。故障验证应包含分片不可用、磁盘水位、映射冲突、切换与快照恢复，才能确认索引不仅能查，也能重新建起来。
