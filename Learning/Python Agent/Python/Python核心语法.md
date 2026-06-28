# Python核心语法
这一页是 Python 的基础底座。目标不是背语法，而是能看懂代码、写小脚本、为后面的 FastAPI / RAG / Agent 项目打基础。

## 学习重点

1. Python 是动态类型语言，变量不需要提前声明类型。
2. 缩进就是代码块，不能像 Java 那样靠 `{}`。
3. `list / dict / set / tuple` 是最常用的数据结构。
4. 函数、异常、文件、JSON、模块、异步是做项目必须掌握的部分。

## 1. 变量与基本类型

Python 变量可以理解为“名字指向一个值”。变量本身不固定类型，值是什么类型，变量就表现成什么类型。

```python
name = "Tom"        # str 字符串
age = 18            # int 整数
price = 19.9        # float 小数
is_active = True    # bool 布尔值，注意 True / False 首字母大写
nothing = None      # None 表示空值，类似 Java 的 null

print(type(name))              # 查看变量当前类型：<class 'str'>
print(isinstance(age, int))    # 判断 age 是否是 int 类型：True
```

<table header-row="true">
<tr>
<td>Python</td>
<td>Java 类比</td>
<td>说明</td>
</tr>
<tr>
<td>`str`</td>
<td>`String`</td>
<td>字符串</td>
</tr>
<tr>
<td>`int`</td>
<td>`int / Integer`</td>
<td>整数</td>
</tr>
<tr>
<td>`float`</td>
<td>`double`</td>
<td>小数</td>
</tr>
<tr>
<td>`bool`</td>
<td>`boolean`</td>
<td>布尔值</td>
</tr>
<tr>
<td>`list`</td>
<td>`ArrayList`</td>
<td>有序、可变、可重复</td>
</tr>
<tr>
<td>`dict`</td>
<td>`HashMap`</td>
<td>key-value 映射</td>
</tr>
<tr>
<td>`set`</td>
<td>`HashSet`</td>
<td>无序、去重</td>
</tr>
<tr>
<td>`tuple`</td>
<td>不可变 list</td>
<td>有序、不可变</td>
</tr>
</table>

常见坑：

- `True / False / None` 首字母必须大写。
- Python 没有 `null`，用 `None`。
- 类型注解不会强制运行时类型，只是给 IDE、类型检查器和读代码的人看的。

## 2. 输入输出

```python
name = input("请输入名字：")       # input 永远返回 str
age = int(input("请输入年龄："))   # 需要自己把 str 转成 int

print(f"name={name}, age={age}")  # f-string：把变量嵌入字符串
print("a", "b", "c", sep="-")   # sep 控制多个值之间的分隔符，输出 a-b-c
print("hello", end=" ")          # end 控制 print 结尾，默认是换行 \n

print("world")                    # 因为上一行 end=" "，这里会接在 hello 后面
```

`input()` 常见坑：

```python
age = input("age: ")
print(age + 1)  # 错误：age 是 str，不能直接和 int 相加

age = int(age)  # 正确：先转成 int
print(age + 1)
```

## 3. 字符串处理

字符串在 Python 里非常重要，后面写 prompt、处理 HTTP 响应、解析文件都会用到。

```python
text = " hello,Python "       # 前后故意留空格，方便演示 strip

clean = text.strip()           # 去掉首尾空格："hello,Python"
lower = text.lower()           # 转小写：" hello,python "
upper = text.upper()           # 转大写：" HELLO,PYTHON "
replaced = text.replace("Python", "AI")  # 替换子串：" hello,AI "
parts = text.split(",")        # 按逗号切分：[' hello', 'Python ']
joined = ",".join(["Tom", "Jack"])      # 用逗号拼接："Tom,Jack"

print(text.startswith("http")) # 判断是否以 http 开头：False
print(text.endswith(".jpg"))   # 判断是否以 .jpg 结尾：False
```

多行字符串常用于 prompt：

```python
prompt = """
你是一个 Python 老师。
请用简单例子解释概念。
"""
```

