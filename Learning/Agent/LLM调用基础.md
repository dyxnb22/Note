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

新项目优先使用 Responses API；下文较长的 Chat Completions 片段保留为兼容参考。模型 ID 不在教程里固定，统一通过环境变量显式指定；当前选型基线见 [版本与来源](./版本与来源.md)。

### 单轮调用

```python
import os
from openai import OpenAI

client = OpenAI()
model = os.environ["OPENAI_MODEL"]

response = client.responses.create(
    model=model,
    instructions="你是一个 Python 助手。",
    input="解释一下 Python 的 GIL",
)

content = response.output_text
```

### 多轮对话（维护历史）

```text
class Conversation:
def __init__(self, system_prompt: str, model: str):
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

```text
def stream_response(prompt: str):
stream = client.chat.completions.create(
    model=MODEL,
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

```text
async def stream_response_async(prompt: str):
async_client = AsyncOpenAI()
stream = await async_client.chat.completions.create(
    model=MODEL,
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
model=MODEL,
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

```text
from pydantic import BaseModel
from typing import Optional

class ExtractedPerson(BaseModel):
name: str
age: Optional[int]
occupation: str
confidence: float

response = client.beta.chat.completions.parse(
model=MODEL,
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

# 估算成本（示例价格会变化，生产环境读取版本化配置）
input_cost = response.usage.prompt_tokens * 2.5 / 1_000_000
output_cost = response.usage.completion_tokens * 10 / 1_000_000
```

**工程建议**：开发时记录每次调用的 token 用量；长期跑的系统必须有 cost monitoring；system prompt 太长 = 每次调用都在烧钱。

---

## 7. 错误处理

```python
import openai
import os
from tenacity import retry, wait_exponential, stop_after_attempt

MODEL = os.environ["OPENAI_MODEL"]  # 显式配置，避免无意使用过期默认值

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True,
)
def call_llm(messages: list) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL,
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

```text
from typing import Protocol

class LLMProvider(Protocol):
def complete(self, messages: list[dict], **kwargs) -> str: ...

class OpenAIProvider:
def __init__(self, model: str):
    self.client = OpenAI()
    self.model = model

def complete(self, messages, **kwargs) -> str:
    response = self.client.chat.completions.create(
        model=self.model, messages=messages, **kwargs,
    )
    return response.choices[0].message.content

class AnthropicProvider:
def __init__(self, model: str):
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
    "primary": OpenAIProvider(settings.primary_model),
    "fast": OpenAIProvider(settings.fast_model),
    "anthropic": AnthropicProvider(settings.anthropic_model),
}
return providers[name]
```

---

## 8.5 Fallback Model 切换（容灾）

生产环境主模型过载（529）时，自动切换到备用模型：

```python
PRIMARY_MODEL = settings.primary_model
FALLBACK_MODEL = settings.fallback_model  # 更便宜、更快，质量略低

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
    model=PRIMARY_MODEL,
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
    model=PRIMARY_MODEL,
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
    model=PRIMARY_MODEL,
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
        model=PRIMARY_MODEL,
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

## 9.5 模型选择与版本管理

模型 ID、能力、价格和可用区域不是稳定知识，不在正文维护“当前最佳模型”榜单。把主力、轻量和回退模型作为部署配置，并对每次替换运行同一套质量、安全、延迟与成本回归。官方入口与升级检查见 [版本与来源](版本与来源.md)。

---

## 10. Prompt Caching（成本优化）

Anthropic 和 OpenAI 支持对 system prompt 的 KV Cache 跨请求复用：

```python
response = anthropic_client.messages.create(
model=settings.anthropic_model,
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

## learn-claude-code 对照：错误恢复不是一个 retry 装饰器

s11 把模型调用失败分成不同恢复路径：临时限流或服务错误走指数退避；输出被截断时提高输出预算或请求 continuation；上下文超限时先做 reactive compact；连续失败时才考虑 fallback model。每条路径都需要上限、transition 原因和最终可诊断错误，不能无限重试。

s20 把恢复层包在主循环外，使工具分发逻辑不必知道 429、529、输出预算和 prompt-too-long 的细节。对应实验：[s11_error_recovery/code.py](./实践/learn-claude-code/s11_error_recovery/code.py) 和 [s20_comprehensive/code.py](./实践/learn-claude-code/s20_comprehensive/code.py)；项目中的模型名、错误码和阈值只作为版本化示例，实际接入时以 Provider 文档为准。

## ai-agent-learning 配套实践

- [03 OpenAI CLI Chat](./实践/ai-agent-learning/agent-learning-projects/03_openai_cli_chat/README.md)：观察 `messages`、system/user/assistant 和多轮上下文。
- [12 Claude API Agent](./实践/ai-agent-learning/agent-learning-projects/12_claude_api_agent/main.py)：对照原生 Anthropic SDK、Streaming、Tool Use 和 Prompt Caching。
- [LangGraph Eval 实验](./实践/ai-agent-learning/langgraph-advanced/07-eval/eval_agent.py)：把模型调用和工具轨迹放进规则检查、关键词检查和 LLM-as-Judge 的评测框架。

这些实践中的 Provider、模型名、依赖版本和缓存参数都是课程示例；运行前按当前 Provider 文档核对。

## 附录：面试高频

**Q：为什么要把 LLM 调用封装成 service，不直接在业务代码调用？**

> 统一管理密钥、重试、超时、日志，不用每个地方重复；测试时可以 mock 这一层；后续切换 Provider 或模型时只改一处；可以在这一层统一做 cost tracking 和 tracing。

**Q：流式输出（streaming）的技术原理是什么？**

> 模型 API 支持 Server-Sent Events（SSE），服务端每生成一个 token 就立即推送给客户端，不等全部生成完。客户端通过迭代 stream 对象逐块接收。对用户体验有显著改善——不用等 10-30 秒才看到任何输出。

**Q：结构化输出和 JSON Mode 有什么区别？**

> JSON Mode 只保证输出是合法 JSON，但不保证字段名称和类型。Pydantic 结构化输出会把 JSON Schema 传给模型，模型必须严格按 schema 生成，如果不符合会被 reject。后者更可靠，下游代码可以直接用，不需要额外验证。
