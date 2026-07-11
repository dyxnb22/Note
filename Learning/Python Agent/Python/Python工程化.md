# Python工程化
这一页解决一个问题：如何把“能跑的脚本”整理成“别人能运行、自己能维护、线上能排错”的 Python 项目。

本页边界：这里重点讲环境、依赖、配置、日志、测试、目录结构、启动方式和简单 CLI 入口。Service / Client / Repository / Pipeline 等更深的架构拆分放到 `Python代码组织与设计模式`。

## 1. 工程化到底解决什么

写脚本时你可能只有一个 `main.py`，但项目变大后会遇到：

- 依赖装在系统 Python 里，换电脑就跑不起来。
- API Key 写死在代码里，不安全。
- 业务逻辑、配置、日志、工具函数混在一个文件里。
- 出错只有一堆 print，不知道哪里坏。
- 没有测试，改一处坏一片。

工程化的目标：

- 依赖可复现。
- 配置可分离。
- 日志可排查。
- 结构可维护。
- 测试可验证。
- 部署可迁移。

## 2. 虚拟环境 venv

每个项目应该有自己的虚拟环境，避免不同项目依赖互相污染。

```bash
python -m venv .venv          # 在当前目录创建虚拟环境，目录名叫 .venv
source .venv/bin/activate     # macOS / Linux 激活虚拟环境
which python                  # 检查 python 是否来自 .venv
which pip                     # 检查 pip 是否来自 .venv
deactivate                    # 退出虚拟环境
```

为什么用 `.venv`：

- 点开项目就知道虚拟环境在哪里。
- VS Code / PyCharm 容易识别。
- 不和系统 Python 混在一起。

`.gitignore`：

```plain text
.venv/          # 虚拟环境很大，不提交
__pycache__/    # Python 运行缓存，不提交
*.pyc           # 编译缓存，不提交
.env            # 本地密钥，不提交
```

## 3. pip 与 requirements.txt

`requirements.txt` 是最简单的依赖清单。

```bash
python -m pip install requests python-dotenv openai  # 安装依赖
python -m pip freeze > requirements.txt              # 导出当前环境依赖
python -m pip install -r requirements.txt            # 根据清单安装依赖
```

建议用 `python -m pip`，而不是直接 `pip`：

```bash
python -m pip install openai
```

这样能确保“当前 python 对应的 pip”在安装包，减少环境错乱。

## 4. pyproject.toml

`pyproject.toml` 是现代 Python 项目的配置中心，可以放项目元信息、依赖、测试、lint 配置。

```toml
[project]
name = "agent-demo"                     # 项目名
version = "0.1.0"                       # 版本号
description = "A simple Python agent demo"
requires-python = ">=3.11"              # 要求 Python 版本
dependencies = [                         # 正式运行需要的依赖
"httpx",
"openai",
"pydantic",
"python-dotenv",
]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]       # 开发阶段才需要的工具

[tool.ruff]
line-length = 100                        # 每行最长 100 字符
target-version = "py311"                # 按 Python 3.11 规则检查

[tool.pytest.ini_options]
testpaths = ["tests"]                   # pytest 默认测试目录
```

简单理解：

- 小脚本：`requirements.txt` 足够。
- 正式项目：建议逐步用 `pyproject.toml`。

## 4.5 uv：现代 Python 项目管理工具

`uv` 是 Astral 做的 Python 包管理和项目管理工具，可以理解成一个更现代、更快、更统一的工具链。它不只是替代 `pip`，还覆盖了 `venv`、`pip-tools`、`pipx`、部分 `poetry`、部分 `pyenv` 的常见工作。

官方给它的定位是：一个用 Rust 写的、速度很快的 Python package and project manager。

### 4.5.1 uv 解决什么问题

传统 Python 项目经常会同时用很多工具：

```plain text
python -m venv .venv       # 创建虚拟环境
pip install xxx            # 安装依赖
pip freeze > requirements  # 固定依赖
pipx run ruff              # 临时运行命令行工具
pyenv install 3.12         # 管理 Python 版本
poetry add xxx             # 项目依赖管理
```

`uv` 的目标是把这些常见动作统一起来：

```plain text
uv venv        # 创建虚拟环境
uv add         # 给项目添加依赖
uv run         # 在项目环境里运行命令或脚本
uv sync        # 根据锁文件同步环境
uv lock        # 生成/更新锁文件
uvx            # 临时运行 Python 命令行工具
uv python      # 安装/切换 Python 版本
```

