# Agent 架构与设计

这篇文档解决一个问题：**Agent 究竟是什么，有哪些架构模式，怎么设计一个可靠的 Agent 系统**。

不是概念科普，而是要能回答：什么时候用 Agent、什么时候不用、各种模式的权衡是什么。

> **职责边界**：本文讲 Agent 的工程定义、核心循环、状态和运行时模式；工具 schema/执行细节集中在 [Tool Calling](./Tool%20Calling.md)，图式编排集中在 [Workflow 与 LangGraph](./Workflow与LangGraph.md)，上下文压缩集中在 [Context 工程](./Context工程.md)。

---

## 1. Agent 与其他范式的区别

### 四种范式对比

| 范式 | 结构 | 灵活性 | 可控性 | 适合场景 |
|------|------|--------|--------|---------|
| **单次 LLM 调用** | Input → LLM → Output | 低 | 高 | 问答、摘要、提取 |
| **链式调用（Chain）** | LLM → LLM → LLM | 中 | 高 | 固定多步骤处理 |
| **Workflow（图编排）** | 固定图结构，节点可含 LLM | 中 | 很高 | 业务流程自动化 |
| **Agent** | 循环：观察→规划→执行→观察 | 高 | 低 | 开放性任务、工具使用、自主探索 |

### Coding Agent 的实用判定维度

```
1. 目标导向：围绕任务推进，而不是只生成一次文本
2. 外部行动：能够调用工具、API、数据库、浏览器或其他执行环境
3. 状态与反馈：能读取中间结果，并据此修正下一步
4. 动态决策：至少有一部分路径由模型根据当前状态决定
```

这不是所有文献都统一采用的必要条件，而是本笔记学习 Coding Agent 时使用的工程定义。Agent 更适合被看成一个连续维度：从单次调用、固定 Workflow，到带工具和反馈的动态循环，边界取决于任务和系统设计。

---

## 2. Agent Loop 的完整结构

```
输入目标
   ↓
[感知 / Perception]
  - 读取当前状态
  - 读取工具执行结果
  - 读取外部信息（检索、数据库）
   ↓
[规划 / Planning]
  - LLM 基于当前状态推理下一步
  - 选择：调用工具 / 继续推理 / 请求人类确认 / 结束
   ↓
[执行 / Action]
  - 调用工具，获取结果
  - 更新状态
   ↓
[判断 / Termination]
  - 目标是否达成？
  - 是否遇到无法处理的失败？
  - 是否超过最大步数？
   ↓
完成 / 失败 / 请求人工介入
```

### Python 最小实现（OpenAI Chat Completions 示例）

下面特意把工具 schema 和 handler 分开；不同 Provider 的消息格式请看 [Tool Calling](./Tool%20Calling.md)。

```python
from typing import Any, Callable
from dataclasses import dataclass, field
import json
import os

from openai import OpenAI

client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # 教学占位值；实际模型名从配置读取

@dataclass
class AgentState:
    goal: str
    messages: list[dict[str, Any]] = field(default_factory=list)
    step: int = 0
    max_steps: int = 20

def run_agent(
    goal: str,
    tool_schemas: list[dict[str, Any]],
    tool_handlers: dict[str, Callable[..., Any]],
) -> str:
    state = AgentState(goal=goal)
    state.messages = [
        {"role": "system", "content": "你是一个助手，通过调用工具来完成用户目标。"},
        {"role": "user", "content": goal},
    ]

    while state.step < state.max_steps:
        state.step += 1

        response = client.chat.completions.create(
            model=MODEL,
            messages=state.messages,
            tools=tool_schemas,
        )

        msg = response.choices[0].message
        state.messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            return msg.content or ""

        for tool_call in msg.tool_calls:
            try:
                args = json.loads(tool_call.function.arguments)
                handler = tool_handlers[tool_call.function.name]
                result = {"ok": True, "data": handler(**args)}
            except KeyError:
                result = {"ok": False, "error": "未知工具"}
            except json.JSONDecodeError:
                result = {"ok": False, "error": "工具参数不是合法 JSON"}
            except Exception as e:
                result = {"ok": False, "error": f"工具执行失败: {type(e).__name__}: {e}"}

            state.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

    return "达到最大步数，任务未完成"
```

