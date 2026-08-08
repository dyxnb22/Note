# Python 核心语法

本文只保留进入 AI/Agent 开发所需的 Python 语言基础：数据、控制流、函数、文件、异常、模块、对象和异步。完整工程规范见 [Python 工程化](./02_Python工程化.md)。

## 学习目标

学完应能读写小型 Python 项目，理解可变对象、作用域、异常和 `asyncio`，并能把输入转换为可验证的数据。

## 1. 变量、类型与表达式

变量是对象的名称绑定，不是固定类型的盒子：

```python
name = "Ada"
age: int = 36
tags: list[str] = ["python", "agent"]
enabled = True

print(type(name), age + 1, enabled)
```

常用类型：`None`、`bool`、`int`、`float`、`str`、`list`、`tuple`、`dict`、`set`。`==` 比较值，`is` 比较身份；判断空值用 `is None`，不要用 `== None`。

```python
items = [1, 2, 3]
alias = items
alias.append(4)       # items 也变了：list 可变
copy = items.copy()   # 浅拷贝
```

可变默认参数、隐式共享列表和混用 `is`/`==` 是常见 bug。

## 2. 字符串与输入输出

```python
text = "  hello, agent  "
clean = text.strip().lower()
parts = [part.strip() for part in clean.split(",")]
message = f"收到 {len(parts)} 个字段"
```

优先使用 f-string；拼接很多片段时用 `"".join(parts)`。外部输入始终是字符串，进入业务前要解析、校验和限制长度，不要直接 `eval()`。

## 3. list、tuple、dict、set

```python
users = [{"id": "u1", "active": True}, {"id": "u2", "active": False}]
active_ids = [user["id"] for user in users if user["active"]]

config = {"timeout": 10}
timeout = config.get("timeout", 30)
unique_tags = set(["agent", "agent", "python"])
```

- `list`：有序、可变、允许重复。
- `tuple`：有序、不可变，适合固定结构。
- `dict`：键到值的映射；用 `.get()` 处理可选键。
- `set`：去重与成员判断，不保证业务顺序。

遍历字典时用 `for key, value in mapping.items()`；需要稳定序列化时不要依赖集合顺序。

## 4. 条件、循环和推导式

```python
def classify(score: int) -> str:
    if score >= 80:
        return "high"
    if score >= 60:
        return "medium"
    return "low"


for item in items:
    if item < 0:
        continue
    print(item)
```

`for` 适合遍历已知集合，`while` 适合由条件控制但必须有停止条件的循环。推导式适合简单转换；逻辑复杂时改回普通循环，优先可读性。

```python
result = [n * 2 for n in range(10) if n % 2 == 0]
```

## 5. 函数、作用域与类型

```python
def parse_limit(value: str, *, default: int = 10) -> int:
    try:
        limit = int(value)
    except ValueError:
        return default
    return max(1, min(limit, 100))
```

参数分为位置参数、关键字参数和可变参数；带副作用的函数要在命名和文档中说明。避免把可变对象作为默认参数：

```python
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    result = [] if items is None else list(items)
    result.append(item)
    return result
```

局部变量、闭包和模块变量有不同作用域；能通过参数返回的数据，不要依赖全局变量。类型注解帮助 IDE、检查器和读者，但不会在运行时自动校验。

## 6. 文件、路径与 JSON

```python
from pathlib import Path
import json

path = Path("data") / "config.json"
payload = {"model": "configured", "timeout": 30}
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
loaded = json.loads(path.read_text(encoding="utf-8"))
```

使用 `Path` 而不是手拼字符串；文件、网络和环境变量都是可能失败的外部边界。生产代码要处理文件不存在、编码错误、权限、大小上限和原子写入。

## 7. 异常处理

```python
class ConfigError(ValueError):
    pass


def load_timeout(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError("timeout must be an integer") from exc
    if value <= 0:
        raise ConfigError("timeout must be positive")
    return value
```

只捕获能处理的异常；不要用裸 `except:`，也不要静默吞错。错误边界要提供稳定错误类型/错误码，底层异常作为原因保留到日志或 Trace。

## 8. 模块、包和对象

模块是一个 `.py` 文件，包是可导入的目录。入口文件负责组装依赖，业务模块负责逻辑，避免导入时就执行网络请求或修改数据。

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    task_id: str
    title: str

    def label(self) -> str:
        return f"{self.task_id}: {self.title}"
```

类适合表达稳定的状态和行为；不要为了“面向对象”给每个函数套一层类。`dataclass` 负责数据承载，继承只在确有替换关系时使用。

## 9. 标准库中最常用的工具

`pathlib` 处理路径，`json` 处理结构化数据，`datetime` 处理时间，`logging` 记录事件，`re` 处理有限模式，`collections` 提供计数/默认字典，`dataclasses` 定义数据对象，`typing` 表达类型边界，`asyncio` 管理异步任务。

## 10. asyncio 基础

`async def` 定义协程，`await` 等待异步结果；异步适合 I/O 等待，不会自动让 CPU 计算变快。

```python
import asyncio


async def fetch(name: str) -> str:
    await asyncio.sleep(0.01)
    return name


async def main() -> list[str]:
    return await asyncio.gather(fetch("a"), fetch("b"))


if __name__ == "__main__":
    print(asyncio.run(main()))
```

真实服务要加超时、取消和并发上限；不要无限创建任务，也不要在事件循环中执行长时间阻塞的同步 I/O。

## 基础不牢时再用

如果现有项目还不能证明这些能力，可用一个命令行任务清单补齐：读取 JSON、解析命令、处理非法输入、保存文件并为边界函数写测试。已经会的话直接跳过。

## 复习清单

- 能解释可变对象、拷贝、`==` 与 `is`；
- 能用函数、类型注解、异常和 `Path` 处理外部输入；
- 能拆分模块，避免导入副作用；
- 能写一个带超时、取消和有限并发的异步调用；
- 能读懂项目中的 `pyproject.toml`、测试和日志入口。

下一篇：[Python 工程化](./02_Python工程化.md)。
