# Eval 与测试体系

这篇文档解决一个问题：**如何让 AI 应用的优化是可验证的**。

这是 AI 应用工程与传统软件工程最大的差异之一：你不能靠"试几次感觉不错"就发布，但也不能套用单元测试——因为 LLM 的输出是概率性的、多维度的。

---

## 1. 为什么 AI 应用需要专门的测试体系

### 传统软件测试的局限

```python
# 传统软件：确定性，容易 assert
assert add(2, 3) == 5  # 要么过，要么不过

# AI 应用：无法精确 assert
answer = llm.answer("Python 中 list 和 tuple 的区别是什么？")
# 什么叫"正确"？内容是否覆盖了关键区别？有没有错误信息？格式对不对？
# assert answer == "..." 根本不可行
```

### 三个核心挑战

1. **输出是多维度的**：质量 / 准确性 / 格式 / 风格都可能同时需要评估
2. **输出是概率性的**：同样的输入可能产生不同输出
3. **"正确"是主观的**：很多任务没有唯一正确答案

---

## 2. 什么是 Eval Harness

Eval Harness 是一套自动化评测基础设施：

```
测试集（Test Set）
  + 评测指标（Metrics）
  + 评测执行器（Runner）
  + 结果存储（Storage）
  + 报告与对比（Reporting）
= Eval Harness
```

### 最小可用实现

```python
from dataclasses import dataclass
from typing import Callable
import time

@dataclass
class EvalCase:
    id: str
    input: dict
    expected: dict
    metadata: dict = None

@dataclass
class EvalResult:
    case_id: str
    actual_output: str
    scores: dict[str, float]
    passed: bool
    latency_ms: float

class EvalRunner:
    def __init__(self, system_fn: Callable, metrics: list[Callable]):
        self.system_fn = system_fn
        self.metrics = metrics
    
    def run(self, test_set: list[EvalCase]) -> list[EvalResult]:
        results = []
        for case in test_set:
            start = time.time()
            actual = self.system_fn(**case.input)
            latency_ms = (time.time() - start) * 1000
            
            scores = {
                metric.__name__: metric(actual=actual, expected=case.expected)
                for metric in self.metrics
            }
            
            results.append(EvalResult(
                case_id=case.id,
                actual_output=str(actual),
                scores=scores,
                passed=all(v >= 0.7 for v in scores.values()),
                latency_ms=latency_ms,
            ))
        
        return results
    
    def summary(self, results: list[EvalResult]) -> dict:
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        avg_scores = {}
        for metric_name in results[0].scores:
            avg_scores[metric_name] = sum(r.scores[metric_name] for r in results) / total
        
        return {
            "total": total,
            "passed": passed,
            "pass_rate": passed / total,
            "avg_scores": avg_scores,
            "avg_latency_ms": sum(r.latency_ms for r in results) / total,
        }
```

---

## 3. 测试集构造

测试集质量是 eval 体系的基础。

### 来源策略

| 来源 | 优点 | 缺点 | 适合 |
|------|------|------|------|
| **手工标注** | 高质量，针对性强 | 慢，贵 | 关键功能、edge cases |
| **Production Log Mining** | 真实用户行为 | 需要脱敏，有偏 | 常见用例覆盖 |
| **合成数据（LLM 生成）** | 快，可扩展 | 质量参差，有系统偏差 | 覆盖面扩展 |
| **对抗样本** | 发现边界 | 需要有经验的人设计 | 安全性、鲁棒性 |

### 手工构造的覆盖原则

```
1. Golden path（最典型的正常用例）
2. 边界条件（空输入、超长输入、特殊字符）
3. 已知失败过的 case（regression set）
4. 对抗性输入（prompt injection、角色扮演绕过）
5. 不同用户语言风格（正式/口语/中英混）
```

### 合成测试集

