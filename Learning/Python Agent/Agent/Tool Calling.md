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

## 10. 面试高频

**Q：Tool Calling 的完整流程是什么？模型真的执行了代码吗？**

> Tool Calling 分两个阶段：首先，用户输入连同工具 schema 一起发给模型，模型返回的不是文字答案，而是一个结构化的"工具调用意图"（tool_call），包含函数名和参数。然后，你的 Python 程序读取这个意图，找到对应函数，真正执行，把结果再返回给模型，模型才生成最终答案。模型自始至终没有执行任何代码——它只生成了一个 JSON 描述"我想调用什么"。

**Q：如果工具调用失败，应该怎么处理？**

> 不应该让异常传到模型外面导致整个 Agent 崩溃。正确做法是 catch 所有异常，把错误信息结构化为 tool result 返回给模型（如 `{"error": "数据库连接超时"}`）。模型收到错误后通常能做出合理反应——重试、换一种方式、或告知用户。幂等工具可以自动重试，非幂等工具的失败不应该自动重试。

**Q：Schema 的 description 写得好不好，对实际效果有影响吗？**

> 影响非常大。模型选工具的决策几乎完全基于 name 和 description。description 写得含糊（"处理用户相关操作"），模型就不知道应不应该用、参数怎么填。description 写得清晰（包含使用场景、不适用场景、参数说明），工具选择准确率会显著提升。在工具选择出问题时，首先检查 schema description 是不是写清楚了。
