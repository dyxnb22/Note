# SQL

SQL（Structured Query Language）是面向关系型数据库的声明式语言：描述“需要什么结果”，由数据库优化器决定具体访问路径。

本文聚焦通用 SQL、关系模型和查询思维。MySQL 的存储引擎、索引实现、事务、锁、日志和方言差异见 [MySQL](MySQL.md)。示例以 MySQL 8.0 可执行语法为主；用于其他数据库时，应确认分页、日期函数、自增列和 UPSERT 等方言差异。

## SQL 和 NoSQL 的区别

| 维度 | 关系型数据库（SQL） | NoSQL |
| --- | --- | --- |
| 数据模型 | 表结构明确，关系和约束清晰 | KV、文档、列族、图等，结构更灵活 |
| 查询能力 | 擅长 JOIN、聚合和复杂查询 | 查询方式依赖具体产品 |
| 事务一致性 | 通常完整支持 ACID 事务 | 依赖具体产品，部分更偏最终一致性 |
| 扩展方式 | 常见读写分离、分库分表 | 通常更容易水平扩展 |
| 典型场景 | 订单、支付、账户、复杂业务查询 | 缓存、日志、内容存储、海量读写 |

两者通常结合使用，而不是相互替代。NoSQL 也不等于不支持事务，具体能力要看产品和使用方式。

## SQL 的分类

| 分类 | 作用 | 常见语句 |
| --- | --- | --- |
| DDL | 定义数据库对象 | `CREATE`、`ALTER`、`DROP`、`TRUNCATE` |
| DML | 新增、修改和删除数据 | `INSERT`、`UPDATE`、`DELETE` |
| DQL | 查询数据 | `SELECT` |
| DCL | 管理权限 | `GRANT`、`REVOKE` |
| TCL | 控制事务 | `COMMIT`、`ROLLBACK`、`SAVEPOINT` |

工程上最重要的安全原则是：执行 `UPDATE`、`DELETE`、`DROP` 或 `TRUNCATE` 前，确认环境、影响范围、事务和备份。特别是修改或删除语句，要先用相同的 `WHERE` 条件执行 `SELECT` 检查目标行。

## 示例数据模型

本文使用用户、订单和订单明细三个对象：

```sql
CREATE TABLE users (
    id          BIGINT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    status      VARCHAR(20) NOT NULL,
    created_at  TIMESTAMP NOT NULL
);

CREATE TABLE orders (
    id          BIGINT PRIMARY KEY,
    user_id     BIGINT NOT NULL,
    amount      DECIMAL(12, 2) NOT NULL,
    status      VARCHAR(20) NOT NULL,
    created_at  TIMESTAMP NOT NULL,
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
    id          BIGINT PRIMARY KEY,
    order_id    BIGINT NOT NULL,
    product_id  BIGINT NOT NULL,
    quantity    INT NOT NULL,
    unit_price  DECIMAL(12, 2) NOT NULL,
    CONSTRAINT fk_items_order FOREIGN KEY (order_id) REFERENCES orders(id),
    CONSTRAINT uk_order_product UNIQUE (order_id, product_id)
);
```

约束是数据正确性的最后防线：

- `PRIMARY KEY` 唯一标识一行。
- `NOT NULL` 禁止缺失值。
- `UNIQUE` 保证业务键不重复。
- `FOREIGN KEY` 保证引用完整性。
- `CHECK` 约束字段的合法范围，但要确认数据库版本是否真正执行它。

## INSERT、UPDATE 和 DELETE

```sql
INSERT INTO users (id, name, status, created_at)
VALUES (1, 'Alice', 'active', CURRENT_TIMESTAMP);

UPDATE orders
SET status = 'paid'
WHERE id = 1001 AND status = 'pending';

DELETE FROM orders
WHERE id = 1001 AND status = 'cancelled';
```

注意：

- 显式写列名，不依赖表的物理列顺序。
- 把业务前置状态放进 `UPDATE` 条件，可减少并发覆盖。
- “先查再写”不能代替唯一约束或事务并发控制。
- `DELETE` 删除行，`TRUNCATE` 清空表，`DROP` 删除对象，三者风险和事务行为不同。

## SELECT 基础查询

```sql
SELECT id, user_id, amount, status
FROM orders
WHERE status = 'paid'
  AND amount >= 100
  AND created_at >= '2026-07-01'
  AND created_at < '2026-08-01'
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

查询时优先明确列名，避免无目的地使用 `SELECT *`：它会增加网络传输、破坏覆盖索引机会，也会让调用方意外依赖新增列。

常见条件包括：

```sql
WHERE amount BETWEEN 100 AND 500
WHERE status IN ('paid', 'shipped')
WHERE name LIKE 'Ali%'
WHERE deleted_at IS NULL
```

没有 `ORDER BY` 时，结果顺序没有保证。分页或取 Top N 时必须定义稳定排序；排序字段可能重复时，追加主键作为最后的排序条件。

## NULL 与三值逻辑

`NULL` 表示未知或缺失，它不等于空字符串或数字 0。

```sql
-- 正确
WHERE deleted_at IS NULL

