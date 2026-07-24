# Agent Eval 实验方法

本文只处理 Agent 特有的评测对象：完整任务、工具轨迹、环境副作用、隔离场景和 Replay。通用测试集、指标、Judge、Mock、Baseline 与 CI 实现统一见 [Eval 与测试体系](./10_Eval与测试体系.md)。

## 1. 评测对象是完整任务

```text
Task
  → Agent trajectory
      → model calls
      → tool calls
      → state changes
      → retries / approvals / interruptions
  → outcome + evidence + cost
```

至少分别判断：

| 层次 | 问题 |
|---|---|
| Task outcome | 用户目标是否真正完成？ |
| Artifact correctness | 代码、文件或外部状态是否正确？ |
| Trajectory quality | 是否误用工具、空转或绕过必要步骤？ |
| Safety / governance | 是否越权、泄露或绕过审批？ |

最终文字正确不代表中间过程安全；任务失败也不等于模型能力不足，可能是工具、权限、环境或恢复逻辑失败。

## 2. Case 要带环境与副作用契约

普通问答 case 只有输入和参考答案；Agent case 还需要 workspace、允许工具、允许副作用、禁止动作和程序化成功证据：

```yaml
id: edit_missing_import
task: 修复指定模块的缺失 import，并保持现有测试通过
workspace: fixtures/edit_missing_import
allowed_tools: [search, read_file, apply_patch, run_tests]
expected:
  files_changed: [src/example.py]
  tests_pass: true
forbidden:
  - 修改测试断言
  - 读取 workspace 外文件
```

测试集必须覆盖正常任务、歧义、超时、权限拒绝、间接 Prompt Injection、重复请求、长 Context、需要审批的副作用和中断恢复。

## 3. 四层实验

### Unit / State-machine

测试路径校验、Schema、预算、权限、重试、取消和状态转换。这些确定性逻辑不用 LLM 判断。

### Mock Provider

用固定模型响应驱动 Agent Loop，检查消息序列、工具结果配对、停止原因和恢复状态。它证明协议实现稳定，不证明模型能完成真实任务。

### Isolated Scenario

在临时 workspace、容器或测试租户运行完整任务，结束后检查：

- 目标文件和允许的外部状态；
- 测试、构建或领域验证器；
- 未授权读取、网络访问和额外副作用；
- Trace、成本、时间和终止原因。

### Online / Replay

真实流量经过授权、抽样和脱敏后形成回归案例。线上信号用于发现未知失败，不能替代发布前的隔离场景。

## 4. Agent 专项指标

不要压成一个总分。除通用质量指标外，至少保留：

- `task_success_rate`、`artifact_correctness`、`regression_rate`；
- `tool_selection_accuracy`、`invalid_argument_rate`、`unnecessary_steps`；
- `retry_count`、`stuck_loop_rate`、`human_takeover_rate`；
- `approval_bypass_rate`、`unauthorized_tool_call_rate`、`secret_exposure_rate`；
- 每任务成本、wall-clock latency 和环境等待时间。

程序验证优先于 LLM Judge。Judge 只能评估开放式质量，并需要人工校准；越权和危险副作用必须由确定性规则判定。

## 5. Replay 记录

一条可重放记录至少包含：

```json
{
  "task_id": "edit_missing_import",
  "agent_version": "versioned-build",
  "model": "configured-model",
  "messages_hash": "...",
  "tool_calls": [],
  "state_events": [],
  "workspace_snapshot": "...",
  "outcome": {"passed": true},
  "usage": {"input_tokens": 0, "output_tokens": 0, "cost": 0}
}
```

Replay 固定环境、工具和输入后比较 Agent 版本；若仍调用实时外部服务，就不是严格重放。日志必须脱敏，Secret、Cookie、个人信息和完整私有源码不默认进入 Trace。

## 6. 发布门槛

Candidate 与 Baseline 至少比较任务成功、风险、成本和延迟，并按任务类型分片。安全硬门槛不能被平均质量提升抵消；已修复事故案例进入永久回归集。

一次发布实验的完成证据是：

1. 固定版本的场景集和环境镜像；
2. 可重复运行的程序验证器；
3. Candidate/Baseline 分片报告；
4. 所有失败 case 可 Replay；
5. 安全指标无退化，质量与成本变化经过明确取舍。

## 7. 与项目测试的边界

`learn-claude-code` 的 [tests](./实践/learn-claude-code/tests/) 主要验证模块导入、消息配对、压缩、后台任务和固定工具响应，属于 Unit/Smoke/Integration 层。它们是 Agent Eval 的底层门槛，但不能证明真实任务成功率。

最小实践应在这些测试之上增加十个隔离场景，覆盖成功、失败、越权和注入，并把程序结果、轨迹和副作用一起纳入报告。

参考：[Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

`#agent #eval #trajectory #replay`
