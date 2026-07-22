# Python Agent 工程化补充

这篇笔记把外部的 `Python-Agent开发学习指南.md` 接入当前知识库，专门补足一条容易被忽略的连接：**Python 语言能力如何转化为 Agent 的可靠运行时**。

它不是新的总目录，也不替代已有笔记。已有页面负责展开主题；本页负责把主题串起来，并保留 Agent 开发中最值得反复练习的代码模式。

## 在知识库中的位置

| 问题 | 先看 | 本页补充 |
| --- | --- | --- |
| Python 语法、dict/list、文件和 JSON | [Python 核心语法](Python核心语法.md) | 模型响应的安全提取与数据边界 |
| 虚拟环境、uv、配置、日志和测试 | [Python 工程化](Python工程化.md) | Agent 项目的工程化检查点 |
| HTTP、timeout、retry、httpx | [HTTP 与 API 调用](HTTP与API调用.md) | 异步调用的并发控制 |
| LLM、多轮、stream、结构化输出 | [LLM 调用基础](../Agent/LLM调用基础.md) | Pydantic 模型作为系统边界 |
| Tool schema、并行调用、权限和重试 | [Tool Calling](../Agent/Tool%20Calling.md) | Tool 执行器的统一实现方式 |
| Agent Loop、State、Memory、Workflow | [Agent 架构与设计](../Agent/Agent架构与设计.md)、[Workflow 与 LangGraph](../Agent/Workflow与LangGraph.md) | Python 能力在运行时中的落点 |

## 最短学习路径

如果 Python 基础尚可，按下面顺序学习：

```text
Python核心语法
  → Python工程化
  → 本页：Pydantic / asyncio / 类型边界
  → LLM调用基础
  → Tool Calling
  → Agent架构与设计
  → Eval与测试体系
```

如果 Python 还不熟，先完成 [Python 核心语法](Python核心语法.md) 的复习清单，再回来做本页练习。

## 1. Agent 的数据边界：先解析，再执行

模型响应、工具参数和外部 API 都是不稳定的输入。不要让未经校验的字典直接进入业务逻辑或文件、网络、数据库操作。

### 1.1 安全读取嵌套数据

简单、层数固定的数据可以使用 `.get()`；复杂响应建议先转成明确的数据结构，而不是在业务代码里堆很多下标。

```python
from collections.abc import Mapping
from typing import Any


def get_tool_calls(response: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """从兼容 Chat Completions 形状的响应中安全取出 tool_calls。"""
    choices = response.get("choices", [])
    if not choices or not isinstance(choices[0], Mapping):
        return []

    message = choices[0].get("message", {})
    if not isinstance(message, Mapping):
        return []

    tool_calls = message.get("tool_calls", [])
    if not isinstance(tool_calls, list):
        return []

    return [call for call in tool_calls if isinstance(call, Mapping)]


def tool_call_names(response: Mapping[str, Any]) -> list[str]:
    names: list[str] = []
    for tool_call in get_tool_calls(response):
        function = tool_call.get("function", {})
        if isinstance(function, Mapping) and isinstance(function.get("name"), str):
            names.append(function["name"])
    return names
```

原则：

- 外部响应先做形状检查，再读取字段。
- 关键参数缺失时返回结构化错误或要求澄清，不要静默执行危险操作。
- 工具名、参数、权限和实际 handler 都要再次校验；模型输出不是执行权限。

### 1.2 解析模型生成的 JSON

模型可能返回 Markdown 代码块、尾部逗号或空字符串。解析器应该是一个独立、可测试的纯函数。

```text
import json
import re
from typing import Any


def parse_model_json(raw: str) -> dict[str, Any]:
    """解析常见的模型 JSON 输出，失败时抛出可定位的 ValueError。"""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"模型返回的 JSON 无法解析: {exc.msg}") from exc

    if not isinstance(value, dict):
        raise ValueError("模型返回的 JSON 顶层必须是 object")
    return value
```

不要无条件执行 `raw.replace("'", '"')`：这会破坏字符串中的英文撇号、路径和内容。确实需要容错时，使用专门的 `json-repair`，并把修复结果当作“不可信输入”继续做 schema 校验。

SSE / streaming 的增量事件也应先逐行解析、再根据 Provider 的事件格式取 delta；不要假设所有 Provider 都使用相同的 `choices[0].delta` 结构。完整的调用和流式输出见 [LLM 调用基础](../Agent/LLM调用基础.md)。

## 2. Pydantic：把模型输出变成系统合同

Pydantic 适合放在系统边界：模型结构化输出、工具输入、配置和需要持久化的状态。内部临时数据可以使用 `TypedDict` 或普通类型，避免所有对象都过度建模。

```python
from typing import Literal

from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str = Field(min_length=1, description="搜索关键词")
    source: Literal["web", "news"] = "web"
    max_results: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str = ""


payload = SearchInput.model_validate({"query": "Python asyncio"})
```

