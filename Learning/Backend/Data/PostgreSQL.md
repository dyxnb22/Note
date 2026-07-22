# PostgreSQL

PostgreSQL 是强调 SQL 标准、可扩展类型系统、复杂查询和一致性的关系型数据库。本页建立与 [SQL](SQL.md) 和 [MySQL](MySQL.md) 并列的 PostgreSQL 入口，不重复通用查询语法。

## 什么时候考虑 PostgreSQL

- 需要复杂 SQL、窗口函数、递归查询和丰富的数据类型。
- 关系数据与 JSON 文档需要在同一事务中协作。
- 需要 GiST、GIN、BRIN、表达式或部分索引等能力。
- 需要扩展、地理空间、全文检索或自定义类型/函数生态。
- 团队愿意理解 MVCC、VACUUM、统计信息和连接管理。

是否选择 PostgreSQL 不能只看功能清单，还要看现有团队经验、云服务、迁移成本、读写模式和运维能力。

## 进程与存储概览

PostgreSQL 传统上为每个客户端连接创建独立后端进程，并通过共享内存、WAL 和后台进程协作。大量短连接通常要使用应用连接池或 PgBouncer 等外部池化方案。

数据库对象组织大致是：Cluster → Database → Schema → Table/Index。这里的 Cluster 指一个 PostgreSQL 实例管理的数据目录，不等于分布式集群。

## 常用数据类型

除了整数、精确小数、字符和时间，常用特色类型包括：

| 类型 | 场景 | 注意点 |
| --- | --- | --- |
| `uuid` | 分布式生成标识 | 索引局部性仍需考虑 |
| `jsonb` | 可查询的半结构化数据 | 不应替代所有关系建模 |
| Array | 小型同类值集合 | 复杂关系仍用关联表 |
| Range | 时间段、数值区间 | 可配合 GiST 和排斥约束 |
| `inet`/`cidr` | IP 与网段 | 优于普通字符串比较 |
| Enum | 稳定的小型枚举 | 演进和跨系统兼容需规划 |

金额使用 `numeric(p,s)` 并明确币种和舍入规则。时间通常优先 `timestamptz` 存储绝对时刻，展示时再按用户时区转换；`timestamp` 不包含时区语义。

## Schema 与搜索路径

Schema 是 Database 内的命名空间，可用于组织对象和隔离职责。对象解析受 `search_path` 影响；安全敏感 SQL、迁移和函数应避免依赖不受控的搜索路径，必要时使用完整限定名。

多租户不应只靠“每租户一个 Schema”就宣称安全，还要考虑连接身份、迁移规模、连接池和跨租户运维。

## MVCC

PostgreSQL 更新行时通常创建新版本，旧版本在不再被任何事务需要后由 VACUUM 清理。这样读写可以减少相互阻塞，但会产生 Dead Tuple 和表/索引膨胀。

长事务会阻止旧版本回收，带来：

- 表和索引膨胀。
- VACUUM 无法推进。
- 事务 ID 冻结压力。
- 复制和存储增长。

排查时同时观察事务持续时间、Dead Tuple、Autovacuum 进度、WAL 和磁盘，而不是只调大 VACUUM 参数。

## VACUUM 与 ANALYZE

- `VACUUM` 回收可复用空间并维护可见性信息，通常不会把普通表文件立即缩小到操作系统。
- `ANALYZE` 收集统计信息供优化器估算行数和选择计划。
- Autovacuum 自动执行清理和分析，但高写入表可能需要按表调整阈值。
- `VACUUM FULL` 重写表并回收文件空间，但锁和资源代价大，不能作为日常操作。

## WAL

WAL（Write-Ahead Log）先记录变更日志，再把脏页异步写入数据文件，用于崩溃恢复、归档和复制。

需要理解：

- Checkpoint 过于频繁会增加写压力，过慢会增加恢复时间和 WAL 空间。
- WAL 归档与基础备份配合可做时间点恢复。
- 复制槽能防止仍被订阅者需要的 WAL 被删除，但失联订阅者可能让磁盘持续增长。

## 索引类型

| 类型 | 适合场景 |
| --- | --- |
| B-tree | 等值、范围、排序，大多数普通字段 |
| Hash | 等值查询，使用范围较窄 |
| GIN | JSONB、Array、全文检索等包含关系 |
| GiST | 范围、几何、相似搜索等可扩展场景 |
| BRIN | 与物理顺序相关的超大表，如时间序列 |

部分索引只索引满足条件的行：

```sql
CREATE INDEX idx_orders_unpaid_created
ON orders (created_at)
WHERE status = 'unpaid';
```

表达式索引可以支持标准化查询：

```sql
CREATE INDEX idx_users_lower_email
ON users (lower(email));
```

