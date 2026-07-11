# LLM 调用基础

这篇文档解决一个问题：**如何用 Python 正确、健壮、可维护地调用 LLM API**。

不只是"能跑起来"，而是：多轮对话、流式输出、结构化输出、错误处理、多 Provider 切换——都能做对。

---

## 1. 安装与初始化

```bash
pip install openai anthropic python-dotenv
```

密钥管理：
```python
## .env 文件（不提交 git）
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

```python
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()  # 自动从环境变量读取
```

**生产项目建议**：把 client 初始化封装在 `services/llm_client.py`，不要在业务代码里直接 import SDK。

---

## 2. Messages 结构

### Role 说明

| Role | 作用 | 何时使用 |
|------|------|---------|
| `system` / `developer` | 持久规则、身份、边界 | 每次对话开头，稳定不变 |
| `user` | 用户当前输入 | 每轮用户发言 |
| `assistant` | 模型历史回答 | 多轮对话时追加 |
| `tool` | 工具执行结果 | Tool Calling 场景 |

### Messages 设计原则

```python
messages = [
## system 设定稳定规则，不要把动态内容放这里
{"role": "system", "content": "你是一个代码审查助手。只分析 Python 代码。"},

## user 是当前输入
{"role": "user", "content": "帮我看看这段代码有没有问题"},

## 多轮时追加 assistant 历史
{"role": "assistant", "content": "这段代码有个问题：..."},

## 用户继续
{"role": "user", "content": "那如果我改成这样呢？"},
]
```

---

## 3. 基础调用

### 单轮调用

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
model="gpt-4o",
messages=[
    {"role": "system", "content": "你是一个 Python 助手。"},
    {"role": "user", "content": "解释一下 Python 的 GIL"},
],
temperature=0.3,
max_tokens=1000,
)

content = response.choices[0].message.content
```

### 多轮对话（维护历史）

```python
class Conversation:
def __init__(self, system_prompt: str, model: str = "gpt-4o"):
    self.model = model
    self.messages = [{"role": "system", "content": system_prompt}]

def chat(self, user_input: str) -> str:
    self.messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=self.model,
        messages=self.messages,
    )

    assistant_msg = response.choices[0].message.content
    self.messages.append({"role": "assistant", "content": assistant_msg})
    return assistant_msg
```

**注意**：messages 列表会无限增长，长对话需要截断策略（见 `Context工程.md`）。

---

## 4. 流式输出（Streaming）

```python
def stream_response(prompt: str):
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    stream=True,
)

full_content = ""
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
        full_content += delta

print()
return full_content
```

**async 版本（FastAPI / async 服务）**：

```python
async def stream_response_async(prompt: str):
async_client = AsyncOpenAI()
stream = await async_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    stream=True,
)

async for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        yield delta
```

---

## 5. 结构化输出

### 方法一：JSON Mode（简单场景）

```python
response = client.chat.completions.create(
model="gpt-4o",
messages=[
    {"role": "system", "content": "总是返回 JSON。"},
    {"role": "user", "content": "从这段文本里提取：姓名、年龄、职业"},
],
response_format={"type": "json_object"},
)

import json
data = json.loads(response.choices[0].message.content)
```

### 方法二：Pydantic 结构化（推荐）

```python
from pydantic import BaseModel
from typing import Optional

class ExtractedPerson(BaseModel):
name: str
age: Optional[int]
occupation: str
confidence: float

response = client.beta.chat.completions.parse(
model="gpt-4o",
messages=[
    {"role": "user", "content": "John Smith, 35 岁，软件工程师"},
],
response_format=ExtractedPerson,
)

person = response.choices[0].message.parsed
print(person.name, person.age)  # 类型安全，IDE 有补全
```

**为什么 Pydantic 比 JSON Mode 好**：JSON Mode 只保证合法 JSON，不保证字段名称和类型。Pydantic 结构化会把 schema 传给模型，输出不符合 schema 会被 reject。

---

## 6. Token 计算与成本意识

```python
response = client.chat.completions.create(...)

print(response.usage.prompt_tokens)      # 输入 token
print(response.usage.completion_tokens)  # 输出 token

## 估算成本（以 gpt-4o 为例，价格会变化）
input_cost = response.usage.prompt_tokens * 2.5 / 1_000_000
output_cost = response.usage.completion_tokens * 10 / 1_000_000
```