使用建议：

- `Field(description=...)` 同时服务于校验、文档和 Tool Schema；描述应写清边界，不要只写“参数”。
- `Literal`、`ge`、`le`、`min_length` 等约束应尽量靠近数据定义。
- 捕获 `ValidationError` 后，返回可诊断的结构化错误；不要把原始异常堆栈直接交给模型。
- 条件约束较多时，优先使用 `model_validator` 或拆成更小的模型，并补测试。

`LLM调用基础.md` 已有结构化输出示例；`Tool Calling.md` 已有 Schema 和参数校验内容，本页只保留工程判断。

## 3. Asyncio：并发不等于无限并发

Agent 经常需要同时执行多个互不依赖的只读工具。生产代码至少要同时考虑并发上限、单项超时、取消和异常是否隔离。

```python
import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


async def execute_parallel(
    calls: list[dict[str, Any]],
    execute: Callable[[dict[str, Any]], Awaitable[Any]],
    *,
    concurrency: int = 8,
    timeout_seconds: float = 30,
) -> list[dict[str, Any]]:
    """并行执行独立工具，并把失败转换为结构化结果。"""
    semaphore = asyncio.Semaphore(concurrency)

    async def run_one(call: dict[str, Any]) -> dict[str, Any]:
        name = str(call.get("name", "unknown"))
        async with semaphore:
            try:
                result = await asyncio.wait_for(execute(call), timeout_seconds)
                return {"name": name, "ok": True, "result": result}
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 - 边界层需要结构化失败
                return {"name": name, "ok": False, "error": str(exc)}

    return await asyncio.gather(*(run_one(call) for call in calls))
```

判断规则：

- 互不依赖的只读工具可以并行；有写入副作用或顺序依赖的操作默认串行。
- 不要在 `async def` 中直接调用阻塞式 `requests`、同步 SDK 或 CPU 密集任务；必要时使用 `asyncio.to_thread()` 或进程池。
- 不要用没有上限的 `gather()` 批量打外部 API；用 `Semaphore` 配合 Provider 的 rate limit。
- `CancelledError` 通常应该继续抛出，让上层能够安全取消；普通工具异常则转为结果，是否终止由 Agent Loop 决定。

详细的 Tool 并行、超时、幂等和权限处理见 [Tool Calling](../Agent/Tool%20Calling.md)；HTTP 客户端选择见 [HTTP 与 API 调用](HTTP与API调用.md)。

## 4. 类型边界：TypedDict、BaseModel 和 Protocol

可以用下面的分工减少混乱：

| 类型 | 适合位置 | 特点 |
| --- | --- | --- |
| `TypedDict` | 已知形状的中间字典、内部消息 | 主要服务静态检查，运行时不校验 |
| `BaseModel` | 外部输入、Tool 参数、配置、持久化状态 | 运行时校验和序列化 |
| `Protocol` | Tool、Provider、Repository 的接口 | 依赖行为，不依赖具体继承关系 |

```python
from collections.abc import Awaitable
from typing import Any, Protocol


class AsyncTool(Protocol):
    name: str

    async def run(self, arguments: dict[str, Any]) -> Any:
        ...


async def invoke_tool(
    tool: AsyncTool,
    arguments: dict[str, Any],
) -> Any:
    return await tool.run(arguments)
```

优先使用组合和接口契约，而不是为了复用少量代码建立很深的继承树。只有当框架确实要求继承基类时，才实现最小的基类适配层。

## 5. 稳定性：重试、超时和幂等

重试不是“所有异常都再试一次”。先区分：

- 可以重试：连接失败、临时超时、429、部分 5xx。
- 通常不应重试：参数校验失败、权限拒绝、业务规则错误、模型输出无法满足合同。
- 写操作重试前必须确认幂等性；发送邮件、扣款、创建资源等操作应使用 idempotency key 或业务去重。

```python
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)


@retry(
    retry=retry_if_exception_type((TimeoutError, ConnectionError)),
    wait=wait_random_exponential(multiplier=1, max=20),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def fetch_external_data(client: object, key: str) -> dict[str, object]:
    # 真实项目中在这里调用 async client，并设置单次 timeout。
    raise NotImplementedError
```

`tenacity` 的装饰器只是机制，重试策略仍应由调用类型决定。更复杂的策略可以在 [HTTP 与 API 调用](HTTP与API调用.md) 和 [Tool Calling](../Agent/Tool%20Calling.md) 中集中维护，避免每个工具各写一套。

## 6. 装饰器与上下文管理器：给 Agent 加横切能力

日志、耗时、token/cost 统计、trace 和预算检查不应散落在每个 Tool 的业务代码里。可以用装饰器或上下文管理器统一包裹。

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from time import perf_counter


