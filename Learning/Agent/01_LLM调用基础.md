# LLM 调用基础

这篇文章只解决一件事：**把模型 API 调用封装成可靠的应用边界**。读完应能处理消息、流式、结构化输出、用量、错误和 Provider 替换。

> **先建立地图**：本章先建立“应用如何调用模型”的边界。`LLM`（大语言模型）负责生成候选输出，`Provider`（模型服务商或运行时）提供 API，`Adapter` 负责翻译，应用只消费自己的 `ModelResult`；工具和循环分别在后面的 [Tool Calling](./02_Tool%20Calling.md) 与 [Agent 架构](./03_Agent架构与设计.md) 中加入。
>
> **位置与完成标准**：这是 Agent 主线第 1 篇。读完能画出“应用请求 → Provider → Adapter → ModelResult”，并解释哪些数据发给模型、哪些只写入 Trace/计费记录；Context、工具权限和 Agent Loop 分别见 `04`、`02`、`03`。

> **边界**：本文只负责 Provider/API 适配和调用级恢复，不维护 Agent Loop、工具权限、完整成本系统或部署 runbook。

> **第一遍只读**：`0–3 → 7 → 11`。先理解调用链、消息合同、最小调用和错误边界；流式、结构化输出、成本缓存、fallback、多模态和升级测试等到项目遇到时再查。

## 0. 本章先看一条链路

```text
业务目标 / Context（本轮选出的模型输入）
  → CallRequest（应用内部语义）
  → Provider Adapter（翻译）
  → Provider API（外部格式）
  ← Provider 原始响应
  ← ModelResult（内部统一语义）
  → Agent 决定：结束、调用工具或重试
```

`Provider 合同`就是外部 API 对请求、响应、错误、流式事件和元数据的约定；`ModelResult` 是应用为了不被某一家 SDK 绑死而定义的内部结果。两者有关，但不是同一个东西。

这里的 `CallRequest` 只是应用内部的一次调用请求；`Provider API` 是外部服务规定的具体字段和事件。一次调用先得到 `ModelResult`，还不等于 Agent 已经完成任务——后续章节才把工具执行和有限循环接上。

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

先把“合同”翻译成一个工程问题：**这一层接收什么、返回什么、失败怎么表达、哪些 ID 必须配对、哪些责任明确不属于它？**

`Message` 是传输层的一条带角色或类型的数据项；`Context` 则是本轮经过筛选后要发送的全部输入，二者不要混为一谈，Context 的选择见 [Context 工程](./04_Context工程.md)。

Provider 合同负责模型 API 的收发格式；工具执行、权限判断和任务成功条件仍属于应用侧。Adapter 负责翻译，不应把业务判断偷偷塞进翻译层。

不同 API 的外形不同，但 Agent 需要的最小语义相同。一次任务通常会涉及：

| 信息 | 作用 |
|---|---|
| 持久指令 | 角色、边界和输出合同；不要把每轮动态数据硬编码进去 |
| 当前用户输入 | 当前目标和用户提供的数据 |
| 历史状态 / Assistant 输出 | 之前的对话、模型回复或模型提出的下一步 |
| Tool 结果 | 外部执行器返回的事实或错误 |
| Usage / Request ID | 成本、限流、Trace 和重放关联；这是调用元数据，不是发给模型的消息 |

这里混合了三类合同：模型输入（指令、用户输入、历史和工具结果）、模型输出（文本或工具调用），以及调用元数据（usage、request ID、延迟和错误）。`Reasoning`/`thinking` 指某些 Provider 返回的推理相关状态；如果它以摘要、签名或 typed item 返回，只保留完成协议、恢复和审计所需的状态，不要把它等同于必须暴露或保存的原始思维链。

OpenAI Responses 使用 typed Items；Chat Completions 和 Anthropic Messages 使用不同的 messages/blocks 形状。不要在业务层直接拼接某个 Provider 的原始字段，先转换成内部结果类型：

