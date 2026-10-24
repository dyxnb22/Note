# SQL：从结果粒度到可靠查询

SQL 描述需要的关系结果，优化器选择物理执行计划。学习查询时，先回答“一行代表什么”，再追踪过滤、关联、聚合如何改变行数。本章以 MySQL 8.4 的语法为基线，查询示例共用一套数据；存储与并发机制见[数据库系统原理](数据库系统原理.md)。

## 建立同一套示例数据

用户、订单、明细分别是一行一个用户、一行一笔订单、一行一种订单商品。金额使用精确十进制类型；币种与舍入规则在真实系统中仍需另行约定。

```sql
CREATE TABLE users (
    id BIGINT NOT NULL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL
);
CREATE TABLE orders (
    id BIGINT NOT NULL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL CHECK (amount >= 0),
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    note VARCHAR(200),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE order_items (
    id BIGINT NOT NULL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price >= 0),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    UNIQUE (order_id, product_id)
);
INSERT INTO users VALUES
    (1, 'Alice', 'active'), (2, 'Bob', 'active'),
    (3, 'Chen', 'active'), (4, 'Dan', 'inactive'), (5, 'Eve', 'active');
INSERT INTO orders VALUES
    (1001, 1, 300.00, 'paid',      '2026-07-01 09:00:00', 'first'),
    (1002, 1, 200.00, 'paid',      '2026-07-02 09:00:00', NULL),
    (1003, 1, 700.00, 'pending',   '2026-07-03 09:00:00', NULL),
    (1004, 2, 500.00, 'paid',      '2026-07-01 10:00:00', 'promo'),
    (1005, 2, 500.00, 'paid',      '2026-07-02 10:00:00', 'promo'),
    (1006, 2, 100.00, 'cancelled', '2026-07-03 10:00:00', NULL),
    (1007, 4,  50.00, 'paid',      '2026-08-01 00:00:00', NULL),
    (1008, 5,  80.00, 'pending',   '2026-07-04 09:00:00', NULL),
    (1009, 2, 200.00, 'paid',      '2026-07-03 11:00:00', NULL);
INSERT INTO order_items VALUES
    (1, 1001, 10, 2, 100.00), (2, 1001, 20, 1, 100.00),
    (3, 1002, 30, 1, 200.00), (4, 1004, 10, 5, 100.00),
    (5, 1005, 40, 2, 250.00), (6, 1009, 20, 2, 100.00),
    (7, 1007, 50, 1,  50.00);
```

主键标识行，外键限制引用，唯一约束限制同一订单内重复商品，NOT NULL 与 CHECK 分别约束缺失和范围。约束并未表达完整下单流程：例如订单金额与明细之和仍需由业务规则维护。MySQL 旧版本对 CHECK 的支持不同，不能把新版本行为反推到旧库。

## SELECT、过滤与稳定排序

下面保留七月已支付订单，以创建时间和唯一 ID 排序，输出为 1009、1005、1002、1004、1001：

```sql
SELECT id, user_id, amount
FROM orders
WHERE status = 'paid'
  AND created_at >= '2026-07-01'
  AND created_at < '2026-08-01'
ORDER BY created_at DESC, id DESC;
```

相同日期的多行仍由 ID 确定顺序。没有 ORDER BY，数据库不承诺按插入或主键顺序返回；只有时间而无唯一补充键，分页也可能在并列值间摆动。

半开时间区间避免依赖“当天最后一微秒”。日期解释还需与列类型和会话时区一致，不能把本地自然日直接当作 UTC 日。选择所需列可稳定返回字段的约定，也减少无谓传输和读取。

## NULL 与三值逻辑

NULL 表示未知或缺失。与 NULL 的普通比较得到 UNKNOWN，WHERE 只保留 TRUE，故检查缺失用 IS NULL。下面的总行数为 9，有备注的订单数为 3：

```sql
SELECT COUNT(*) AS rows_total, COUNT(note) AS rows_with_note
FROM orders;
```

没有已支付订单的活跃用户是 Chen、Eve：

```sql
SELECT u.id, u.name
FROM users AS u
WHERE u.status = 'active'
  AND NOT EXISTS (
      SELECT 1 FROM orders AS o
      WHERE o.user_id = u.id AND o.status = 'paid'
  )
ORDER BY u.id;
```

