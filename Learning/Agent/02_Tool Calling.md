# Tool Calling

这篇文章解决一个问题：**如何把模型提出的动作转换成可校验、可授权、可恢复的工具执行**。

> **前提与位置**：先读 [LLM 调用基础](./01_LLM调用基础.md)。这是主线第 2 篇，本章新增 `ToolCall`（模型的动作提案）和 `ToolResult`（执行器的事实/错误）。
>
> **边界**：Provider 合同规定消息如何传输，Tool 合同规定动作如何校验和执行，Agent Loop 决定拿到结果后是否继续；本文负责工具执行边界，不展开整体 Loop、安全威胁和治理。

## 0. 先看一次工具循环

```text
模型：ToolCall(read_file, path="src/app.py")
应用：解析 → schema 校验 → 授权 → 执行
应用：ToolResult(call_id, 文件内容或错误)
模型：根据 ToolResult 输出答案、再调用工具或停止
```

工具调用不是“模型执行了代码”。它是模型给应用的一张结构化请求单；应用可以拒绝、延迟、审批或改写为安全错误结果。

## 1. 模型不会执行代码

```text
用户目标
  → 模型选择工具并生成结构化参数
  → 应用解析、校验、授权、执行
  → 应用返回 tool result
  → 模型根据事实继续、改用工具、请求审批或结束
```

模型输出的是动作提案，不是执行权限。工具执行器必须独立于模型，能够拒绝未知工具、非法参数、越权资源和超预算动作。

### Provider 协议不是 Agent 原理

| 层 | 负责什么 |
|---|---|
| Provider API | 规定 tool call、tool result、结束原因和流式事件的消息形状 |
| 内部 Tool Contract | 统一名称、参数、结果、错误、权限和幂等语义 |
| Agent Loop | 决定执行后是否继续以及何时终止 |

消息层的 `ToolCall` / `ToolResult` 统一形状见 [LLM 调用基础](./01_LLM调用基础.md)。本篇在此基础上增加执行合同：`call_id` 既用于消息配对，也用于幂等追踪；Provider 的 block、字段名和错误形状由适配器转换，不应泄漏到业务循环。

不要把某家 SDK 的 `stop_reason` 或 block 类型当成通用 Agent 定义；适配层应把它们转换成内部结果。

## 2. Tool Contract 与 Schema

一个工具至少需要：

- 稳定名称和清晰描述：何时使用、何时不用；
- 参数 schema：类型、必填、范围、枚举和跨字段约束；
- 返回合同：成功数据、稳定错误码和是否可重试；
- 权限元数据：动作、资源范围、是否有副作用、是否需要审批；
- 运行元数据：超时、并发安全、幂等键和输出上限。

```python
from pydantic import BaseModel, Field


class SearchOrdersArgs(BaseModel):
    user_id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$")
    status: str | None = None
    limit: int = Field(default=10, ge=1, le=100)


TOOL_SPEC = {
    "name": "search_orders",
    "description": (
        "查询当前用户有权访问的订单。只读；不用于退款或修改订单。"
    ),
    "input_schema": SearchOrdersArgs.model_json_schema(),
    "action": "order.read",
    "side_effecting": False,
    "idempotent": True,
}
```

描述应让模型能做出选择，但不能把权限规则只写在描述里；服务端仍要重新授权。Schema 校验只证明参数形状正确，不证明用户有权访问资源。

## 3. 一次工具调用的执行顺序

推荐固定为：

```text
parse → allowlist → schema → resource scope → policy/approval
→ idempotency check → timeout/limit → execute
→ sanitize result → audit → return stable result
```

```python
async def execute_tool_call(call, *, registry, policies, allowed_tools):
    if call.name not in registry or call.name not in allowed_tools:
        return {"ok": False, "call_id": call.call_id, "error_code": "tool_denied"}

    policy = policies[call.name]
    try:
        args = validate_schema(call.name, call.arguments)
        authorize(call, policy)  # 策略判断不依赖模型的理由。
        if policy.side_effecting:
            require_idempotency_key(args)
        async with asyncio.timeout(policy.timeout_s):
            value = await registry.get(call.name)(**args)
        return {"ok": True, "call_id": call.call_id, "value": limit_result(value)}
    except TimeoutError:
        return {"ok": False, "call_id": call.call_id, "error_code": "tool_timeout"}
    except PermissionError:
        return {"ok": False, "call_id": call.call_id, "error_code": "policy_denied"}
    except Exception as exc:  # 详细堆栈进入受控 Trace，不回给模型。
        return {"ok": False, "call_id": call.call_id,
                "error_code": "tool_failed", "error_type": type(exc).__name__}
```

生产实现还要限制工具结果大小，并在进入 Context、Trace、日志和用户界面前分别执行敏感信息处理。

下面省略类型定义和依赖注入，只保留执行器边界；真实实现应把 `validate_schema`、`authorize`、`limit_result` 和错误映射接到项目的确定性组件。

## 4. Loop 中如何回填结果

工具执行器只负责一次调用；循环负责把结果配对回填，并根据停止原因决定下一步：

下面的 `completed_text` 只表示“模型返回了文本候选”，不等于业务任务已经满足成功条件；成功判定仍由上层验证器负责。

