# Python Agent 工程化补充

本文只补 Python 如何承载 Agent Runtime：数据边界、Pydantic、异步、类型、重试、超时、幂等和测试。Agent 的整体架构与安全策略回到 [Agent 面试题库](../Agent面试题库/README.md)；Python 基础见 [核心语法](./01_Python核心语法.md) 与 [工程化](./02_Python工程化.md)。

## 学习位置

```text
Python 核心语法 → Python 工程化 → 本文 → Agent LLM/Tool/Loop
```

本文的核心分工是：模型提出不可信数据和动作意图，Python Runtime 负责解析、验证、授权、执行、恢复和记录。

## 1. 先解析，再执行

不要把模型返回的 JSON、工具参数或用户输入直接当成可信对象：

```python
from typing import Any


def required_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid_{key}")
    return value.strip()
```

解析边界应同时限制类型、长度、枚举、嵌套深度、文件路径和可执行内容。`json.loads` 只保证语法可解析，不保证业务合法；解析失败要返回稳定错误，不要半执行。

## 2. Pydantic：把数据变成合同

```python
from pydantic import BaseModel, Field


class SearchArgs(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    limit: int = Field(default=10, ge=1, le=50)


args = SearchArgs.model_validate(raw_arguments)
```

Pydantic 适合请求、工具参数和内部状态合同；业务权限、资源存在性和副作用仍由服务端/工具层检查。模型输出 schema 通过不等于事实正确，也不等于用户有权执行。

## 3. Asyncio 与有界并发

异步适合 HTTP、数据库和模型等 I/O 等待；并发必须有上限、超时和取消传播：

```python
import asyncio


async def bounded_map(items: list[str], worker, *, limit: int = 5) -> list[object]:
    semaphore = asyncio.Semaphore(limit)

    async def run(item: str):
        async with semaphore:
            return await asyncio.wait_for(worker(item), timeout=10)

    return await asyncio.gather(*(run(item) for item in items))
```

工具并发还要考虑资源冲突：只读查询可并行，同一文件/订单/账户的写入通常串行或加锁。取消后要回收任务和底层连接；不要把“收到多个 tool call”直接等同于全部并行。

## 4. 类型边界

```python
from dataclasses import dataclass
from typing import Protocol, TypedDict


class ToolResult(TypedDict):
    ok: bool
    error_code: str | None


class ModelClient(Protocol):
    async def complete(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class Budget:
    max_steps: int
    max_cost_usd: float
```

`TypedDict` 适合轻量协议，`BaseModel` 适合运行时校验，`Protocol` 适合依赖替换，`dataclass(frozen=True)` 适合不可变配置。类型注解是协作合同，不是权限控制。

## 5. 超时、重试与幂等

```python
async def call_with_retry(operation, *, attempts: int = 3):
    for attempt in range(attempts):
        try:
            return await asyncio.wait_for(operation(), timeout=10)
        except (TimeoutError, ConnectionError):
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(2**attempt)
```

这段只适合可重试的临时错误。写数据库、发消息、扣款、发布和删除必须带幂等键、去重记录、状态查询或补偿；结果未知时先查事实，不能盲目重做。重试预算、停止原因和错误码要进 Trace。

## 6. 装饰器与上下文管理器

横切能力可以用装饰器或上下文管理器集中实现，但不要隐藏权限和副作用：

```python
from contextlib import asynccontextmanager


@asynccontextmanager
async def traced(operation: str):
    trace_id = start_trace(operation)
    try:
        yield trace_id
    finally:
        finish_trace(trace_id)
```

超时、日志、指标、Trace 和资源清理适合横切；工具授权、参数校验和成功验证必须在显式执行边界可见。

## 7. 线程、进程还是异步

| 工作 | 选择 |
|---|---|
| 网络/文件等待 | `asyncio` 或异步库 |
| 阻塞第三方库 | 线程池，设置上限和取消边界 |
| CPU 密集计算 | 进程池或独立服务 |
| 需要隔离的不可信代码 | 容器/微 VM，不靠线程隔离 |

线程共享内存，进程有序列化和启动成本；无论选择什么，都要记录任务 ID、超时、取消和结果。

## 8. 测试：把模型放在可控边界外

模型调用应通过接口注入，测试用固定响应验证：

- 参数解析失败不会执行工具；
- 未知/越权工具被拒绝；
- 工具结果按 `call_id` 回填；
- 超时、取消和限流有稳定错误码；
- 非幂等失败不会重复副作用；
- 成功必须由程序化证据确认。

模型质量用独立 Eval；Python 单元测试负责确定性边界，集成测试负责真实协议和临时资源。

## 9. 项目遇到对应边界时

下列能力不单独再做一套练习；当 Agent 项目需要对应边界时，逐项落到项目里：

1. 用 Pydantic 校验搜索和写入参数；
2. 用 `asyncio` 并发执行两个只读查询，并限制并发与超时；
3. 为写操作加入审批和幂等键；
4. 用固定 ModelClient mock 驱动一次成功、拒绝、超时和恢复；
5. 记录状态、工具轨迹、成本和停止原因。

验收重点不是模型回答漂亮，而是“坏输入、坏工具、进程取消和重复投递时不会越过执行边界”。

配套刷题：[Tool Calling 与 MCP](../Agent面试题库/04_Tool与协议/Tool Calling与MCP.md)、[Agent 基础与架构](../Agent面试题库/01_基础架构/Agent基础与架构.md)。
