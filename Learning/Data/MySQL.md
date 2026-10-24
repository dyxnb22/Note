# MySQL：索引、事务与恢复的执行链

本章以 MySQL 8.4、InnoDB 为基线，沿“一次写入如何受约束、如何找到记录、如何并发修改、如何确认与恢复”展开。通用查询和共用的 users/orders 示例见[SQL](SQL.md)，旧版引擎与文件布局只在版本差异中解释。

## 字段语义先于存储优化

VARCHAR(n) 的 n 是字符数，字节数还受字符集影响。CHAR 有定长语义，但实际占用、尾空格处理与比较仍受引擎、字符集和排序规则影响，不宜简单按 n 字节估算。

唯一业务键还需明确大小写、重音与规范化规则。某排序规则认为相等的两个字符串，可能在唯一约束中冲突；显示不同并不能证明数据库认为不同。

| 数据 | 表达与边界 |
|---|---|
| 金额 | DECIMAL(p,s) 为精确十进制，仍需币种、舍入、范围规则 |
| 测量近似值 | FLOAT/DOUBLE 使用二进制近似，不按十进制金额等值规则比较 |
| 整数 | INT 为 4 字节，旧式 INT(n) 的 n 是显示宽度，不改变取值范围；显示宽度与 ZEROFILL 属旧接口边界 |
| 文本 | TINYTEXT/TEXT/MEDIUMTEXT/LONGTEXT 上限分别为 2⁸−1、2¹⁶−1、2²⁴−1、2³²−1 字节，不是同等数量字符 |
| 地址 | IPv4 可用无符号整数，IPv4/IPv6 可用 VARBINARY(16) 配合 INET6_ATON/INET6_NTOA |
| 时间 | DATETIME 保存字面日期时间；TIMESTAMP 按会话时区转换时间点，范围与前者不同 |

长度上限不代表一次请求就可安全装入最大值，还受行布局、协议、内存与应用约束影响。跨时区要明确原始事件时刻与本地日历含义，不能只给列起名 created_at。

## 唯一约束与重复请求

应用先查再插有并发窗口，业务键需要数据库唯一约束。重复键既可能是安全重试，也可能是同一键携带了不同业务内容，应比较必要事实再返回结果。

INSERT IGNORE 不只可能忽略重复键，也可能把其他可忽略错误转为告警或产生转换，不能把“没抛异常”当成正确落库。ON DUPLICATE KEY UPDATE 则可能由任一相关唯一键冲突触发，需要明确更新语义与影响行数。

```sql
CREATE TABLE payment_events (
    id BIGINT NOT NULL PRIMARY KEY,
    business_id VARCHAR(64) NOT NULL UNIQUE,
    payload_hash CHAR(64) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL CHECK (amount >= 0)
);
```

这里只表达唯一性和范围，不替代支付状态机或外部执行结果。DECIMAL、唯一键、CHECK 与应用事务各保护不同条件。

## Server、引擎与文件布局

```text
连接与认证 → 解析、绑定和权限检查 → 优化计划
→ 执行器调用存储引擎 → 页、索引、锁和相应日志
```

MySQL 8 已移除旧查询缓存，不能把它继续画成当前请求必经步骤。Server 管理 SQL 与 binlog 等能力，InnoDB 管理自身的记录、索引、事务、MVCC 与恢复。

InnoDB 支持事务、外键和记录级并发；MyISAM 缺少这些事务保证，保存的表行数也不能用来推断 InnoDB 的 COUNT(*) 成本；MEMORY 的数据在重启后丢失。选引擎先看所需保证，不能泛称“读多就用 MyISAM”。

MySQL 8 用事务型数据字典取代旧 .frm。独立表空间常见 .ibd，系统、通用与 undo 表空间各有职责；现代默认 undo 与字典布局不能一律套用早期 ibdata1 说明。文件名不能说明备份是否完整一致，复制几个数据文件不自动得到一致备份。

检查实际环境与对象定义时，可用以下管理语句，而非仅从应用实体推测表结构：

```sql
SELECT VERSION();
SHOW ENGINES;
SHOW DATABASES;
SHOW TABLES;
DESCRIBE orders;
SHOW CREATE TABLE orders;
SHOW INDEX FROM orders;
```

## 聚簇组织与索引访问

### 从二级索引回到记录

InnoDB 聚簇索引叶层保存行数据；若没有显式主键，会选择合适的非空唯一键，仍没有时使用内部行标识。二级索引保存其索引键及聚簇键，因此主键长度会扩散到多个索引。

回表是经二级键再访问聚簇记录。覆盖表示所需列已由索引提供，能减少这类读取；但二级页上的删除标记或版本可见性仍可能要求访问聚簇记录，不能把覆盖说成所有情况下都零回表。[InnoDB 版本与二级索引](https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html)

B+Tree 的高扇出减少层数，有序叶层支持范围访问；页内还可借助页目录定位记录分组。树层数不直接等于每次物理 I/O 次数，热点索引页可能已缓存。

### 主键选择与写入局部性

