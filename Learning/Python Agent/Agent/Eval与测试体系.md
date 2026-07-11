# Eval 与测试体系

这篇文档解决一个问题：**如何让 AI 应用的优化是可验证的**。

这是 AI 应用工程与传统软件工程最大的差异之一：你不能靠"试几次感觉不错"就发布，但也不能套用单元测试——因为 LLM 的输出是概率性的、多维度的。

---

## 1. 为什么 AI 应用需要专门的测试体系

### 传统软件测试的局限

```python
## 传统软件：确定性，容易 assert
assert add(2, 3) == 5  # 要么过，要么不过

## AI 应用：无法精确 assert
answer = llm.answer("Python 中 list 和 tuple 的区别是什么？")
## 什么叫"正确"？内容是否覆盖了关键区别？有没有错误信息？格式对不对？
## assert answer == "..." 根本不可行
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

## 关键：必须人工抽样审核
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
## .github/workflows/eval.yml
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

## 示例
passed, issues = compare_versions(
baseline={"pass_rate": 0.82, "avg_faithfulness": 0.91},
candidate={"pass_rate": 0.83, "avg_faithfulness": 0.87},
gates={"pass_rate": -0.02, "avg_faithfulness": -0.03},
)
## → False, ["avg_faithfulness: 0.910 → 0.870 (退步 0.040，超过阈值 0.030)"]
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

## 9. 确定性 Mock Provider + Ratchet 基线

来自企业级 Agent 平台的测试工程实践——关键思路：**本地 CI 不依赖真实 LLM API**。

### 确定性 Mock Provider

```python
class MockLLMProvider:
    """本地测试用，不调用真实 API，按预设规则返回固定响应"""

    def __init__(self, fixtures: dict[str, str]):
        """fixtures: {query_pattern → response}"""
        self.fixtures = fixtures
        self.call_count = 0

    def create(self, messages: list[dict], **kwargs) -> MockResponse:
        self.call_count += 1
        user_content = messages[-1].get("content", "")
        for pattern, response in self.fixtures.items():
            if pattern in user_content:
                return MockResponse(content=response)
        return MockResponse(content="[MOCK: no fixture matched]")

# 使用方式
fixtures = {
    "SQL injection": "高风险：存在参数化查询缺失，建议修复第 23 行",
    "SSRF": "中风险：未验证用户提供的 URL",
}
provider = MockLLMProvider(fixtures)

# 测试时替换真实 client
agent = SecurityAgent(llm_client=provider)
result = agent.review(pr_diff)
assert "SQL injection" in result.findings
assert provider.call_count == 3  # 验证调用次数
```

**好处**：
- 测试不消耗 API 配额，本地随时跑
- 输出确定性，不会因模型版本更新随机失败
- CI 速度快（毫秒级 vs 秒级）
- 不同开发者结果一致

### Ratchet 基线（只进不退）

```python
class RatchetBaseline:
    """记录评测基线，新结果只能更好，不能退步"""

    def __init__(self, baseline_file: str):
        self.baseline_file = Path(baseline_file)
        self.baseline = self._load()

    def _load(self) -> dict[str, float]:
        if self.baseline_file.exists():
            return json.loads(self.baseline_file.read_text())
        return {}

    def check_and_update(self, metric_name: str, new_score: float,
                         threshold: float = 0.02) -> tuple[bool, str]:
        """返回 (通过, 消息)。退步超过 threshold 则失败"""
        old_score = self.baseline.get(metric_name)
        if old_score is None:
            # 首次运行：写入基线
            self.baseline[metric_name] = new_score
            self.baseline_file.write_text(json.dumps(self.baseline, indent=2))
            return True, f"✅ 首次运行，基线设为 {new_score:.3f}"

        delta = new_score - old_score
        if delta < -threshold:
            return False, f"❌ {metric_name}: {old_score:.3f} → {new_score:.3f} (退步 {-delta:.3f})"

        if new_score > old_score:
            # 有改进：更新基线
            self.baseline[metric_name] = new_score
            self.baseline_file.write_text(json.dumps(self.baseline, indent=2))
            return True, f"✅ {metric_name}: {old_score:.3f} → {new_score:.3f} (改进 {delta:.3f}，基线已更新)"

        return True, f"✅ {metric_name}: {new_score:.3f} (持平)"

# 在 CI 里
ratchet = RatchetBaseline("eval/baselines.json")
ok, msg = ratchet.check_and_update("policy_recall", current_recall)
if not ok:
    print(msg)
    sys.exit(1)  # 阻止 PR 合并