---

## 3. 主流 Agent 范式

### ReAct（Reasoning + Acting）

最基础的 Agent 范式。模型交替输出 Thought（推理）和 Action（动作）：

```
Thought: 用户想知道今天北京天气，我需要调用天气 API
Action: call_weather(city="Beijing")
Observation: {"temp": 28, "condition": "Sunny"}
Thought: 已经获取到天气，可以回答了
Action: finish(answer="今天北京天气晴，气温 28°C")
```

**优点**：简单、透明、容易 debug
**缺点**：不做长期规划，容易在复杂任务中迷失

### Plan-and-Execute

先生成完整计划，再逐步执行：

```
1. Planner LLM：把大目标分解成有序的子任务列表
2. Executor：逐个执行子任务
3. Replanner：如果某步失败，重新规划剩余步骤
```

**优点**：更适合需要长远规划的任务
**缺点**：初始计划可能不适应执行过程中发现的情况

### Router Agent

根据用户输入，把请求路由到不同的专门处理路径：

```
用户输入 → Router LLM（分类意图）
   ├── "代码问题" → Code Agent
   ├── "查询订单" → Order Agent
   ├── "投诉"     → Human Agent（人工介入）
   └── "其他"     → General Agent
```

**适合**：多领域客服、多能力系统、降低单个 Agent 复杂度。

### Reflection Agent

Agent 完成任务后，评估自己的输出，不满意就重来：

```
Task → Draft Answer → Critic LLM（评分 + 改进意见）→ 修改 → 再评估
```

**适合**：要求高质量输出的场景（代码生成、写作）
**注意**：成本高，可能陷入无限改进循环，必须设最大轮数。

### Multi-Agent

多个专门的 Agent 协作完成复杂任务：

```
Orchestrator Agent（协调者）
   ├── Research Agent（信息收集）
   ├── Analysis Agent（分析）
   ├── Writer Agent（写作）
   └── Reviewer Agent（审查）
```

**适合**：超出单个 context window 的长任务、需要并行处理的场景。
**注意**：协调开销大，错误会传播，不要轻易用——很多时候一个好的 ReAct Agent 已经够用。

---

## 4. 自主性与可控性的权衡

这是 Agent 设计中最核心的张力。

| 自主程度 | 人工介入点 | 适合场景 | 风险 |
|---------|-----------|---------|------|
| 全自动 | 无 | 低风险、可逆操作 | 无人监督，错误放大 |
| 半自动 | 关键决策节点 | 大多数生产场景 | 需要设计确认流程 |
| 辅助模式 | 每一步都人审 | 高风险操作（删数据、发邮件） | 效率低，但安全 |

### 为什么生产系统不做全自动 Agent

1. **错误成本高**：自动发邮件、改数据库、触发外部付费 API——出错影响真实用户
2. **可观测性差**：LLM 推理不透明，出了问题很难追因
3. **边界难以定义**：告诉模型"不要删数据"，但模型可能用间接方式绕过
4. **合规要求**：很多场景需要人工审批记录

**实际经验**：先从 Human-in-the-loop 开始，逐步观察失败模式，再有选择地自动化低风险步骤。

---

## 5. Human-in-the-loop 设计模式

Human-in-the-loop 的典型触发条件：
- 操作涉及真实副作用（发邮件、写数据库、调用外部付费 API）
- Agent 的置信度低（模型自己表达不确定）
- 超过预设成本阈值
- 处理敏感数据或个人信息

```python
### LangGraph 里的中断示例（详见 Workflow与LangGraph.md）
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

### `interrupt_before` 让图在这个节点前暂停，等待人工确认
compiled = graph.compile(
checkpointer=MemorySaver(),
interrupt_before=["sensitive_action_node"],
)
```

---

## 6. 终止条件设计

Agent 最容易出现的问题：无法正确终止。