字符串隐式拼接常用于避免一行太长：

```python
summary = (
    "LangGraph 可以把 Agent 拆成状态、节点和边，"
    "让复杂流程变得可观察、可控制。"
)

print(summary)
# 输出：LangGraph 可以把 Agent 拆成状态、节点和边，让复杂流程变得可观察、可控制。
```

解释：

- 相邻的字符串字面量会被 Python 自动拼成一个字符串。
- 外层括号只是为了允许换行，不会生成 tuple。
- 最终 `summary` 是一个完整的 `str`，不是两个字符串，也不是 list。

它等价于：

```python
summary = "LangGraph 可以把 Agent 拆成状态、节点和边，让复杂流程变得可观察、可控制。"
```

适合场景：

- 长提示词、长说明文案、长返回文本。
- 不想写 `+` 拼接。
- 不需要在中间插入变量。

如果需要插入变量，用 f-string：

```python
name = "LangGraph"
summary = (
    f"{name} 可以把 Agent 拆成状态、节点和边，"
    "让复杂流程变得可观察、可控制。"
)
```

注意：只有“字符串字面量相邻”才会隐式拼接。变量不会自动拼接：

```python
a = "hello"
b = "world"

# 错误：变量不能这样相邻拼接
# text = a b

# 正确：用 + 或 join
text = a + b
```

原始字符串常用于路径和正则：

```python
path = r"C:\test\demo"  # r 表示 raw string，反斜杠不用重复转义
```

字符串常见坑：

- 字符串不可变，`text.strip()` 不会修改原字符串，而是返回一个新字符串。
- `split()` 返回 list，`join()` 是字符串方法，不是 list 方法。
- 判断包含用 `in`：`"Python" in text`。

## 4. 条件判断

```python
score = 85

if score >= 90:
    level = "A"
elif score >= 80:
    level = "B"
elif score >= 60:
    level = "C"
else:
    level = "D"

print(level)
```

常见判断：

```python
name = "Tom"
age = 18

if name and age >= 18:       # name 非空，并且 age >= 18
    print("adult user")

if name is not None:         # 判断不是 None，推荐用 is / is not
    print("name exists")

if name == "Tom":           # == 比较值是否相等
    print("same value")
```

会被当成 false 的值：

```python
False
None
0
0.0
""
[]
{}
set()
```

三元表达式：

```python
status = "成年" if age >= 18 else "未成年"
```

`is` 和 `==`：

- `==` 比较值是否相等。
- `is` 比较是不是同一个对象。
- 判断 None 用 `is None` / `is not None`。

## 5. 循环与推导式

```python
for i in range(1, 6):     # 生成 1,2,3,4,5；右边界 6 不包含
    print(i)

names = ["Tom", "Jack", "Lucy"]
for index, name in enumerate(names):  # 同时拿到索引和值
    print(index, name)

user = {"name": "Tom", "age": 18}
for key, value in user.items():       # 遍历 dict 的 key 和 value
    print(key, value)
```

列表推导式：

```python
nums = [i * 2 for i in range(5)]              # [0, 2, 4, 6, 8]
even_nums = [i for i in range(10) if i % 2 == 0]  # 只保留偶数
```

`while`：

```python
count = 3
while count > 0:
    print(count)
    count -= 1          # 每次循环减 1，否则容易死循环
```

控制循环：

```python
for i in range(10):
    if i == 3:
        continue        # 跳过本次循环，继续下一次
    if i == 8:
        break           # 直接结束整个循环
    print(i)
```

## 6. list

list 是有序、可变、可重复的集合。

```python
nums = [1, 2, 3]

nums.append(4)           # 末尾添加：[1, 2, 3, 4]
nums.remove(2)           # 删除值为 2 的元素；如果不存在会报错
last = nums.pop()        # 删除并返回最后一个元素
first = nums[0]          # 下标从 0 开始
part = nums[1:3]         # 切片，取索引 1 到 2，不包含 3

print(len(nums))         # 列表长度
print(3 in nums)         # 判断元素是否存在
```

排序：