-- 错误：结果不是 true
WHERE deleted_at = NULL
```

SQL 条件可能得到 `TRUE`、`FALSE` 或 `UNKNOWN`。`WHERE` 只保留 `TRUE`，因此 `NOT IN` 的集合中只要可能含 `NULL`，就容易产生意外结果。可优先使用保证非空的列，或改写为 `NOT EXISTS`。

`COUNT(*)` 统计行数，`COUNT(column)` 只统计该列非 `NULL` 的行数。

## 条件表达式与常用函数

```sql
SELECT
    id,
    amount,
    CASE
        WHEN amount >= 1000 THEN 'large'
        WHEN amount >= 100 THEN 'medium'
        ELSE 'small'
    END AS amount_level,
    COALESCE(note, '') AS note
FROM orders;
```

常见的标准或广泛支持函数包括 `COUNT`、`SUM`、`AVG`、`MIN`、`MAX`、`LOWER`、`UPPER`、`TRIM` 和 `COALESCE`。字符串、日期和 JSON 函数的方言差异较大，使用前应查对应数据库文档。

不要在筛选条件里无必要地包裹索引列。例如：

```sql
-- 通常不利于普通索引检索
WHERE DATE(created_at) = '2026-07-22'

-- 更适合范围扫描
WHERE created_at >= '2026-07-22'
  AND created_at <  '2026-07-23'
```

## 聚合、GROUP BY 与 HAVING

```sql
SELECT
    user_id,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount
FROM orders
WHERE status = 'paid'
GROUP BY user_id
HAVING SUM(amount) >= 1000
ORDER BY total_amount DESC;
```

- `WHERE` 在分组前过滤行。
- `GROUP BY` 把行划分为组。
- 聚合函数对每组计算结果。
- `HAVING` 在分组后过滤聚合结果。

分组查询中，非聚合列原则上必须出现在 `GROUP BY` 中。不要依赖某些数据库宽松模式下返回的任意值。

条件聚合可以在一次扫描中计算多个指标：

```sql
SELECT
    user_id,
    SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) AS paid_count,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count
FROM orders
GROUP BY user_id;
```

## JOIN

JOIN 根据关联条件组合多张表。

| 类型 | 返回结果 |
| --- | --- |
| `INNER JOIN` | 两边能够匹配的行 |
| `LEFT JOIN` | 保留左表全部行，右表无匹配时补 `NULL` |
| `RIGHT JOIN` | 保留右表全部行，左表无匹配时补 `NULL` |
| `FULL OUTER JOIN` | 保留两边全部行；MySQL 不直接支持 |
| `CROSS JOIN` | 两个集合的笛卡尔积 |

```sql
SELECT
    o.id,
    u.name,
    o.amount
