# LLM 调用基础

这篇文档解决一个问题：**如何用 Python 正确、健壮、可维护地调用 LLM API**。

不只是"能跑起来"，而是：多轮对话、流式输出、结构化输出、错误处理、多 Provider 切换——都能做对。

> **职责边界**：本文负责 Provider/API 适配、消息格式、流式、结构化输出、usage 和调用级恢复。Context 的构造、压缩和注入策略见 [Context 工程](./04_Context工程.md)，工具合同与执行边界见 [Tool Calling](./02_Tool%20Calling.md)。

---

## 1. 安装与初始化

```bash
pip install openai anthropic python-dotenv
```

密钥管理：
```dotenv
# .env 文件（不提交 git）
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

## 2. Messages 与 Items

Chat Completions 和 Anthropic Messages 主要围绕 messages/blocks 组织上下文；OpenAI Responses 使用 `input` / `output` typed Items，一条 message、一次 reasoning、一次 function call 都是不同 Item。下面的 role 表用于理解兼容 messages 输入，不代表所有 Provider 的完整线协议。

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

```pseudocode
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
**注意**：messages 列表会无限增长，长对话需要截断策略（见 `04_Context工程.md`）。

---

## 4. 流式输出（Streaming）

```pseudocode
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

```pseudocode
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

### 方法一：JSON Mode（旧接口兼容）

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

### 方法二：Responses + Pydantic 结构化（推荐）

```pseudocode
from pydantic import BaseModel
from typing import Optional

class ExtractedPerson(BaseModel):
name: str
age: Optional[int]
occupation: str
confidence: float

response = client.responses.parse(
model=os.environ["OPENAI_MODEL"],
input=[
    {"role": "user", "content": "John Smith, 35 岁，软件工程师"},
],
text_format=ExtractedPerson,
)

person = response.output_parsed
print(person.name, person.age)  # 类型安全，IDE 有补全
```
**为什么 Structured Outputs 比 JSON Mode 好**：JSON Mode 只保证合法 JSON，不保证字段名称和类型；Structured Outputs 按 schema 约束字段，并能让 SDK 解析成类型对象。仍要处理拒绝、截断、业务约束和下游权限。

---

## 6. Token 计算与成本意识

```python
response = client.responses.create(...)

print(response.usage.input_tokens)
print(response.usage.output_tokens)

# 单价必须来自带核对日期的版本化配置，不能写死在教程或业务逻辑中
input_cost = response.usage.input_tokens * pricing.input_per_token
output_cost = response.usage.output_tokens * pricing.output_per_token
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

```pseudocode
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

图片格式、单张大小、每请求数量和 token 计算都属于 Provider 与模型能力，上传前按官方 Vision 指南校验；客户端也应先限制 MIME、像素、文件大小和解码资源，不能只依赖 API 拒绝。

### PDF 文档输入

部分 Claude 模型和请求形态支持直接提交 PDF；这不表示所有模型、平台或文档都能保留同等布局理解，运行前检查模型能力，并为扫描件、超大文件和敏感内容保留提取或拒绝路径：

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

## 9.6 可测试的 Provider 适配边界（注释版）

把 Provider SDK 包在一个很薄的适配层里，Agent 层只依赖自己的结果类型。这样可以把“超时、空响应、可重试错误”等边界写成单元测试，而不是散落在业务代码中。

下面是一个可运行的 Python 3.11 结构示意；`Provider` 是协议，具体厂商 SDK 需要在适配器中实现它。

```python
import asyncio
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ProviderResult:
    """统一后的模型结果；Agent 不需要知道底层 SDK 的字段名。"""

    text: str | None
    tool_calls: list[dict[str, Any]]
    request_id: str | None = None  # 用于把模型调用和日志/账单关联起来。


class Provider(Protocol):
    async def complete(self, *, messages: list[dict[str, str]]) -> ProviderResult:
        """厂商适配器必须提供的最小接口。"""


class LLMCallError(RuntimeError):
    """让上层按稳定错误码处理，而不是匹配厂商异常文本。"""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


async def call_model(
    provider: Provider,
    messages: list[dict[str, str]],
    *,
    timeout_s: float = 30.0,
) -> ProviderResult:
    # 超时必须在调用边界处理，避免一次卡住拖垮整个 Agent 请求。
    try:
        result = await asyncio.wait_for(
            provider.complete(messages=messages),
            timeout=timeout_s,
        )
    except TimeoutError as exc:
        raise LLMCallError("provider_timeout") from exc

    # 空文本且没有工具调用通常不是有效的 Agent 步骤；尽早失败便于重试或降级。
    if not result.text and not result.tool_calls:
        raise LLMCallError("empty_provider_response")
    return result
```

这个边界还应至少覆盖三类测试：Provider 超时会被转换为稳定错误码；空响应不会进入下一轮循环；合法的工具调用不会被误判为空响应。重试策略建议放在更上层统一实现，并使用请求级幂等键，避免适配器和 Agent 各自重试造成倍增。

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

**工程效益**：长而稳定的前缀更容易从缓存受益，但命中条件、最低长度、保留时间和折扣会变化。用真实 usage 与账单验证收益，不在教程里承诺固定节省比例。

---

## learn-claude-code 对照：错误恢复不是一个 retry 装饰器

s11 把模型调用失败分成不同恢复路径：临时限流或服务错误走指数退避；输出被截断时提高输出预算或请求 continuation；上下文超限时先做 reactive compact；连续失败时才考虑 fallback model。每条路径都需要上限、transition 原因和最终可诊断错误，不能无限重试。

s20 把恢复层包在主循环外，使工具分发逻辑不必知道 429、529、输出预算和 prompt-too-long 的细节。对应实验：[s11_error_recovery/code.py](./实践/learn-claude-code/s11_error_recovery/code.py) 和 [s20_comprehensive/code.py](./实践/learn-claude-code/s20_comprehensive/code.py)；项目中的模型名、错误码和阈值只作为版本化示例，实际接入时以 Provider 文档为准。

## 官方来源

- [OpenAI Responses 迁移](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Anthropic Messages API](https://platform.claude.com/docs/en/api/messages)

核对日期：2026-07-30。模型、媒体限制、缓存条件、错误类型和存储默认值在部署或升级前重新核对。