```python
class TerminationCondition:
    def __init__(self, max_steps=20, max_cost_usd=1.0, max_tokens=100_000):
        self.max_steps = max_steps
        self.max_cost = max_cost_usd
        self.max_tokens = max_tokens

    def should_stop(self, state) -> tuple[bool, str]:
        if state.step >= self.max_steps:
            return True, f"超过最大步数 {self.max_steps}"
        if state.total_cost_usd > self.max_cost:
            return True, f"超过成本上限 ${self.max_cost}"
        if state.total_tokens > self.max_tokens:
            return True, "超过 token 限制"
        if state.consecutive_errors >= 3:
            return True, "连续失败 3 次，中止"
        return False, ""
```

**原则**：任何生产 Agent 都必须有最大步数、最大成本的硬性上限。

---

## 7. 状态设计

好的状态设计是 Agent 可维护的关键：

```python
from pydantic import BaseModel
from typing import Optional, Literal

class AgentState(BaseModel):
    goal: str
    task_id: str
    messages: list[dict] = []
    step: int = 0
    status: Literal["running", "waiting_human", "done", "failed"] = "running"
    tool_calls_log: list[dict] = []
    final_answer: Optional[str] = None
    error_message: Optional[str] = None
    total_tokens: int = 0
    total_cost_usd: float = 0.0
```

状态应该可序列化（Pydantic），方便：持久化到数据库、断点续传、审计和调试。

---

## 8. 常见设计错误

| 错误 | 问题 | 正确做法 |
|------|------|---------|
| 没有最大步数限制 | Agent 可能无限循环 | 强制设置 max_steps |
| 工具失败直接抛异常 | 一个工具失败整个 Agent 崩溃 | catch 异常，把错误作为 tool result 返回给模型 |
| 把所有工具都给 Agent | 模型选择困难，容易误用 | 按任务范围限制可用工具 |
| 不记录中间状态 | 出错后无法 debug | 每一步都 log state |
| system prompt 太简单 | 模型对任务边界不清楚 | 明确写出能做什么、不能做什么、何时请求人工 |
| 不处理工具幂等性 | 重试时副作用重复 | 工具要标注是否幂等 |

---

## 9. Harness 哲学：Harness = Model + Infrastructure

来自实际工程项目的核心认知，区分两件事：

```
模型能力        ← 来自训练和推理能力
Harness 行为    ← 由工具、环境、上下文、权限和反馈共同塑造
```

对 Coding Agent 而言，大多数工程工作确实是在构建 Harness，但不能把 Harness 理解成“只负责转发模型输出”。它决定模型能观察什么、能执行什么、遇到失败如何恢复，也会显著影响系统最终行为。

```
Harness = Tools + Knowledge + Observation + Action Interfaces + Permissions

Tools:       文件 I/O、shell、网络、数据库
Knowledge:   产品文档、API spec、代码库
Observation: git diff、错误日志、任务状态
Action:      CLI 命令、API 调用
Permissions: 沙箱、审批流程、信任边界
```

实际上大多数"Agent 平台"做的是 Harness，不是训练，认清这一点才能正确设计系统。

---

## 10. Hook 系统：跨切面关注点

当 Agent 需要在工具执行前后注入通用逻辑（日志、权限检查、输出摘要）时，Hook 系统是比 if-else 更清晰的模式：

```python
HOOKS = {
    "UserPromptSubmit": [],   # 用户提交输入后
    "PreToolUse": [],         # 工具执行前
    "PostToolUse": [],        # 工具执行后
    "Stop": [],               # Agent 结束时
}

def trigger_hooks(event: str, context: dict) -> str | None:
    """返回第一个非 None 值作为拦截信号"""
    for hook in HOOKS.get(event, []):
        result = hook(context)
        if result is not None:
            return result
    return None
```

**执行顺序实例**：用户输入一条消息，完整 Hook 触发顺序为：

```
UserPromptSubmit → [context_inject hook 运行]
   ↓
PreToolUse（第 1 个工具） → [permission hook + log hook 运行]
PostToolUse（第 1 个工具） → [large_output hook 运行]
PreToolUse（第 2 个工具） → ...
PostToolUse（第 2 个工具） → ...
Stop → [summary hook 运行]
```