若将不存在判断写成 NOT IN，又让子查询混入 NULL，非匹配项可能变成 UNKNOWN。下面返回空集，不能得到上面的两个人：

```sql
SELECT id
FROM users
WHERE status = 'active'
  AND id NOT IN (
      SELECT user_id FROM orders WHERE status = 'paid'
      UNION ALL SELECT NULL
  );
```

COALESCE 可为显示提供默认值，但把缺失金额改成零也是一次业务决策。COUNT 忽略 NULL、SUM 在空输入上通常返回 NULL，也都应纳入结果的含义与空值约定。

## JOIN 与结果粒度

LEFT JOIN 保留左侧用户，右侧无匹配时补 NULL。若希望没有已支付订单的人也显示出来，把订单条件放在 ON 中：

```sql
SELECT u.id, u.name,
       COUNT(o.id) AS paid_count,
       COALESCE(SUM(o.amount), 0) AS paid_amount
FROM users AS u
LEFT JOIN orders AS o
  ON o.user_id = u.id
 AND o.status = 'paid'
 AND o.created_at >= '2026-07-01'
 AND o.created_at < '2026-08-01'
WHERE u.status = 'active'
GROUP BY u.id, u.name
ORDER BY u.id;
```

结果是 Alice 的 2 笔、500，Bob 的 3 笔、1200，以及 Chen、Eve 各 0 笔。若改在 WHERE 要求 o.status='paid'，补 NULL 的行会被过滤；若用 COUNT(*)，无订单的用户也会被计为一行。

INNER JOIN 只保留匹配，CROSS JOIN 产生组合，RIGHT JOIN 与左连接角色相反。FULL OUTER JOIN 保留双方未匹配行，MySQL 8.4 没有直接提供这一语法，其他产品要按方言确认。

### 一对多关联如何放大金额

1001 有两条明细，因此订单连明细后，订单金额出现两次。下面按用户计算的 Alice 金额是错误的 800，而订单本身只有 500：

```sql
SELECT o.user_id, SUM(o.amount) AS duplicated_amount
FROM orders AS o
JOIN order_items AS i ON i.order_id = o.id
WHERE o.status = 'paid'
GROUP BY o.user_id
ORDER BY o.user_id;
```

不能普遍用 SUM(DISTINCT amount) 补救，Bob 的两笔 500 是不同订单，去重金额会误删事实。需要订单金额就直接汇总订单；需要明细指标，则先把明细聚合到每订单一行，再与订单关联。

## 分组、HAVING 与条件聚合

WHERE 过滤输入行，GROUP BY 建立每组粒度，HAVING 再过滤组。下面只返回已支付总额至少 1000 的 Bob：

```sql
SELECT user_id, COUNT(*) AS order_count, SUM(amount) AS total_amount
FROM orders
WHERE status = 'paid'
GROUP BY user_id
HAVING SUM(amount) >= 1000
ORDER BY total_amount DESC, user_id;
```

分组输出应由分组键、聚合或数据库认可的函数依赖决定，避免依赖宽松模式返回不确定列。条件聚合则在同一粒度里分开计算多种状态：

```sql
SELECT user_id,
       SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) AS paid_count,
       SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count
FROM orders
GROUP BY user_id
ORDER BY user_id;
```

## 子查询、CTE 与集合运算

EXISTS 判断是否存在匹配，IN 判断值是否属于集合，标量子查询表达一个值。MySQL 中标量子查询无行时返回 NULL，多行时出错；不能把其他数据库容忍多行的行为当成可移植规则。

CTE 给中间关系命名，可把“每订单明细合计”和“每用户汇总”分开：

```sql
WITH item_totals AS (
    SELECT order_id, SUM(quantity * unit_price) AS items_amount
    FROM order_items
    GROUP BY order_id
)
SELECT o.user_id, SUM(t.items_amount) AS paid_items_amount
FROM orders AS o
JOIN item_totals AS t ON t.order_id = o.id
WHERE o.status = 'paid'
GROUP BY o.user_id
ORDER BY o.user_id;
```

