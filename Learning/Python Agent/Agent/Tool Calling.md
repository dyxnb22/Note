# Tool Calling

这篇文档解决一个问题：**如何设计一个健壮、安全、可维护的工具调用系统**。

不只是让工具"能跑"，而是：schema 质量、错误恢复、幂等性、权限边界、并发处理——都做对。

---

## 1. 本质理解

```
用户输入
   ↓
LLM 理解意图 → 决定调用哪个工具 → 生成工具调用参数（JSON）
             （模型不执行代码）
   ↓
你的 Python 程序
  - 解析工具名称和参数
  - 找到对应函数
  - 真正执行
  - 捕获结果（或错误）
   ↓
把结果返回给模型 → 模型生成最终回答
```

**关键分工**：模型负责意图理解和参数生成；Python 程序负责真实执行、安全检查、错误处理。

---

## 2. Schema 设计

Schema 质量直接影响工具选择的准确率。

### 完整 Schema 结构

```python
tools = [
{
    "type": "function",
    "function": {
        "name": "search_orders",
        "description": (
            "搜索用户订单。当用户询问订单状态、查找特定订单、"
            "统计历史购买时使用。不用于创建或修改订单。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "用户唯一标识符",
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "shipped", "delivered", "cancelled"],
                    "description": "订单状态过滤。不传则返回所有状态",
                },
                "limit": {
                    "type": "integer",
                    "description": "最多返回几条记录，默认 10，最大 100",
                    "default": 10,
                },
            },
            "required": ["user_id"],
        },
    },
}
]
```

### Schema 设计原则

| 原则 | 好的 | 坏的 |
|------|------|------|
| description 明确边界 | "搜索订单。不用于创建订单" | "处理订单相关操作" |
| 参数 description 说明何时传 | "不传则返回所有状态" | "状态过滤" |
| 用 enum 约束枚举值 | `"enum": ["pending", "shipped"]` | `"type": "string"` |
| 参数名称语义清晰 | `user_id`, `start_date` | `id`, `d1` |
| required 只包含真正必须的 | `["user_id"]` | `["user_id", "limit"]` |

**核心规律**：模型选工具时看 name 和 description，生成参数时主要看 parameters 里每个字段的 description。工具选择出问题时，先检查 description 是不是写清楚了。

---

## 3. 完整执行循环

```python
import json
from typing import Callable

def run_tool_loop(
messages: list[dict],
tools: list[dict],
tool_registry: dict[str, Callable],
max_iterations: int = 10,
) -> str:
for _ in range(max_iterations):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )

    choice = response.choices[0]
    messages.append(choice.message)

    if not choice.message.tool_calls:
        return choice.message.content

    for tool_call in choice.message.tool_calls:
        result = execute_tool(tool_call, tool_registry)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result, ensure_ascii=False),
        })

return "达到最大迭代次数"

def execute_tool(tool_call, registry: dict[str, Callable]) -> dict:
name = tool_call.function.name

try:
    args = json.loads(tool_call.function.arguments)
except json.JSONDecodeError:
    return {"error": "参数解析失败，JSON 格式错误"}

if name not in registry:
    return {"error": f"工具 '{name}' 不存在"}

try:
    result = registry[name](**args)
    return {"success": True, "data": result}
except TypeError as e:
    return {"error": f"参数错误: {e}"}
except PermissionError as e:
    return {"error": f"权限拒绝: {e}", "code": "PERMISSION_DENIED"}
except Exception as e:
    return {"error": f"执行失败: {type(e).__name__}: {e}"}
```

---

## 4. 并行工具调用

模型可以在一次响应里发出多个工具调用（并行意图）：

```python
import asyncio

async def execute_tools_parallel(tool_calls, registry):
tasks = [execute_tool_async(tc, registry) for tc in tool_calls]
results = await asyncio.gather(*tasks, return_exceptions=True)
return results
```

**注意**：必须把所有工具的结果都收集后，才能把结果一起返回给模型，不能只返回部分。

---

## 5. 工具注册表

生产系统用注册表统一管理工具：

