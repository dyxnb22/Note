# MySQL

# SQL 基础

<details>
<summary>SQL 和 NoSQL 有什么区别？</summary>
	SQL 通常指关系型数据库，数据以二维表形式组织，表之间可以通过主键、外键、索引和 JOIN 建立关系，强调结构化数据、事务一致性和 SQL 查询能力，典型产品有 MySQL、PostgreSQL、Oracle。

	NoSQL 指非关系型数据库，数据模型不局限于二维表，常见形式包括 KV、文档、列族、图等，典型产品有 Redis、MongoDB、Cassandra。它通常更强调高并发、水平扩展和灵活的数据结构，但不同产品的能力差异很大，不能把某个产品的特性当成全部 NoSQL 的共性。
</details>

<details>
<summary>数据库三大范式是什么？</summary>
	第一范式（1NF）：字段具有原子性，每一列都不可再拆分。例如不要把多个手机号塞进同一个字段。
	第二范式（2NF）：在满足 1NF 的基础上，非主属性必须完全依赖于候选键，不能只依赖联合主键中的一部分，主要用于消除部分依赖。
	第三范式（3NF）：在满足 2NF 的基础上，非主属性不能依赖其他非主属性，必须直接依赖主键，主要用于消除传递依赖。
</details>

<details>
<summary>MySQL 怎么做连表查询？</summary>
	常见 JOIN：

	<table header-row="true" header-column="false">
<tr>
<td>类型</td>
<td>含义</td>
</tr>
<tr>
<td>INNER JOIN</td>
<td>内连接，只返回两表都匹配的数据</td>
</tr>
<tr>
<td>LEFT JOIN</td>
<td>左外连接，保留左表全部数据，右表不匹配则为 NULL</td>
</tr>
<tr>
<td>RIGHT JOIN</td>
<td>右外连接，保留右表全部数据，左表不匹配则为 NULL</td>
</tr>
<tr>
<td>FULL JOIN</td>
<td>全外连接，MySQL 不直接支持，可用 LEFT JOIN UNION RIGHT JOIN 模拟</td>
</tr>
	</table>
</details>

<details>
<summary>MySQL 如何避免重复插入数据？</summary>
	常用方式：
	- 建唯一索引或唯一约束，从数据库层保证唯一性。
	- 使用 `INSERT IGNORE`，重复键冲突时忽略该行，不报错。
	- 使用 `INSERT ... ON DUPLICATE KEY UPDATE`，重复时改为更新。
	- 业务侧先查再插不可靠，高并发下仍可能并发插入，最终要依赖数据库唯一约束兜底。
</details>

<details>
<summary>CHAR 和 VARCHAR 有什么区别？</summary>
	`CHAR(n)` 是定长字符串，长度固定，适合长度稳定的数据，如性别、MD5、身份证固定长度编码等。
	`VARCHAR(n)` 是变长字符串，会额外记录长度信息，更适合长度波动明显的字段，如用户名、标题、地址。

	一般情况下，字符串长度不固定优先使用 `VARCHAR`。
</details>

<details>
<summary>INT(11) 中的 11 表示什么？</summary>
	在 MySQL 里，`INT(11)` 的 11 不是存储字节数，也不是能存 11 位数字，它只是历史上的显示宽度概念。真正的 `INT` 始终占 4 字节，取值范围由类型本身决定。
</details>

<details>
<summary>TEXT 和 VARCHAR 有什么区别？</summary>
	两者都能存字符串，但有几个差异：
	- `VARCHAR` 更适合普通业务字段。
	- `TEXT` 适合较长文本，如文章内容、日志详情。
	- `TEXT` 一般不能直接设置默认值。
	- 在索引、内存临时表、排序等场景上，`TEXT` 的限制更多。
</details>

<details>
<summary>IN 和 EXISTS 有什么区别？</summary>
	`IN` 更适合子查询结果集较小的情况；`EXISTS` 更适合外层表大、内层子查询能快速命中的情况。

	现代 MySQL 优化器会做一定重写，但面试回答时可以理解为：
	- `IN` 倾向于先处理子查询结果。
	- `EXISTS` 倾向于外层循环、内层命中即返回。
</details>

<details>
<summary>SQL 的逻辑执行顺序是什么？</summary>
	典型顺序是：
	`FROM -> JOIN -> ON -> WHERE -> GROUP BY -> HAVING -> SELECT -> DISTINCT -> ORDER BY -> LIMIT`

	这也是为什么 `WHERE` 里不能直接用 `SELECT` 别名，而 `ORDER BY` 往往可以。
</details>

---

# 执行流程与存储引擎

<details>
<summary>一条 SQL 请求在 MySQL 中如何执行？</summary>
	以查询为例，整体流程：
	连接器建立连接、认证和权限校验；解析器做词法和语法分析；预处理器检查表和字段；优化器选择索引和执行计划；执行器按计划调用存储引擎；存储引擎真正读写数据页、索引和日志。
</details>

<details>
<summary>MySQL 常见存储引擎有哪些？</summary>
	<table header-row="true" header-column="false">
