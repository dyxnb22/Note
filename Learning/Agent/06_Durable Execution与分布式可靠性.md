# Durable Execution 与分布式可靠性

当 Agent 任务超过一次 HTTP 请求，或者需要后台执行、多人协作和断点恢复时，它就不再只是一个 while-loop，而是一个小型分布式系统。

> **学习位置**：完成 `03 Agent 架构`、`05 代码 Agent` 和一次可运行的有限 Loop 后阅读。先把“为什么要恢复”说清楚，再学习 Checkpoint、Journal、Queue 和 Lease。
>
> **本章完成标准**：能区分内存里的循环状态、持久化任务状态和外部副作用状态，并解释恢复时为什么不能盲目重做工具。

> **职责边界**：本文是 Checkpoint、Journal、Queue、Lease、幂等、取消和 Resume 的唯一主文档。`03` 只讲状态与终止的概念，`Workflow` 只讲这些原语如何映射到流程，`12` 只讲部署时的版本兼容和运行配置。

## 1. 先定义任务状态

不要用一堆布尔值表达任务状态。用明确的状态机：

```text
pending
  → running
  → waiting_approval
  → running
  → succeeded
  → failed / cancelled / expired
```

每个状态转换都应有：操作者、时间、原因、版本和幂等键。

```python
ALLOWED_TRANSITIONS = {
    "pending": {"running", "cancelled"},
    "running": {"waiting_approval", "succeeded", "failed", "cancelled"},
    "waiting_approval": {"running", "cancelled", "expired"},
}
```

非法转换应被拒绝，而不是静默修正。

## 2. Exactly-once 是目标，不是默认事实

网络重试、进程崩溃和 worker 超时意味着同一个动作可能被执行多次。多数系统实际提供的是 **at-least-once delivery**，因此要把工具设计成幂等或可去重。

```text
请求带 idempotency_key
  → 服务端记录 key + operation_hash
  → 相同 key 且参数相同：返回已有结果
  → 相同 key 但参数变化：拒绝
```

读取、查询、测试通常容易幂等；发送邮件、扣款、发布、删除和写外部系统必须显式设计去重。

## 3. Checkpoint 与 Journal

### Checkpoint

保存任务继续执行所需的最小状态：当前节点、消息摘要、工具结果引用、预算、审批状态和环境版本。

不要把所有大工具结果直接塞进数据库；大结果存对象或文件，状态只保存内容 hash、路径和权限信息。

### Journal

Journal 记录 `event_id`、`task_id`、顺序、事件类型、`operation_id`、结果引用和时间。Checkpoint 负责快速恢复，Journal 负责审计、Replay 和定位问题；两者可以同时存在。

## 4. Queue、Lease 与 Worker

后台 Agent 通常使用任务队列：

```text
API 创建 task
  → queue.enqueue(task_id)
  → worker claim（带 lease）
  → 执行一个可恢复步骤
  → 保存状态 / 续 lease
  → 完成、失败或重新入队
```

Lease 防止失联 worker 永久占有任务：claim 写入 `lease_owner/lease_until`，worker heartbeat，过期后允许接管；接管前重新读状态并核对 `operation_id`，避免重复副作用。

## 5. Retry、Timeout 与 Cancellation

三者解决不同问题：

| 机制 | 解决 | 注意 |
|---|---|---|
| Retry | 暂时性失败 | 只对可重试错误使用，带指数退避和上限 |
| Timeout | 执行时间过长 | 必须终止或隔离底层进程 |
| Cancellation | 用户不想继续 | 传播到队列、模型请求和工具进程 |

取消不是简单地把 HTTP 请求断开。任务恢复时必须识别“取消已请求但动作可能已发生”的中间状态。

## 6. Outbox 与外部副作用

如果数据库事务提交成功，但发送消息失败，或者消息发送成功但数据库提交失败，就会产生状态不一致。

Outbox 模式：

```text
同一事务写业务状态 + outbox 事件
  → outbox worker 发送外部消息
  → 成功后标记 sent
  → 失败后按策略重试
```

外部系统仍需 idempotency key。Outbox 解决“要发送什么”的可靠记录，不保证第三方执行一次。

## 7. 并发与资源隔离

同一文件、订单、账户或审批 Grant 的写操作通常串行或加资源锁；互不相关的只读检索、不同 worktree 可以并行，但合并仍需冲突检查。每个任务独立设置 Token/费用、CPU/内存/时长、网络出口和 Trace correlation ID。

## 8. Resume 的正确姿势

恢复时不要简单地“把最后一条消息再发一次”。应当：

```text
读取最新 checkpoint
  → 校验 workspace / code version
  → 读取未完成 operation
  → 判断工具是否可能已经产生副作用
  → 查询 operation status 或人工确认
  → 继续下一个安全状态
```

尤其是发送、删除、发布等动作，不能因为 worker 崩溃就盲目重试。

## 9. 练习与验收

把本地 Coding Agent 改造成后台任务系统：

1. 使用 SQLite 或 PostgreSQL 保存 task、checkpoint 和 journal；
2. 用一个 worker + lease 执行任务；
3. 模拟进程在工具执行前后崩溃；
4. 支持 retry、timeout、cancel 和 resume；
5. 对一个非幂等工具使用 idempotency key；
6. 用两个 worker 验证同一任务不会被并发执行；
7. 写测试证明状态机不会出现非法转换。

最终要能解释：**系统失败后，如何知道动作有没有发生，以及下一步为什么安全**。

## learn-claude-code 对照

`s12` 的任务状态与依赖图、`s13` 的后台通知、`s14` 的调度器分别对应状态机、投递和进程生命周期边界。教学版任务定义可跨重启保存，但进程关闭后仍要依赖外部调度器；真正实现还需 owner 检查、原子 claim、取消、超时和重试。实验入口：[s12](./实践/learn-claude-code/s12_task_system/code.py)、[s13](./实践/learn-claude-code/s13_background_tasks/code.py)、[s14](./实践/learn-claude-code/s14_cron_scheduler/code.py)。
