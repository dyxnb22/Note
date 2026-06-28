# Agent 架构与设计

这篇文档解决一个问题：**Agent 究竟是什么，有哪些架构模式，怎么设计一个可靠的 Agent 系统**。

不是概念科普，而是要能回答：什么时候用 Agent、什么时候不用、各种模式的权衡是什么。

---

## 1. Agent 与其他范式的区别

### 四种范式对比

| 范式 | 结构 | 灵活性 | 可控性 | 适合场景 |
|------|------|--------|--------|---------|
| **单次 LLM 调用** | Input → LLM → Output | 低 | 高 | 问答、摘要、提取 |
| **链式调用（Chain）** | LLM → LLM → LLM | 中 | 高 | 固定多步骤处理 |
| **Workflow（图编排）** | 固定图结构，节点可含 LLM | 中 | 很高 | 业务流程自动化 |
| **Agent** | 循环：观察→规划→执行→观察 | 高 | 低 | 开放性任务、工具使用、自主探索 |

### Agent 的四个必要特征

```
1. 目标导向：有明确的目标或任务，不是单次问答
2. 工具使用：能调用外部工具（函数、API、数据库、浏览器）
3. 状态管理：在多步骤过程中维护中间状态
4. 自主循环：能自主决定下一步，直到目标达成或失败
```

没有工具的"Agent"只是多轮对话。
没有状态的"Agent"只是 pipeline。
没有循环的"Agent"只是一次调用。

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

### Python 最小实现

```python
from dataclasses import dataclass, field
import json

@dataclass
class AgentState:
    goal: str
    messages: list[dict] = field(default_factory=list)
    step: int = 0
    max_steps: int = 20
    done: bool = False

def run_agent(goal: str, tools: dict) -> str:
    state = AgentState(goal=goal)
    state.messages = [
        {"role": "system", "content": "你是一个助手，通过调用工具来完成用户目标。"},
        {"role": "user", "content": goal},
    ]
    
    while not state.done and state.step < state.max_steps:
        state.step += 1
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=state.messages,
            tools=list(tools.values()),
        )
        
        msg = response.choices[0].message
        
        if msg.tool_calls:
            state.messages.append(msg)
            
            for tool_call in msg.tool_calls:
                tool_fn = tools[tool_call.function.name]["fn"]
                args = json.loads(tool_call.function.arguments)
                
                try:
                    result = tool_fn(**args)
                except Exception as e:
                    result = f"Error: {e}"
                
                state.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })
        else:
            state.done = True
            return msg.content
    
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
# LangGraph 里的中断示例（详见 Workflow与LangGraph.md）
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

# interrupt_before 让图在这个节点前暂停，等待人工确认
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

## 9. 面试高频

**Q：Agent 和 Workflow 的区别是什么？什么时候用 Agent，什么时候用 Workflow？**

> Workflow 的路径是设计时确定的：步骤 A → 步骤 B → 步骤 C，每步做什么由开发者写死。Agent 的路径是运行时由模型动态决定的：模型观察当前状态，自主决定下一步。如果任务流程相对固定，用 Workflow——更可预测、可控、可测试。如果任务路径本身就是不确定的，需要根据中间结果灵活调整，才用 Agent。生产环境里大多数"Agent 系统"实际上是 Workflow + 少量动态决策点的组合。

**Q：ReAct、Plan-and-Execute、Multi-Agent，各自适合什么场景？**

> ReAct 适合单目标、工具密集、步骤相对直线的任务。Plan-and-Execute 适合需要长期规划的复杂任务，先分解再执行，执行失败可以重新规划。Multi-Agent 适合任务复杂到单个 Agent 无法处理，或者需要并行执行多个子任务的场景。但 Multi-Agent 协调复杂度很高，不要盲目用。

**Q：为什么生产中的 Agent 不做全自动，要 Human-in-the-loop？**

> 三个核心原因：一是错误成本——自动发邮件、改数据库出错影响真实用户；二是可观测性——LLM 的决策不透明，出了问题很难追因，人在关键节点可以作为安全阀；三是合规和责任——很多业务场景需要明确的人工审批记录。Human-in-the-loop 不是不信任 AI，而是在技术成熟度和业务风险之间找到合理平衡。