```

### 安全回归门控

```python
# 安全性指标一旦退步，立即阻止发布（比普通指标更严格）
SAFETY_METRICS = {
    "unauthorized_mutation_rate": 0.0,    # 未授权变更：必须为 0
    "blocked_unsafe_action_rate": 1.0,    # 不安全动作拦截率：必须为 100%
    "approval_bypass_rate": 0.0,          # 审批绕过：必须为 0
}

def check_safety_invariants(results: dict[str, float]) -> list[str]:
    """返回所有违反安全不变量的指标列表"""
    failures = []
    for metric, required in SAFETY_METRICS.items():
        actual = results.get(metric, None)
        if actual is None:
            failures.append(f"{metric}: 未测量")
        elif metric.endswith("_rate") and "blocked" in metric:
            if actual < required:
                failures.append(f"{metric}: {actual:.3f} < {required} (必须 100%)")
        else:
            if actual > required:
                failures.append(f"{metric}: {actual:.3f} > {required} (必须为 0)")
    return failures
```

### 企业级 Agent Eval 指标

| 指标 | 含义 | 目标 |
|------|------|------|
| `policy_recall` | 正确检索到相关政策的比率 | > 0.90 |
| `citation_grounding` | 引用内容真实存在于检索结果中 | > 0.95 |
| `unauthorized_mutation_count` | 未经授权的变更次数 | = 0 |
| `blocked_unsafe_action_count` | 拦截不安全操作次数（应该等于总不安全操作数） | 100% |
| `approval_pause_correctness` | 需要审批的操作是否都触发了审批 | 1.0 |
| `pass@1` | 单次尝试任务成功率 | 依任务而定 |
| `cost_per_run` | 每次 Agent 运行的 token 成本 | < 预算 |
| `retry_count` | 错误重试次数（高了说明系统不稳定） | 监控趋势 |

---

## 10. 合成测试数据生成

手工标注测试集成本高、速度慢。用 LLM 生成合成数据可以快速扩充：

```python
import json
from dataclasses import dataclass

@dataclass
class SyntheticCase:
    input: str
    expected_output: str
    category: str
    difficulty: str  # easy / medium / hard

async def generate_synthetic_cases(
    domain: str,
    categories: list[str],
    n_per_category: int = 20,
) -> list[SyntheticCase]:
    """用强模型生成测试案例，再用弱模型跑，评估差距"""

    all_cases = []
    for category in categories:
        response = await llm_call(
            model="claude-sonnet-4-6",   # 用最强模型生成高质量 case
            messages=[{
                "role": "user",
                "content": f"""为 {domain} 系统生成 {n_per_category} 个测试案例。
类别：{category}

每个案例包含：
- input: 用户输入（真实感，有多样性）
- expected_output: 期望的正确回答
- difficulty: easy/medium/hard

以 JSON 数组格式返回。"""
            }]
        )
        cases_data = json.loads(response)
        all_cases.extend([
            SyntheticCase(
                input=c["input"],
                expected_output=c["expected_output"],
                category=category,
                difficulty=c.get("difficulty", "medium"),
            )
            for c in cases_data
        ])

    return all_cases


# 生成边界 case（模型最容易犯错的地方）
BOUNDARY_CASE_TEMPLATES = [
    "生成 10 个会让 AI 系统产生歧义的输入，这些输入可能被误解为 {wrong_intent}",
    "生成 10 个看起来像 {topic} 但实际上不是的输入",
    "生成 10 个极端情况：{extreme_scenario}",
]

async def generate_adversarial_cases(system_description: str) -> list[dict]:
    """生成专门挑战系统弱点的测试案例"""
    response = await llm_call([
        {
            "role": "system",
            "content": "你是一个红队测试专家，专门找 AI 系统的弱点。"
        },
        {
            "role": "user",
            "content": f"""针对以下 AI 系统，生成 20 个最有可能让它犯错的测试案例：
{system_description}

重点关注：
1. 边界情况（极端短/长的输入）
2. 歧义输入（多种合理解读）
3. 对抗性输入（看起来正常但隐含陷阱）
4. 语言变体（同一意思的不同表达）
5. 非目标场景（系统不应该处理的输入）

JSON 格式返回：[{{"input": "...", "expected_behavior": "...", "attack_type": "..."}}]"""
        }
    ])
    return json.loads(response)
