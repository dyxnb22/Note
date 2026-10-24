# MongoDB：从文档边界到一致性合同

MongoDB 以 BSON 文档组织数据。文档模型让一起访问和更新的有界内容形成明确聚合；跨文档事务、关联和索引则承担其他成本。本章示例采用 MongoDB 8.0 的常用 mongosh 语法，从未分片的订单集合开始。

## 嵌入与引用围绕生命周期

订单中的少量商品快照适合嵌入，因为它们随订单一起读取，历史价格也应独立于当前商品价格。不断增长的浏览、评论或审计记录则更适合单独集合，避免无界数组。

引用节省重复并允许独立演进，却把关联和一致性移到查询或业务协议。一个 BSON 文档有 16 MiB 上限，规模更小时也可能已出现更新竞争与传输成本，不能把上限当成设计目标。

## 给灵活 Schema 明确约束

下面限制必要字段、金额类型、状态与明细数量；100 条是演示中的业务上限。

```javascript
db.createCollection("course_orders", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "tenant_id", "status", "version", "amount_cents", "created_at", "items"],
      properties: {
        _id: { bsonType: "string" },
        tenant_id: { bsonType: "string" },
        status: { enum: ["pending", "paid", "cancelled"] },
        version: { bsonType: "int", minimum: 1 },
        amount_cents: { bsonType: "long", minimum: 0 },
        created_at: { bsonType: "date" },
        items: { bsonType: "array", maxItems: 100 }
      }
    }
  }
});
db.course_orders.insertOne({
  _id: "t1:o1", tenant_id: "t1", status: "pending", version: NumberInt(1),
  amount_cents: NumberLong("9900"), created_at: ISODate("2026-10-22T09:00:00Z"),
  items: [{ sku: "p1", quantity: 1 }]
});
```

结构校验不自动限制合法状态迁移，也未验证每条明细的完整业务约束。新增字段时还需约定缺失、默认值和读写版本，既有文档不会因验证器更新而自动完成迁移。

## 单文档原子更新与条件

```javascript
const result = db.course_orders.updateOne(
  { _id: "t1:o1", tenant_id: "t1", status: "pending", version: NumberInt(1) },
  { $set: { status: "paid" }, $inc: { version: NumberInt(1) } }
);
```

状态和版本与修改在同一单文档操作中判断；成功后为 paid、version=2。重复相同调用通常匹配零条，零条也可能表示不存在或版本冲突，因此应重查必要事实，不能一律宣布“重复成功”。[原子性与事务](https://www.mongodb.com/docs/manual/core/write-operations-atomicity/)

跨文档事务可组合多条修改，但仍有失败、重试与提交结果未知的情况。普通 updateMany 也不能仅因是一个 API 调用就推断全部文档组成同一原子事务，外部支付更不会自动回滚。

## 由查询形状选择索引

```javascript
db.course_orders.createIndex({ tenant_id: 1, status: 1, created_at: -1, _id: -1 });
db.course_orders.find({ tenant_id: "t1", status: "paid" })
  .sort({ created_at: -1, _id: -1 }).limit(20).explain("executionStats");
```

等值前缀收窄范围，后续键服务排序。ESR 是常用分析方法，不是“高选择性字段永远第一”；范围极窄、排序代价较小时也可能选别的顺序。检查扫描键、扫描文档、返回量与排序阶段，而非只看出现 IXSCAN。[ESR 指南](https://www.mongodb.com/docs/manual/tutorial/equality-sort-range-guideline/)

数组会形成多键索引，条目规模、复合限制与覆盖条件需另外分析。增加索引也增加写入与工作集成本，不应把每个可查询字段都独立建一遍。

## 聚合流水线与中间粒度

```javascript
db.course_orders.aggregate([
  { $match: { tenant_id: "t1", status: "paid" } },
  { $group: { _id: "$tenant_id", paid_cents: { $sum: "$amount_cents" } } }
]);
```

match 过滤、project 选字段、group 改变粒度，lookup 引入关联。unwind 明细后再汇总订单总额也可能重复计数，原理与 SQL 一对多 JOIN 相同。优化器可能调整可安全移动的阶段，不能把“永远先 match”当成所有流水线的合法改写。

## 复制集与读写关注

Primary 接受相应写入，Secondary 通过复制历史跟进，切换可能造成暂时错误或未知结果。三个设置分别回答不同问题：

| 设置 | 决定什么 |
|---|---|
| Write Concern | 写入确认等待哪些副本或持久化条件 |
| Read Concern | 允许读取哪类已确认/快照状态 |
| Read Preference | 选择到哪类成员读取 |

majority 读取不等于每次必读到整个系统最新值，secondary 也不因叫副本就已同步当前写。因果会话、线性一致读和事务快照有额外条件，应按各机制的适用条件组合；重试写的去重范围也不能替代跨资源业务幂等。

## 分片键决定局部性与热点

mongos 按元数据路由，Config Server 保存相应集群元数据，各 Shard 又可由复制集承担。复制增加同一事实的副本，分片拆开不同键，两者并非替代方案。

租户键有利于定位租户查询，但一个超大热租户仍可能集中；哈希能分散不同键，不能自动拆散相同键的流量。范围键有局部性，单调写入又可能追逐末尾区间。要同时分析基数、频率、查询定位和迁移成本。

重新分片、更改键与全局唯一索引有版本和结构限制。不能把未分片集合的唯一性推断直接搬到分片集合，尤其要核对 shard key 与唯一约束的关系。

## Change Stream 与重建

消费者保存 Resume Token，恢复需依赖仍可用的变更历史；保存进度与完成下游修改不原子时，仍会产生重复或丢失窗口。Token 不是永久备份，失效后需有重新快照、衔接增量与对账的路径。[Change Stream](https://www.mongodb.com/docs/manual/changestreams/)

数据库变更也不等于已经设计好的领域事件。订阅索引、缓存或仓库时，分别处理删除、版本、乱序与业务字段演进；备份恢复还要覆盖复制/分片元数据并验证真实恢复结果。