**工程建议**：开发时记录每次调用的 token 用量；长期跑的系统必须有 cost monitoring；system prompt 太长 = 每次调用都在烧钱。

---

## 7. 错误处理

```python
import openai
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
wait=wait_exponential(multiplier=1, min=2, max=10),
stop=stop_after_attempt(3),
reraise=True,
)
def call_llm(messages: list) -> str:
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    return response.choices[0].message.content

except openai.RateLimitError:
    raise  # tenacity 会自动重试

except openai.APIConnectionError:
    raise  # 重试

except openai.AuthenticationError:
    raise RuntimeError("API Key 无效，请检查 OPENAI_API_KEY")

except openai.BadRequestError as e:
    raise ValueError(f"请求格式错误: {e}")
```

### 常见错误对照表

| 错误类型 | 原因 | 处理方式 |
|---------|------|---------|
| `RateLimitError` | 超过速率限制 | 指数退避重试 |
| `APIConnectionError` | 网络超时 | 重试 + 超时设置 |
| `AuthenticationError` | Key 无效 | 不重试，报警 |
| `BadRequestError: context_length_exceeded` | 输入太长 | 截断 context 后重试 |
| `BadRequestError: content_policy` | 触发内容过滤 | 不重试，返回友好提示 |

---

## 8. 多 Provider 设计

```python
from typing import Protocol

class LLMProvider(Protocol):
def complete(self, messages: list[dict], **kwargs) -> str: ...

class OpenAIProvider:
def __init__(self, model: str = "gpt-4o"):
    self.client = OpenAI()
    self.model = model

def complete(self, messages, **kwargs) -> str:
    response = self.client.chat.completions.create(
        model=self.model, messages=messages, **kwargs,
    )
    return response.choices[0].message.content

class AnthropicProvider:
def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
    import anthropic
    self.client = anthropic.Anthropic()
    self.model = model

def complete(self, messages, **kwargs) -> str:
    system = next((m["content"] for m in messages if m["role"] == "system"), None)
    user_messages = [m for m in messages if m["role"] != "system"]
    response = self.client.messages.create(
        model=self.model, system=system,
        messages=user_messages, max_tokens=kwargs.get("max_tokens", 1024),
    )
    return response.content[0].text

def get_provider(name: str) -> LLMProvider:
providers = {
    "gpt-4o": OpenAIProvider("gpt-4o"),
    "gpt-4o-mini": OpenAIProvider("gpt-4o-mini"),
    "claude-sonnet": AnthropicProvider(),
}
return providers[name]
```

---

## 8.5 Fallback Model 切换（容灾）

生产环境主模型过载（529）时，自动切换到备用模型：

```python
PRIMARY_MODEL  = "claude-sonnet-4-6"
FALLBACK_MODEL = "claude-haiku-4-5"  # 更便宜、更快，质量略低

class ModelSelector:
    def __init__(self):
        self.current = PRIMARY_MODEL
        self.consecutive_529 = 0
        self.MAX_CONSECUTIVE_529 = 3

    def on_overloaded(self):
        self.consecutive_529 += 1
        if self.consecutive_529 >= self.MAX_CONSECUTIVE_529:
            if self.current == PRIMARY_MODEL:
                print(f"[429/529 x{self.MAX_CONSECUTIVE_529}] switching to fallback")
                self.current = FALLBACK_MODEL
                self.consecutive_529 = 0

    def on_success(self):
        self.consecutive_529 = 0
        # 可选：成功多次后切回主模型
        # self.current = PRIMARY_MODEL

selector = ModelSelector()

def call_with_fallback(messages: list, **kwargs):
    for attempt in range(10):
        try:
            resp = client.messages.create(model=selector.current, messages=messages, **kwargs)
            selector.on_success()
            return resp
        except Exception as e:
            if "overloaded" in str(e).lower() or "529" in str(e):
                selector.on_overloaded()
                wait = min(0.5 * (2 ** attempt), 32)
                time.sleep(wait)
                continue
            raise  # 非过载错误直接抛出
    raise RuntimeError("Max retries exceeded")
```

---

## 9. 多模态输入（Vision + PDF）

### 图片输入

Agent 可以接受图片作为输入（截图分析、图表理解、UI 检查等）：