@asynccontextmanager
async def tool_span(name: str) -> AsyncIterator[dict[str, float | str]]:
    span = {"name": name, "started_at": perf_counter()}
    try:
        yield span
    finally:
        span["elapsed_seconds"] = perf_counter() - float(span["started_at"])
        # 这里接入结构化日志或 trace exporter；不要记录完整 secrets/messages。
```

边界规则：

- 统计逻辑失败时，不应掩盖 Tool 的原始错误。
- 日志默认记录 tool 名、request id、耗时、状态和结果摘要，不记录 API Key、完整消息和敏感文档。
- 预算、超时和取消应由上层 Agent Runtime 统一控制；Tool 自己只负责正确释放资源。

相关内容见 [可观测性与调试](../Agent/可观测性与调试.md)、[成本与性能工程](../Agent/成本与性能工程.md) 和 [安全与可控性](../Agent/安全与可控性.md)。

## 7. 线程、进程与异步的选择

```text
外部 API / 数据库 / 网络 I/O       → asyncio
只有同步接口、少量阻塞 I/O          → asyncio.to_thread / ThreadPool
PDF 解析、图像处理、复杂计算        → ProcessPool / multiprocessing
有副作用的工具或共享状态             → 先确认顺序、锁和幂等，再谈并发
```

不要因为“并发更快”就把所有工具并行化。Agent 的可靠性通常优先于单次请求的理论吞吐量；并发还会放大 rate limit、共享文件冲突和重复写入问题。

## 8. 测试：把不稳定的模型包在可控边界外

模型输出不可控，但以下逻辑必须可确定地测试：

1. JSON 清洗和解析；
2. Pydantic 校验与错误转换；
3. Tool 注册、参数校验和权限判断；
4. 并行执行、超时、取消和单项失败；
5. Agent Loop 的终止条件、最大步数和预算；
6. Session checkpoint、恢复和 replay。

建议测试分层：

| 层级 | 是否调用真实模型 | 重点 |
| --- | --- | --- |
| 单元测试 | 否 | 纯函数、模型、Tool handler |
| Mock Provider | 否 | 固定多轮响应、异常和 tool call |
| Scenario / Eval | 可选 | 完整轨迹、质量和安全门槛 |
| Online Eval | 是 | 真实流量、成本、延迟和回归 |

不要用“响应包含某句话”作为 Agent 唯一测试标准。更有价值的是断言：工具是否被正确选择、参数是否正确、危险操作是否被拦截、失败后是否安全结束，以及预算是否生效。

## 9. 一个适合练习的最小项目

```text
agent-demo/
├── pyproject.toml
├── .env.example
├── src/
│   └── agent_demo/
│       ├── config.py          # Pydantic Settings
│       ├── models.py          # Tool 输入输出模型
│       ├── llm.py             # Provider client
│       ├── tools.py           # search / calculator / weather
│       ├── runtime.py         # Agent Loop、timeout、budget
│       └── observability.py   # logging / trace / cost
└── tests/
    ├── test_models.py
    ├── test_tools.py
    └── test_runtime.py
```

验收标准：

- 至少三个 Tool，输入输出使用 Pydantic；
- 独立的只读 Tool 能并行执行，写操作有权限和确认；
- 外部调用有 timeout、有限重试和幂等策略；
- 每一步有结构化 trace，并能记录 token、耗时和成本；
- Mock Provider 覆盖成功、参数错误、工具失败、超时、取消和 max_steps；
- 用 `uv` 或 `pyproject.toml` 固定依赖，`.env` 不进入版本库。

## 10. 对原始学习指南的修订说明

原指南适合作为主题清单，但直接复制代码前要注意：

- “把单引号替换成双引号”不是可靠的 JSON 修复策略；优先标准解析，必要时使用专门修复库，再做 Pydantic 校验。
- `asyncio.gather()` 需要配合超时、并发上限、取消传播和异常策略。
- “uv 是某年最快的工具”属于会变化的比较结论；把它作为当前推荐工具即可，版本和命令以官方文档为准。
- Pydantic、OpenAI、Anthropic、LangGraph 的 API 会演进；示例中的模型名、参数和协议细节应以对应 Provider 的最新文档为准。
- 示例代码中的 `BaseTool`、`Agent` 等有些是教学用伪实现，不能直接当作现成框架 API。

回到原始资料查看完整章节和练习：

外部参考：`Python-Agent开发学习指南.md`

## 配套实践

如果想把本篇的配置、日志、HTTP 和异步基础直接跑起来，可以按顺序完成 [01 Python 工程模板](../Agent/实践/ai-agent-learning/agent-learning-projects/01_python_project_template/README.md) 和 [02 HTTP API Client](../Agent/实践/ai-agent-learning/agent-learning-projects/02_http_api_client/README.md)。它们是 Agent 开发的工程前置，不需要先接入大模型。
