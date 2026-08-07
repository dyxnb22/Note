# LLM 调用基础

这篇文章只解决一件事：**把模型 API 调用封装成可靠的应用边界**。读完应能处理消息、流式、结构化输出、用量、错误和 Provider 替换。

> **学习位置**：这是 Agent 主线的第 1 篇。Context 的装配与压缩见 [Context 工程](./04_Context工程.md)，工具合同与执行见 [Tool Calling](./02_Tool%20Calling.md)。
>
> **职责边界**：本文负责 Provider/API 适配和调用级恢复；不维护 Agent Loop、工具权限、完整成本系统或部署 runbook。

## 1. 配置和客户端

```bash
pip install openai anthropic python-dotenv pydantic
```

```dotenv
# .env 不提交 git；生产环境改用 Secret Manager 或受控环境注入。
OPENAI_API_KEY=...
OPENAI_MODEL=...
```

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
model = os.environ["OPENAI_MODEL"]  # 模型 ID 由部署配置提供，不写死在业务逻辑中。
```

客户端初始化应集中在适配层，业务代码只依赖自己的接口；这样密钥、超时、重试、usage 和 Provider 替换不会散落在各处。

## 2. 消息和 Provider 合同

不同 API 的外形不同，但 Agent 需要的最小信息相同：

| 信息 | 作用 |
|---|---|
| 持久指令 | 角色、边界和输出合同；不要把每轮动态数据硬编码进去 |
| 用户输入 | 当前目标和用户提供的数据 |
| Assistant/Reasoning 结果 | 多轮状态或模型提出的下一步 |
| Tool 结果 | 外部执行器返回的事实或错误 |
| Usage/Request ID | 成本、限流、Trace 和重放关联 |

OpenAI Responses 使用 typed Items；Chat Completions 和 Anthropic Messages 使用不同的 messages/blocks 形状。不要在业务层直接拼接某个 Provider 的原始字段，先转换成内部结果类型。

```python
messages = [
    # 稳定规则和权限边界；动态资料应由 Context 层装配。
    {"role": "system", "content": "你是只读代码分析助手。"},
    {"role": "user", "content": "分析这个函数的错误。"},
]
```

## 3. 最小调用和会话历史

新项目优先使用当前 Provider 的推荐 API；下面示例只展示应用边界，不固定模型能力。

```python
response = client.responses.create(
    model=model,
    instructions="你是一个 Python 助手。",
    input="解释 list 和 tuple 的区别。",
)

answer = response.output_text
usage = response.usage  # 记录 usage；不要把完整响应原样写入普通日志。
```

多轮对话的历史应由外部 State 持久化；调用前交给 [Context 工程](./04_Context工程.md) 做裁剪、摘要、检索或拒绝，不在 Provider 适配层静默丢消息。

## 4. 流式输出和取消

流式只改变传输方式，不改变任务合同：服务端仍要保存最终结果、处理断线和区分“用户看到部分文本”与“任务已成功”。

```python
def stream_text(prompt: str):
    stream = client.responses.create(model=model, input=prompt, stream=True)
    for event in stream:
        # 只把安全的文本增量发给前端；工具事件走独立事件通道。
        if event.type == "response.output_text.delta":
            yield event.delta
```

生产接口还要支持：请求级超时、用户取消、Provider 断线、重连后的重复事件过滤，以及最终结果落库。长任务不要占住一次 HTTP 连接，转到 [Durable Execution](./06_Durable%20Execution与分布式可靠性.md)。

## 5. 结构化输出

JSON Mode 通常只保证可解析 JSON；结构化输出通过 schema 降低字段错误，但仍要处理拒答、截断、业务约束和权限。

```python
from pydantic import BaseModel, ValidationError


class Person(BaseModel):
    name: str
    age: int | None = None
    occupation: str


response = client.responses.parse(
    model=model,
    input="John Smith，35 岁，软件工程师。",
    text_format=Person,
)

try:
    person = response.output_parsed