短且稳定的键减少空间和更新成本。递增键通常便于尾部写入，也可能集中竞争；随机 UUID、带时间顺序的 UUID 与不同二进制编码有不同局部性，不能把所有 UUID 都写成随机字符串。

自增值也不承诺连续无缺口，更不能单独代表业务发生或提交的全局顺序。标识方案需同时考虑生成吞吐、跨节点、长度与排序含义。

## 用一条查询设计联合索引

在 SQL 章的 orders 上考虑“某用户的已支付订单，按时间继续读取”：

```sql
CREATE INDEX idx_orders_user_status_created
ON orders (user_id, status, created_at);

EXPLAIN
SELECT id, created_at
FROM orders
WHERE user_id = 1 AND status = 'paid'
  AND created_at >= '2026-07-01'
ORDER BY created_at, id
LIMIT 20;
```

前两列等值收窄到连续范围，created_at 继续限定扫描；二级索引中的主键可提供 id。示例表很小时，优化器仍可能选其他路径，目的在于分析结构，而非承诺固定执行计划。

### 最左前缀、范围与下推

(A,B,C) 按字典序排列。缺少 A 或跳过 B 后，后续条件通常不能直接组成同样紧的连续定位范围；这不等于优化器绝不会选它，覆盖扫描、Skip Scan 等还有各自条件。

范围列之后的字段仍可能用于过滤，ICP 可以在索引层判断部分条件以减少回表。定位范围、过滤、排序和覆盖是不同收益，不能都混称“索引是否失效”。

低基数字段也非一律无用：大多数订单已完成、待处理很少时，按待处理状态和时间组织的联合索引仍可能很有效。关键是具体值的分布、查询形状和写成本。

### 表达式与扫描量

DATE(created_at)=某日 通常不利于普通列索引的直接范围定位，半开时间范围常更明确；表达式/生成列索引、隐式转换、排序规则也会改变计划。LIKE 的模式、OR 两侧条件和统计信息同样需具体分析。

常用函数包括 COUNT/SUM/AVG、CONCAT/SUBSTRING、LENGTH/CHAR_LENGTH、NOW/DATE_ADD 和 CASE/COALESCE。LENGTH 计算字节，CHAR_LENGTH 计算字符，语义正确与访问路径应一起核对。

## 事务、Read View 与并发修改

InnoDB 的普通一致性读通过 Read View 判断版本可见性：本事务修改、视图建立前已提交版本，与当时活跃或后来开始的其他事务版本分别处理；不可见时沿 undo 找历史版本。

| 隔离级别 | 主要读取语义 |
|---|---|
| READ UNCOMMITTED | 允许读到未提交修改 |
| READ COMMITTED | 普通一致性读按语句取得相应新视图 |
| REPEATABLE READ | 通常首个一致性读建立视图，后续复用；本事务写入仍可见 |
| SERIALIZABLE | 提供可串行化语义，实际加锁还受 autocommit 等上下文影响 |

稳定快照不是“本事务内所有查询永远返回相同行”：自己的修改、锁定读与更新会改变观察。RR 的快照读与基于锁的当前读也不是同一条版本路径。[InnoDB 隔离级别](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html)

### 行锁不代替业务并发协议

若 A 读到余额 100，B 扣 10 并提交，A 再把旧值减 20 的结果 80 写回，就可能覆盖 B 的事实。写操作有锁，并不自动修复应用中已经算好的旧结果。

```sql
UPDATE accounts
SET balance = balance - :amount, version = version + 1
WHERE id = :id AND balance >= :amount
  AND version = :expected_version;
```

这是命名参数框架中的示意，需要检查影响行数并在冲突后重读或返回冲突。跨行不变量还可能出现写偏差，不能仅凭 RR 或单行原子更新就认为整个用例已串行化。

普通 InnoDB UPDATE 的事务性修改可由相应回滚机制撤销，但错误的回滚范围不同：死锁可能回滚整个事务，锁等待超时默认通常只撤销语句；重试前需确认事务已回到干净边界。

## 锁的对象与实际范围

记录锁落在索引记录上；Gap Lock 阻止相应间隙插入，Next-Key 是记录与前间隙的组合。Gap Lock 的兼容规则不同于普通记录 S/X 锁，不能把一张读写锁表套给所有锁。

唯一键精确查找、范围扫描、未找到的键、隔离级别和访问路径都会改变加锁范围。缺少合适索引可能扫描并锁定更多记录，不代表 InnoDB 必然自动升级成一把表锁。

MDL 保护对象元数据，长事务可能使 DDL 等待；意向锁协调表与记录级访问，FLUSH TABLES WITH READ LOCK 又是全局备份窗口机制。应沿阻塞链区分资源，而非看到“锁等待”就增大超时。

SERIALIZABLE 表示结果等价于某个串行顺序，并不是所有事务物理上依次运行。InnoDB 在关闭 autocommit 的相应情形将普通 SELECT 转为共享锁定读，独立自动提交的只读 SELECT 可以有不同路径。

## Redo、Undo 与 Binlog

| 日志 | 主要职责 |
|---|---|
| redo | 记录可恢复的页修改，参与崩溃恢复 |
| undo | 回滚与历史版本读取 |
| binlog | Server 层变更事件，支持复制与恢复回放 |
| relay log | 副本收到的复制事件，供应用线程回放 |