Hook 与工具调用完全解耦，添加新的横切关注点（rate limiting、成本追踪）不需要修改工具代码。

---

## 11. Subagent 隔离模式

Multi-Agent 系统里，Subagent 隔离是保证 context 不污染父 Agent 的关键机制：

```python
def spawn_subagent(description: str) -> str:
    """Subagent 启动时只有一条消息，完全隔离"""
    messages = [{"role": "user", "content": description}]

    # SUB_TOOLS 排除 task 工具，防止递归 spawn
    response = client.messages.create(
        model=MODEL,
        tools=SUB_TOOLS,
        messages=messages,
        max_tokens=8096,
    )
    # 只返回最终文字摘要，中间历史完全丢弃
    return extract_final_text(response)
```

**关键设计决策**：
- Subagent 是全新的 context，不携带父 Agent 的任何历史
- 只返回 summary（文字），不返回中间的 tool_result 序列
- 排除某些工具（如再次 spawn 的能力），防止无限递归
- 父 Agent 的 context 保持 O(父消息) 不增长，Subagent 独自消耗 token

---

## 12. "模型输出永远不是执行权限"

这是 SafeCodeAgent Enterprise 中的一条安全不变量，也适合作为通用的工具执行原则：

> **Model output is a proposal, never execution authority.**

这一原则的实际含义：

```
❌ 错误认知：模型说"执行 rm -rf /tmp/data" → 直接执行
✅ 正确认知：模型说"执行 rm -rf /tmp/data" → 这是一个提案
              → 经过策略引擎检查
              → 经过权限层验证
              → 如果是变更操作，经过人工审批
              → 审批 Grant 绑定到该具体提案的摘要 hash
              → 才能真正执行
```

这个原则意味着：工具执行层必须有独立于模型的判断机制。模型的指令只是输入，不是授权。对应到代码层面：工具函数内部需要自己做权限检查，而不是相信"模型调用了我就肯定合法"。

---

## 13. Cron Scheduler 四层架构

Agent 需要定时自动执行任务时（每天报告、定时清理），Cron 调度的标准实现是四层解耦：

```
Layer 1: Scheduler（守护线程，每秒检查时间）
Layer 2: Queue（thread-safe 队列，解耦调度和执行）
Layer 3: Queue Processor（消费队列，唤醒 Agent）
Layer 4: Consumer（agent_loop 消费任务，注入 messages）
```

```python
import threading
import queue
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CronJob:
    id: str
    cron: str          # "0 9 * * 1-5"（5字段：分 时 日 月 周）
    prompt: str        # 注入 Agent 的指令
    recurring: bool    # True=重复，False=单次
    durable: bool      # True=持久化到磁盘，重启后恢复

cron_queue: queue.Queue = queue.Queue()
CRON_JOBS: dict[str, CronJob] = {}

def cron_matches(cron_expr: str, now: datetime) -> bool:
    """检查当前时间是否匹配 5 字段 cron 表达式"""
    minute, hour, dom, month, dow = cron_expr.split()
    cron_dow = (now.weekday() + 1) % 7  # Python: Monday=0；cron: Sunday=0
    base_match = (
        _field_match(minute, now.minute)
        and _field_match(hour, now.hour)
        and _field_match(month, now.month)
    )
    dom_match = _field_match(dom, now.day)
    dow_match = _field_match(dow, cron_dow)
    # 两个字段都受限时采用 OR；任一为 * 时，另一个字段必须匹配。
    day_match = (dom_match or dow_match) if dom != "*" and dow != "*" else (dom_match and dow_match)
    return base_match and day_match

def cron_scheduler_loop():
    """Layer 1: 守护线程，每秒轮询一次"""
    fired = set()  # 防止同一分钟内重复触发
    while True:
        now = datetime.now()
        minute_key = now.strftime("%Y%m%d%H%M")
        for job_id, job in list(CRON_JOBS.items()):
            key = f"{job_id}:{minute_key}"
            if key not in fired and cron_matches(job.cron, now):
                cron_queue.put(job)
                fired.add(key)
                if not job.recurring:
                    del CRON_JOBS[job_id]
        # 清理过期的 fired 记录（防内存泄漏）
        fired = {k for k in fired if k.endswith(minute_key)}
        time.sleep(1)

# 启动守护线程
threading.Thread(target=cron_scheduler_loop, daemon=True).start()

# Layer 4: agent_loop 顶部消费 cron 队列
def consume_cron_queue(messages: list):
    while not cron_queue.empty():
        job = cron_queue.get_nowait()
        messages.append({"role": "user", "content": f"[Cron] {job.prompt}"})
```