<tr>
<td>引擎</td>
<td>特点</td>
<td>适用场景</td>
</tr>
<tr>
<td>InnoDB</td>
<td>默认引擎，支持事务、行锁、外键、崩溃恢复、MVCC</td>
<td>绝大多数 OLTP 场景</td>
</tr>
<tr>
<td>MyISAM</td>
<td>不支持事务和行锁，表锁，读性能较好但崩溃恢复弱</td>
<td>历史遗留或只读场景</td>
</tr>
<tr>
<td>MEMORY</td>
<td>数据在内存中，重启丢失</td>
<td>临时数据、缓存类场景</td>
</tr>
	</table>
</details>

<details>
<summary>为什么 InnoDB 会成为默认引擎？</summary>
	因为它支持事务、行级锁、崩溃恢复、MVCC、外键，综合能力更强，适合大多数业务系统。MyISAM 读快但不支持事务和行锁，已经不适合作为现代业务数据库默认选择。
</details>

---

# 索引

<details>
<summary>索引有哪些分类？</summary>
	常见分类：
	- 按数据结构：B+Tree、Hash、Full-text。
	- 按物理存储：聚簇索引、二级索引。
	- 按字段特性：主键索引、唯一索引、普通索引、前缀索引。
	- 按字段数量：单列索引、联合索引。
</details>

<details>
<summary>为什么 InnoDB 选择 B+Tree 作为默认索引结构？</summary>
	B+Tree 适合磁盘/页式存储，树高低，查询稳定，支持范围查询和排序。相比二叉树层级更低；相比红黑树磁盘 IO 更少；相比 Hash 索引，B+Tree 不仅支持等值查询，还支持范围、排序和最左匹配等场景。
</details>

<details>
<summary>什么是聚簇索引和二级索引？</summary>
	在 InnoDB 中，主键索引通常就是聚簇索引，叶子节点直接存放整行数据。
	普通索引、唯一索引等大多是二级索引，叶子节点存的是主键值，再通过主键回表取整行数据。
</details>

<details>
<summary>为什么建议主键尽量短、稳定、递增？</summary>
	因为 InnoDB 的数据页按聚簇索引组织：
	- 主键越短，二级索引叶子节点里保存的主键值也越小，索引更省空间。
	- 主键稳定，避免主键更新导致整行移动和二级索引维护成本增加。
	- 递增主键能减少页分裂、页移动，插入更友好。
</details>

<details>
<summary>联合索引为什么要遵循最左匹配？</summary>
	联合索引底层按最左字段优先排序，再依次按后续字段排序。只有查询条件从最左列开始连续使用时，才能充分利用索引有序性。

	例如索引 `(a, b, c)`：
	- `where a = ?` 可以用
	- `where a = ? and b = ?` 可以用
	- `where a = ? and c = ?` 只能部分利用
	- `where b = ?` 通常不能直接利用这个联合索引
</details>

<details>
<summary>什么是覆盖索引？</summary>
	如果查询所需字段全部都能从索引里拿到，就不需要回表读取聚簇索引数据页，这就是覆盖索引。它能减少 IO，通常性能更好。
</details>

<details>
<summary>什么情况会导致索引失效？</summary>
	常见情况：
	- 左模糊或全模糊。
	- 对索引列使用函数或表达式。
	- 隐式类型转换。
	- 联合索引不满足最左匹配。
	- `OR` 一侧无索引。
	- 低选择性字段或返回数据量过大时，优化器主动放弃索引。
</details>

---

# 事务与 MVCC

<details>
<summary>事务的 ACID 特性是什么？InnoDB 怎么实现？</summary>
	原子性依赖 undo log；一致性由原子性、隔离性、持久性共同保证；隔离性依赖锁和 MVCC；持久性依赖 redo log 和 WAL。
</details>

<details>
<summary>事务隔离级别有哪些？</summary>
	读未提交、读已提交、可重复读、串行化。MySQL InnoDB 默认是可重复读。
</details>

<details>
<summary>脏读、不可重复读、幻读分别是什么？</summary>
	- 脏读：读到别的事务尚未提交的数据。
	- 不可重复读：同一事务中多次读取同一行，结果不一致。
	- 幻读：同一事务中按条件查询，多次读取到的“记录数量/范围”发生变化。
</details>

<details>
<summary>什么是 MVCC？</summary>
	MVCC 是多版本并发控制。它通过隐藏字段、undo log、Read View 等机制，让读操作尽量不加锁就能看到合适版本的数据，从而提升并发性能。
</details>

<details>
<summary>为什么 InnoDB 可重复读下还能较好解决幻读？</summary>
	普通快照读依靠 MVCC；当前读（如 `select ... for update`、`update`、`delete`）依靠 next-key lock（记录锁 + 间隙锁）限制范围内插入，从而降低幻读问题。
</details>

<details>
<summary>为什么不建议大事务？</summary>
	大事务会带来：
	- 锁持有时间长，影响并发。
	- undo log / redo log 压力大。
	- 回滚成本高。
	- 主从复制延迟变大。
	- 崩溃恢复时间更长。
