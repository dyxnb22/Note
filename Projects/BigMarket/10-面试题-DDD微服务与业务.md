---
tags: [BigMarket, 面试]
---

# 面试题：DDD、微服务与业务

> [!tip] 练习方式
> 先遮住“答题要点”口述，再检查自己是否同时说到：业务目标、代码对象、数据/业务号、失败分支、限制条件。

## 1. 项目介绍

### Q1：用两分钟介绍 BigMarket

**答题要点：**

1. 营销抽奖学习/作品集项目，不夸大为生产系统。
2. 7 服务：Gateway/Auth/Admin/Market/Chatbot/Message-Job/Account。
3. DDD 边界：Activity/Strategy/Award/Credit/Rebate。
4. 抽奖亮点：Redis 预装配概率表，责任链+决策树。
5. 可靠性：Outbox、幂等业务号、Redis 预留 + MySQL ledger、XXL-Job 补偿。
6. 结尾讲一条端到端发奖闭环。

### Q2：你在项目中最能体现技术深度的部分是什么？

**答题要点：** 选“积分奖端到端一致性”，从 award record + task 讲到 MQ、credit_award_task、account 流水，再讲重复和 UNKNOWN。不要一口气列中间件。

### Q3：这个项目的局限是什么？

**答题要点：** 共享物理 MySQL，DAO 归属主要靠约束；学习账号来自配置；没有生产 HA/容量/灾备/灰度证据；fresh/secure 需单独验证；默认奖品履约范围有限。

## 2. DDD

### Q4：你们如何划分限界上下文？

**要点：** 按业务语言和不变量，不按数据表数量。Activity 管参与/额度/抽奖单，Strategy 管概率/规则/库存，Award 管中奖事实/履约，Credit 管账户/流水，Rebate 管行为到奖励。

### Q5：DDD 分层中 Trigger/Application/Domain/Infrastructure 各做什么？

**要点：** Trigger 协议适配；Application 用例编排；Domain 业务规则与聚合；Infrastructure 实现 MyBatis/Redis/MQ/RPC。举 `RaffleApplicationService` 和 `AwardDispatchSupport` 的例子。

### Q6：Application Service 与 Domain Service 的区别？

**要点：** 前者表达一次用例的时序和跨域协作，后者表达某个领域内的规则。`RaffleApplicationService` 编排，`AbstractRaffleStrategy/AwardService` 执行领域规则。

### Q7：Repository 和 Port 有什么区别？

**要点：** Repository 抽象领域对象持久化；Port 抽象本领域需要的外部业务能力。举 `IActivityRepository` 与 `IStrategyDecisionPort/IActivityAccountPort` 对比。

### Q8：举一个聚合的例子。

**要点：** `UserAwardRecordAggregate`；中奖记录与 task 必须同事务，保证中奖事实一旦存在就有可恢复的履约任务。不要说聚合能跨 RPC 保证事务。

### Q9：为什么 Domain 不直接依赖 Redis/MyBatis？

**要点：** 业务规则的变化原因与技术实现不同；Domain 定义所需能力，Infrastructure 实现，使本地适配器切 RPC 时少改核心规则。

### Q10：一个领域是否必须对应一个微服务？

**要点：** 否。模型边界和部署边界不同；Strategy/Rebate 是独立领域边界但当前 market-local，以控制拓扑和运维复杂度。

## 3. 抽奖算法和规则

### Q11：O(1) 概率抽奖怎么实现？

**要点：** 上线时按概率展开 awardId 槽位，shuffle 后存 Redis Hash；抽奖时 SecureRandom 生成下标，一次 HGET 取 awardId。这是将加权计算前置，用空间换实时路径时间。

### Q12：为什么还需要 O(log n) 算法？

**要点：** 概率精度过高会使 O(1) 展开表过大，Redis 空间成本不可控；超过阈值切分段查找，在空间与时间之间折中。

### Q13：权重抽奖如何实现？