**守护线程（daemon=True）的含义**：主进程退出时，守护线程自动终止，不会阻止程序退出。

---

## 14. 卡死循环检测（Stuck-Loop Detection）

Agent 可能陷入循环——对同一个工具调用相同参数，无法前进：

```python
from collections import deque

class LoopStuckDetector:
    """检测连续相同的工具意图（3次 = 卡死）"""
    def __init__(self, threshold: int = 3):
        self.threshold = threshold
        self.recent_intents: deque = deque(maxlen=threshold)

    def _intent_key(self, tool_name: str, args: dict) -> str:
        """生成工具调用的身份标识（忽略无关字段）"""
        return f"{tool_name}:{json.dumps(args, sort_keys=True)}"

    def check(self, tool_name: str, args: dict) -> bool:
        """返回 True = 检测到卡死"""
        key = self._intent_key(tool_name, args)
        self.recent_intents.append(key)
        if len(self.recent_intents) == self.threshold:
            if len(set(self.recent_intents)) == 1:
                return True  # 所有最近意图都相同
        return False

# 在工具执行前检查
detector = LoopStuckDetector(threshold=3)

for block in response.content:
    if block.type == "tool_use":
        if detector.check(block.name, block.input):
            print(f"⚠️  检测到卡死循环：{block.name} 连续 3 次相同调用")
            # 注入提示让模型换思路
            messages.append({
                "role": "user",
                "content": f"[System] 工具 {block.name} 已连续调用相同参数 3 次，请换一种方法。"
            })
            break
```

---

## 15. Worktree 隔离（多 Agent 任务隔离）

多个 Agent 并行处理不同任务时，共用同一个工作目录会造成文件冲突。Git Worktree 给每个任务提供独立的文件系统视图：

```python
import subprocess
from pathlib import Path

WORKTREES_DIR = Path(".worktrees")

def create_worktree(name: str, task_id: str) -> str:
    """给任务创建独立的 git worktree，分支名: wt/{name}"""
    wt_path = WORKTREES_DIR / name
    if wt_path.exists():
        return f"Worktree '{name}' already exists"
    result = subprocess.run([
        "git", "worktree", "add",
        str(wt_path), "-b", f"wt/{name}"
    ], capture_output=True, text=True)
    if result.returncode != 0:
        return f"Error: {result.stderr}"
    return f"Created worktree: {wt_path} (branch: wt/{name})"

def remove_worktree(name: str, discard_changes: bool = False) -> str:
    """移除 worktree，可选丢弃未提交变更"""
    wt_path = WORKTREES_DIR / name
    if not wt_path.exists():
        return f"Worktree '{name}' not found"
    if not discard_changes:
        # 检查是否有未提交的变更
        r = subprocess.run(["git", "status", "--porcelain"], cwd=wt_path,
                           capture_output=True, text=True)
        if r.stdout.strip():
            return "Has uncommitted changes. Use discard_changes=True to force."
    subprocess.run(["git", "worktree", "remove", str(wt_path), "--force"])
    subprocess.run(["git", "branch", "-D", f"wt/{name}"])
    return f"Removed worktree '{name}'"
```

**场景**：Lead Agent 收到三个并行任务 → 为每个任务创建独立 worktree → 三个 Worker Agent 分别在自己的 worktree 里操作 → 完成后合并 → Lead 决定保留或丢弃。

---

## 16. Session Journal 与断点恢复