</details>

---

# 锁

<details>
<summary>InnoDB 常见锁有哪些？</summary>
	- 共享锁（S）：允许读，不允许别人改。
	- 排他锁（X）：允许改，不允许别人读写当前读相关数据。
	- 行锁：锁具体行。
	- 表锁：锁整张表。
	- 间隙锁：锁索引记录之间的间隙。
	- Next-Key Lock：记录锁 + 间隙锁。
</details>

<details>
<summary>为什么说 InnoDB 是“行锁”，但本质上锁的是索引？</summary>
	InnoDB 行锁是基于索引项加锁实现的。如果查询没走索引，可能退化为扫描大量记录，甚至产生更大范围的锁影响。
</details>

<details>
<summary>什么情况下容易发生死锁？</summary>
	两个事务以不同顺序加锁同一批资源时容易发生死锁。例如事务 A 先锁 1 再锁 2，事务 B 先锁 2 再锁 1。

	常见优化：
	- 固定加锁顺序。
	- 缩短事务时间。
	- 尽量走索引，减少锁范围。
	- 把大事务拆小。
</details>

---

# 日志系统

<details>
<summary>redo log、undo log、binlog 分别是什么？</summary>
	- `redo log`：InnoDB 引擎层日志，记录页修改后的物理变化，用于崩溃恢复，保证持久性。
	- `undo log`：记录修改前的逻辑信息，用于回滚和 MVCC。
	- `binlog`：Server 层归档日志，记录逻辑操作，用于主从复制和数据恢复。
</details>

<details>
<summary>为什么既要 redo log 又要 binlog？</summary>
	因为两者职责不同：
	- redo log 面向崩溃恢复，是 InnoDB 私有的物理日志。
	- binlog 面向复制与归档，是 MySQL Server 层的逻辑日志。

	一个偏“恢复本机”，一个偏“同步和审计”。
</details>

<details>
<summary>什么是两阶段提交？</summary>
	为了避免 redo log 和 binlog 状态不一致，MySQL 提交事务时会做两阶段提交：先写 redo log prepare，再写 binlog，最后把 redo log 标记为 commit。这样崩溃恢复时可以根据日志状态判断事务是否真正提交成功。
</details>

---

# 性能调优

<details>
<summary>EXPLAIN 有什么作用？</summary>
	`EXPLAIN` 用于查看 SQL 执行计划，重点关注 `type`、`key`、`rows`、`Extra`，判断是否走索引、扫描行数是否过大、是否出现 filesort 或 temporary。
</details>

<details>
<summary>SQL 调优一般从哪些方面入手？</summary>
	常见思路：
	- 看执行计划，判断是否走索引。
	- 补充或调整索引，尤其是联合索引顺序。
	- 尽量减少 `select *`。
	- 避免在索引列上做函数、计算和隐式转换。
	- 拆分复杂 SQL 或减少无意义连表。
	- 控制分页深度，避免深分页。
</details>

<details>
<summary>为什么深分页慢？怎么优化？</summary>
	`limit 100000, 20` 这类深分页需要先扫描并丢弃前面大量记录，代价高。

	优化方式：
	- 通过“基于上次最大 ID/游标”的方式分页。
	- 先用覆盖索引查出主键，再回表取详情。
	- 尽量减少需要排序和大范围扫描的场景。
</details>

---

# 主从复制与分库分表

<details>
<summary>MySQL 主从复制大致流程是什么？</summary>
	主库写 binlog，从库 IO 线程拉取 binlog 写入 relay log，从库 SQL 线程（或多线程回放）重放 relay log，从而同步数据。
</details>

<details>
<summary>为什么会出现主从延迟？</summary>
	常见原因：
	- 主库写入压力大。
	- 从库回放能力不足。
	- 大事务。
	- 从库还承担查询压力。
	- 网络抖动。
</details>

<details>
<summary>什么时候需要分库分表？</summary>
	当单库单表在容量、并发、IO、维护窗口等方面接近瓶颈，并且通过索引优化、冷热分离、读写分离仍无法满足需求时，才考虑分库分表。
</details>

---

# 高频简答

<details>
<summary>为什么不用 UUID 作为主键？</summary>
	UUID 无序且长，作为聚簇索引主键会导致页分裂、二级索引膨胀、插入局部性差，通常不如自增或趋势递增主键友好。
</details>

<details>
<summary>数据库和缓存双写时，为什么建议“先更新数据库，再删除缓存”？</summary>
	因为直接“更新数据库 + 更新缓存”更容易出现并发覆盖问题。常见更稳妥模式是 Cache Aside：先改库，再删缓存，让后续读请求重新回填缓存，保证最终一致。
</details>

<details>
<summary>面试里怎么简洁解释 MySQL 的核心能力？</summary>
	MySQL 本质上是一个关系型数据库系统，InnoDB 通过 B+Tree 索引、事务、MVCC、锁机制和日志系统支撑高并发读写。实际优化重点通常围绕索引设计、SQL 执行计划、事务粒度、锁冲突、日志机制和主从复制展开。
</details>
