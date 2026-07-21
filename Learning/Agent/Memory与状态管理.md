# Memory 与状态管理

这篇文档解决一个问题：**如何让 AI 应用记住需要记住的东西，在正确的时机把正确的记忆带入 context**。

Memory 是生产系统里容易被低估的难题——入门级实现是"把历史消息全塞进 context"，这在实际中根本不够用。

---

## 1. 为什么 Memory 是独立问题

模型是无状态的（每次请求相互独立），所以要实现"记住用户"就需要在应用层处理：

```
问题 1：记什么？（不是所有内容都值得记）
问题 2：存在哪里？（context / 向量库 / 关系数据库）
问题 3：怎么召回？（每次都全量加载太贵）
问题 4：什么时候更新？（对话结束？实时？）
问题 5：脏信息怎么处理？（用户说了相互矛盾的事）
```

---

## 2. 四类 Memory

### 类型一：In-Context Memory（短期工作记忆）

```
存在：messages 列表里
范围：当前会话
特点：模型能直接"看到"，无延迟
限制：受 context window 约束
```

就是 messages 历史，超长时需要截断或压缩（见 `Context工程.md`）。

适合：当前任务需要的信息（最近几轮对话、当前任务状态）。

### 类型二：External Short-term Memory（会话存储）

```
存在：Redis，按 session_id 索引
范围：一次会话（可跨 HTTP 请求）
特点：持久化，不受 context 限制，设 TTL 自动过期
```

```python
import redis
import json

redis_client = redis.Redis(host="localhost", port=6379)

def save_session_state(session_id: str, state: dict, ttl: int = 3600):
redis_client.setex(
    f"session:{session_id}",
    ttl,
    json.dumps(state, ensure_ascii=False),
)

def load_session_state(session_id: str) -> dict:
data = redis_client.get(f"session:{session_id}")
return json.loads(data) if data else {}
```

适合：跨请求的会话状态（当前任务进度、临时用户偏好）。

### 类型三：Long-term User Memory（用户画像）

```
存在：向量数据库 + 关系数据库
范围：跨会话、跨时间
特点：需要按语义召回
更新：会话结束后提取
```

```python
from pydantic import BaseModel
from datetime import datetime

class UserMemoryItem(BaseModel):
content: str
category: str  # preference / fact / feedback / goal
source_session: str
created_at: datetime
importance: float  # 0-1

async def extract_memories_from_session(
session_messages: list[dict],
user_id: str,
) -> list[UserMemoryItem]:
"""从会话中提取值得长期记住的信息"""

prompt = """从以下对话中提取用户的长期偏好、重要事实、明确目标。
不要提取临时信息、一次性问题。以 JSON 数组格式返回。"""

memories = await llm_call_structured(
    prompt=prompt,
    context=format_messages(session_messages),
    output_schema=list[UserMemoryItem],
)

await store_user_memories(user_id, memories)
return memories
```

适合：用户画像、长期偏好、用户表达的目标。

### 类型四：Workflow State Memory（任务状态）

```
存在：数据库（需要持久化 + 可恢复）
范围：一个任务的完整生命周期
特点：结构化，有状态机转换
```

```python
from enum import Enum
from pydantic import BaseModel

class TaskStatus(Enum):
PENDING = "pending"
RUNNING = "running"
WAITING_HUMAN = "waiting_human"
COMPLETED = "completed"
FAILED = "failed"

class WorkflowState(BaseModel):
task_id: str
status: TaskStatus
steps_completed: list[str] = []
current_step: str = ""
artifacts: dict = {}        # 中间产出物
error_log: list[str] = []
created_at: datetime
updated_at: datetime
```

适合：长任务（代码生成、报告撰写、多步骤审批）的状态追踪。

---

## 3. 召回策略

| 召回方式 | 触发时机 | 实现 | 适合 |
|---------|---------|------|------|
| 全量加载 | 每次请求 | 直接注入 context | 记忆量小（<500 token） |
| 语义检索 | 每次请求前检索 | 向量相似度 | 大量用户记忆 |
| 时间窗口 | 加载最近 N 条 | SQL ORDER BY time | 时序重要场景 |
| 重要性排序 | 加载评分最高的 | 重要性字段 | 混合策略 |