```python
nums = [3, 1, 2]
nums.sort()              # 原地升序排序：[1, 2, 3]
nums.sort(reverse=True)  # 原地降序排序：[3, 2, 1]

items = [("apple", 10), ("banana", 5)]
items.sort(key=lambda x: x[1])  # 按元组第二个元素排序
```

常见坑：

- `list.sort()` 会修改原列表，返回值是 `None`。
- `sorted(nums)` 会返回新列表，不改原列表。
- 切片 `[start:end]` 永远不包含 `end`。

## 7. dict

`dict` 是 key-value 结构，后面处理 JSON、API 响应、工具参数都会大量使用。

```python
user = {
    "name": "Tom",
    "age": 18,
}

print(user["name"])          # 直接取值；key 不存在会 KeyError
print(user.get("city"))      # key 不存在返回 None，不报错
print(user.get("city", "HK")) # key 不存在返回默认值 HK

user["age"] = 20             # 修改已有 key
user["city"] = "Hong Kong"   # 新增 key

del user["age"]              # 删除 key
```

遍历：

```python
for key in user:
    print(key, user[key])

for key, value in user.items():
    print(key, value)
```

嵌套 dict：

```python
response = {
    "data": {
        "user": {
            "name": "Tom"
        }
    }
}

name = response["data"]["user"]["name"]
```

常见坑：

- `user["x"]` 适合你确定 key 一定存在。
- `user.get("x")` 适合 key 可能不存在。
- API 返回的数据层级经常很深，先 `print(response)` 看结构再取值。

## 8. set / tuple

`set` 用于去重和集合运算。

```python
ids = {1, 2, 3}
ids.add(4)              # 添加元素
ids.discard(2)          # 删除元素，不存在也不报错
ids.remove(3)           # 删除元素，不存在会报错

nums = [1, 1, 2, 2, 3]
unique_nums = list(set(nums))  # 去重，但顺序不保证
```

集合运算：

```python
a = {1, 2, 3}
b = {3, 4, 5}

print(a & b)  # 交集：{3}
print(a | b)  # 并集：{1,2,3,4,5}
print(a - b)  # 差集：{1,2}
```

`tuple` 是不可变有序集合：

```python
point = (1, 2)
x, y = point           # 解包
```

## 9. 函数

函数用来把逻辑拆小，让代码可复用、可测试。

```python
def add(a: int, b: int) -> int:
    """返回两个整数之和。"""
    return a + b

result = add(1, 2)
print(result)
```

返回多个值：

```python
def get_user() -> tuple[str, int]:
    return "Tom", 18       # 本质返回 tuple

name, age = get_user()     # 解包
```

默认参数和命名参数：

```python
def hello(name: str = "Tom") -> None:
    print(f"hello {name}")

hello()                    # 使用默认值 Tom
hello("Jack")              # 传位置参数
hello(name="Lucy")         # 传命名参数，可读性更好
```

`*args` 和 `**kwargs`：

```python
def debug(*args, **kwargs):
    print(args)     # 多个位置参数组成 tuple
    print(kwargs)   # 多个 key=value 参数组成 dict

debug(1, 2, name="Tom", age=18)
```

函数也是对象：

```python
def hello():
    print("hello")

fn = hello  # 不加括号，表示把函数本身赋值给 fn
fn()        # 调用 fn，相当于调用 hello()
```

## 10. 文件与 JSON

优先用 `pathlib`，写法更现代、更面向对象。

```python
from pathlib import Path

path = Path("data/user.json")                  # 创建路径对象
path.parent.mkdir(parents=True, exist_ok=True)  # 确保 data 目录存在
path.write_text('{"name": "Tom"}', encoding="utf-8")  # 写文本
text = path.read_text(encoding="utf-8")        # 读文本
```

JSON：

```python
import json
from pathlib import Path

data = {"name": "Tom", "age": 18}

# dict -> JSON 字符串 -> 写入文件
Path("user.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

# 读取文件 -> JSON 字符串 -> dict
loaded = json.loads(Path("user.json").read_text(encoding="utf-8"))
print(loaded["name"])
```

