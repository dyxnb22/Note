# Eval 与测试体系

这篇文章解决一个问题：**如何让 Prompt、模型、工具和代码的改动可比较、可回归、可发布**。

> **学习位置**：先读 [Agent Eval 实验方法](./09_Agent%20Eval实验方法.md) 理解评测对象，再读本文搭建通用 Harness。
>
> **职责边界**：本文负责测试集、通用指标、Mock Provider、Judge、Baseline、Pairwise、合成数据和 CI。完整 Agent 的工具轨迹、环境副作用、Replay 和安全门槛只在 `09` 维护；Trace 记录见 [可观测性与调试](./11_可观测性与调试.md)。

## 1. 什么叫“正确”

LLM 输出通常不是一个固定字符串。先把任务拆成可验证维度：

```text
任务结果 / 事实正确性 / 格式合同 / 引用证据
安全与权限 / 工具行为 / 延迟 / 成本 / 用户体验
```

确定性逻辑用 Unit Test 和程序断言；开放式质量用人工标注或校准后的 LLM Judge；安全和副作用不能只交给 Judge。

## 2. Eval Harness 的最小结构

```text
Case 数据集 + 版本
  → Runner 执行被测系统
  → Metric / Checker 逐条评分
  → 结果存储（版本、输入、输出、失败原因）
  → Report 分片比较 Baseline/Candidate
  → CI/发布门禁
```

```python
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    input: dict
    expected: dict
    slice: str = "default"


@dataclass(frozen=True)
class EvalResult:
    case_id: str
    scores: dict[str, float]
    passed: bool
    reason: str


def run_eval(
    cases: list[EvalCase],
    system: Callable[[dict], dict],
    checkers: dict[str, Callable[[dict, dict], float]],
) -> list[EvalResult]:
    results = []
    for case in cases:
        try:
            actual = system(case.input)
            scores = {
                name: checker(actual, case.expected)
                for name, checker in checkers.items()
            }
            passed = all(score >= 0.8 for score in scores.values())
            reason = "ok" if passed else "metric_below_threshold"
        except Exception as exc:  # noqa: BLE001 - Harness 要把失败保存成结果。
            scores = {}
            passed = False
            reason = f"runner_error:{type(exc).__name__}"
        results.append(EvalResult(case.case_id, scores, passed, reason))
    return results
```

示例阈值只是结构示意；真实阈值要按任务和基线定义，并保存每条 Case 的失败证据，不能只保存平均分。

## 3. 测试集构造

测试集应同时包含：

- Golden path：正常任务；
- 边界：空输入、超长、歧义、特殊格式和无答案；
- 历史事故：每个修复过的 Bug 进入永久回归集；
- 对抗样本：注入、越权、敏感信息、工具错误和资源滥用；
- 分布切片：语言、任务类型、租户、数据来源和用户阶段。

来源组合：手工高质量样例 + 脱敏生产样例 + 合成扩展 + 专家标注。合成 Case 必须抽样人工审核，不能让模型自己生成并自己证明 ground truth。

每条 Case 的 metadata 至少包含：数据集版本、任务类型、风险等级、期望工具/副作用、难度、来源和是否属于回归集。

## 4. 指标选择

| 类型 | 示例 | 适合 |
|---|---|---|
| 程序断言 | schema、JSON、文件 diff、测试、引用 ID | 确定性结果，优先使用 |
| 检索指标 | Recall@K、MRR、NDCG、引用覆盖 | RAG 的召回/排序 |
| 任务指标 | success、artifact correctness、拒答正确 | 有明确成功证据的任务 |
| 质量评分 | 相关性、完整性、清晰度、风格 | 开放式输出，需标注校准 |
| 体验指标 | 延迟、澄清接受率、人工接管、成本 | 产品和生产权衡 |

不要把所有指标压成一个总分。安全硬门槛（越权、秘密泄露、未授权副作用）不能被平均质量提升抵消。

### LLM-as-Judge 的使用边界