```python
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class Tool:
name: str
description: str
fn: Callable
schema: dict
requires_permission: Optional[str] = None
is_idempotent: bool = True
max_retries: int = 3

class ToolRegistry:
def __init__(self):
    self._tools: dict[str, Tool] = {}

def register(self, tool: Tool):
    self._tools[tool.name] = tool

def get_schemas(self, allowed_names: list[str] = None) -> list[dict]:
    """返回 schema 列表，可按名称过滤"""
    tools = self._tools.values()
    if allowed_names:
        tools = [t for t in tools if t.name in allowed_names]
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.schema,
            }
        }
        for t in tools
    ]

def execute(self, name: str, args: dict, user_permission: str = "read") -> dict:
    tool = self._tools.get(name)
    if not tool:
        return {"error": f"工具不存在: {name}"}
    if tool.requires_permission and tool.requires_permission != user_permission:
        return {"error": "权限不足", "code": "PERMISSION_DENIED"}
    try:
        result = tool.fn(**args)
        return {"success": True, "data": result}
    except Exception as e:
        return {"error": str(e)}
```

---

## 6. 幂等性、重试、超时

### 幂等性分类

| 工具 | 幂等性 | 重试安全 |
|------|--------|---------|
| `search_orders()` | 是 | 可以放心重试 |
| `get_weather()` | 是 | 可以放心重试 |
| `send_email()` | **否** | 重试会重复发送 |
| `charge_user()` | **否** | 重试会重复扣款 |

非幂等工具：不应该自动重试；失败时返回可识别的错误；考虑加幂等 key 让服务端去重。

### 超时设置

```python
import httpx

async def call_external_api(url: str, timeout: float = 10.0):
async with httpx.AsyncClient(timeout=timeout) as client:
    try:
        response = await client.get(url)
        return response.json()
    except httpx.TimeoutException:
        return {"error": "请求超时", "timeout_seconds": timeout}
    except httpx.ConnectError:
        return {"error": "连接失败，服务不可达"}
```

---

## 7. 权限与审计

### 权限边界设计

```
读操作（查询、搜索）       → 低权限，可自动执行
写操作（更新、创建）       → 中权限，记录日志
破坏性操作（删除、发送）   → 高权限，需要人工确认
```

### 审计日志

```python
import structlog
from datetime import datetime

log = structlog.get_logger()

def logged_tool_execution(tool_name: str, args: dict, user_id: str, fn: Callable):
start = datetime.utcnow()
log.info("tool_call_start", tool=tool_name, user=user_id,
         args_keys=list(args.keys()))  # 不 log 参数值（可能含敏感数据）

try:
    result = fn(**args)
    duration = (datetime.utcnow() - start).total_seconds()
    log.info("tool_call_success", tool=tool_name, user=user_id, duration_s=duration)
    return result
except Exception as e:
    log.error("tool_call_failed", tool=tool_name, user=user_id,
              error=str(e), error_type=type(e).__name__)
    raise
```

---

## 8. 工具沙箱

如果工具会执行用户提供的代码（Code Interpreter 场景），必须隔离执行环境：

| 沙箱方案 | 隔离级别 | 性能 | 适用场景 |
|---------|---------|------|---------|
| `subprocess` + 资源限制 | 进程级 | 快 | 简单代码执行 |
| Docker 容器 | 容器级 | 中 | 需要文件系统隔离 |
| E2B / Modal 等云服务 | 托管 | 按需 | 快速集成 |

**原则**：永远不要在主进程里 `eval()` 用户提供的代码。

---

## 9. 常见误区

| 误区 | 问题 | 正确做法 |
|------|------|---------|
| 工具出错就抛异常传到模型 | 模型可能理解错误或循环重试 | 把错误信息结构化为 tool result 返回 |
| 工具数量越多越好 | 模型选择困难，误用率高 | 只给当前任务需要的工具 |
| 不验证模型生成的参数 | 可能收到非预期类型或恶意输入 | 用 Pydantic 验证参数 |
| tool description 太简单 | 模型不知道何时该/不该用 | 写清楚使用场景和边界 |
| 不记录工具调用日志 | 出了问题无法 debug | 每次工具调用都写日志 |

