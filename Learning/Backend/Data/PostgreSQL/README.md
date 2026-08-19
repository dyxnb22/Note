---
type: practice
status: developing
---
# PostgreSQL 实践路线

这里把 [PostgreSQL](../PostgreSQL.md) 的概念转换成可运行、可观测、可恢复的数据库实践。它不复制 PostgreSQL 正文，而是记录迁移、排障、恢复和容量实验。

## 实践边界

- PostgreSQL 正文回答“数据库为什么这样工作”。
- 本目录回答“如何把它接入服务、如何验证失败行为”。
- 实验环境必须是本地或明确授权的环境；不要在生产库上随意制造锁、故障或删除数据。
- 文档中的方案不是完成证据。只有保存环境、命令、原始输出和失败记录后，才能标记为已验证。

## 建议顺序

1. [迁移与 Schema 演进](./01_迁移与Schema演进.md)
2. [查询计划与性能诊断](./02_查询计划与性能诊断.md)
3. [连接池、并发与锁排障](./03_连接池并发与锁排障.md)
4. [备份恢复与高可用演练](./04_备份恢复与高可用演练.md)
5. [生产观测与容量治理](./05_生产观测与容量治理.md)

## 练习对象

优先使用 [Go 后端项目](../../Go/实践/go-backend-service/README.md) 的订单模型：

- 订单、幂等键和金额不变量保留在数据库约束中。
- PostgreSQL Repository 替换内存 Repository。
- 迁移、集成测试、故障测试和恢复报告独立记录。
- 不把“应用能启动”当成数据库可靠性已经证明。

## 证据矩阵

| 能力 | 最低证据 |
|---|---|
| Schema 演进 | 空库和上一版本数据都能迁移；失败时不会留下不可解释的半成品 |
| 查询性能 | 固定数据量、查询、版本和硬件；保存计划、耗时和资源指标 |
| 并发与锁 | 能制造阻塞、定位持锁者和等待者，并验证超时或恢复策略 |
| 备份恢复 | 在隔离环境恢复，并核对行数、约束、关键业务不变量 |
| 高可用 | 明确 RPO/RTO；演练副本延迟、切换、旧主隔离和客户端路由 |
| 容量治理 | 连接、WAL、表膨胀、磁盘和尾延迟都有阈值与处置动作 |

## 相关主题

- PostgreSQL 原理
- [数据库系统原理](../数据库系统原理.md)
- [SQL](../SQL.md)
- [生产系统工程](../../Delivery/07_生产系统工程.md)
- [后端测试体系](../../Testing.md)

## 官方资料

- [PostgreSQL Documentation](https://www.postgresql.org/docs/current/)
- [Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [Routine Vacuuming](https://www.postgresql.org/docs/current/routine-vacuuming.html)
- [Backup and Restore](https://www.postgresql.org/docs/current/backup.html)
- [High Availability, Load Balancing, and Replication](https://www.postgresql.org/docs/current/high-availability.html)

具体命令和参数随 PostgreSQL 版本变化；实践时记录版本和扩展清单。