Judge 适合开放式质量，不适合判断是否真的写入了某文件、是否越权或是否重复扣款。减轻偏差的方法：明确 rubric、使用独立模型、随机化答案顺序、多人/多次评分、人工校准并记录 Judge 版本。

RAGAS、DeepEval、TruLens 等是指标实现工具，不是评测方法本身；先定义 Case、金标、无答案和权限，再接套件。

## 5. Offline、Online 和 Replay

| 方式 | 用途 | 限制 |
|---|---|---|
| Offline | 发布前固定集、快速回归 | 可能不代表真实分布 |
| Online | 真实流量抽样、反馈和漂移 | 失败会影响用户，需脱敏和采样 |
| Replay | 固定输入、工具和环境重现失败 | 外部实时依赖必须冻结或替换 |

线上反馈（重新提问、人工接管、撤销、投诉）用于发现新 Case；发现后脱敏、隔离、加入回归集，再进入发布门禁。

完整 Agent Replay 的记录合同见 [Agent Eval 实验方法](./09_Agent%20Eval实验方法.md)；Trace 中不要默认保存完整私有消息和密钥。

## 6. Mock Provider 和隔离场景

Mock Provider 证明消息协议、调用次数、错误处理和状态转换稳定，不证明真实模型能力。至少准备：固定成功、工具调用、空响应/格式错误、超时/限流、重复调用和取消等 Fixture。

真实 Agent Case 应在临时 workspace、容器或测试租户运行，结束后比较目标文件、外部状态、未授权访问、Trace、成本和耗时。环境必须可清理、可重置，避免 Case 互相污染。

## 7. Baseline、Slice 和发布门禁

一次改动至少比较 Candidate 与 Baseline 的成功率、风险、成本和延迟，并按任务切片查看；整体均值可能掩盖某个高风险 slice 的退化。

```python
def compare(
    baseline: dict[str, float],
    candidate: dict[str, float],
    gates: dict[str, float],
) -> list[dict]:
    failures = []
    for metric, allowed_regression in gates.items():
        delta = candidate.get(metric, 0.0) - baseline.get(metric, 0.0)
        if delta < -allowed_regression:
            failures.append({"metric": metric, "delta": delta})
    return failures
```

发布规则要区分：

- 安全指标：未授权变更、秘密泄露和审批绕过必须为零或达到组织门槛；
- 质量指标：按任务类型设置可接受退化；
- 成本/延迟：写清为了质量允许增加多少；
- 新功能：没有基线时先灰度，不直接全量。

## 8. CI 与测试分层

```text
每次提交：Unit / Schema / State / Mock Provider
每次 PR：核心回归集 + 安全 Case + 关键 RAG/工具 Case
每日或发布前：完整隔离场景 + Judge + 分片报告
线上：抽样、漂移监控、失败脱敏回灌
```

CI 需要记录数据集、Prompt、模型、工具 schema、策略和代码版本。质量回归阻止发布；安全硬门槛直接阻止发布并保留失败样例。

## 9. Pairwise 和合成数据

没有稳定绝对分数时，可以让评审者比较 A/B 哪个更好，但要随机化顺序，明确“事实、引用、安全、风格”的优先级，并保留平局和不确定样例。Pairwise 不能替代程序化安全检查。

合成数据适合扩大主题、语言和边界覆盖；生成后要去重、人工抽样、检查数据泄露和标注质量，并把合成数据与真实样例分片报告。

## 10. 练习与验收

为一个 Tool Agent 建立最小 Eval：

1. 10 条 Case，覆盖成功、参数错误、拒权、超时、注入和重复副作用；
2. 一个 Mock Provider 和一个隔离运行器；
3. 程序化成功断言、轨迹检查、成本/延迟记录；
4. 一份 Baseline/Candidate 报告和一条 CI 门禁；
5. 一次失败 Replay，并把修复 Case 加入回归集。

实践：[langgraph-advanced/07-eval](./实践/ai-agent-learning/langgraph-advanced/07-eval/eval_agent.py)、[Agent Eval 实验方法](./09_Agent%20Eval实验方法.md)。
