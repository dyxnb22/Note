# ClickHouse：从列扫描到可见性与去重

ClickHouse 以列式分析为中心：少量列、大量行、聚合与压缩常能获得很高吞吐。布局、批处理与执行路径决定优势；点查、更新和事务范围则需要按表引擎、版本与操作分别分析。

## 列式布局与访问范围

只读取需要的列，可减少宽表分析的输入；同列编码与压缩也更有机会利用重复和局部性。向量化按批处理数据，减少逐对象开销；实际收益仍取决于类型、分布、过滤和查询形状。

主键点查、整行读取与高频状态更新有另一套成本，应按需要的事务范围与延迟验证。典型协作是把订单事实留在事务库，将版本化事件送入分析存储，而非让两者对相同状态各自作互相矛盾的决定。

## MergeTree 的 Part 与索引

写入生成相应数据 part，后台合并整理 part。成功写入的数据可以在合并前查询，不能把“后台去重尚未发生”理解成“新数据一律还不可见”。异步插入缓冲、副本读取与确认设置另有各自条件。

ORDER BY 定义排序键；PRIMARY KEY 定义稀疏主索引，允许采用排序键前缀。它们不是 OLTP 的唯一约束：相同键可以有多行，稀疏索引主要裁剪 granule 范围，不为每行维护 B+Tree 指针。[MergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree)

PARTITION BY 决定数据组织和生命周期范围。小批量频繁写入、多分区扇出容易产生大量小 part，后台合并追不上时会形成压力；更多分区也不是让所有查询更快的通用索引。

## 用版本例子理解 ReplacingMergeTree

```sql
CREATE TABLE course_orders (
    tenant_id String,
    order_id String,
    revision UInt64,
    event_day Date,
    amount_cents Int64
)
ENGINE = ReplacingMergeTree(revision)
PARTITION BY toYYYYMM(event_day)
PRIMARY KEY (tenant_id)
ORDER BY (tenant_id, order_id);

INSERT INTO course_orders VALUES
    ('t1', 'o1', 1, '2026-10-22', 10000),
    ('t1', 'o1', 2, '2026-10-22', 12000),
    ('t1', 'o2', 1, '2026-10-22', 5000);

SELECT tenant_id, order_id, revision, amount_cents
FROM course_orders FINAL
ORDER BY tenant_id, order_id;
```

有效结果是 o1 的版本 2、12000，以及 o2 的版本 1、5000。合并前普通查询可能仍看到三条原始记录；后台何时整理不确定，部分数据也不应假定一定很快再次合并。

Replacing 按完整 ORDER BY 键识别相同逻辑行，不按另写的 PRIMARY KEY 自动唯一。revision 需有可靠业务顺序，同版本的冲突内容不能靠后台替应用决定。FINAL 在查询时应用相应归并语义，带来查询成本，不等于强制把所有文件物理重写。[ReplacingMergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/replacingmergetree)

同一逻辑行的分区字段也应稳定：后台合并不跨分区，查询时跨分区处理又受设置影响。把分区日期随更新移动，可能让版本永远留在不同后台合并范围。

## 引擎语义不能互换

SummingMergeTree 聚合相应数值，Collapsing 系列按符号等规则对消，Replacing 选择相应版本。它们需要不同的数据约定，不是任选一种就获得业务幂等。

插入重试去重还可能依赖块、token 与保留窗口，不等于永远按订单 ID 去重。跨表、多语句、跨节点提交与回滚也需查看具体支持，不能把单次写入的某个保证扩展成通用 OLTP 事务。

## 物化视图与重复输入

增量物化视图处理插入的数据块，把转换结果写入目标；源表后来后台合并，不会自动让目标表撤销此前累计。如果 o1 的两个版本都贡献了一次收入，不能期待源表去重后收入汇总自然变成只算一次。

刷新型视图定期重算相应查询，是另一类模型。选择时明确输出是追加事实、最新版本还是可替换快照，再决定去重与聚合在哪一层执行，不能泛称“写时同步或异步做一下”。

## 副本、分片与查询

Replicated MergeTree 系列在同分片副本间协调和复制，Keeper/ZooKeeper 主要保存相应协调元数据，不替代数据文件。复制通常有异步窗口，确认与 quorum 设置不能直接理解成所有副本立刻返回相同查询结果。

Distributed 表提供跨分片路由与汇总，目标表和分片键决定数据落点。增加节点不自动均匀迁移全部旧数据，重分片还需明确写入路由、历史搬迁、重复与查询完整性。

## 分析性能的证据

观察扫描行与字节、裁剪效果、解压与聚合成本、内存、part 数、合并队列、复制积压与磁盘余量。索引减少扫描，预聚合减少在线工作，批量写入减少 part 压力，各自解决不同瓶颈。

更新、删除和 mutation 的同步/异步行为随版本、引擎与操作方式变化，不能统一写成“都立即可见”或“都不可接受”。保留周期、TTL、冷存储与回灌还需连到真实数据恢复流程，而非只验证一条报表查询够快。