```text
while budget.allows():
    response = provider.complete(context)
    record assistant output and finish reason

    if response.text is not None and not response.tool_calls:
        return completed_text(response.text)  # 业务层仍需检查成功证据。

    for call in response.tool_calls:
        result = execute_tool_call(call)
        record call_id, decision, duration and safe result summary
        append provider-compatible tool result

    if no_progress or cancelled:
        return stopped(reason)

return stopped("budget_exhausted")
```

不同 Provider 对 `tool_call_id`、assistant block 和 tool result 的配对要求不同。适配器必须保证：每个调用只回填一次、ID 对应、错误也有合法的 tool result 形状；否则不要进入下一轮。

## 5. Registry、分发和错误语义

注册表把工具名称映射到执行函数，避免在循环中写一长串 `if/elif`：

```python
TOOL_HANDLERS = {
    "search_orders": search_orders,
    "read_file": read_file,
}


def resolve_tool(name: str):
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        raise LookupError("unknown_tool")
    return handler
```

错误要让模型知道“下一步能做什么”，同时不给它内部秘密：

| 错误 | 是否可重试 | 应返回什么 |
|---|---|---|
| 参数校验失败 | 通常否，先修正参数 | `invalid_arguments` + 字段原因 |
| 未授权/需审批 | 否，等待授权或换方案 | `policy_denied` / `approval_required` |
| 超时/暂时不可用 | 仅幂等动作限次重试 | `tool_timeout` / `dependency_unavailable` |
| 副作用结果未知 | 先查状态 | `outcome_unknown`，不要直接重做 |
| 工具不存在 | 否 | `unknown_tool`，重新路由或结束 |

## 6. 幂等、重试、超时和并发

| 工具 | 默认幂等性 | 处理 |
|---|---|---|
| 搜索、查询、读取 | 通常是 | 可在预算内重试或短暂缓存 |
| 创建、更新、发送、扣款 | 通常否 | 使用幂等键、状态查询或补偿；不盲目重试 |
| 删除、发布、迁移 | 高风险 | 预览/审批/审计；结果未知时先核实 |

幂等键应绑定租户、任务、操作摘要和业务对象，并由服务端去重；只在 Python 内存里记一次调用不足以抵御重启或并发。

只读且资源不冲突的调用可以并行；写操作按资源依赖串行或使用显式锁。并行不是“收到多个 call 就全部开线程”，还要考虑 rate limit、取消、结果顺序和单任务预算。

## 7. 权限、审计和沙箱

工具层至少检查：主体、租户、资源、动作、策略版本、审批范围、过期时间和幂等状态。高风险工具的完整治理见 [安全与可控性](./08_安全与可控性.md)；威胁来源见 [Agent 安全与威胁建模](./07_Agent安全与威胁建模.md)。

审计事件记录 `task_id`、`call_id`、actor、tenant、tool、resource、policy_decision、approval_id、duration、outcome 和版本信息；不要默认记录完整参数、Prompt 或工具原文。

执行用户代码、Shell 或浏览器时，工具必须进入受限 workspace/沙箱，设置 CPU、内存、网络、文件和时间边界。不要在主进程 `eval()` 用户代码。Coding Agent 的文件和命令细节见 [代码 Agent 基础设施](./05_代码%20Agent%20基础设施.md)。

## 8. 长任务和后台工具

“后台执行”不是在当前请求里启动一个无记录的线程。长工具应创建有状态任务，返回 `task_id`，由 Queue/Worker/Lease 驱动；完成结果作为事件写回下一轮 Context。Checkpoint、取消、重复投递和恢复见 [Durable Execution](./06_Durable%20Execution与分布式可靠性.md)。

## 9. Provider 特性：tool choice 和 streaming

某些 Provider 支持强制使用任意工具或指定工具，可用于分类、结构化提取和固定 Workflow 节点；它只约束模型输出形状，不绕过执行器权限。

工具参数流式返回时，必须等 JSON 增量完整后再解析；前端可以提前展示文本或进度，但不能把未完成参数当作执行请求。Provider 事件形状以 [版本与来源](./版本与来源.md) 和官方文档为准。

## 10. 工具膨胀与路由

工具超过几十个时，不要把全部 schema 放进每次请求：

```text
用户意图
  → 静态域/技能路由
  → 组内候选工具
  → 只注入候选 schema
  → 执行器再次授权
```

优先级通常是：静态规则 → 工具描述的语义召回 → 两级模型路由。路由只解决模型“看见谁”，不解决权限、参数、幂等和副作用；`Skills` 负责能力正文的渐进式披露，见 [Skills 与渐进式披露](./Skills与渐进式披露.md)。

## 11. 练习与验收

实现三个工具：一个查询、一个可审批写操作、一个会超时的外部调用，并证明：

1. 未知工具和越权工具不会执行；
2. 参数错误变成结构化结果；
3. 查询可限次重试，写操作不会因不明结果重复执行；
4. 每个调用都能按 `call_id` 回放和解释；
5. 预算、取消、超时和审批都有明确停止原因。

实践：[Tool Calling Agent](./实践/ai-agent-learning/agent-learning-projects/04_tool_calling_agent/README.md)、[Simple Agent Loop](./实践/ai-agent-learning/agent-learning-projects/05_simple_agent_loop/README.md)。

## 官方来源

- [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling)
- [Anthropic Tool Use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)

核对日期：2026-07-30。Provider 消息形状、strict 支持、并行调用和流式事件升级时重新核对。