递归 CTE 需要终止条件与循环处理，适合树或路径等查询；普通 CTE 是否物化则由版本与优化决定，不等于建立临时缓存。

UNION 合并并去重，UNION ALL 保留重复；INTERSECT 取交集，EXCEPT 取左侧独有值。MySQL 8.4 支持这三种集合操作，使用时仍需区分重复与 NULL 语义。[MySQL 集合运算](https://dev.mysql.com/doc/refman/8.4/en/set-operations.html)

```sql
SELECT user_id FROM orders WHERE status = 'paid'
INTERSECT
SELECT user_id FROM orders WHERE status = 'pending';
```

这里交集只有 Alice。各分支列数与类型需兼容，最终顺序另加 ORDER BY，不依赖分支输入顺序。

## 窗口函数与并列排名

聚合会合并行，窗口函数保留每一条明细，再计算其所在窗口的值。Bob 有 500、500、200 三笔已支付订单：

```sql
SELECT id, amount,
       ROW_NUMBER() OVER (ORDER BY amount DESC, id) AS row_no,
       RANK() OVER (ORDER BY amount DESC) AS rank_no,
       DENSE_RANK() OVER (ORDER BY amount DESC) AS dense_rank_no,
       SUM(amount) OVER (
           ORDER BY created_at, id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_amount
FROM orders
WHERE user_id = 2 AND status = 'paid'
ORDER BY amount DESC, id;
```

三个编号分别为 1/2/3、1/1/3、1/1/2，累计金额为 500、1000、1200。若给 RANK 的排序也加入唯一 ID，相同金额就不再并列；“稳定选三行”和“保留并列前三名”是不同合同。

每用户 Top N 可用 PARTITION BY user_id 排名，再在外层筛选编号。LAG/LEAD 获取相邻行；累计值还应显式选择 ROWS 或 RANGE 及并列值规则，不能只写 ORDER BY 就假设窗口一定逐行增长。

## 逻辑顺序与物理计划

```text
FROM / JOIN / ON → WHERE → GROUP BY → HAVING
→ 窗口计算与输出表达式 → DISTINCT → ORDER BY → LIMIT
```

这是理解语义的顺序，不是实际执行时间线。WHERE 通常不能引用本层输出别名或窗口结果，ORDER BY 常能使用输出别名；优化器可以下推过滤、重排连接，只要保留语义。

排查性能时再查看估算与实际行数、扫描、连接、排序及资源等待。不能由“SQL 写在后面”推断“数据库一定最后执行”。

## 分页与可变数据

连续翻页可把上一页末尾的唯一排序键作为游标：

```sql
SELECT id, created_at, amount
FROM orders
WHERE (created_at, id) < ('2026-07-03 10:00:00', 1006)
ORDER BY created_at DESC, id DESC
LIMIT 3;
```

游标必须保留完整排序键、过滤条件与方向。唯一补充键解决并列顺序，不能阻止排序字段更新后跨页移动；稳定导出还需快照、不可变键或固定截止边界。深 offset 的工作量与访问路径有关，keyset 也不会自动提供任意跳页。

## 写操作、约束与事务

CREATE/ALTER/DROP 定义结构，INSERT/UPDATE/DELETE 修改行，GRANT/REVOKE 控制权限，COMMIT/ROLLBACK/SAVEPOINT 控制相应事务。SELECT 常单独称为查询类，也有分类将其归入广义 DML，不必把教学缩写当成执行机制。

下面把状态前提写入更新，再撤销本次演示修改：

```sql
START TRANSACTION;
UPDATE orders SET status = 'paid'
WHERE id = 1003 AND status = 'pending';
SELECT status FROM orders WHERE id = 1003;
ROLLBACK;
```

应用还要检查影响行数：零行可能表示不存在、状态不匹配或动作已完成，应按合同区分。唯一约束、条件更新与事务共同保护并发；事先 SELECT 不会冻结之后的事实。

DELETE 删行，TRUNCATE 清空表，DROP 删除对象，但事务行为不能按名字推测。MySQL 的相关 DDL 可能隐式提交，不能认为所有操作都能用 ROLLBACK 撤销。示例的查询结果也不能替代目标数据库中对精度、约束、锁与迁移的验证。