except ValidationError:
    # 结构校验失败时走明确的重试、拒答或人工路径，不把坏数据交给下游。
    raise
```

结构化输出不是业务事实验证。金额、权限、文件路径和外部动作仍由工具/服务端校验。

## 6. Usage、成本和缓存

调用层至少记录：`model`、`request_id`、输入/输出 token、缓存命中、延迟、结束原因和错误类别。价格不写死在本文，统一由 [成本与性能工程](./成本与性能工程.md) 使用版本化配置计算。

最小记录可以是：`model`、`request_id`、输入/输出 token、缓存命中、延迟、结束原因和错误类别。

Prompt Cache 只解决稳定前缀的重复计算；缓存条件、保留时间和价格随 Provider 变化，使用真实 usage 验证，不在这里维护固定折扣或实现。

## 7. 超时、错误和重试

重试必须区分“暂时不可用”和“请求本身错误”。非幂等工具调用的重试由 [Tool Calling](./02_Tool%20Calling.md) 和 [Durable Execution](./06_Durable%20Execution与分布式可靠性.md) 决定，不能在 Provider 适配层盲目重试。

```python
import asyncio


class LLMCallError(RuntimeError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


async def call_model(provider, messages: list[dict], *, timeout_s: float = 30.0):
    try:
        # 超时在调用边界处理，避免一次 Provider 卡住整个 Agent。
        return await asyncio.wait_for(
            provider.complete(messages=messages), timeout=timeout_s
        )
    except TimeoutError as exc:
        raise LLMCallError("provider_timeout") from exc
    except PermissionError as exc:
        # 认证/权限问题不应反复重试；应报警并返回明确失败。
        raise LLMCallError("provider_auth") from exc
```

建议把错误归一化为稳定错误码，例如 `rate_limited`、`provider_timeout`、`invalid_request`、`context_too_large`、`provider_unavailable`。指数退避、最大次数、fallback 和响应式压缩都应记录停止原因。

## 8. Provider 适配和 fallback

Agent 层只依赖内部结果类型，不依赖某个 SDK 的字段名：

```text
Agent → Provider Adapter → ModelResult(text, tool_calls, usage, request_id)
```

fallback 只对 `rate_limited`、`provider_unavailable`、`provider_timeout` 等暂时错误生效；仍要检查数据区域、模型能力、工具兼容性、质量回归和租户策略，并复用相同的安全与预算边界。

fallback 选择不仅看价格和可用性，还要检查数据区域、模型能力、工具调用兼容性、质量回归和租户策略。部署级灰度和回滚见 [部署与生产化](./12_部署与生产化.md)。

## 9. 图片、PDF 和其他多模态输入

多模态输入属于 Provider 能力，不是 Agent 特有机制。上传前必须校验 MIME、大小、像素/页数、敏感信息和解析失败路径；不要把“模型能看 PDF”当作所有文档都能正确读取。

- PDF、扫描件、Office 和表格入库：看 [文档摄取与解析](./文档摄取与解析.md)。
- 截图驱动操作：看 [Computer Use 与 GUI Agent](./Computer%20Use与GUI%20Agent.md)。
- 语音实时通道：看 [语音与实时对话 Agent](./语音与实时对话Agent.md)。

## 10. 测试和升级

Provider 适配层至少测试：超时转稳定错误码、空响应被拒绝、结构化输出失败、工具调用被正确归一化、取消不会留下未关闭资源。Provider、模型 ID、媒体限制、结构化输出和错误字段在升级前重新核对 [版本与来源](./版本与来源.md)。

实践对照：[ai-agent-learning 项目 03](./实践/ai-agent-learning/agent-learning-projects/03_openai_cli_chat/README.md)、[learn-claude-code s11](./实践/learn-claude-code/s11_error_recovery/code.py)。

## 官方来源

- [OpenAI Responses API](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Anthropic Messages API](https://platform.claude.com/docs/en/api/messages)

核对日期：2026-07-30。模型、媒体限制、错误类型、缓存条件和价格在部署或升级前重新核对。
