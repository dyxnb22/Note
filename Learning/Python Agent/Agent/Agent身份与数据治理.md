# Agent 身份、隐私与数据治理

安全与威胁建模关注“攻击如何发生”；这篇笔记关注“数据和权限在 Agent 生命周期中如何被管理”。

## 1. 四种身份不要混为一谈

```text
人类用户 identity
  → 谁在发起任务

Agent identity
  → 哪个 Agent / 版本在执行

Service identity
  → 哪个服务或 worker 在调用工具

Resource identity
  → 正在访问哪个租户、仓库、文件或业务对象
```

工具执行时至少记录：`actor_id`、`tenant_id`、`agent_id`、`task_id`、`resource_id` 和 `operation_id`。

不要只把用户 token 放进模型 context。身份应在服务端 request context 中传递，并由工具层重新校验。

## 2. 权限判断的完整范围

```text
谁（actor）
在什么租户（tenant）
对什么资源（resource）
执行什么动作（operation）
在什么条件下（policy / time / approval）
```

一个通用授权结果可以表示为：

```python
decision = policy.authorize(
    actor=actor,
    tenant=tenant,
    resource=resource,
    operation=operation,
    context={"task_id": task_id, "approval": approval},
)
if not decision.allowed:
    raise PermissionError(decision.reason)
```

RAG 检索、工具列表、工具参数和最终写入都要执行权限检查。只在 UI 隐藏按钮不算权限控制。

## 3. 数据分类

至少为 Agent 会接触的数据标记分类：

| 类型 | 例子 | 默认处理 |
|---|---|---|
| Public | 公开文档 | 可进入普通 context |
| Internal | 内部代码、设计文档 | 仅限组织和项目范围 |
| Confidential | 合同、客户资料、源代码 | 最小权限、审计、短期保留 |
| Restricted | 密钥、支付数据、健康信息 | 默认不进模型，特殊审批 |

数据分类要贯穿：存储、检索、模型请求、工具结果、trace、备份和导出。

## 4. 数据最小化

每次模型调用前问三个问题：

1. 这个字段完成任务是否必需？
2. 是否可以脱敏、摘要或只传 hash？
3. 是否应该由工具在本地处理，而不是发送到模型？

```text
原始客户表
  → 工具本地过滤
  → 删除姓名、电话和完整账户号
  → 只把完成任务所需的聚合结果传给模型
```

“模型能看到”不等于“模型需要看到”。

## 5. Secret 生命周期

密钥不应出现在：

- system prompt；
- 普通消息历史；
- 工具描述；
- Git diff；
- 完整 trace；
- LLM Judge 输入；
- 用户可下载的错误报告。

推荐流程：

```text
Secret Manager
  → 短期凭证 / 受限 scope
  → 工具进程环境或安全句柄
  → 工具内部使用
  → 输出和日志脱敏
  → 过期 / 撤销 / 轮换
```

如果工具结果包含疑似秘密，先执行 redaction，再进入 context。Redaction 不是权限控制，工具本身仍不能读取不必要的秘密。

## 6. 租户隔离

多租户 Agent 至少隔离：

- 数据库查询条件；
- 向量索引和缓存 key；
- 文件 workspace；
- 队列和任务状态；
- trace、日志和导出；
- 模型 provider 的请求元数据。

每条数据访问都应有 tenant scope。不要依赖调用者“记得传 tenant_id”，可以从已认证的 request context 注入并覆盖用户参数。

## 7. 数据保留和删除

为不同数据设定明确的保留周期：

```text
原始 prompt / tool result → 短期保留，默认脱敏
任务状态 / 审批记录      → 按业务和合规要求保留
聚合指标                 → 尽量去标识化后长期保留
用户要求删除的数据       → 删除主数据、索引、缓存和可恢复副本
```

删除不是只删主表。需要检查对象存储、向量库、缓存、日志、备份和 replay fixture。

## 8. 访问与导出审计

审计事件至少记录：

```json
{
  "actor_id": "user_1",
  "tenant_id": "tenant_a",
  "agent_id": "code-agent",
  "task_id": "task_1",
  "resource": "repo_a/src/example.py",
  "operation": "read",
  "decision": "allow",
  "policy_version": "policy_7",
  "timestamp": "..."
}
```

审计日志要防篡改、可查询、可脱敏；但不要把完整敏感内容复制进审计记录。

## 9. 外部 Provider 与数据边界

接入模型 Provider 前要确认：

- 哪些字段会离开本地环境；
- Provider 如何处理请求和日志；
- 是否支持区域、保留期和删除控制；
- 是否允许使用客户数据训练；
- 失败重试是否会把数据发给备用 Provider；
- 不同模型路由是否有不同的数据策略。

Fallback 不能只按价格和可用性选择，也要检查数据分类和合规边界。

## 10. 练习与验收

为一个多租户知识型 Agent 设计数据治理方案：

1. 定义四类身份和三种数据分类；
2. 为 RAG、工具调用和 trace 写 tenant/resource scope；
3. 实现一条脱敏规则并测试；
4. 模拟用户删除数据，验证主库、索引、缓存、日志和备份处理；
5. 用审计记录证明一次读取和一次拒绝访问；
6. 写清楚 fallback Provider 的数据边界。