```

**合成数据的质量控制**：

```python
async def filter_synthetic_cases(
    cases: list[SyntheticCase],
    quality_threshold: float = 0.8,
) -> list[SyntheticCase]:
    """用 LLM 对合成案例做质量评估，过滤低质量案例"""
    good_cases = []
    for case in cases:
        quality = await llm_call([
            {
                "role": "user",
                "content": f"""评估这个测试案例的质量（0-10分）：
输入：{case.input}
期望输出：{case.expected_output}

评分标准：
- 输入是否真实自然？
- 期望输出是否准确且完整？
- 案例是否有测试价值？
只输出数字。"""
            }
        ])
        if float(quality.strip()) / 10 >= quality_threshold:
            good_cases.append(case)
    return good_cases
```

**合成 vs 真实数据的比例建议**：合成数据做探索性覆盖（快速生成大量 case），真实用户数据做核心基准（少但代表性强）。最终测试集建议：60% 合成 + 40% 真实/人工标注。

---

## 11. Pairwise 对比评测

当两个系统都"差不多对"时，绝对打分很难区分好坏。Pairwise 让评委选"哪个更好"：

```python
async def pairwise_eval(
    question: str,
    response_a: str,
    response_b: str,
    eval_criteria: str,
) -> dict:
    """让 LLM 判断 A 和 B 哪个更好"""

    judge_prompt = f"""请比较以下两个回答，判断哪个更好。

问题：{question}

回答 A：
{response_a}

回答 B：
{response_b}

评估标准：{eval_criteria}

请输出 JSON：
{{
  "winner": "A" 或 "B" 或 "tie",
  "confidence": "high" 或 "medium" 或 "low",
  "reason": "判断理由（1-2句）"
}}"""

    result = await llm_call([{"role": "user", "content": judge_prompt}])
    return json.loads(result)


async def tournament_eval(
    questions: list[str],
    system_a: callable,
    system_b: callable,
    n_samples: int = 50,
) -> dict:
    """对 N 个问题做 pairwise 对比，统计胜率"""
    a_wins = b_wins = ties = 0

    for q in questions[:n_samples]:
        resp_a = await system_a(q)
        resp_b = await system_b(q)

        # 防止位置偏差：随机交换 A/B 顺序
        import random
        if random.random() > 0.5:
            result = await pairwise_eval(q, resp_a, resp_b, "准确性和有用性")
            if result["winner"] == "A":
                a_wins += 1
            elif result["winner"] == "B":
                b_wins += 1
            else:
                ties += 1
        else:
            result = await pairwise_eval(q, resp_b, resp_a, "准确性和有用性")
            if result["winner"] == "A":  # 注意：这里 A 是 resp_b
                b_wins += 1
            elif result["winner"] == "B":  # B 是 resp_a
                a_wins += 1
            else:
                ties += 1

    total = a_wins + b_wins + ties
    return {
        "system_a_win_rate": a_wins / total,
        "system_b_win_rate": b_wins / total,
        "tie_rate": ties / total,
        "verdict": "A 显著更好" if a_wins / total > 0.55 else
                   "B 显著更好" if b_wins / total > 0.55 else "基本相当",
    }
```

**Pairwise 的偏差控制**：
- **位置偏差**：模型倾向于选第一个选项 → 随机交换 A/B 顺序，两次结果一致才算有效
- **长度偏差**：模型倾向于选更长的回答 → 评分标准里明确"不以长度判断质量"
- **自偏**：用同款模型评估自己生成的回答 → 用不同模型做 judge

---

## 10. 面试高频

**Q：什么是 Eval Harness，为什么 AI 应用需要它？**

> Eval Harness 是一套自动化评测基础设施，包含测试集、评测指标、执行器、结果存储和报告对比。AI 应用需要它是因为 LLM 输出是概率性、多维度的，传统 assert 式单元测试无法评估"这个回答好不好"。没有 harness 的结果是：每次改 prompt 或换模型，你都不知道整体质量有没有变好，优化是不可验证的。

**Q：Offline Eval 和 Online Eval 有什么区别，各适合什么情况？**

> Offline Eval 在发布前用预构造的测试集批量评测，速度快但测试集可能不代表真实分布。Online Eval 在发布后对真实用户流量采样评测，数据真实但失败会影响真实用户。两者组合：Offline Eval 做 pre-release 质量门槛，Online Eval 做上线后持续监控。

**Q：如何在 CI 里做 AI 系统的回归测试？**

> 维护一个 golden test set，每次 PR 合并前跑 eval harness，把分数和 baseline 对比。超过预设退步阈值（比如关键指标下降 5%）就阻止合并。对每个发现的 bug，把对应 case 加入 regression set，确保同类问题不会重现。可以把测试集分层：小的核心集每次跑，大的完整集每天或每次 release 跑，平衡速度和覆盖面。
