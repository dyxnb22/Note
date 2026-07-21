# Agent 运维与事故响应

这篇笔记关注 Agent 上线后的现实问题：模型、Prompt、工具和数据都会变化，系统必须能够观测、降级、回滚和复盘。

## 1. SLI / SLO

不要只监控 HTTP 200。Agent 服务至少需要以下指标：

| 维度 | 例子 |
|---|---|
| 可用性 | 任务能否创建、继续、取消 |
| 质量 | task success、回归率、人工接管率 |
| 安全 | 越权调用、审批绕过、秘密暴露 |
| 延迟 | TTFT、单步 latency、任务 P50/P95 |
| 成本 | 每请求、每任务、每租户 token/cost |
| 可靠性 | 工具超时、重试、stuck loop、恢复成功率 |

SLO 要按任务类型分开。例如代码修改、知识问答和后台批处理的成功和延迟标准不同。

## 2. 发布对象不只是代码

Agent 的可发布版本应至少包括：

```text
application code
model ID / provider
system prompt
tool schema / handler
policy version
retrieval index version
eval dataset / baseline
runtime configuration
```

只发布代码而不记录 Prompt、模型和工具版本，生产问题无法复现。

## 3. 发布门禁

推荐顺序：

```text
Unit / contract tests
  → 安全回归
  → Mock Provider Eval
  → Scenario Eval
  → baseline / candidate 对比
  → staging 灰度
  → 小流量生产
  → 全量
```

安全硬门槛不能因为平均质量提升而放宽。质量、成本和延迟之间的权衡必须有明确预算。

## 4. 灰度与回滚

灰度对象可以是：

- Prompt 版本；
- 模型版本；
- 工具 schema；
- 策略版本；
- 检索索引；
- Agent loop 实现。

同一用户或租户在实验期间应保持稳定分组，否则无法比较前后行为。回滚时要考虑正在执行的任务：

```text
新版本停止接收新任务
  → 旧版本继续处理兼容任务
  → 不兼容任务暂停或迁移
  → 记录 checkpoint / policy / schema 版本
  → 验证后恢复执行
```

不要让旧 checkpoint 在新 schema 下静默解释成另一种动作。

## 5. 告警设计

告警应对应明确的处理动作：

| 告警 | 可能动作 |
|---|---|
| Provider 错误率升高 | 切换备用 Provider 或降级为只读 |
| 成本异常 | 限制预算、暂停后台任务 |
| stuck loop 增多 | 降低 max_steps，阻止相关版本 |
| 审批拒绝率突增 | 检查 Prompt、工具描述和策略变更 |
| 越权尝试 | 立即冻结高风险工具并保留 trace |
| RAG 召回退化 | 回滚索引或切换旧检索路径 |

告警必须包含 task、tenant、agent version、model、policy 和 correlation id，避免只能看到一个总量曲线。

## 6. 降级策略

降级应预先设计，而不是事故中临时修改：

```text
完整 Agent
  → 只读 Agent
  → 固定 Workflow
  → 仅生成建议，不执行工具
  → 静态帮助 / 人工处理
```

每一级都要明确：保留哪些工具、哪些数据、哪些用户体验和哪些审计要求。Fallback Provider 不能绕过原有安全策略。

## 7. 事故分级

### P0

发生数据外泄、未授权写入、批量破坏或生产权限绕过。立即冻结相关能力、保全证据、通知负责人并确认影响范围。

### P1

大量任务失败、成本失控、任务无法恢复或关键租户不可用。切换降级路径，暂停高成本任务并修复状态。

### P2

局部工具错误、质量退化或延迟升高。保留样本，按 slice 分析，安排修复和回归。

## 8. 事故响应流程

```text
发现
  → 定级
  → 遏制（kill switch / revoke / freeze）
  → 保全 trace、audit、workspace snapshot
  → 判断影响范围
  → 修复或回滚
  → 逐步恢复
  → 验证无回归
  → 复盘并新增 Eval case
```

复盘不要只写“模型产生幻觉”。应定位到：输入、context、模型、工具 schema、权限策略、执行环境、数据或运维流程中的具体层。

## 9. Kill Switch

高风险能力需要独立于模型和 Prompt 的关闭开关：

- 禁止写工具；
- 禁止网络出口；
- 禁止特定 MCP Server；
- 暂停后台队列；
- 降低每任务预算；
- 强制所有动作进入人工审批。

Kill switch 本身需要权限、审计和演练，不能只存在于文档里。

## 10. 练习与验收

为 Mini-Codex 写一份运维方案：

1. 定义质量、成本、安全和延迟 SLO；
2. 记录完整版本矩阵；
3. 实现 Prompt/模型/策略的灰度和回滚；
4. 设计 Provider 故障、成本失控和越权调用三个事故 runbook；
5. 实现一个能立即禁止写工具的 kill switch；
6. 每次事故自动生成一个脱敏 Eval case。