---

## 9. TOOL_HANDLERS dispatch 模式

最简洁的工具分发实现——Strategy Pattern 用 dict 实现：

```python
TOOL_HANDLERS: dict[str, callable] = {
    "bash":         run_bash,
    "read_file":    run_read_file,
    "write_file":   run_write_file,
    "list_dir":     run_list_dir,
}

def execute_tool(block) -> str:
    """block 是 response.content 里的 tool_use block"""
    handler = TOOL_HANDLERS.get(block.name)
    if handler is None:
        return f"Unknown tool: {block.name}"
    try:
        return handler(**block.input)
    except Exception as e:
        return f"Error: {e}"  # 错误作为字符串返回给模型，不抛异常
```

**与 stop_reason 的配合**——这是 Anthropic API 的循环控制机制：

```python
while True:
    response = client.messages.create(model=MODEL, tools=TOOLS, messages=messages)

    if response.stop_reason == "end_turn":
        # 模型认为任务完成，没有工具调用
        break

    if response.stop_reason == "tool_use":
        # 模型发出工具调用，需要执行并把结果返回
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,  # 必须对应 tool_use 的 id
                    "content": result,
                })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
        # 继续 while True，回到 LLM 调用
```

**关键点**：`stop_reason` 由 LLM 设置，代码只是读取它来决定是否继续循环。`tool_use_id` 必须和对应的 `tool_use` block 的 `id` 匹配，否则 API 报错。

---

## 10. 三关卡权限系统

比单纯"白名单/黑名单"更细粒度的权限模型：

```python
DENY_LIST = ["rm -rf /", "sudo rm", "mkfs", "> /dev/sda"]  # Gate 1：永远拒绝

PERMISSION_RULES = [
    {
        "name": "block_path_traversal",
        "check": lambda cmd: ".." in cmd,  # Gate 2：规则引擎
        "message": "路径穿越攻击",
    },
    {
        "name": "require_approval_for_delete",
        "check": lambda cmd: cmd.startswith("rm "),
        "message": "删除操作需要人工确认",
    },
]

def check_permission(command: str) -> bool:
    # Gate 1: 永久拒绝列表
    for denied in DENY_LIST:
        if denied in command:
            return False

    # Gate 2: 规则引擎
    for rule in PERMISSION_RULES:
        if rule["check"](command):
            # Gate 3: 人工确认
            answer = input(f"[{rule['name']}] {command}\n允许执行？(y/n): ")
            return answer.lower() == "y"

    return True  # 通过所有关卡
```

**路径穿越防护**（文件工具的基本安全要求）：

```python
from pathlib import Path

def safe_path(user_input: str, workspace: Path) -> Path:
    """防止 ../../etc/passwd 类攻击"""
    target = (workspace / user_input).resolve()
    if not str(target).startswith(str(workspace.resolve())):
        raise ValueError(f"路径越界: {user_input}")
    return target
```

攻击路径追踪：`safe_path("../../etc/passwd", workspace)` → `resolve()` 得到 `/etc/passwd` → 不以 workspace 开头 → `ValueError` → 返回给模型作为错误字符串，不执行。

---

## 11. 工具参数扩展：`run_in_background`

不需要新增一个"后台执行"工具，在现有工具 schema 里加一个可选参数即可：

```python
# bash 工具的 schema
{
    "name": "bash",
    "description": "Run a shell command.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {"type": "string"},
            "run_in_background": {
                "type": "boolean",
                "description": "Set true for long-running commands (install, build, test). Returns immediately."
            }
        },
        "required": ["command"],
    }
}
```

**双重决策机制**——模型显式指定优先，启发式作兜底：