```python
async def generate_synthetic_cases(
    task_description: str,
    existing_cases: list[EvalCase],
    num_new: int = 50,
) -> list[EvalCase]:
    
    prompt = f"""
任务描述：{task_description}

已有案例示例：{format_cases(existing_cases[:3])}

请生成 {num_new} 个新的测试案例，要求：覆盖不同主题和复杂度，包含边界情况，不与已有案例重复。
JSON 格式返回。
"""
    
    cases = await llm_call_structured(prompt, output_schema=list[EvalCase])
    
    # 关键：必须人工抽样审核
    print(f"生成了 {len(cases)} 个案例，请抽样审核 ground truth 质量")
    return cases
```

**关键原则**：LLM 生成的 ground truth 必须人工抽样验证。LLM 倾向于生成它自己擅长回答的问题，有系统性偏差。

---

## 4. 评测指标

### 程序验证（最可靠）

```python
def eval_tool_selection(actual: dict, expected: dict, **_) -> float:
    return 1.0 if actual.get("tool_name") == expected.get("tool_name") else 0.0

def eval_json_schema(actual: dict, expected: dict, **_) -> float:
    try:
        ExpectedSchema(**actual)
        return 1.0
    except Exception:
        return 0.0

def eval_contains_key_facts(actual: str, expected: dict, **_) -> float:
    required_facts = expected.get("required_facts", [])
    if not required_facts:
        return 1.0
    hits = sum(1 for fact in required_facts if fact.lower() in actual.lower())
    return hits / len(required_facts)
```

### LLM-as-Judge

```python
async def llm_judge(
    question: str,
    actual_answer: str,
    reference_answer: str,
    criteria: str = "accuracy, completeness, clarity",
) -> float:
    
    prompt = f"""你是严格的评分员。请评估 AI 的回答质量。

评估标准：{criteria}
问题：{question}
参考答案：{reference_answer}
AI 的实际回答：{actual_answer}

请在 0-10 分打分，只输出数字。"""
    
    score_str = await llm_call(prompt)
    try:
        return max(0.0, min(1.0, float(score_str.strip()) / 10.0))
    except ValueError:
        return 0.5
```

**LLM-as-judge 的偏差**：
- 倾向于给较长的答案更高分（verbosity bias）
- 用同款模型评估自己会有自偏（self-serving bias）
- 对参考答案措辞相似的答案打分更高（anchoring）

**缓解**：用比被测系统更强的模型做评估；多次打分取平均；prompt 里明确评分标准。

---

## 5. Offline Eval vs Online Eval

| 维度 | Offline Eval | Online Eval |
|------|-------------|-------------|
| 数据来源 | 预构造的测试集 | 真实用户流量 |
| 时机 | 发布前 | 发布后 |
| 速度 | 快（批量） | 慢（实时收集） |
| 真实性 | 低（可能不代表真实分布） | 高 |
| 安全性 | 高（失败不影响用户） | 低（失败影响真实用户） |

**结论**：两者要组合使用。Offline Eval 做 pre-release 质量门槛，Online Eval 做上线后的持续监控。

### Online Eval 采样

```python
import random, asyncio

def production_eval_middleware(request, response, user_id: str):
    if random.random() > 0.05:  # 采样 5%
        return
    
    asyncio.create_task(log_for_eval({
        "input": request.user_message,
        "output": response.content,
        "session_id": request.session_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "latency_ms": response.latency_ms,
    }))
```

**隐式反馈信号**：用户点赞/踩（显式）；重新提问（负反馈）；复制内容（正反馈）；对话中止（负反馈）。

---

## 6. Agent 专项评测

Agent 的路径是动态的，要评过程，不只是最终结果：