binlog 的 STATEMENT、ROW、MIXED 记录方式不同。ROW 降低某些语句重放歧义，但仍需主键、Schema 和消费语义，不能称为绝对安全。

### WAL 约束的是顺序

```text
执行修改 → undo/redo 与 Buffer Pool 脏页
提交协调 → 相应 redo/binlog 状态 → 按同步策略确认
后台刷页 → 必须遵守对应恢复日志先持久化的要求
```

脏页并非一定等到提交后才刷盘，未提交修改也可在日志保护下写出；崩溃时再据提交与版本状态恢复。大事务会增加日志、旧版本、持锁和回放成本，不能只把压力归到最后一次 commit。[Redo 与恢复](https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html)

innodb_flush_log_at_trx_commit=1 让提交满足相应 redo 同步要求；2 通常每次提交写系统缓存、周期同步；0 通常把写与同步都交给周期任务。周期不是严格准点保证，binlog 还受 sync_binlog 等策略约束，redo 配好不等于全部复制日志也已持久化。

启用 binlog 的常见 InnoDB 提交通过内部协调使 redo 准备、binlog 提交事实与引擎提交一致；恢复会结合完整提交记录处理准备态事务。这与跨多个业务数据库的分布式 2PC 范围不同。

### Doublewrite 与 Checkpoint

InnoDB 默认页大小为 16 KiB，可在相应初始化条件下采用其他大小。若一次页写只完成一部分，redo 未必能直接作用于坏页；Doublewrite 先保留完整页副本，供恢复修复，再重放相应日志。

Checkpoint 表示恢复与日志复用的进度，受脏页刷新等条件约束。旧 Read View 还可能阻碍 undo 清理；大事务、缓存与日志压力需放到同一时间窗口观察。

## 备份与时间点恢复

```bash
mysqldump --single-transaction --source-data=2 -u backup -p app_db > app_db.sql
mysql -u restore -p app_db < app_db.sql
```

这是逻辑导出/导入示意，账户需有相应权限。single-transaction 的一致性视图主要针对事务表，并发 DDL、非事务表与记录复制坐标所需锁仍要按实际版本处理。

恢复应从备份记录的一致性 binlog/GTID 坐标继续回放，不能机械选择“文件备份结束时间”。在目标事务边界停止后校验数据；任意跳过误操作再照常回放后续事件，可能破坏后续依赖，并非普遍安全的恢复算法。

物理备份工具如 Percona XtraBackup 复制页和必要日志，通常还需 prepare 与版本兼容；物理增量是相对基线的页变更，binlog 回放是继续推进逻辑历史。两者需明确基线、顺序与恢复目标，并实际演练。

## 执行计划与慢查询证据

EXPLAIN 展示计划，EXPLAIN ANALYZE 会实际执行相应支持语句。看估算与实际行数、循环、读取、排序、回表及锁等待，不按 const/ref/range/index/ALL 排一个永远成立的快慢榜。

Using filesort 不等于一定写磁盘，Using temporary 也不自动表示计划错误；大范围分析时扫描可能比大量随机回表更合适。ANALYZE TABLE 更新统计，USE/IGNORE/FORCE INDEX 等提示限制候选、排除索引或加强相应偏好，最终仍需同负载验证。

批量 INSERT 和 LOAD DATA 可减少调用开销，但批次需限制锁、日志与内存，LOCAL 文件导入还涉及客户端与服务端许可及文件来源。深 offset 常要访问并跳过大量候选，可以优化成覆盖索引加延迟关联或稳定 keyset；不是“深分页必定没有索引”。

视图保存查询定义，可限制输出与权限而不保证物化；存储过程靠近数据执行多步逻辑，触发器引入隐式动作。三者都需要明确版本、事务和运维归属，不替代执行计划或业务职责。

## 复制确认与读写路由

典型复制由源端 binlog 经接收线程写 relay log，再由副本应用线程执行；并行回放也受依赖与资源约束。默认异步确认不能证明某副本已可读到本次提交。

半同步在相应协议中等待副本接收并持久化 relay log，不等于已经回放，超时等情况还可能转入异步。它改变确认窗口，并不会自动加速日志传输或消除副本读取延迟。[半同步复制](https://dev.mysql.com/doc/refman/8.4/en/replication-semisync.html)

需要读己之写时，可走正确的新主、等待已知提交位点或采用明确版本路由；固定等 N 秒只是一种延迟假设。监测位点、回放错误与业务对账，不能单看一个延迟数字推断数据正确。

## 分区、分片与容量边界

原生表分区、同实例拆表和跨实例分片解决不同问题。垂直拆分分离职责或大字段，水平分片按键拆同构数据；总数据变少并不意味着某条跨分片查询自然变便宜。

引入分片之前先确认瓶颈确在数据与写入分布，而非错误 SQL、连接等待或热点。跨实例之后，唯一性、关联、事务、全局排序与扩容迁移都需新协议；备份与故障恢复也要覆盖整个数据布局。