```python
async def retrieve_relevant_memories(
user_id: str,
current_query: str,
top_k: int = 5,
) -> list[UserMemoryItem]:
query_embedding = await embed(current_query)

results = await vector_store.search(
    collection=f"user_memory_{user_id}",
    vector=query_embedding,
    top_k=top_k,
)

## 加时间权重（最近的记忆更重要）
scored = []
for item in results:
    days_ago = (datetime.utcnow() - item.created_at).days
    recency_score = max(0, 1 - days_ago / 365)
    combined = 0.7 * item.relevance_score + 0.3 * recency_score
    scored.append((combined, item))

scored.sort(reverse=True)
return [item for _, item in scored[:top_k]]
```

---

## 4. 更新策略

| 时机 | 优点 | 缺点 | 适合 |
|------|------|------|------|
| 实时（每轮对话后） | 记忆最新 | 频繁写入，延迟高 | 重要状态 |
| 会话结束后批量提取 | 有完整上下文，质量高 | 会话中不可用 | 长期记忆 |
| 定时任务 | 计算资源集中 | 延迟高 | 分析类记忆 |
| 触发式（用户明确表达） | 精准 | 需要意图检测 | 用户主动更新偏好 |

---

## 5. 脏信息与冲突处理

用户在不同时间说了相互矛盾的话：

```python
async def handle_memory_conflict(
existing: UserMemoryItem,
new_info: str,
) -> str:
"""判断如何处理新旧记忆的冲突"""
resolution = await llm_call([
    {
        "role": "system",
        "content": "判断两条用户信息是否矛盾。如果矛盾，判断新信息是否应该覆盖旧信息。",
    },
    {
        "role": "user",
        "content": f"旧信息（{existing.created_at.date()}）：{existing.content}\n新信息：{new_info}\n\n判断：覆盖/合并/保留两者",
    },
])
return resolution
```

**实践原则**：
- 有明确时间戳时，新信息优先于旧信息
- 用户主动修正（"我之前说错了"）立即更新
- 模糊矛盾时：保留两条并标注不确定，不要强行合并

---

## 6. 会话恢复

```python
async def resume_workflow(task_id: str) -> WorkflowState:
state = await db.get_workflow_state(task_id)

if state.status == TaskStatus.FAILED:
    last_success = state.steps_completed[-1] if state.steps_completed else None
    if last_success:
        state.status = TaskStatus.RUNNING
        state.current_step = get_next_step(last_success)
        await db.save_workflow_state(state)

return state
```

---

## 7. 文件型 Memory：MEMORY.md 索引模式

对于 CLI/本地 Agent，向量数据库往往过重。一种轻量可行的方案：文件系统 + MEMORY.md 索引。

```
memory/
├── MEMORY.md              ← 索引文件，每行一个指针（始终注入 System Prompt）
├── user_preferences.md    ← 具体记忆文件
├── feedback_testing.md
└── project_context.md
```

**MEMORY.md 格式**：

```markdown
# Memory Index
- [用户偏好](user_preferences.md) — 用户是高级 Go 工程师，React 新手
- [测试反馈](feedback_testing.md) — 集成测试必须用真实数据库，不用 mock
- [项目背景](project_context.md) — 当前重构由合规要求驱动，不是技术债
```

**每个记忆文件的结构**（frontmatter + 正文）：

```markdown
---
name: feedback-testing
description: 关于测试策略的用户反馈
metadata:
  type: feedback
---

集成测试必须用真实数据库，不用 mock。

**Why:** 上季度发生过 mock 测试通过但生产 migration 失败的事故。
**How to apply:** 每次写测试时检查：有没有 mock 了数据库？
```

**记忆类型**：
| 类型 | 存什么 | 示例 |
|------|--------|------|
| `user` | 用户角色、技能水平、偏好 | "是 Go 专家，React 新手" |
| `feedback` | 用户对行为的修正或肯定 | "不要在回答末尾总结你刚做了什么" |
| `project` | 当前工作的背景和决策 | "重构由合规要求驱动，截止日期 2026-07-01" |
| `reference` | 外部系统的位置指针 | "bug 追踪在 Linear 项目 INGEST" |

**注入时机**：