<table header-row="true">
<tr>
<td>方法</td>
<td>作用</td>
</tr>
<tr>
<td>`json.dumps`</td>
<td>dict/list → JSON 字符串</td>
</tr>
<tr>
<td>`json.loads`</td>
<td>JSON 字符串 → dict/list</td>
</tr>
<tr>
<td>`json.dump`</td>
<td>dict/list → JSON 文件</td>
</tr>
<tr>
<td>`json.load`</td>
<td>JSON 文件 → dict/list</td>
</tr>
</table>

### 10.1 从小项目理解“文件就是程序状态”

`python-learning-stages/01_file_io_note_tool` 和 `02_json_task_tracker` 的核心思想是：命令执行完以后，内存会消失；如果下次命令还要接着用上次的结果，就必须把状态写进文件。

文件读写小工具对应的是最基础的文本状态：

```python
from pathlib import Path
from datetime import datetime
import shutil

DATA_DIR = Path("data")                 # 统一保存运行时数据
NOTES_FILE = DATA_DIR / "notes.txt"     # 用 / 拼路径，比字符串拼接更稳
BACKUP_DIR = Path("backups")            # 备份目录，类似 checkpoint


def add_note(text: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)  # 目录不存在就创建
    now = datetime.now().isoformat(timespec="seconds")

    # "a" 表示 append：追加写入，不覆盖原文件
    with NOTES_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{now}] {text}\n")


def backup_notes() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_file = BACKUP_DIR / f"notes-{datetime.now():%Y%m%d-%H%M%S}.txt"

    # copy2 会尽量保留源文件的元数据，比单纯复制文本更适合做备份
    shutil.copy2(NOTES_FILE, backup_file)
    return backup_file
```

JSON task tracker 对应的是结构化状态：

```python
import json
from pathlib import Path

TASK_FILE = Path("data/tasks.json")


def load_tasks() -> list[dict]:
    if not TASK_FILE.exists():
        return []  # 第一次运行还没有状态文件，就返回空列表

    text = TASK_FILE.read_text(encoding="utf-8")
    return json.loads(text)  # JSON 字符串 -> Python list/dict


def save_tasks(tasks: list[dict]) -> None:
    TASK_FILE.parent.mkdir(parents=True, exist_ok=True)
    TASK_FILE.write_text(
        json.dumps(tasks, ensure_ascii=False, indent=2),  # Python list/dict -> JSON 字符串
        encoding="utf-8",
    )
```

和 SafeCode Agent 的对应关系：

- `notes.txt` 像最简单的运行日志。
- `tasks.json` 像 `.sac/pending_patch.json`，保存下一条命令要继续处理的状态。
- `backups/` 像 `.sac/checkpoints/`，用于回滚。
- 先 `load_*()` 再修改再 `save_*()`，是很多 CLI 工具的基本节奏。

常见坑：

- 中文 JSON 建议 `ensure_ascii=False`。
- 读写文本建议显式写 `encoding="utf-8"`。
- `json.loads()` 处理字符串，`json.load()` 处理文件对象。

## 11. 异常处理

异常处理不是为了隐藏错误，而是为了在可预期错误发生时给出清晰处理。

```python
try:
    age = int(input("age: "))   # 可能 ValueError
    result = 10 / age            # 可能 ZeroDivisionError
except ValueError:
    print("请输入数字")
except ZeroDivisionError:
    print("不能为 0")
else:
    print("成功", result)        # 没有异常才执行
finally:
    print("结束")               # 无论是否异常都会执行
```

主动抛异常：

```python
age = -1
if age < 0:
    raise ValueError("年龄不能小于 0")
```

自定义异常：

```python
class BusinessError(Exception):
    pass

raise BusinessError("业务规则不允许这样操作")
```

常见坑：

- 不要写 `except: pass`，会把真实问题吞掉。
- 能捕获具体异常就不要直接捕获 `Exception`。
- 项目里通常用 `logger.exception()` 记录完整错误栈。