**要点：** Armory 阶段根据 `rule_weight` 为每个权重段过滤奖品子集，建 `strategyId_weight` 子概率表；责任链命中用户段位后从对应子表抽。

### Q14：责任链和决策树为什么两层？

**要点：** 链线性决定“从哪里抽什么”，树多分支决定“候选奖能不能发”；将抽前分流和抽后校验的变化原因分开。

### Q15：为什么责任链节点用 Prototype？

**要点：** 节点有可变 `next` 指针；若是单例，不同 strategyId 构造链会互相改写下一节点。

### Q16：黑名单直接给兜底奖后，为什么还要走库存树？

**要点：** 责任链接管只选定候选奖品，没有完成库存预留。若该奖配了规则树，必须继续执行，否则接管路径可超卖。

### Q17：概率公平性如何验证？

**要点：** 单次不可验证，应对固定配置进行大样本统计，查频率误差；同时分别测主表、权重子表和规则树兜底，避免把业务规则造成的分布当成算法偏差。

## 4. 微服务

### Q18：7 个服务如何分工？

**要点：** 能不看资料说出 8080–8086 和职责，特别是 market 实时业务与 message-job 异步任务、account 账本权威的边界。

### Q19：为什么 market 不能扫描 listener/job？

**要点：** 会让 market 与 message-job 同时注册 Consumer/XXL handler，产生重复消费、重复任务和不清晰的运行归属。源码在 shared JAR 不代表运行在每个引用它的进程。

### Q20：HTTP、Dubbo、MQ 如何选型？

**要点：** 外部客户端和统一接入用 HTTP；必须同步获得 account 结果的内部契约用 Dubbo；可延后、要削峰/重试的履约用 MQ。

### Q21：RPC 超时后能否重试？

**要点：** 可以在业务幂等下重试，但必须使用原业务号；先把超时当 UNKNOWN，查远程订单终态，不能生成新业务号盲目重执行。

### Q22：网关熔断和业务降级开关有什么区别？

**要点：** 熔断根据技术失败率/超时自动保护下游；业务开关是运营通过 Nacos 主动停止抽奖。两者触发条件和响应语义不同。

### Q23：微服务拆分后遇到的最大问题是什么？

**要点：** 跨服务本地事务消失，出现超时 UNKNOWN、重复请求、配置收敛和可观测性问题；项目分别用 Outbox/幂等键/对账任务/Nacos/trace+business ID 处理。

## 5. 业务流程

### Q24：介绍一次完整抽奖。

**要点：** Gateway/JWT → Activity 扣额度建单 → Strategy 链+树+库存 → Award record+task → send_award → credit_award_task → account。加一个失败分支：抽奖中途失败回退额度。

### Q25：为什么先扣额度再抽奖？

**要点：** 抽奖必须先获得一张唯一 orderId 作为参与事实，它同时是后续库存预留和补偿的关联键。如果后续失败，通过订单状态 CAS 和原 orderId 回退额度。

### Q26：为什么会复用 create 状态抽奖单？

**要点：** 前一次请求可能已扣额度建单，但客户端没收到结果。复用可避免重试再扣一次额度，并让后续继续沿同一 orderId 收敛。

### Q27：签到如何防重？

**要点：** `userId + rebateType + yyyyMMdd` 构成 bizId，返利订单唯一约束，Consumer 继续用同一 bizId 幂等发放。

### Q28：积分兑换 SKU 的完整路径？

**要点：** requestId → 预留 SKU + wait_pay 订单 → account 扣积分 → success event → 增额度/完成订单；REJECTED 幂等恢复，UNKNOWN 保留预留和订单对账。

### Q29：Chat 为什么先写 `deducting` 会话？

**要点：** 先记录扣款意图，再调 account，使得超时或本地宕机后仍能通过原业务号查扣款终态并安全退款。

### Q30：Chat 扣款和退款如何幂等？

**要点：** Redis `chat:request:userId:requestId` 防并发和复用回答；account 扣款用 `chat_user_requestId`，退款用 `chat_refund_user_requestId`，MySQL 唯一键保证最终只一次账户效果。