### 4.5.2 安装 uv

macOS / Linux：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

也可以用 Homebrew：

```bash
brew install uv
```

检查是否安装成功：

```bash
uv --version
```

### 4.5.3 用 uv 创建项目

```bash
uv init my-agent-demo
cd my-agent-demo
```

它会创建一个带 `pyproject.toml` 的项目。之后添加依赖：

```bash
uv add requests python-dotenv openai
```

这通常会产生：

```plain text
pyproject.toml   # 项目依赖声明
uv.lock          # 锁定完整依赖版本，保证可复现
.venv/           # 项目虚拟环境
```

运行代码：

```bash
uv run python main.py
```

重点：`uv run` 会在项目环境里运行命令，不需要你手动先 `source .venv/bin/activate`。

### 4.5.4 uv 和 pip / venv 的关系

可以这样理解：

| 传统工具 | uv 对应能力 | 说明 |
| --- | --- | --- |
| `python -m venv .venv` | `uv venv` | 创建虚拟环境 |
| `pip install requests` | `uv pip install requests` 或 `uv add requests` | 安装依赖 |
| `pip freeze` | `uv lock` / `uv export` | 锁定或导出依赖 |
| `python main.py` | `uv run python main.py` | 在项目环境中运行脚本 |
| `pipx run ruff` | `uvx ruff` | 临时运行命令行工具 |
| `pyenv install 3.12` | `uv python install 3.12` | 安装 Python 版本 |

### 4.5.5 两种使用方式：项目模式 vs pip 兼容模式

项目模式适合新项目：

```bash
uv init
uv add fastapi uvicorn
uv run uvicorn app.main:app --reload
uv lock
uv sync
```

特点：依赖写入 `pyproject.toml`，完整版本写入 `uv.lock`。

pip 兼容模式适合旧项目：

```bash
uv venv
uv pip install -r requirements.txt
uv pip install requests
```

特点：保留原来的 `requirements.txt` 工作流，只是用 uv 提升速度和一致性。

### 4.5.6 常用命令速查

```bash
uv init my-project                 # 新建项目
uv add requests                    # 添加正式依赖
uv add --dev pytest ruff           # 添加开发依赖
uv remove requests                 # 移除依赖
uv run python main.py              # 在项目环境里运行脚本
uv run pytest -q                   # 在项目环境里跑测试
uv lock                            # 更新锁文件
uv sync                            # 根据 pyproject.toml / uv.lock 同步环境
uv venv                            # 创建 .venv
uv pip install -r requirements.txt # 安装 requirements 依赖
uvx ruff check .                   # 临时运行工具，不污染当前项目
```

### 4.5.7 管理 Python 版本

安装 Python：

```bash
uv python install 3.12
```

查看可用版本：

```bash
uv python list
```

给当前项目固定 Python 版本：

```bash
uv python pin 3.12
```

这会生成 `.python-version`，让当前目录默认使用指定 Python 版本。

### 4.5.8 单文件脚本也可以用 uv

如果只是一个脚本，也可以直接：

```bash
uv run script.py
```

如果脚本依赖第三方包，可以给脚本声明依赖：

```bash
uv add --script script.py requests
uv run script.py
```

这样 uv 会为脚本自动管理隔离环境，不需要你手动创建 venv。

### 4.5.9 uv.lock 要不要提交

一般建议提交：

```plain text
pyproject.toml  # 依赖声明：我需要哪些包
uv.lock         # 精确锁定：最终解析到了哪些具体版本
```

提交 `uv.lock` 的好处：

- 你和别人安装到的依赖版本一致。
- CI / 部署环境更可复现。
- 避免今天装出来能跑，过几天依赖升级后突然坏掉。

### 4.5.10 什么时候用 uv

适合：

- 新 Python 项目。
- Agent / FastAPI / RAG 项目。
- 经常重建虚拟环境的项目。
- 需要锁定依赖、提升安装速度的项目。
- 需要管理多个 Python 版本的学习环境。

可以先不急着换的情况：

- 课程或公司项目明确要求 `pip + requirements.txt`。
- 你只是临时跑一个极小脚本。
- 项目部署流程已经稳定，暂时不想动工具链。

### 4.5.11 推荐学习用法

对你现在的 Python / Agent 学习来说，推荐优先掌握这组命令：