```python
@dataclass
class AgentEvalCase:
    task: str
    expected_final_answer: str
    expected_tools_used: list[str]
    forbidden_tools: list[str]
    max_acceptable_steps: int

def eval_agent_trajectory(
    actual_trajectory: list[dict],
    expected: AgentEvalCase,
) -> dict[str, float]:
    
    tools_used = [step["tool"] for step in actual_trajectory if "tool" in step]
    
    return {
        "answer_correctness": compare_answers(
            actual_trajectory[-1]["output"],
            expected.expected_final_answer,
        ),
        "tool_precision": len(set(tools_used) & set(expected.expected_tools_used)) / len(tools_used) if tools_used else 1.0,
        "tool_recall": len(set(tools_used) & set(expected.expected_tools_used)) / len(expected.expected_tools_used),
        "no_forbidden_tools": 1.0 if not any(t in expected.forbidden_tools for t in tools_used) else 0.0,
        "step_efficiency": min(1.0, expected.max_acceptable_steps / max(1, len(actual_trajectory))),
    }
```

---

## 7. 回归测试与 CI 集成

```yaml
# .github/workflows/eval.yml
name: AI System Eval
on:
  pull_request:
    paths: ['src/agent/**', 'prompts/**', 'src/rag/**']

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - name: Run eval
        run: |
          python eval/run_eval.py \
            --test-set eval/test_sets/core.jsonl \
            --output eval/results/pr-${{ github.event.number }}.json
      
      - name: Check regression
        run: |
          python eval/compare.py \
            --baseline eval/results/baseline.json \
            --current eval/results/pr-${{ github.event.number }}.json \
            --fail-if-regression 0.05
```

**回归测试关键**：维护固定的 golden test set；每次改动后对比分数；退步超阈值阻止合并；把每个发现的 bug 对应的 case 加入 regression set。

---

## 8. Benchmark 的局限性

不要只靠公开 benchmark 评估你的系统：

| 问题 | 说明 |
|------|------|
| 数据污染 | 公开 benchmark 可能已经在模型训练数据里 |
| 分布偏移 | Benchmark 数据不代表你的实际用户 |
| 指标与实际不符 | MMLU 高分不代表你的任务质量高 |

最有价值的评估永远是基于真实用户 case 构建的测试集。

---

## 9. 如何把 Eval 运营成工程流程

知道"要做 eval"是一回事，让团队把 eval 跑成持续流程是另一回事。

### Slice-based Eval：按维度分桶看退化

整体指标掩盖局部退化。改了一处 prompt，整体分数不变，但某类任务退步了 30%——这在 aggregate 指标里看不出来。

```python
@dataclass
class SlicedEvalResult:
    slice_name: str
    total: int
    passed: int
    pass_rate: float
    avg_scores: dict[str, float]

def eval_by_slice(
    results: list[EvalResult],
    cases: list[EvalCase],
    slice_key: str,  # metadata 里的 key，例如 "task_type" / "user_segment"
) -> list[SlicedEvalResult]:
    from collections import defaultdict
    slices: dict[str, list] = defaultdict(list)
    
    for result, case in zip(results, cases):
        slice_val = (case.metadata or {}).get(slice_key, "unknown")
        slices[slice_val].append(result)
    
    output = []
    for slice_name, slice_results in slices.items():
        total = len(slice_results)
        passed = sum(1 for r in slice_results if r.passed)
        avg_scores = {}
        for metric in slice_results[0].scores:
            avg_scores[metric] = sum(r.scores[metric] for r in slice_results) / total
        output.append(SlicedEvalResult(slice_name, total, passed, passed / total, avg_scores))
    
    return sorted(output, key=lambda x: x.pass_rate)  # 最差的排前面
```

**常用切分维度**：任务类型（问答 / 摘要 / 代码生成）；用户分层（新用户 / 活跃用户）；数据来源（手工标注 / 合成 / 线上日志）；语言（中文 / 英文 / 中英混）。

### Baseline vs Candidate：版本对比与发布门槛

每次发布本质上是"candidate 和 baseline 的对比实验"，需要明确的退步阈值：