FROM orders AS o
JOIN users AS u ON u.id = o.user_id
WHERE o.status = 'paid';
```

使用 JOIN 时重点检查：

- 关联关系是一对一、一对多还是多对多；一对多 JOIN 会增加结果行数。
- 过滤条件放在 `ON` 还是 `WHERE`；对外连接右表字段在 `WHERE` 中过滤，可能把它变成内连接效果。
- 关联字段的数据类型应一致，并建立合适索引。
- 不要机械套用“小表驱动大表”，现代优化器会根据统计信息、过滤率和成本选择顺序。

查找“没有订单的用户”属于反连接：

```sql
SELECT u.id, u.name
FROM users AS u
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.user_id = u.id
);
```

## 子查询、IN 与 EXISTS

```sql
SELECT id, name
FROM users AS u
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.user_id = u.id
      AND o.status = 'paid'
);
```

| 写法 | 含义 | 注意点 |
| --- | --- | --- |
| `IN` | 值是否属于结果集合 | `NOT IN` 要特别留意 `NULL` |
| `EXISTS` | 相关子查询是否至少返回一行 | 返回的具体列不重要 |
| 标量子查询 | 子查询返回一个值 | 返回多行会报错 |

不要把“`EXISTS` 一定比 `IN` 快”当成规则。优化器可能把两者转换成相似的半连接计划，实际选择应结合可读性、NULL 语义和执行计划。

## UNION 与集合运算

```sql
SELECT user_id FROM orders_2025
UNION ALL
SELECT user_id FROM orders_2026;
```

- `UNION ALL` 直接合并结果，通常更快。
- `UNION` 合并后去重，需要额外计算。
- 各查询的列数必须相同，对应列类型应兼容。
- 最终顺序仍需在整个集合查询末尾使用 `ORDER BY`。

标准 SQL 还定义了 `INTERSECT` 和 `EXCEPT`，但数据库支持情况不同；MySQL 中通常用 JOIN 或 `EXISTS` 改写。

## CTE

CTE（Common Table Expression）给中间结果命名，适合分步表达复杂查询：

```sql
WITH user_totals AS (
    SELECT user_id, SUM(amount) AS total_amount
    FROM orders
    WHERE status = 'paid'
    GROUP BY user_id
)
SELECT u.id, u.name, t.total_amount
FROM user_totals AS t
JOIN users AS u ON u.id = t.user_id
WHERE t.total_amount >= 1000;
```

递归 CTE 可处理组织树、分类树和序列生成，但要设置合理的终止条件，并关注数据库的递归层数限制。CTE 主要提升表达能力，不代表一定物化或一定更快，具体执行方式由数据库和版本决定。

## 窗口函数

窗口函数在保留明细行的同时，计算排名、累计值或相邻行差异。

```sql
SELECT
    id,
    user_id,
    amount,
    ROW_NUMBER() OVER (
        PARTITION BY user_id
        ORDER BY amount DESC, id
    ) AS rn,
    SUM(amount) OVER (
        PARTITION BY user_id
        ORDER BY created_at, id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_amount
FROM orders
WHERE status = 'paid';
```

常用窗口函数：

| 函数 | 用途 |
| --- | --- |
| `ROW_NUMBER()` | 为每组生成唯一序号 |
| `RANK()` | 并列排名并跳号 |
| `DENSE_RANK()` | 并列排名但不跳号 |
| `LAG()`、`LEAD()` | 读取前一行或后一行 |
| `SUM() OVER (...)` | 累计值或移动汇总 |

“每个用户金额最高的三笔订单”可以先用 `ROW_NUMBER()` 分组排名，再在外层筛选 `rn <= 3`。

## SQL 查询的逻辑执行顺序

```text
FROM / JOIN / ON
→ WHERE
→ GROUP BY
→ HAVING
→ SELECT
→ DISTINCT
→ ORDER BY
→ LIMIT / OFFSET
```

这是语义上的逻辑顺序，不是数据库真实的物理执行顺序。因此：

- `WHERE` 通常不能使用 `SELECT` 中刚定义的别名。
- `ORDER BY` 通常可以使用输出别名。
- 优化器可以在保持结果语义的前提下改写执行方式。

## 关系建模与范式

| 范式 | 核心要求 | 主要解决的问题 |
| --- | --- | --- |
| 1NF | 字段值具有原子性 | 一列存储多个业务值 |
| 2NF | 非主属性完全依赖候选键 | 对联合候选键的部分依赖 |
| 3NF | 非主属性不传递依赖候选键 | 传递依赖 |

建模时先识别实体、属性、关系、主键和业务唯一键，再决定表结构。范式用于减少冗余和更新异常，但不是越高越好；订单快照、历史价格等场景会为了保留历史事实或提高查询效率而有意冗余。

外键可以把引用完整性交给数据库保证，但也会增加批量写入、迁移和分库分表的复杂度。是否使用物理外键应结合一致性要求和架构约束决定；即使不用物理外键，也必须通过应用逻辑、巡检和修复机制维护关系。

常见设计检查：

- 主键是否稳定、简短且没有业务含义变化风险。
- 是否存在需要唯一约束保护的业务键。
- 金额是否使用精确数值类型，并明确币种和舍入规则。
- 时间字段记录的是事件时间、处理时间还是更新时间。
- 状态字段是否有清晰的状态机和合法转换。
- 多对多关系是否使用中间表，并对组合键建立唯一约束。

## 分页、去重与 Top N

大偏移分页会扫描并丢弃大量记录。对于连续翻页，优先使用游标式分页：

```sql
SELECT id, created_at, amount
FROM orders
WHERE (created_at, id) < ('2026-07-22 12:00:00', 1001)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

去重要先定义“重复”的业务含义。`DISTINCT` 是对输出列组合去重；如果要保留每个业务键最新的一行，通常使用 `ROW_NUMBER()` 按业务键分区、按时间倒序编号。

Top N 也必须明确范围：全局 Top N 直接排序限制行数；分组 Top N 使用窗口函数。

## 编写和排查清单

写 SQL 前：

1. 明确结果粒度：一行代表用户、订单还是订单明细。
2. 明确表之间的基数，预判 JOIN 后是否会增行。
3. 明确 `NULL`、重复数据和时间边界的处理方式。
4. 明确是否需要稳定排序，以及并列时如何处理。

SQL 写完后：

1. 用小样例验证空集、单行、多行、重复值和 `NULL`。
2. 检查聚合前后的行数是否符合预期。
3. 对写操作先用相同条件执行 `SELECT`。
4. 对关键查询查看执行计划、扫描行数、索引选择和排序方式。
5. 用真实数量级的数据验证性能，不只看少量测试数据。

## 方言边界与延伸

SQL 有标准，但不同数据库在以下方面差异明显：

- 自增列：`AUTO_INCREMENT`、identity、sequence。
- 分页：`LIMIT`、`OFFSET ... FETCH` 等。
- UPSERT：`ON DUPLICATE KEY UPDATE`、`ON CONFLICT`、`MERGE`。
- 日期、字符串、JSON 和正则函数。
- 标识符大小写、引号和隐式类型转换。
- `FULL OUTER JOIN`、`INTERSECT`、`EXCEPT` 的支持情况。

学习顺序建议：先掌握本文中的关系模型和通用查询，再进入 [MySQL](MySQL.md) 理解 SQL 在具体数据库中如何通过索引、事务、锁和日志执行。