```python
SLOW_KEYWORDS = [
    "install", "build", "test", "deploy", "compile",
    "docker build", "pip install", "npm install", "pytest", "make",
]

def should_run_background(tool_name: str, tool_input: dict) -> bool:
    # 优先级 1：模型明确要求
    if tool_input.get("run_in_background"):
        return True
    # 优先级 2：启发式（命令关键词判断是否耗时）
    if tool_name == "bash":
        cmd = tool_input.get("command", "").lower()
        return any(kw in cmd for kw in SLOW_KEYWORDS)
    return False

# 在 agent_loop 中
for block in response.content:
    if block.type == "tool_use":
        if should_run_background(block.name, block.input):
            bg_id = start_background_task(block)
            # 立即返回占位结果，不阻塞模型
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": f"[Background {bg_id} started] Result arrives when done.",
            })
        else:
            output = execute_tool(block)
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
```

**通知注入时机**：后台任务完成后，通知与下一批 tool_result 合并进同一条 `role: "user"` 消息，而不是单独发一条：

```python
# 合并：tool_results + background_notifications 一起发
user_content = list(results)                     # 当前工具结果
bg_notifications = collect_background_results()  # 已完成的后台任务
for notif in bg_notifications:
    user_content.append({"type": "text", "text": notif})  # 附加进去

messages.append({"role": "user", "content": user_content})
```

---

## 12. 只读工具并行分发

当模型一次发出多个工具调用，读操作之间没有依赖，可以并行执行：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

# 写操作不能并行（有顺序和副作用依赖）
WRITE_TOOL_NAMES = frozenset({
    "edit_file", "write_file", "run_command",
    "github_create_pr", "github_push_branch",
})

MAX_TURN_TOOLS = 20  # 每次 LLM 响应最多处理 N 个工具调用

def dispatch_tool_calls(tool_calls: list, handlers: dict) -> list[dict]:
    if len(tool_calls) > MAX_TURN_TOOLS:
        tool_calls = tool_calls[:MAX_TURN_TOOLS]

    # 分拣：只读 vs 写操作
    read_calls  = [c for c in tool_calls if c.name not in WRITE_TOOL_NAMES]
    write_calls = [c for c in tool_calls if c.name in WRITE_TOOL_NAMES]

    results = {}

    # 只读：并行执行
    with ThreadPoolExecutor() as pool:
        futures = {pool.submit(handlers[c.name], **c.input): c for c in read_calls}
        for future in as_completed(futures):
            call = futures[future]
            try:
                output = future.result()
            except Exception as e:
                output = f"Error: {e}"
            results[call.id] = output

    # 写操作：串行执行（保证顺序）
    for call in write_calls:
        try:
            results[call.id] = handlers[call.name](**call.input)
        except Exception as e:
            results[call.id] = f"Error: {e}"

    # 按原始顺序返回
    return [
        {"type": "tool_result", "tool_use_id": c.id, "content": results[c.id]}
        for c in tool_calls
    ]
```

**为什么写操作不能并行**：两个写操作可能修改同一个文件，并行会产生竞争条件。只读操作（read_file、search、list）没有这个问题。

---

## 13. `tool_choice` — 强制工具调用

默认情况下模型自己决定是否调工具。有时候你需要强制它用某个工具：

```python
# 强制调用任意一个工具（不允许模型直接文字回答）
response = client.messages.create(
    model="claude-sonnet-4-6",
    tools=tools,
    tool_choice={"type": "any"},          # 必须调用某个工具
    messages=messages,
    max_tokens=1024,
)

# 强制调用特定工具
response = client.messages.create(
    model="claude-sonnet-4-6",
    tools=tools,
    tool_choice={"type": "tool", "name": "search_knowledge_base"},
    messages=messages,
    max_tokens=1024,
)

# 让模型自己决定（默认行为）
response = client.messages.create(
    model="claude-sonnet-4-6",
    tools=tools,
    tool_choice={"type": "auto"},         # 默认，可省略
    messages=messages,
    max_tokens=1024,
)
```

**适合场景**：

| `tool_choice` | 使用场景 |
|---------------|---------|
| `"auto"` | 默认，让模型决定 |
| `"any"` | 分类任务（强制模型输出结构化结果而不是文字）|
| `"tool": "name"` | Pipeline 中某步骤必须调用特定工具（如强制触发 search）|

**用 `tool_choice` 做强制结构化输出**：

```python
# 比 JSON Mode 更可靠：强制通过工具返回结构化数据
classify_tool = {
    "name": "classify_sentiment",
    "description": "对文本进行情感分类",
    "input_schema": {
        "type": "object",
        "properties": {
            "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "reason": {"type": "string"},
        },
        "required": ["sentiment", "confidence"],
    }
}