生产 Agent 需要在崩溃或审批中断后，从记录的执行历史中恢复状态，而不是从头来：

```python
import jsonlines

@dataclass
class JournalEvent:
    session_id: str
    step: int
    type: str        # "plan" | "step_result" | "typed_result"
    timestamp: str
    payload: dict

class AgentJournal:
    def __init__(self, journal_dir: Path):
        self.journal_dir = journal_dir

    def write(self, session_id: str, event: JournalEvent):
        """追加写入，不覆盖"""
        path = self.journal_dir / f"{session_id}.jsonl"
        with jsonlines.open(path, "a") as w:
            w.write(asdict(event))

    def read(self, session_id: str) -> list[JournalEvent]:
        """读取完整执行历史"""
        path = self.journal_dir / f"{session_id}.jsonl"
        if not path.exists():
            return []
        with jsonlines.open(path) as r:
            return [JournalEvent(**e) for e in r]

def resume_from_journal(session_id: str, journal: AgentJournal) -> AgentSessionState:
    """从 journal 重建 session 状态（不重新执行）"""
    events = journal.read(session_id)
    last_plan = None
    last_step = 0
    last_observation = ""
    pending_step = None

    for event in events:
        if event.type == "plan":
            last_plan = event.payload.get("plan")
        if event.type == "typed_result":
            last_step = event.step
            if event.payload.get("status") == "waiting_for_user":
                pending_step = event.step  # 在这里等待人工确认

    return AgentSessionState(
        session_id=session_id,
        plan=last_plan or DEFAULT_PLAN,
        current_step=pending_step if pending_step else last_step,
        status="waiting_for_user" if pending_step else "active",
    )
```

---

## 17. 执行前歧义检测（Pre-Task Clarification）

Agent 开始执行之前，先判断目标是否足够具体——模糊的指令会导致 Agent 方向错误：

```python
import re
from dataclasses import dataclass, field

# 具体性信号：包含文件路径、行号、函数名、测试名等
_SPECIFIC_PATTERNS = [
    re.compile(r"\b\w[\w/\\]+\.\w{1,6}\b"),       # 带扩展名的路径
    re.compile(r"\bline\s+\d+\b", re.IGNORECASE),  # "line 42"
    re.compile(r"\bdef\s+\w+|\bclass\s+\w+"),       # "def foo" / "class Bar"
    re.compile(r"\btest_\w+\b"),                    # 测试函数名
    re.compile(r"\b(TypeError|ValueError|ImportError)"),  # 具体错误类型
]

# 模糊动词（单独出现时需要追问）
_VAGUE_VERBS = frozenset({"fix", "update", "improve", "refactor", "clean", "add", "remove", "change"})

def _is_specific_enough(goal: str) -> bool:
    """启发式判断：目标是否具体到可以执行"""
    if len(goal) > 120:
        return True  # 长描述通常有足够细节
    for pattern in _SPECIFIC_PATTERNS:
        if pattern.search(goal):
            return True
    # 只有模糊动词 + 泛指词 = 太模糊
    words = {w.lower().strip(".,!?") for w in goal.split()}
    meaningful = words - _VAGUE_VERBS - {"the", "a", "an", "it", "this", "that"}
    return len(meaningful) >= 3

@dataclass(frozen=True)
class ClarificationResult:
    needs_clarification: bool
    questions: tuple[str, ...] = field(default_factory=tuple)

def clarify_if_needed(goal: str, llm_client) -> ClarificationResult:
    """先用启发式过滤，再用 LLM 判断是否需要追问"""
    if _is_specific_enough(goal):
        return ClarificationResult(needs_clarification=False)

    # 启发式认为模糊，再调用 LLM 确认（1次 API 调用，用便宜模型）
    response = llm_client.messages.create(
        model=FAST_MODEL,  # 用便宜模型做分类
        system=(
            "判断任务是否足够具体可执行。"
            "返回 JSON: {\"needs_clarification\": bool, \"questions\": [最多2个问题]}"
        ),
        messages=[{"role": "user", "content": goal}],
        max_tokens=200,
    )
    import json
    result = json.loads(extract_text(response.content))
    if result.get("needs_clarification") and result.get("questions"):
        return ClarificationResult(
            needs_clarification=True,
            questions=tuple(result["questions"][:2])
        )
    return ClarificationResult(needs_clarification=False)

# 在 agent_loop 开始前调用
clarification = clarify_if_needed(user_goal, client)
if clarification.needs_clarification:
    print("在开始之前，我需要了解更多：")
    for q in clarification.questions:
        print(f"  • {q}")
    # 等待用户回答后再继续
```

