# PostgreSQL：版本可见性、并发更新与回收

PostgreSQL 的约束、MVCC、锁与 WAL 协作保护事务事实。沿一次并发修改理解它们，再追踪查询计划、后台清理和恢复，可以连接每个阶段的实际行为。本章以 PostgreSQL 17 的核心机制为基线，通用查询见[SQL](SQL.md)。

## 进程、对象与类型

常见架构为每条客户端连接提供后端进程，共享缓冲、WAL 和后台服务协作。短连接与连接过量仍有成本，应用池或 PgBouncer 需按连接、会话与事务约定选择，不是加一层池就自动兼容所有会话能力。

Cluster 在此常指实例的数据目录与数据库集合，不等于分布式集群。其下 Database、Schema、表与索引各有边界，search_path 参与名称解析；安全敏感函数和 SQL 应避免解析到不受控对象。

| 类型 | 语义与代价 |
|---|---|
| numeric | 精确小数，需精度、币种与舍入规则 |
| timestamptz | 表达绝对时刻，按会话时区显示，不保留原始时区名称 |
| timestamp | 无时区字面日期时间，不能单凭它唯一确定瞬间 |
| uuid | 标识类型，版本和生成方式仍影响局部性 |
| jsonb / Array | 文档或小型集合，不能自动代替关系、约束与权限 |
| Range / inet / cidr | 区间与网络地址，可配相应操作和索引 |
| Enum | 有界命名值，演进与跨系统兼容另需规划 |

如果业务需要“用户当时选的时区”，还应保留 Zone 标识；timestamptz 不负责替应用记住该信息。

## MVCC 与隔离级别

更新通常形成新行版本，读取按相应快照看可见状态。READ COMMITTED 的普通查询以语句取得快照，REPEATABLE READ 维持相应事务快照，自己的写入仍可见；快照建立时机也不能简单等同于写下 BEGIN 的那一刻。