```python
import base64
import anthropic

client = anthropic.Anthropic()

# 方式一：base64 编码（本地文件）
with open("screenshot.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",   # image/jpeg, image/gif, image/webp
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": "这张截图里有什么错误？",
                },
            ],
        }
    ],
)

# 方式二：URL（公开可访问的图片）
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": "https://example.com/chart.png",
                    },
                },
                {"type": "text", "text": "分析这个图表的趋势"},
            ],
        }
    ],
)
```

**图片规格**：
- 支持格式：JPEG、PNG、GIF、WebP
- 单张最大：5 MB（base64 前）
- 每次请求最多 20 张图
- 图片按 token 计费（约 1000-2000 token/张，取决于尺寸）

### PDF 文档输入

Claude 原生支持 PDF，不需要先提取文本：

```python
with open("technical_report.pdf", "rb") as f:
    pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                },
                {"type": "text", "text": "总结这份报告的核心结论"},
            ],
        }
    ],
)
```

**PDF 使用场景**：
- 合同、法律文件分析（保留原始格式和布局）
- 技术文档 QA
- 财务报告提取（包含图表和表格）
- 比先 OCR 再传文本质量更高（模型直接看 PDF 原始渲染）

### 多模态在 Agent Pipeline 中的应用

```python
def analyze_ui_screenshot(screenshot_path: str) -> dict:
    """Agent 工具：分析 UI 截图，返回结构化分析结果"""
    with open(screenshot_path, "rb") as f:
        img_data = base64.standard_b64encode(f.read()).decode("utf-8")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/png", "data": img_data},
                    },
                    {
                        "type": "text",
                        "text": """分析这个界面截图，返回 JSON：
{
  "errors": ["可见的错误信息列表"],
  "current_state": "当前界面状态描述",
  "suggested_action": "建议的下一步操作"
}""",
                    },
                ],
            }
        ],
    )
    import json
    return json.loads(response.content[0].text)
```

---

## 9.5 当前主流模型命名参考（2026 年）

笔记里其他地方可能出现旧版模型名，以此为准：

| 用途 | 当前模型 ID | 特点 |
|------|-----------|------|
| 主力（复杂任务） | `claude-sonnet-4-6` | 性能均衡，主力选择 |
| 旗舰（最强）| `claude-opus-4-7` | 最强，最贵 |
| 轻量（高吞吐）| `claude-haiku-4-5-20251001` | 最便宜，延迟低 |
| 推理任务 | `claude-sonnet-4-6` + `thinking` | Extended Thinking 场景 |

```python
# 推荐写法：用变量管理模型名，便于统一升级
PRIMARY_MODEL  = "claude-sonnet-4-6"
FLAGSHIP_MODEL = "claude-opus-4-7"
FAST_MODEL     = "claude-haiku-4-5-20251001"
```

---

## 10. Prompt Caching（成本优化）

Anthropic 和 OpenAI 支持对 system prompt 的 KV Cache 跨请求复用：

```python
response = anthropic_client.messages.create(
model="claude-3-5-sonnet-20241022",
system=[
    {
        "type": "text",
        "text": very_long_system_prompt,
        "cache_control": {"type": "ephemeral"},
    }
],
messages=[{"role": "user", "content": user_input}],
max_tokens=1024,
)

print(response.usage.cache_read_input_tokens)   # 命中的 token 数
```

**工程效益**：长 system prompt（>1K token）的场景，cache 命中可以节省 90% 的 input token 成本。

---

## 10. 面试高频

**Q：为什么要把 LLM 调用封装成 service，不直接在业务代码调用？**

> 统一管理密钥、重试、超时、日志，不用每个地方重复；测试时可以 mock 这一层；后续切换 Provider 或模型时只改一处；可以在这一层统一做 cost tracking 和 tracing。

**Q：流式输出（streaming）的技术原理是什么？**

> 模型 API 支持 Server-Sent Events（SSE），服务端每生成一个 token 就立即推送给客户端，不等全部生成完。客户端通过迭代 stream 对象逐块接收。对用户体验有显著改善——不用等 10-30 秒才看到任何输出。

**Q：结构化输出和 JSON Mode 有什么区别？**

> JSON Mode 只保证输出是合法 JSON，但不保证字段名称和类型。Pydantic 结构化输出会把 JSON Schema 传给模型，模型必须严格按 schema 生成，如果不符合会被 reject。后者更可靠，下游代码可以直接用，不需要额外验证。