---

## 18. 写操作后自动验证 + 修复循环

每次 Agent 写完文件或执行了变更，自动运行测试套件验证正确性，失败后按类型生成修复提示：

```python
VALIDATION_ORDER = ("test", "lint", "typecheck", "build")

from enum import Enum

class RepairStrategy(str, Enum):
    SYNTAX_ERROR = "syntax_error"
    IMPORT_ERROR = "import_error"
    TEST_FAILURE = "test_failure"
    TYPE_ERROR   = "type_error"
    LINT_ERROR   = "lint_error"
    GENERIC      = "generic"

import re
_SYNTAX = re.compile(r"SyntaxError:|IndentationError:", re.IGNORECASE)
_IMPORT = re.compile(r"ModuleNotFoundError:|ImportError:|No module named", re.IGNORECASE)
_TYPE   = re.compile(r"TypeError:|mypy|pyright", re.IGNORECASE)
_LINT   = re.compile(r"ruff|flake8|E[0-9]{3,4}\b", re.IGNORECASE)
_TEST   = re.compile(r"FAILED tests/|AssertionError:|pytest", re.IGNORECASE)

def classify_failure(output: str, suite: str) -> RepairStrategy:
    """按优先级匹配：语法 > 导入 > 测试 > 类型 > lint > 通用"""
    if _SYNTAX.search(output): return RepairStrategy.SYNTAX_ERROR
    if _IMPORT.search(output): return RepairStrategy.IMPORT_ERROR
    if suite == "test" and _TEST.search(output): return RepairStrategy.TEST_FAILURE
    if _TYPE.search(output): return RepairStrategy.TYPE_ERROR
    if _LINT.search(output): return RepairStrategy.LINT_ERROR
    return RepairStrategy.GENERIC

REPAIR_INSTRUCTIONS = {
    RepairStrategy.SYNTAX_ERROR: (
        "修复策略：语法错误。\n"
        "1. 用 read_file 读取报错中提到的文件\n"
        "2. 定位语法错误行\n"
        "3. 只修改语法问题，不改其他代码"
    ),
    RepairStrategy.IMPORT_ERROR: (
        "修复策略：导入错误。\n"
        "1. 用 glob 或 bash grep 找到正确的模块路径\n"
        "2. 确认符号确实存在于该模块\n"
        "3. 只修改 import 语句"
    ),
    RepairStrategy.TEST_FAILURE: (
        "修复策略：测试失败。\n"
        "1. 仔细读 AssertionError 和 FAILED 行\n"
        "2. 理解期望值 vs 实际值\n"
        "3. 修复实现逻辑，而不是修改测试断言"
    ),
    # ...其他策略
}

def run_validation_and_repair(messages: list, client, max_repair: int = 2):
    """写操作后运行：test → lint → typecheck → build，失败后最多修复 N 次"""
    for suite in VALIDATION_ORDER:
        result = run_suite(suite)  # 实际运行测试命令
        if result.exit_code == 0:
            continue

        failure_output = (result.stdout + result.stderr)[-4000:]  # 只取最后 4000 字符
        strategy = classify_failure(failure_output, suite)
        instruction = REPAIR_INSTRUCTIONS.get(strategy, "检查失败原因并修复。")

        for attempt in range(max_repair):
            # 把失败信息 + 修复指导注入 messages，让模型修复
            messages.append({
                "role": "user",
                "content": f"[Validation Failed] Suite: {suite}\n{instruction}\n\nFail output:\n{failure_output}"
            })
            # 执行一轮 agent_loop（模型修复）
            agent_loop_one_turn(messages, client)

            result = run_suite(suite)
            if result.exit_code == 0:
                break  # 修复成功
```