READ UNCOMMITTED 按 READ COMMITTED 行为处理。SERIALIZABLE 通过 SSI 检测相应依赖，失败事务需要从完整用例边界有界重试，而非只重跑最后一条 SQL。[隔离模型](https://www.postgresql.org/docs/17/transaction-iso.html)

同一稳定快照不自动守住跨行不变量。两名值班员各看见对方仍在岗，再分别更新自己的行，就可能形成写偏差；应采用能约束整体状态的机制，而不是只把单行写改成原子语句。

## 条件更新与 RETURNING

```sql
CREATE TABLE course_accounts (
    id bigint PRIMARY KEY,
    balance numeric(12, 2) NOT NULL CHECK (balance >= 0),
    version bigint NOT NULL DEFAULT 0
);
INSERT INTO course_accounts (id, balance) VALUES (1, 100.00);

UPDATE course_accounts
SET balance = balance - 30.00, version = version + 1
WHERE id = 1 AND balance >= 30.00 AND version = 0
RETURNING id, balance, version;
```

首次得到余额 70、版本 1。重复同一前提不再返回行，但零行仍可能是版本冲突、余额不足或记录不存在，应用需要按事先约定的错误分类区分。

INSERT ... ON CONFLICT 依赖明确的冲突目标，可组合 DO NOTHING 或更新。RETURNING 减少额外读取，不让多条操作自动成为同一事务，也不能把不同业务内容的重复键一律视为安全重试。

## 锁与任务领取

普通更新、锁定读、DDL 与显式表锁有不同模式和对象。SKIP LOCKED 适合竞争领取，但只能跳过当时冲突的行，不是公平、无饥饿且可恢复的完整队列。

下面建立一个有租期与领取版本的任务表：

```sql
CREATE TABLE course_jobs (
    id bigint PRIMARY KEY,
    status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'done', 'failed')),
    available_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lease_until timestamptz,
    claim_token bigint NOT NULL DEFAULT 0,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX course_jobs_ready
ON course_jobs (available_at, id) WHERE status = 'pending';
INSERT INTO course_jobs (id, payload) VALUES
    (1, '{"kind":"email"}'::jsonb),
    (2, '{"kind":"reconcile"}'::jsonb);

WITH picked AS (
    SELECT id FROM course_jobs
    WHERE status = 'pending' AND available_at <= statement_timestamp()
    ORDER BY available_at, id
    LIMIT 10
    FOR UPDATE SKIP LOCKED
)
UPDATE course_jobs AS j
SET status = 'running',
    lease_until = clock_timestamp() + interval '1 minute',
    claim_token = claim_token + 1
FROM picked
WHERE j.id = picked.id
RETURNING j.id, j.claim_token, j.lease_until, j.payload;
```

领取与状态更新组成一条语句，尽快提交后再执行外部工作。完成时带回 id 与 claim_token，通过条件更新确认当前领取身份；过期重领递增版本，旧工作者的完成结果不能覆盖新领取。

租期到期并不物理终止旧线程，任务还需重领、退避、失败终态和业务幂等。若远端动作不可回滚，其授权或幂等也要在远端成立，不能只凭本表 token 宣称外部效果一定一次。

## 锁等待与连接预算

从等待者追到阻塞者，再关联事务与应用，而非只数锁的数量：

```sql
SELECT pid, usename, state, wait_event_type, wait_event,
       clock_timestamp() - xact_start AS transaction_age,
       pg_blocking_pids(pid) AS blockers
FROM pg_stat_activity
WHERE datname = current_database()
  AND pid <> pg_backend_pid()
  AND (wait_event_type = 'Lock' OR state LIKE 'idle in transaction%');
```

在短事务或自动提交中采样，列可见性受角色权限影响；持续观测并追溯阻塞链，区分长事务、DDL、正常竞争和异常重试。statement_timeout 限制相应语句，lock_timeout 只约束等待锁；客户端放弃等待不证明服务端已停止或事务已回滚。

序列化失败和死锁通常需要在清理后的事务边界重试，连接在提交期间断开则可能已有提交事实，应先查业务键或提交结果。自动重试前必须排除重复外部效果。

连接池按实例数、总连接预算、借用时长和排队目标配置。把池从 20 增到 200 可能只让更多线程等数据库，持有连接期间的 HTTP 等待也会直接扩大需求。

## VACUUM、ANALYZE 与版本保留

不再被相应可见性需求保留的旧版本可被清理，普通 VACUUM 主要使空间可复用、维护可见性与冻结等信息，不普遍立即缩小操作系统文件。ANALYZE 则收集统计，两者不是同一动作。

持有旧快照、idle in transaction、复制相关保留等可能推迟清理，但不能仅凭“连接时间长”判断所有回收都无法推进。应观察相应 xmin、旧事务、Dead Tuple、Autovacuum 与磁盘证据，区分具体保留者。

VACUUM FULL 重写并获取较强锁，不是日常无成本清理。HOT、页面修剪和索引维护又有各自条件，不能把文件增长都归结成“VACUUM 没跑”。

## 索引类型与表达式

B-tree 常服务等值、范围和排序，Hash 偏等值，GIN 服务相应包含/倒排查询，GiST 提供区间、空间等可扩展搜索，BRIN 利用块范围与物理相关性。

部分索引如上面的 pending 索引只保存匹配行。规划器需证明查询条件适用，参数化条件也可能影响这项证明；“建了部分索引”不保证每个近似写法都用它。

表达式索引可支持 lower(email) 等查询，但表达式、类型与排序规则要兼容。jsonb 的路径、操作符与 GIN 策略不同，索引不能把任意 JSON 查询都变成廉价操作。

## EXPLAIN 与实际执行

EXPLAIN 展示估算，EXPLAIN (ANALYZE, BUFFERS) 实际执行支持语句并给出相应观测。比较行数、循环、缓冲、排序和等待，Sequential Scan 对大比例数据可能合理，不应见到就判错。

对写语句，即便包在事务后回滚，也不能普遍撤销序列取值或任意外部函数副作用；执行前应先界定实际环境和动作范围。统计过期、倾斜与列相关性导致的估算偏差，也不能靠一律强制索引修复。

## WAL、Checkpoint 与保留

WAL 先满足相应恢复顺序，数据页再按策略写出。同步策略、Checkpoint 与存储决定提交成本和恢复工作；频繁 Checkpoint 可能增加写压力，过长恢复距离又会增加回放需求。

复制槽保留订阅者可能需要的日志与相应清理边界。失联消费者会增加保留压力，限制设置可以改变允许保留的范围，也可能导致原进度不可继续，需重新建立同步。磁盘容量、消费进度与恢复窗口要一起观测。

## 复制、读己之写与故障切换

物理流复制基于 WAL，逻辑复制面向相应表与变更，DDL、Sequence 和冲突有独立限制。同步配置还区分确认到接收、落盘或回放，不能直接将“有同步副本”理解为任意副本此刻均可读到最新值。

切换需要故障检测、选主、路由与旧主隔离。复制不替代备份，误删也可能被同步；逻辑导出、物理基线和归档 WAL 各有恢复范围，并需实测目标时间与数据校验。

## 迁移与 Schema 演进

增加任务的稳定请求键，可按 Expand、Migrate、Contract 分开进行：先增加兼容字段，读者兼容缺失；再让所有新写入者填入新键，回填历史；验证后才建立最终约束并移除旧兼容路径。

```sql
ALTER TABLE course_jobs ADD COLUMN request_id text;

WITH batch AS (
    SELECT id FROM course_jobs
    WHERE request_id IS NULL
    ORDER BY id
    LIMIT 1000
    FOR UPDATE SKIP LOCKED
)
UPDATE course_jobs AS j
SET request_id = 'legacy:' || j.id::text
FROM batch
WHERE j.id = batch.id AND j.request_id IS NULL;
```

示例约定 legacy: 前缀专用于历史映射。条件回填可避免覆盖已存在的新值，分批减小锁与 WAL；跳过锁的某批返回零行，并不证明全部历史都完成，仍需整体校验。仅写旧格式的入口也必须在收紧约束前退出。

```sql
CREATE UNIQUE INDEX CONCURRENTLY course_jobs_request_uq
ON course_jobs (request_id);
```

并发建索引允许更多在线访问，但有等待、额外扫描与失败后的无效索引状态，需要独立于普通事务块执行。唯一索引默认允许多个 NULL，若业务要求必填，还要验证并设置相应非空约束。[并发索引构建](https://www.postgresql.org/docs/17/sql-createindex.html)

ADD COLUMN、默认值、类型转换、约束验证所需锁和重写条件不同。常量默认值可能使用元数据优化，也仍需取得相应锁；每条 DDL 应按目标版本与代表数据验证，不把整个迁移包成一个长事务。[ALTER TABLE](https://www.postgresql.org/docs/17/sql-altertable.html)

空库构建、旧版升级和带倾斜数据的演练覆盖不同风险。保存数据库/应用版本、迁移编号、锁等待、WAL 增量与恢复结果；应用回滚可依兼容窗口完成，不代表被删的数据或不可逆转换也可自动撤销。

## 备份恢复的执行范围

逻辑恢复需校验对象、约束、序列、扩展与权限；物理基线加归档 WAL 需保证日志链、目标时间线和停止位置。恢复到误删之前与恢复到最新状态是两种不同目标，校验应使用已知订单、幂等键与业务总额。

切换候选的日志位置、旧主隔离、提升、路由、连接缓存和应用验证都占时间。若文件恢复 8 分钟、回放 11 分钟、校验 6 分钟、路由验证 3 分钟，这条流程已用 28 分钟；30 分钟的 RTO 目标只剩 2 分钟余量，并非文件复制结束就已恢复服务。

RPO 应按实际可恢复的业务位置计算，而非只看最近备份文件时间。扩展不兼容、WAL 缺段、容量不足和密钥缺失都应进入演练，恢复后旧主也不能未经处理直接重新接受写入。

## 观测与容量模型

在稳定负载中，入库用例每秒 400 次，平均每用例累计占用连接 0.05 秒，则平均占用约 20 个连接。若这个时长已覆盖同一用例的全部 SQL，就不应再乘一次 SQL 条数；突发、方差与等待目标仍需额外验证。

容量按实际存储范围相加：数据、索引、WAL 保留、备份以及维护/迁移临时空间。副本和备份可能在不同磁盘或节点，先画清归属再算总量，避免用无单位的连乘公式。

将请求时延拆到排队、借连接、执行、传输与映射，并关联锁、I/O、WAL、Autovacuum、复制与恢复。告警应连接影响、责任与动作，高基数订单/用户标识留在受控日志或 Trace，而非无限扩展普通指标标签。

慢查询、索引构建、备份和清理会争用资源，维护需按热表和容量安排。优化结果用相同负载与数据版本比较吞吐、尾延迟、错误和等待，才能确认成本没有被转移到另一个阶段。

## 与 MySQL 的机制差异

InnoDB 围绕聚簇组织、undo、Read View 与 purge 理解版本；PostgreSQL 围绕堆元组、快照、VACUUM、冻结与索引访问理解。WAL 与 MySQL redo/binlog 的职责也不能按名称一一替换。

框架可以统一 Repository 接口，不能统一底层隔离、DDL、锁与精度行为。迁移与容量验证应在目标版本执行，既核对数据结果，也核对等待、清理和失败恢复。