```python
def build_system(memory_dir: Path) -> str:
    """每次用户消息到来时调用一次，重新构建 System Prompt"""
    index = read_memory_index(memory_dir / "MEMORY.md")
    # 只把 MEMORY.md 注入，不全量加载每个记忆文件
    return f"{BASE_PROMPT}\n\n## 记忆索引\n{index}"
```

关键时序：`build_system()` 在 `while True` 之前调用（每次用户消息一次），意味着**本次对话中新写入的记忆，要到下一条用户消息才能进入 System Prompt**。

---

## 8. 对话摘要作为 Memory 压缩

长对话不能全量保存，但全量摘要又损失细节。分层摘要是生产可行的方案：

```python
async def compress_conversation_to_memory(
    messages: list[dict],
    keep_recent_n: int = 6,
) -> tuple[str, list[dict]]:
    """
    把旧对话压缩成摘要 memory，保留最近 N 轮原文
    返回：(摘要字符串, 保留的最近消息)
    """
    if len(messages) <= keep_recent_n * 2:
        return "", messages   # 不需要压缩

    to_compress = messages[:-keep_recent_n * 2]
    recent = messages[-keep_recent_n * 2:]

    summary = await llm_call([
        {
            "role": "system",
            "content": (
                "请把以下对话摘要成一段话，保留：\n"
                "1. 用户的核心诉求和目标\n"
                "2. 已经完成的关键决策\n"
                "3. 用户表达的重要偏好或约束\n"
                "不需要保留：聊天寒暄、重复的确认、临时性讨论"
            )
        },
        {
            "role": "user",
            "content": "\n".join(
                f"{m['role']}: {m['content']}" for m in to_compress
            )
        }
    ])

    return summary, recent


async def build_messages_with_memory(
    new_input: str,
    conversation_id: str,
    system_prompt: str,
) -> list[dict]:
    """构建带历史摘要的 messages 列表"""
    raw_history = await load_conversation(conversation_id)
    summary, recent = await compress_conversation_to_memory(raw_history)

    messages = []

    # 如果有历史摘要，注入到 system prompt 末尾
    if summary:
        messages.append({
            "role": "user",
            "content": f"[之前对话摘要]\n{summary}\n[/之前对话摘要]"
        })
        messages.append({"role": "assistant", "content": "好的，我已了解之前的对话背景。"})

    # 追加最近几轮原文
    messages.extend(recent)
    # 追加当前输入
    messages.append({"role": "user", "content": new_input})
    return messages
```

**分层策略**：

```
Level 1（最近 6 轮）：原文保留，模型能精确引用
Level 2（之前的对话）：LLM 摘要，保留关键信息
Level 3（更早/跨会话）：关键 fact 提取，存入向量 memory
```

---

## 9. Memory 注入模式

Memory 怎么放进 context 影响模型的注意力分配：

```python
# 模式一：放在 system prompt 末尾（推荐，优先级高）
system_prompt = f"""
你是用户的个人助手。

## 关于用户的记忆
{user_memories}

## 你的能力和限制
{capabilities}
"""

# 模式二：作为 user/assistant 对话预填充（模拟"之前聊过"）
def inject_as_history(memories: list[str]) -> list[dict]:
    return [
        {"role": "user", "content": "（回顾一下我们之前讨论的内容）"},
        {"role": "assistant", "content": "\n".join(f"- {m}" for m in memories)},
    ]

# 模式三：XML 标签标注（清晰区分 memory 和对话内容）
memory_block = "<memory>\n" + "\n".join(memories) + "\n</memory>"
```

**注入位置对质量的影响**：

| 位置 | 模型注意力 | 适合 |
|------|-----------|------|
| System prompt 开头 | 最高 | 永久规则、身份定义 |
| System prompt 末尾 | 高 | 用户 memory、当前任务背景 |
| 历史消息开头 | 中 | 长期 memory（模拟历史对话）|
| 历史消息末尾（紧挨当前输入）| 高 | 短期工作记忆 |

**按 token 预算分配 memory**：