```bash
uv init my-agent-demo
cd my-agent-demo
uv add python-dotenv openai fastapi uvicorn
uv add --dev pytest ruff
uv run python main.py
uv run pytest -q
uv sync
```

记住一句话：

```plain text
pip / venv 是基础，uv 是更现代的一体化工具；先理解环境隔离和依赖声明，再用 uv 提升效率和可复现性。
```

## 5. .env 与配置管理

`.env` 存真实配置，`.env.example` 存模板，`config.py` 负责读取并校验。

```plain text
.env              # 本地真实配置，不提交 Git
.env.example      # 配置模板，可以提交 Git
app/config.py     # 读取配置，提供给代码使用
```

`.env.example`：

```plain text
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-5
TIMEOUT_SECONDS=30
```

`app/config.py`：

```python
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # 把 .env 文件里的配置加载到环境变量

@dataclass(frozen=True)
class Settings:
openai_api_key: str             # 必填配置
model_name: str = "gpt-5"       # 有默认值
timeout_seconds: float = 30.0

def load_settings() -> Settings:
api_key = os.getenv("OPENAI_API_KEY")  # 从环境变量读取 API Key
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing")

return Settings(
    openai_api_key=api_key,
    model_name=os.getenv("MODEL_NAME", "gpt-5"),
    timeout_seconds=float(os.getenv("TIMEOUT_SECONDS", "30")),
)
```

原则：

- 密钥不要写死在代码里。
- `.env` 不提交 Git。
- 程序启动时尽早校验关键配置。

## 6. 推荐目录结构

```plain text
my-agent-project/
├── app/
│   ├── __init__.py          # 标记 app 是 Python package
│   ├── config.py            # 配置读取和校验
│   ├── logger.py            # 日志配置
│   ├── prompts.py           # prompt 模板
│   ├── schemas.py           # Pydantic / 数据结构
│   ├── services.py          # 外部 API / Notion / 数据库封装
│   ├── tools.py             # 可被 Agent 调用的工具函数
│   └── agent.py             # Agent 主流程
├── tests/
│   └── test_agent.py        # 测试
├── main.py                  # CLI 或程序入口
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml
└── README.md
```

小项目可以先简单一点：

```plain text
main.py
config.py
services.py
tests/
```

等复杂度上来再拆，不要为了“看起来专业”一开始拆太碎。

## 7. 模块拆分原则

常见职责：

- `main.py`：只做启动和参数接收。
- `config.py`：只负责配置读取和校验。
- `services.py`：封装外部 API 调用。
- `tools.py`：放明确可调用的工具函数。
- `agent.py`：组织 Agent 流程。
- `schemas.py`：定义请求、响应、结构化数据模型。
- `prompts.py`：集中管理 prompt。

反例：

```python
def run_agent():
## 读取配置
## 拼 prompt
## 调 OpenAI
## 调工具
## 写日志
## 处理异常
## 返回结果
pass
```

更好的拆法：

```python
def build_messages(user_input: str) -> list[dict]:
return [{"role": "user", "content": user_input}]

def call_llm(messages: list[dict]) -> str:
## 只负责调用模型
...

def run_agent(user_input: str) -> str:
## 只负责编排流程
messages = build_messages(user_input)
return call_llm(messages)
```

## 8. logging 日志

工程项目里不要到处 `print()`。日志要能区分级别、记录上下文，并且不要泄露密钥。

`app/logger.py`：

```python
import logging

logging.basicConfig(
level=logging.INFO,  # INFO 及以上级别会输出
format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent-demo")
```

使用：

```python
from app.logger import logger

logger.info("程序启动")                 # 普通运行信息
logger.debug("工具结果：%s", result)    # 调试信息，不建议生产默认开启
logger.warning("配置缺少可选项")        # 警告
logger.exception("调用外部 API 失败")   # 在 except 中记录完整异常栈
```

日志等级：

| 等级 | 用途 |
| --- | --- |
| DEBUG | 调试细节，最详细 |
| INFO | 正常运行信息 |
| WARNING | 可恢复的异常情况 |
| ERROR | 操作失败 |
| CRITICAL | 程序可能无法继续 |

不要记录：

- API Key。
- Token。
- 密码。
- 用户隐私原文。

## 9. 代码规范

命名：

```python
user_name = "Tom"          # 变量 / 函数：snake_case
DEFAULT_MODEL = "gpt-5"    # 常量：UPPER_CASE

class AgentRunner:          # 类名：PascalCase
pass
```