## 12. 面向对象

类适合表达“有状态的数据 + 行为”。小脚本不必强行写类，但项目里会经常用类封装 client、service、配置对象。

```python
class User:
    count = 0  # 类变量，所有对象共享

    def __init__(self, name: str, age: int):
        self.name = name  # 实例变量，每个对象各有一份
        self.age = age

    def hello(self) -> None:
        print(f"hello {self.name}")

user = User("Tom", 18)
user.hello()
```

继承：

```python
class Admin(User):
    def __init__(self, name: str, age: int, role: str):
        super().__init__(name, age)  # 调用父类构造函数
        self.role = role

    def hello(self) -> None:         # 方法重写
        print(f"admin {self.name}")
```

`dataclass` 适合纯数据对象：

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

u = User("Tom", 18)
print(u)  # 自动生成可读的 repr
```

## 13. 模块与包

一个 `.py` 文件就是一个 module；带 `__init__.py` 的目录可以作为 package。

```plain text
project/
├── app/
│   ├── __init__.py
│   ├── config.py
│   └── services.py
└── main.py
```

```python
from app.services import call_api

if __name__ == "__main__":
    call_api()
```

`if __name__ == "__main__"` 的作用：

- 当前文件被直接运行时，里面代码会执行。
- 当前文件被 import 时，里面代码不会自动执行。

## 14. 必会标准库

<table header-row="true">
<tr>
<td>模块</td>
<td>用途</td>
</tr>
<tr>
<td>`os`</td>
<td>环境变量、系统路径、进程相关</td>
</tr>
<tr>
<td>`pathlib`</td>
<td>现代路径和文件操作</td>
</tr>
<tr>
<td>`json`</td>
<td>JSON 编解码</td>
</tr>
<tr>
<td>`datetime`</td>
<td>时间日期</td>
</tr>
<tr>
<td>`collections`</td>
<td>Counter、defaultdict 等容器工具</td>
</tr>
<tr>
<td>`itertools`</td>
<td>迭代器工具</td>
</tr>
<tr>
<td>`re`</td>
<td>正则表达式</td>
</tr>
<tr>
<td>`logging`</td>
<td>日志</td>
</tr>
<tr>
<td>`traceback`</td>
<td>打印完整错误栈</td>
</tr>
<tr>
<td>`sys`</td>
<td>命令行参数、解释器信息</td>
</tr>
</table>

例子：

```python
import os
from datetime import datetime
from collections import Counter

api_key = os.getenv("OPENAI_API_KEY")  # 从环境变量读取配置
now = datetime.now()                    # 当前时间
counts = Counter(["a", "b", "a"])     # 统计次数：Counter({'a': 2, 'b': 1})
```

## 15. asyncio 基础

`asyncio` 是单线程并发：遇到等待就切换去做别的任务，适合网络请求、API 调用、数据库查询等等待型任务。

```python
import asyncio

async def work(name: str) -> str:
    await asyncio.sleep(1)      # 模拟等待网络请求
    return f"done {name}"

async def main():
    results = await asyncio.gather(
        work("a"),
        work("b"),
    )
    print(results)

asyncio.run(main())             # 启动异步程序入口
```

常见关键词：

- `async def`：定义异步函数。
- `await`：等待异步结果。
- `asyncio.create_task()`：创建后台任务。
- `asyncio.gather()`：并发等待多个任务。
- `asyncio.Semaphore()`：控制并发数量。

常见坑：

- 调用异步函数必须 `await`，否则只会得到 coroutine 对象。
- `asyncio.run()` 一般只在程序入口调用一次。
- `async def` 里不要执行长时间阻塞的同步代码。

## 复习清单

- 能解释 `list / dict / set / tuple` 的区别。
- 能给字符串常用方法写出带注释例子。
- 能用函数拆分逻辑，并写类型注解。
- 能用 `pathlib + json` 读写文件。
- 能写异常处理，并说明为什么不要 `except: pass`。
- 能解释 `__name__ == "__main__"`。
- 能理解 `async/await` 适合等待型任务。
