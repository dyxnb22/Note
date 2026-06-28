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
    
    # 加时间权重（最近的记忆更重要）
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

## 7. 面试高频

**Q：Memory 的几种类型，分别适合什么场景？**

> 通常分四类：一是 in-context memory，就是 messages 历史，当前会话内可见，受 context window 限制；二是会话级外部存储，用 Redis，跨请求但同一会话可见；三是长期用户记忆，跨会话的用户画像和偏好，需要向量库做语义召回；四是工作流状态，当前任务的执行进度，需要持久化到数据库支持断点续传。选哪种取决于记忆的时间范围和访问方式。

**Q：为什么不把所有历史对话都塞进 context？**

> 三个问题：成本（每次调用的 input token 线性增长）；质量（context 太长，模型对早期内容关注度下降，lost-in-the-middle 现象）；延迟（更多 token = 更慢的 TTFT）。正确做法是根据当前问题语义检索相关记忆，只注入真正需要的部分，而不是全量。

**Q：如果用户在不同会话说了相互矛盾的信息，怎么处理？**

> 策略：时间优先，后面说的通常覆盖之前的；用户明确修正时立即更新；对于模糊矛盾，保留两条并标注不确定，不要强行合并；对重要的长期记忆可以定期让用户确认。关键是记忆存储要有时间戳和来源字段，才有能力做冲突分析。