**这个模式的价值**：Agent 写完代码不是终点，验证通过才算完成。失败时按错误类型给出定向修复指导，比让模型"自己看报错猜"效果好得多。

---

## learn-claude-code 对照：机制如何挂在同一个 Loop

`learn-claude-code` 的 s01-s20 很适合用来验证本篇的架构判断：每一章只增加一个 Harness 机制，但核心 `while True` 循环保持稳定。对应关系如下：

| 项目章节 | 机制 | 本篇应掌握的重点 |
|---|---|---|
| s01 | Agent Loop | 先追加 assistant 消息，再根据 tool-use 信号决定执行工具或结束；工具结果回到下一轮消息 |
| s04 | Hook | UserPromptSubmit、PreToolUse、PostToolUse、Stop 把扩展逻辑移出主循环 |
| s05-s06 | Todo / Subagent | 计划状态和子 Agent 上下文隔离；子 Agent 不继承递归派生能力，也不能绕过权限 |
| s11 | Error Recovery | 把重试、提高输出预算、响应式压缩和 fallback model 作为循环外的恢复层 |
| s20 | 综合 Harness | 工具、权限、Context、Memory、后台任务、团队和 MCP 都围绕同一个循环组合，而不是互相复制循环 |

阅读时重点对比 [s01_agent_loop/code.py](./实践/learn-claude-code/s01_agent_loop/code.py) 与 [s20_comprehensive/code.py](./实践/learn-claude-code/s20_comprehensive/code.py)：前者用于手写最小不变量，后者用于定位每个机制在循环前、循环中和循环后的挂载点。教学实现是 Python 单进程和简化状态，不应直接当作生产级并发、权限或持久化实现。

## ai-agent-learning 配套实践

- [Simple Agent Loop](./实践/ai-agent-learning/agent-learning-projects/05_simple_agent_loop/main.py)：最小 while loop、最大步数和工具观察结果。
- [LangGraph 基础图](./实践/ai-agent-learning/langgraph-advanced/01-basics/hello_graph.py)：把 Agent 的 State、Node、Edge 和条件路由显式化。
- [DevPilot 综合项目](./实践/ai-agent-learning/DevPilot/README.md)：把 Router、Analyzer、Fixer、Approval、Reviewer 和 PR Creator 组合成一个可控流程。

阅读 DevPilot 时重点看状态字段、节点职责和审批边界，不要只把它当成一个可以自动改代码的成品。

## 附录：面试高频

**Q：Agent 和 Workflow 的区别是什么？什么时候用 Agent，什么时候用 Workflow？**

> Workflow 的路径是设计时确定的：步骤 A → 步骤 B → 步骤 C，每步做什么由开发者写死。Agent 的路径是运行时由模型动态决定的：模型观察当前状态，自主决定下一步。如果任务流程相对固定，用 Workflow——更可预测、可控、可测试。如果任务路径本身就是不确定的，需要根据中间结果灵活调整，才用 Agent。生产环境里大多数"Agent 系统"实际上是 Workflow + 少量动态决策点的组合。

**Q：ReAct、Plan-and-Execute、Multi-Agent，各自适合什么场景？**

> ReAct 适合单目标、工具密集、步骤相对直线的任务。Plan-and-Execute 适合需要长期规划的复杂任务，先分解再执行，执行失败可以重新规划。Multi-Agent 适合任务复杂到单个 Agent 无法处理，或者需要并行执行多个子任务的场景。但 Multi-Agent 协调复杂度很高，不要盲目用。

**Q：为什么生产中的 Agent 不做全自动，要 Human-in-the-loop？**

> 三个核心原因：一是错误成本——自动发邮件、改数据库出错影响真实用户；二是可观测性——LLM 的决策不透明，出了问题很难追因，人在关键节点可以作为安全阀；三是合规和责任——很多业务场景需要明确的人工审批记录。Human-in-the-loop 不是不信任 AI，而是在技术成熟度和业务风险之间找到合理平衡。
