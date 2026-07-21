# Agent 安全与威胁建模

这篇笔记不是 Prompt Injection 技巧清单，而是学习如何回答：**谁能影响 Agent，Agent 能触碰什么，最坏后果是什么，哪一层负责阻止它**。

> **职责边界**：本文负责威胁建模、信任边界、资产/主体、攻击面和安全设计评审。具体的防御代码、权限策略、沙箱、脱敏和恢复实现见 [安全与可控性](./安全与可控性.md)；身份、租户和数据生命周期见 [Agent 身份与数据治理](./Agent身份与数据治理.md)。

## 1. 先画信任边界

```text
用户输入 ─┐
仓库文件 ─┼→ Context 组装 → 模型决策 → 工具执行 → 外部系统
网页内容 ─┤                         ↑
工具结果 ─┘                    权限 / 策略 / 沙箱
```

默认把以下内容视为不可信数据，而不是指令：

- 用户提供的文本；
- 仓库中的 README、issue、注释和测试数据；
- RAG 文档和网页；
- MCP Server 的工具描述和返回结果；
- 外部 API 的错误信息。

真正的权限判断必须在模型之外完成。模型输出是提案，不是执行授权。

## 2. 资产、主体和最坏后果

### 资产

- API key、cookie、数据库凭证；
- 用户文件、代码和个人信息；
- 外部系统中的写权限；
- Agent 的 system prompt、内部工具和审计数据；
- 任务状态、审批记录和供应链配置。

### 主体

- 正常用户；
- 恶意用户；
- 被污染的仓库或文档；
- 恶意 MCP Server / 插件；
- 被攻陷的外部服务；
- 同一租户中的其他用户。

### 风险等级

| 级别 | 例子 | 默认策略 |
|---|---|---|
| 低 | 读取当前仓库文件 | 自动执行，记录日志 |
| 中 | 修改代码、运行测试 | workspace 限制，保留 diff |
| 高 | 删除文件、发请求、写数据库 | 明确审批，最小权限 |
| 极高 | 读取密钥、转账、生产变更 | 默认拒绝或人工全程控制 |

## 3. 主要攻击面

| 攻击面 | 例子 | 关键防线 |
|---|---|---|
| Direct Injection | 用户要求忽略安全规则 | 指令分层、策略检查、拒绝高风险动作 |
| Indirect Injection | README 要求 Agent 上传密钥 | 外部内容只作数据、出口控制、工具权限 |
| Tool Misuse | 错误参数调用删除或发信工具 | schema 校验、策略引擎、审批 |
| Data Exfiltration | 读取秘密后通过网络外传 | secret redaction、网络 egress、域名白名单 |
| Supply Chain | 恶意 MCP 描述或插件 | 来源审核、allowlist、沙箱、权限声明 |
| Cross-tenant Access | 查询到其他租户数据 | actor scope 在检索和工具层都过滤 |
| Excessive Autonomy | 长循环不断扩大副作用 | max steps、预算、stuck detection、人工接管 |
| Replay / Race | 重试导致重复扣款或重复写入 | idempotency key、状态机、审计 |

## 4. 多层防线

不要把安全寄托在某一个 prompt 或分类器上：

```text
模型层：识别风险、请求澄清
应用层：工具 allowlist、参数校验、策略判断
权限层：用户/租户/资源 scope、审批 Grant
执行层：workspace、sandbox、timeout、CPU/memory 限制
网络层：出口白名单、DNS/域名限制、禁止访问 metadata endpoint
数据层：密钥注入隔离、日志脱敏、RAG 权限过滤
治理层：审计、告警、回放、人工复核
```

某一层失效时，其他层仍应限制爆炸半径。

## 5. Capability Security

工具不应只接受一个模糊的 `user_id` 或 `is_admin`。更好的做法是让一次授权绑定到具体能力、资源和任务：

```json
{
  "grant_id": "grant_123",
  "actor": "user_456",
  "capability": "repo.write",
  "resource": "repo_a/src/example.py",
  "operation_hash": "sha256:...",
  "expires_at": "...",
  "single_use": true
}
```

执行前重新验证：主体、能力、资源、操作摘要、过期时间和是否已消费。审批“允许写仓库”不应自动等于“允许访问所有仓库并发送网络请求”。

## 6. Prompt Injection 的实际处理

正确目标不是“永远检测出所有注入”，而是让注入即使成功，也无法造成不可接受的副作用。

```text
识别：标记可疑指令
隔离：把外部内容作为数据传递
限制：不给当前任务不需要的工具
验证：高风险动作由独立策略判断
执行：在沙箱和网络边界内运行
监控：记录异常轨迹并支持人工接管
```

例如，仓库中的文字可以建议“运行某命令”，但不能直接改变允许命令集合；网页中的文字可以影响模型判断，但不能授予网络或文件权限。

## 7. 审批不是一个布尔值

审批应展示足够上下文：

- 谁发起；
- Agent 想做什么；
- 目标资源是什么；
- 参数和副作用是什么；
- 哪些证据导致了这个动作；
- 允许一次、允许本任务，还是永久允许；
- 过期时间和撤销方式。

审批后如果操作摘要变化，必须重新审批。

## 8. MCP 与外部工具

远程工具至少需要考虑：

- server 身份和来源；
- OAuth / token 的生命周期；
- 工具描述是否能诱导模型越权；
- server 能访问哪些数据和网络；
- 返回结果是否含敏感信息；
- 用户身份是否沿调用链传递。

MCP 的 HTTP 授权规范可以作为协议层学习材料，但协议授权不等于业务权限；业务系统仍需检查 actor、tenant、resource 和 operation。[MCP Authorization](https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization)

## 9. 练习与验收

为一个“代码修改 Agent”画一份威胁模型：

1. 列出至少 8 个资产和 5 类主体；
2. 标出用户、仓库、模型、工具、沙箱和网络之间的信任边界；
3. 写 10 个攻击 case，至少包含间接注入、密钥外传、路径穿越和重复副作用；
4. 每个 case 指定检测层、阻断层、审计字段和回归测试；
5. 证明“模型被注入”不会自动变成“外部系统被写入”。

参考：[Trustworthy agents in practice](https://www.anthropic.com/research/trustworthy-agents)