```python
def compare_versions(
    baseline: dict,   # {"pass_rate": 0.82, "avg_faithfulness": 0.91, ...}
    candidate: dict,
    gates: dict,      # {"pass_rate": -0.02, "avg_faithfulness": -0.03}  允许的最大退步
) -> tuple[bool, list[str]]:
    """
    返回 (是否通过, 未通过的指标列表)
    gates 里的负数是允许退步的最大幅度
    """
    failures = []
    for metric, max_regression in gates.items():
        delta = candidate.get(metric, 0) - baseline.get(metric, 0)
        if delta < max_regression:
            failures.append(
                f"{metric}: {baseline[metric]:.3f} → {candidate[metric]:.3f} "
                f"(退步 {abs(delta):.3f}，超过阈值 {abs(max_regression):.3f})"
            )
    return len(failures) == 0, failures

# 示例
passed, issues = compare_versions(
    baseline={"pass_rate": 0.82, "avg_faithfulness": 0.91},
    candidate={"pass_rate": 0.83, "avg_faithfulness": 0.87},
    gates={"pass_rate": -0.02, "avg_faithfulness": -0.03},
)
# → False, ["avg_faithfulness: 0.910 → 0.870 (退步 0.040，超过阈值 0.030)"]
```

**发布门槛设计原则**：
- 不同指标设不同阈值（faithfulness 要求严，latency 可以宽）
- 关键指标退步直接 block；次要指标退步 warning
- 新功能 PR 允许特定 slice 的分数暂时下降（有 issue 追踪）

### 标注协议：谁来标、怎么判、分歧怎么处理

没有标注协议，测试集质量会随时间退化。

```
标注协议文档应包含：

1. 任务定义
   - 这道题考什么（准确性？完整性？格式？）
   - 回答什么算"好"、什么算"差"

2. 评分标准（带示例）
   - 0 分：答非所问、有明显错误事实
   - 1 分：方向正确但不完整
   - 2 分：准确完整
   附：各分值的真实示例各 3 条

3. 边界情况处理
   - 答案正确但格式不对 → 扣 0.5 分
   - 无法判断（需要专业知识）→ 标注 uncertain，送专家复审

4. 分歧处理
   - 两标注者分歧 > 1 分 → 第三人裁决
   - 裁决仍有分歧 → 该 case 加入 ambiguous set，不计入主要指标
   - 记录分歧率（目标 < 15%），高分歧说明标注标准不清晰
```

**实践**：每隔一段时间做标注者间一致性检验（Inter-Annotator Agreement），Kappa 值 < 0.6 要重新对齐标注标准。

---

## 10. 面试高频

**Q：什么是 Eval Harness，为什么 AI 应用需要它？**

> Eval Harness 是一套自动化评测基础设施，包含测试集、评测指标、执行器、结果存储和报告对比。AI 应用需要它是因为 LLM 输出是概率性、多维度的，传统 assert 式单元测试无法评估"这个回答好不好"。没有 harness 的结果是：每次改 prompt 或换模型，你都不知道整体质量有没有变好，优化是不可验证的。

**Q：Offline Eval 和 Online Eval 有什么区别，各适合什么情况？**

> Offline Eval 在发布前用预构造的测试集批量评测，速度快但测试集可能不代表真实分布。Online Eval 在发布后对真实用户流量采样评测，数据真实但失败会影响真实用户。两者组合：Offline Eval 做 pre-release 质量门槛，Online Eval 做上线后持续监控。

**Q：如何在 CI 里做 AI 系统的回归测试？**

> 维护一个 golden test set，每次 PR 合并前跑 eval harness，把分数和 baseline 对比。超过预设退步阈值（比如关键指标下降 5%）就阻止合并。对每个发现的 bug，把对应 case 加入 regression set，确保同类问题不会重现。可以把测试集分层：小的核心集每次跑，大的完整集每天或每次 release 跑，平衡速度和覆盖面。