## 6. 一致性与高并发

### Q31：如何保证 DB 和 MQ 一致？

**要点：** 业务记录+task 同事务，事务后发 MQ，confirm+no return 才 completed，失败由 Job 有界重试，Consumer 业务幂等。

### Q32：为什么积分奖要二级 Outbox？

**要点：** 第一级解决 market DB 到 MQ/message-job，第二级解决 message-job 已接管之后到 account RPC。两个分布式边界需要两个可持久化接管点。

### Q33：如何防止奖品库存超卖？

**要点：** Redis Lua/原子预留快速裁决，reservationId 唯一；MySQL ledger 保留 reserved 事实，Job 幂等将库存 -1 与 ledger applied 同事务。

### Q34：为什么 Redis 锁/SETNX 不能单独保证幂等？

**要点：** Redis 可过期、淘汰、丢失，且 SETNX 成功到 DB 写入之间有宕机窗口。它是性能优化，最终底线是稳定业务号 + MySQL 唯一约束/状态机。

### Q35：你们能保证 exactly-once 吗？

**要点：** 不宣称传输 exactly-once；MQ 至少一次，通过幂等 Consumer 达到一次业务效果。

### Q36：任务一直失败怎么办？

**要点：** 有界重试 + `next_retry_time` + 退避，超限进 `manual_pending`；金钱效应 DLQ 默认人工审核，用原业务号重放，先查远程终态。

### Q37：如何理解 UNKNOWN？

**要点：** 调用方没收到结果，不等于远程失败。保留中间状态和原业务号，后续查远程订单终态；不提前释放库存，不盲目补扣/回滚。

## 7. 安全、配置与排障

### Q38：JWT 如何实现注销？

**要点：** jti + Redis 吊销 key + 剩余 TTL；多服务共享检查；Redis 故障 fail-closed，写失败不报假成功。

### Q39：Nacos 动态配置如何收敛？

**要点：** Nacos 唯一权威源，contentHash 乐观并发，publish 成功是提交点，listener 整体替换不可变快照，删除/非法值回安全默认。

### Q40：如何排查积分奖没到账？

**要点：** 从 awardOrderId 查 award record，再查 task/messageId、credit_award_task、account credit order/balance；找第一个未达终态的节点，配合 backlog/age 指标和 traceId 日志。

## 8. 反问与深挖

### Q41：如果让你改进这个项目，会做什么？

可选答案：

- 增加 account RPC 故障注入和 UNKNOWN 终态契约测试。
- 对 fresh volume 和 secure overlay 建立稳定 CI 证据。
- 用更明确的编译/模块门禁强化 DAO 归属，减少共享 Infrastructure 越界风险。
- 增加容量基准测试，而不是只用复杂度宣称性能。
- 完善真实奖品履约和人工工单流程。

### Q42：你如何证明不是只会背项目？

应当能够现场：

1. 画出一次抽奖的同步/异步边界。
2. 说出核心类名和两个聚合。
3. 选一个业务号，说明它穿过哪些表/消息。
4. 分析一个宕机窗口和恢复方式。
5. 说出自己没有验证过的边界。

## 9. 简历表述校正

| 容易被追问穿的说法 | 更准确的说法 |
|---|---|
| 多线程预装配概率表 | 上线前预装配；线程池主要用于大范围查找和库存异步回写 |
| 保证 MQ exactly-once | MQ 至少一次 + 业务幂等，最终一次业务效果 |
| `award_state=completed` 代表已入账 | 仅代表本地履约接管，还需查 credit task 和 account 流水 |
| 已完成集群高可用 | 已验证本地 7 服务 Docker 学习拓扑，不宣称生产 HA |
| Java 8 + Boot 2.7 是当前代码 | 当前代码是 Java 17 + Spring Boot 3.5.x，Java 8/2.7 是历史基线 |

## 10. 关联

- 学习入口：[[00-项目学习地图]]
- 实战勾选：[[09-代码走读清单]]

