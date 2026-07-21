# Agent Eval 实验方法

这篇笔记解决一个问题：**如何知道 Agent 真的变好了，而不是只是某次回答看起来不错**。

Agent Eval 的对象不是一段最终文本，而是一个完整任务：输入、工具调用轨迹、环境状态变化、最终结果、安全事件、成本和延迟。

> **职责边界**：本文专注 Agent 的 Task/Trajectory、隔离场景、Replay 和发布门槛。通用的 Eval Harness、测试集生成、指标实现和 CI 细节见 [Eval 与测试体系](./Eval与测试体系.md)；安全设计本身见 [Agent 安全与威胁建模](./Agent安全与威胁建模.md)。

## 1. 评测对象

```text
Task
  → Agent trajectory
      → model calls
      → tool calls
      → state changes
      → retries / approvals / interruptions
  → outcome + evidence + cost
```

至少区分四类结果：

| 层次 | 问题 |
|---|---|
| Task outcome | 用户目标是否完成？ |
| Artifact correctness | 代码、报告或数据是否正确？ |
| Trajectory quality | 是否走了不必要的步骤、调用了错误工具？ |
| Safety / governance | 是否越权、泄露数据或绕过审批？ |

最终回答正确，不代表中间过程安全；任务失败，也不代表模型本身失败，可能是工具、权限或环境问题。

## 2. 测试集设计

不要只收集“成功案例”。测试集应覆盖：

```text
正常任务
边界输入
歧义请求
工具超时
工具返回错误
权限拒绝
间接 Prompt Injection
并发 / 重复请求
长 context
需要人工确认的副作用
```

每个 case 至少包含：

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

测试集应版本化。修改任务描述、工具定义或参考答案时，要记录原因，否则无法解释评测变化。

## 3. 评测层次

### Unit Eval

测试确定性代码：路径检查、schema 校验、预算、权限、重试和状态转换。不要用 LLM 测试这些逻辑。

### Mock Provider Eval

用固定模型响应测试 Agent Loop：

```text
预设 assistant tool_call
  → 工具返回固定结果
  → 预设下一次 tool_call 或 final answer
  → 检查消息序列、停止原因和状态
```

它不能证明模型能力，但能稳定发现循环、协议和恢复逻辑的回归。

### Scenario Eval

在隔离 workspace 中运行完整任务，检查文件、测试、权限和最终结果。适合 Coding Agent。

### Online Eval

从真实流量抽样，经过脱敏后做人工标注或离线 replay。线上指标用于发现未知失败，不应替代离线回归集。

## 4. 指标设计

### 任务质量

- `task_success_rate`：目标完成率；
- `artifact_correctness`：产物是否通过程序验证；
- `regression_rate`：是否破坏原有行为；
- `evidence_grounding`：结论是否能回指文件、测试或工具结果。

### 轨迹质量

- `tool_selection_accuracy`；
- `invalid_argument_rate`；
- `unnecessary_steps`；
- `retry_count`；
- `stuck_loop_rate`；
- `human_takeover_rate`。

### 系统指标

- 每任务 token、成本和 wall-clock latency；
- 工具超时、队列等待和外部 API 错误；
- context 压缩次数和丢失关键信息的比例。

### 安全指标

- `approval_bypass_rate`；
- `unauthorized_tool_call_rate`；
- `secret_exposure_rate`；
- `prompt_injection_resistance`；
- 越权读取或网络外传次数。

不要把所有指标压成一个总分。至少同时观察质量、成本和安全三条轴。

## 5. LLM-as-Judge 的正确用法

LLM Judge 适合评估开放式答案，但它不是事实来源，也不是安全边界。

使用时要：

1. 给出明确 rubric，而不是“看起来好不好”；
2. 尽可能提供 reference、工具轨迹和程序验证结果；
3. 用人工标注样本校准 judge；
4. 监控 judge 与人工的分歧；
5. 对安全违规使用程序规则强制阻断。

```python
def judge_prompt(case, result, evidence) -> str:
    return f"""
你是评测员，只根据给定证据打分。

任务：{case.task}
参考标准：{case.expected}
程序验证：{evidence}
Agent 结果：{result}

返回 JSON：
{{"score": 0, "passed": false, "reasons": [], "missing_evidence": []}}
"""
```

## 6. Baseline、Ratchet 与发布门槛

每次改动都要比较 `baseline` 和 `candidate`：

```text
candidate 成功率上升
但成本上升 40% → 需要产品决策

candidate 平均分上升
但安全指标退步 → 阻止发布

整体不变
但某类任务明显退步 → 做 slice-based 分析
```

Ratchet 适合防止已修复的问题重新出现，但不能让所有指标只增不减。指标要区分：

- 安全硬门槛：不能退步；
- 正确性门槛：按业务设最低值；
- 成本和延迟：允许在质量收益下有预算内波动。

## 7. 轨迹记录与 Replay

一条可 replay 的记录应包含：

```json
{
  "task_id": "edit_missing_import",
  "agent_version": "2026-07-21",
  "model": "configured-model",
  "messages_hash": "...",
  "tool_calls": [],
  "state_events": [],
  "workspace_snapshot": "...",
  "outcome": {"passed": true},
  "usage": {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0}
}
```

生产日志需要脱敏。API key、cookie、个人信息和完整源码不应无条件写入 trace。

## 8. 练习与验收

为自己的 Coding Agent 建立一个最小 Eval Harness：

1. 10 个固定任务，覆盖成功、失败、越权和注入；
2. Mock Provider 测试 Loop 协议；
3. Scenario Eval 在临时 workspace 中执行；
4. 至少一个程序化判定和一个人工校准过的 Judge；
5. CI 比较 baseline/candidate；
6. 任一安全指标退步时阻止发布；
7. 任意失败 case 能 replay。

## learn-claude-code 对照：Smoke Test 不等于 Agent Eval

`learn-claude-code` 自带的 [tests](./实践/learn-claude-code/tests/) 主要验证实现协议和回归行为，例如模块能否导入、关键 Agent 是否能启动、压缩工具的 tool pair 是否匹配、后台任务是否能完成。这些测试属于 Unit/Smoke/Integration 层，适合证明 Harness 没有明显坏掉，但不能证明模型在真实任务上的质量。

因此可以把项目测试作为 Eval Harness 的底层门槛：先保证 `s01-s20` 的确定性状态机、工具结果格式、权限拦截和通知注入通过，再用本文的 Scenario Eval 去评估任务成功率、轨迹质量、安全事件、成本和延迟。项目中的教学 demo、mock MCP 和固定工具响应也应明确标记为测试夹具，而不是生产能力证明。

参考：[Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