import 顺序：

```python
## 1. 标准库
import json
import logging

## 2. 第三方库
import httpx
from openai import OpenAI

## 3. 本项目模块
from app.config import load_settings
from app.logger import logger
```

类型注解：

```python
def get_weather(city: str) -> dict[str, str]:
return {
    "city": city,
    "temperature": "24°C",
}
```

类型注解的好处：

- IDE 提示更好。
- 读代码更清楚。
- Codex / ChatGPT 更容易理解项目。
- 更容易发现低级错误。

## 10. 异常处理规范

不要吞异常。

```python
try:
result = call_api()
except Exception:
logger.exception("调用 API 失败")  # 记录完整错误栈
raise                              # 继续抛出，让上层决定怎么处理
```

如果是面向用户的接口，可以转成友好错误：

```python
try:
result = call_api()
except Exception:
logger.exception("调用 API 失败")
return "服务暂时不可用，请稍后重试。"
```

注意：

- 底层函数不要随便 `return {}` 掩盖错误。
- 能处理就处理，不能处理就记录并抛出。
- 用户看到的是友好错误，日志里保留技术细节。

## 11. 测试 pytest

测试不一定一开始很多，但核心函数要能测。

```python
## app/tools.py
def add(a: int, b: int) -> int:
return a + b
```

```python
## tests/test_tools.py
from app.tools import add

def test_add():
assert add(1, 2) == 3
```

运行：

```bash
python -m pytest -q
```

测试优先覆盖：

- 纯函数。
- 工具函数。
- 配置读取。
- RAG chunking。
- API client 的错误处理。

## 12. Ruff

Ruff 用来做代码检查和格式化。

```bash
python -m pip install ruff
ruff check .       # 检查问题
ruff format .      # 自动格式化
```

建议提交前至少跑：

```bash
ruff check .
python -m pytest -q
```

## 13. README 模板

```markdown
## 项目名称

## 项目简介
说明这个项目解决什么问题。

## 功能说明
列出核心功能。

## 技术栈
Python / FastAPI / OpenAI / RAG / Docker 等。

## 项目结构
解释主要目录和文件。

## 环境准备
Python 版本、Docker、依赖工具。

## 安装依赖
如何创建 venv、安装 requirements。

## 配置 .env
说明需要哪些环境变量。

## 运行方式
本地如何启动。

## 测试
如何运行测试。

## 常见问题
记录常见报错和解决方法。
```

## 最小工程化清单

1. 每个项目使用 `.venv`。
2. 依赖写入 `requirements.txt` 或 `pyproject.toml`。
3. API Key 放 `.env`，并提供 `.env.example`。
4. 配置统一从 `config.py` 读取。
5. 日志用 `logging`，不要打印敏感信息。
6. 入口、服务、工具、prompt、测试分开。
7. 重要函数写类型注解。
8. 不写 `except: pass`。
9. 提交前运行 `ruff check .` 和 `python -m pytest -q`。

## 14. ai-agent-learning 里的工程化写法

这些写法在 `ai-agent-learning` 里频繁出现，读懂它们会比单纯背语法更有收益。

### 14.1 `Path(__file__).resolve().parent`：定位当前文件目录

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
```

逐段解释：

- `__file__`：当前 Python 文件路径。
- `Path(__file__)`：把字符串路径变成 Path 对象。
- `.resolve()`：转成绝对路径。
- `.parent`：取父目录。
- `BASE_DIR / ".env"`：用 `/` 拼路径，比字符串拼接更稳。

### 14.2 `@dataclass(frozen=True)`：配置对象不可修改

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
app_name: str
log_level: str
```

`dataclass` 自动生成初始化方法；`frozen=True` 表示创建后不允许随便改字段，适合配置对象。

### 14.3 `.env` 显式路径加载

```python
from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env")
```

比直接 `load_dotenv()` 更清楚，因为它明确告诉程序从哪个目录读 `.env`。在脚本从不同工作目录启动时，这点尤其重要。

### 14.4 `getattr(logging, level.upper(), logging.INFO)`

```python
import logging

def setup_logger(level: str = "INFO") -> logging.Logger:
logging.basicConfig(
    level=getattr(logging, level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
return logging.getLogger("project-template")
```

含义：把字符串 `"INFO" / "DEBUG"` 转成 logging 模块里的常量。第三个参数 `logging.INFO` 是默认值，避免用户传错配置时程序直接崩。