查询表达式必须与索引定义兼容，索引是否值得建立仍取决于选择性、写入成本和执行计划。

## EXPLAIN

`EXPLAIN` 显示估算计划，`EXPLAIN ANALYZE` 会真实执行语句并返回实际时间与行数。对写语句使用后者时要放在可回滚事务或安全环境中。

重点比较：

- estimated rows 与 actual rows 是否差异巨大。
- Sequential Scan 是否符合数据比例，而不是见到就判错。
- Nested Loop、Hash Join、Merge Join 的输入规模。
- Sort 是否溢出磁盘。
- Buffer hit/read 和临时文件。
- 查询是否被锁等待或 I/O 拖慢。

估算偏差通常来自统计信息陈旧、列相关性、数据倾斜或表达式缺少统计，不应第一反应强制索引。

## 隔离级别

PostgreSQL 默认 `READ COMMITTED`，每条语句看到自己的快照。`REPEATABLE READ` 为事务提供稳定快照，但并发写仍要处理序列化冲突或约束竞争。

`SERIALIZABLE` 使用 Serializable Snapshot Isolation 检测可能破坏串行语义的依赖，并可能让事务以 Serialization Failure 失败；应用必须能重试整个事务。

PostgreSQL 的 `READ UNCOMMITTED` 按 `READ COMMITTED` 行为处理，不提供脏读。

## 锁与并发更新

普通更新会取得行级锁，DDL、索引创建和显式表锁的锁级别不同。排障时查询阻塞链，区分持锁事务和等待事务。

常用并发方式：

```sql
-- 悲观锁
SELECT * FROM jobs
WHERE status = 'pending'
FOR UPDATE SKIP LOCKED
LIMIT 10;

-- 乐观条件更新
UPDATE accounts
SET balance = balance - :amount, version = version + 1
WHERE id = :id
  AND version = :expected_version
  AND balance >= :amount;
```

`SKIP LOCKED` 适合多 Worker 竞争任务，但要设计饥饿、失败重试和任务 Lease，不能只依赖行锁代表完整队列语义。

## UPSERT 与 RETURNING

```sql
INSERT INTO user_settings (user_id, theme)
VALUES (:user_id, :theme)
ON CONFLICT (user_id)
DO UPDATE SET theme = EXCLUDED.theme
RETURNING user_id, theme;
```

`ON CONFLICT` 的冲突目标应由唯一约束保护。`RETURNING` 可在 INSERT/UPDATE/DELETE 后直接返回最终行，减少额外查询。

## JSONB 的边界

JSONB 适合变化较快、字段稀疏或需要保留原始 Payload 的局部数据。核心关联、唯一性、金额、状态和频繁过滤字段仍优先使用明确列和约束。

JSONB 索引会增加写入和存储成本；查询路径固定后，可以把热点字段提升为列、生成列或表达式索引。

## 复制与高可用

流复制把 WAL 传给 Standby，可用于高可用和只读副本。同步复制降低数据丢失窗口但增加写延迟；异步复制延迟较低但故障切换可能丢失尚未复制的事务。

高可用还需要故障检测、选主、客户端路由、防脑裂和旧主隔离。只有一个副本并不等于自动高可用。

逻辑复制按表和逻辑变更传输，适合部分数据同步和版本迁移，但 DDL、Sequence 和冲突处理要单独规划。

## 备份与恢复

- 逻辑备份适合对象级迁移和较小数据集。
- 物理基础备份配合 WAL 归档支持完整实例和时间点恢复。
- 备份成功不等于可恢复，必须定期在隔离环境演练恢复并校验数据。

## 与 MySQL 的学习差异

| 主题 | PostgreSQL 学习重点 | MySQL 学习重点 |
| --- | --- | --- |
| MVCC 清理 | VACUUM、Dead Tuple、冻结 | Undo、Read View、Purge |
| 日志 | WAL、归档、复制槽 | redo、undo、binlog |
| 索引 | B-tree、GIN、GiST、BRIN、部分/表达式 | InnoDB B+Tree、聚簇与二级索引 |
| 半结构化 | JSONB 与 GIN | JSON 与生成列/索引策略 |
| 高可用 | 流复制、逻辑复制和外部编排 | binlog 复制、组复制等 |

不要把一个数据库的锁、日志和优化经验直接套到另一个数据库。

## 验收清单

- 能解释 MVCC 为什么需要 VACUUM，以及长事务为什么危险。
- 能为 B-tree、GIN、GiST 和 BRIN 选择适用场景。
- 能使用 `EXPLAIN ANALYZE` 比较估算行数与实际行数。
- 能解释 WAL、基础备份、归档和时间点恢复的关系。
- 能设计 UPSERT、条件更新和可重试的序列化事务。
- 能说明 JSONB 什么时候适用、什么时候应恢复关系建模。