```python
def select_memories_for_budget(
    all_memories: list[dict],
    budget_tokens: int = 2000,
) -> list[dict]:
    """按重要性+相关性排序，贪心填入 budget"""
    selected, used = [], 0
    for m in sorted(all_memories, key=lambda x: x["score"], reverse=True):
        cost = len(m["content"]) // 4   # 粗估 token 数
        if used + cost > budget_tokens:
            break
        selected.append(m)
        used += cost
    return selected
```

---

## 10. 企业级 Memory 生命周期管理

文件型 Memory 无法满足多用户、合规、审计要求时，需要完整的 Memory 治理：

```
Memory 的生命周期：
  Admission（准入）→ Active（活跃）→ Revocation（撤销）→ Expiry（过期）

准入控制：
- 新记忆必须经过策略审查，不能直接写入
- 涉及敏感数据的记忆需要管理员批准

撤销机制：
- 记忆可以被明确撤销（用户主动或管理员操作）
- 撤销后不立即删除，而是标记为 revoked，保留审计轨迹

过期机制：
- 设置 TTL，过期记忆不再注入 context
- 重要记忆可以定期让用户确认续期
```

```python
class ManagedMemory:
    content: str
    category: str
    admitted_at: datetime
    admitted_by: str  # 谁批准的
    expires_at: datetime | None
    revoked_at: datetime | None = None
    revoked_by: str | None = None

def get_active_memories(user_id: str) -> list[ManagedMemory]:
    now = datetime.utcnow()
    return [
        m for m in load_memories(user_id)
        if m.revoked_at is None
        and (m.expires_at is None or m.expires_at > now)
    ]
```

---

## learn-claude-code 对照：选择、提取、整理三段式 Memory

s09 的实现把 Memory 分成三个动作：

1. **选择**：根据当前任务只加载相关记忆，而不是把整个 `.memory/` 目录塞进 prompt；
2. **提取**：一轮结束后从对话中提取用户偏好、反馈、项目背景和参考位置等长期信息；
3. **整理**：低频合并、去重和更新索引，避免记忆文件持续膨胀。

它采用 `MEMORY.md` 索引 + 类型化 Markdown 文件的轻量存储。这个模式适合本地 Coding Agent，但生产环境还要补并发锁、租户隔离、敏感信息过滤、删除/导出和记忆冲突处理。项目里的 forked extractor、Dream 整理和 side-query 都是实现思路，不是必须照搬的框架。对应实验：[s09_memory/code.py](./实践/learn-claude-code/s09_memory/code.py)。

## ai-agent-learning 配套实践

- [LangGraph Memory Agent](./实践/ai-agent-learning/agent-learning-projects/09_langgraph_memory_agent/README.md)：观察 `messages`、结构化 State、MemorySaver 和 `thread_id` 的关系。
- [Advanced Memory 实验](./实践/ai-agent-learning/langgraph-advanced/03-memory/memory_agent.py)：对照更小的 Checkpointer 示例，验证同一线程恢复状态、不同线程隔离状态。

这两组代码主要演示短期会话状态；长期 Memory、召回、冲突和生命周期治理仍以本篇理论为准。

## 附录：面试高频

**Q：Memory 的几种类型，分别适合什么场景？**

> 通常分四类：一是 in-context memory，就是 messages 历史，当前会话内可见，受 context window 限制；二是会话级外部存储，用 Redis，跨请求但同一会话可见；三是长期用户记忆，跨会话的用户画像和偏好，需要向量库做语义召回；四是工作流状态，当前任务的执行进度，需要持久化到数据库支持断点续传。选哪种取决于记忆的时间范围和访问方式。

**Q：为什么不把所有历史对话都塞进 context？**

> 三个问题：成本（每次调用的 input token 线性增长）；质量（context 太长，模型对早期内容关注度下降，lost-in-the-middle 现象）；延迟（更多 token = 更慢的 TTFT）。正确做法是根据当前问题语义检索相关记忆，只注入真正需要的部分，而不是全量。

**Q：如果用户在不同会话说了相互矛盾的信息，怎么处理？**

> 策略：时间优先，后面说的通常覆盖之前的；用户明确修正时立即更新；对于模糊矛盾，保留两条并标注不确定，不要强行合并；对重要的长期记忆可以定期让用户确认。关键是记忆存储要有时间戳和来源字段，才有能力做冲突分析。