response = client.messages.create(
    model="claude-sonnet-4-6",
    tools=[classify_tool],
    tool_choice={"type": "tool", "name": "classify_sentiment"},
    messages=[{"role": "user", "content": f"分类：{text}"}],
    max_tokens=256,
)

result = response.content[0].input   # 直接拿结构化结果
print(result["sentiment"], result["confidence"])
```

---

## 14. Streaming Tool Use

工具调用也支持流式，适合需要尽快显示部分结果的场景：

```python
import anthropic
import json

client = anthropic.Anthropic()

def stream_with_tools(messages: list, tools: list):
    tool_use_blocks = {}  # tool_use_id → {name, input_json_parts}
    text_buffer = ""

    with client.messages.stream(
        model="claude-sonnet-4-6",
        tools=tools,
        messages=messages,
        max_tokens=2048,
    ) as stream:
        for event in stream:
            if not hasattr(event, "type"):
                continue

            if event.type == "content_block_start":
                block = event.content_block
                if block.type == "tool_use":
                    # 工具调用开始
                    tool_use_blocks[block.id] = {
                        "name": block.name,
                        "input_parts": [],
                    }
                elif block.type == "text":
                    pass  # 文本内容开始

            elif event.type == "content_block_delta":
                delta = event.delta
                if delta.type == "input_json_delta":
                    # 工具参数的 JSON 增量（流式发来的）
                    # 找到对应的 tool_use block
                    for block_id, block_data in tool_use_blocks.items():
                        block_data["input_parts"].append(delta.partial_json)

                elif delta.type == "text_delta":
                    text_buffer += delta.text
                    print(delta.text, end="", flush=True)

            elif event.type == "message_stop":
                # 流结束，工具的 JSON 参数已完整
                for block_id, block_data in tool_use_blocks.items():
                    full_json = "".join(block_data["input_parts"])
                    block_data["input"] = json.loads(full_json)

    return tool_use_blocks, text_buffer

# 使用
tool_calls, text = stream_with_tools(messages, tools)
for tool_id, tool_data in tool_calls.items():
    result = execute_tool(tool_data["name"], tool_data["input"])
    # 把结果追加到 messages 继续对话
```

**注意**：tool 参数是以 `input_json_delta` 流式发来的，不能直接 parse JSON——需要等所有 delta 拼完整再 `json.loads()`。

---

## 10. 面试高频

**Q：Tool Calling 的完整流程是什么？模型真的执行了代码吗？**

> Tool Calling 分两个阶段：首先，用户输入连同工具 schema 一起发给模型，模型返回的不是文字答案，而是一个结构化的"工具调用意图"（tool_call），包含函数名和参数。然后，你的 Python 程序读取这个意图，找到对应函数，真正执行，把结果再返回给模型，模型才生成最终答案。模型自始至终没有执行任何代码——它只生成了一个 JSON 描述"我想调用什么"。

**Q：如果工具调用失败，应该怎么处理？**

> 不应该让异常传到模型外面导致整个 Agent 崩溃。正确做法是 catch 所有异常，把错误信息结构化为 tool result 返回给模型（如 `{"error": "数据库连接超时"}`）。模型收到错误后通常能做出合理反应——重试、换一种方式、或告知用户。幂等工具可以自动重试，非幂等工具的失败不应该自动重试。

**Q：Schema 的 description 写得好不好，对实际效果有影响吗？**

> 影响非常大。模型选工具的决策几乎完全基于 name 和 description。description 写得含糊（"处理用户相关操作"），模型就不知道应不应该用、参数怎么填。description 写得清晰（包含使用场景、不适用场景、参数说明），工具选择准确率会显著提升。在工具选择出问题时，首先检查 schema description 是不是写清楚了。