```python
from dataclasses import dataclass


@dataclass
class ToolCall:
    call_id: str
    name: str
    arguments: dict


@dataclass
class ToolResult:
    call_id: str
    ok: bool
    value: object | None = None
    error_code: str | None = None


@dataclass
class ModelResult:
    text: str | None
    tool_calls: list[ToolCall]
    usage: dict[str, int] | None
    request_id: str | None
    finish_reason: str | None
```

Agent 只依赖 `ModelResult` 的语义；Provider Adapter 负责把 `output_text`、tool blocks、结束原因和 usage 等原始字段转换进来。`ModelResult.text` 也不自动等于任务成功，成功仍要由工具结果、测试或其他确定性证据确认。

```python
messages = [
    # 稳定规则和权限边界；动态资料应由 Context 层装配。
    {"role": "system", "content": "你是只读代码分析助手。"},
    {"role": "user", "content": "分析这个函数的错误。"},
]
```

以只读代码分析为例，消息和执行边界大致是：

```text
第 1 轮：持久指令 + 用户任务
  ← 模型返回 ToolCall(read_file, path="src/app.py")
执行器：校验路径、授权并读取文件
第 2 轮：原有状态 + ToolResult(call_id, 文件内容或错误)
  ← 模型返回分析文本或下一次 ToolCall
```

模型只提出 `ToolCall`，应用执行后再回填 `ToolResult`；调用 ID 必须一一对应，错误也要用 Provider 合法的结果形状回填。工具的 schema、权限、幂等和重试见 [Tool Calling](./02_Tool%20Calling.md)，消息如何从历史、检索和 State 中选出见 [Context 工程](./04_Context工程.md)。

上面的 `messages` 是便于理解的概念示例，不是所有 Provider 的固定请求格式。Responses API 通常把稳定指令放在 `instructions`，把输入放在 `input`；适配层应保持业务层不感知这种差异。

### 2.1 从具体 API 映射到内部语义

第一遍学习时先选一套 API 跑通，不要同时背两套 SDK。可以先用实践项目中的 messages 风格 API；下面只看语义映射：

| 内部语义 | messages 风格 API | typed items 风格 API |
|---|---|---|
| 稳定指令 | system message | instructions 或等价字段 |
| 当前输入 | user message | input item |
| 模型文本 | assistant content | output text item |
| 工具调用 | assistant tool call | function/tool call item |
| 工具结果 | tool message + call ID | tool result item + call ID |
| Usage / Request ID | 响应元数据 | 响应元数据 |

这张表是语义地图，不是跨版本复制合同。具体字段由 Adapter 根据 [版本与来源](./版本与来源.md) 和 Provider 官方文档实现。

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

## 11. 读完应能说明

不需要为本章单独再造练习。结合 [项目 03](./实践/ai-agent-learning/agent-learning-projects/03_openai_cli_chat/README.md) 中已有的调用代码，确认自己能回答：

1. 为什么 Agent 不应该直接依赖 `choices[0].message` 之类的 Provider 字段？
2. `ModelResult.text`、`tool_calls`、`usage` 和 `request_id` 分别给谁使用？
3. 为什么 Usage/Request ID 不进入 messages？
4. Provider 超时和结构化输出失败，为什么要先归一化再交给上层？

如果你还分不清“模型输入”和“调用元数据”，先回到本章第 2 节；如果分不清 State、Context 和 Memory，再读 [Context 工程](./04_Context工程.md) 的第 0 节，不要先钻进 fallback 和多模态。能结合已有项目解释清楚即可，不要求重新实现一套 Provider Adapter。

## 官方来源

- [OpenAI Responses API](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Anthropic Messages API](https://platform.claude.com/docs/en/api/messages)

核对日期：2026-07-30。模型、媒体限制、错误类型、缓存条件和价格在部署或升级前重新核对。
