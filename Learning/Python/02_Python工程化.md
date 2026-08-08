# Python 工程化

工程化解决的不是“代码能不能跑”，而是环境、依赖、配置、日志、测试和发布能否重复。本文给出学习项目和 AI 服务都能使用的最小闭环；Python 语法见 [核心语法](./01_Python核心语法.md)，Agent 边界见 [Python Agent 工程化补充](./04_Python%20Agent工程化补充.md)。

## 1. 最小工程合同

一个可交付 Python 项目至少需要：

```text
pyproject.toml / requirements.txt
src 或 app/              # 业务代码
tests/                   # 可重复测试
.env.example             # 配置示例，不放真实密钥
README.md                # 安装、运行、测试和边界
.gitignore
```

代码、依赖、配置、数据和运行命令要能被另一台机器理解并复现。

## 2. 环境与依赖

传统 `venv + pip` 足够学习和小项目：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

现代项目可以使用 `uv`，但不要同时维护多套互相矛盾的依赖真相：

```bash
uv init
uv add httpx pydantic
uv add --dev pytest ruff
uv run pytest
```

团队项目提交锁文件；升级依赖前运行测试、检查 changelog 并记录版本变化。依赖应按运行时/开发时区分，避免把整个开发环境打进生产镜像。

## 3. pyproject.toml

```toml
[project]
name = "example-agent"
requires-python = ">=3.11"
dependencies = ["httpx>=0.27", "pydantic>=2"]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[tool.ruff]
line-length = 100
```

Python 版本、依赖范围、格式和检查规则写进项目文件；不要只依赖个人机器上的全局环境。

## 4. 配置与 Secret

```python
import os


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing configuration: {name}")
    return value


API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = required_env("API_KEY")
```

配置来源按“代码默认值 → 环境/配置文件 → Secret Manager”分层；`.env.example` 只写变量名和示例格式，真实 `.env` 不提交。启动时校验必填配置、类型、范围和互斥关系。

## 5. 推荐目录与模块边界

```text
src/app/
  main.py          # 组装依赖和启动
  config.py        # 配置读取
  domain.py        # 领域类型和规则
  clients/         # 外部 API 客户端
  services/        # 用例编排
  repositories/    # 数据持久化
tests/
```

依赖方向尽量单向：入口 → Service → Domain/Repository/Client。Service 不应偷偷读取环境变量或创建全局客户端；外部客户端通过参数注入，测试才能替换。

## 6. 日志与错误

```python
import logging

logger = logging.getLogger(__name__)


def process(task_id: str) -> None:
    logger.info("task_started", extra={"task_id": task_id})
    try:
        run_task(task_id)
    except ExpectedError:
        logger.warning("task_rejected", extra={"task_id": task_id})
        raise
    except Exception:
        logger.exception("task_failed", extra={"task_id": task_id})
        raise
```

日志记录事件、任务 ID、耗时、结果和错误类别，不默认记录密钥、完整用户输入或大响应。库代码不要配置 root logger；由应用入口统一决定格式、级别、输出和脱敏。

错误分层：输入错误返回可理解的错误码；外部依赖错误记录上下文并按策略重试；不可恢复错误停止并报警。不要裸捕获后返回“成功”。

## 7. 测试

测试优先覆盖纯函数、边界和失败路径，再覆盖外部集成：

```python
def normalize_limit(value: int) -> int:
    if value < 1 or value > 100:
        raise ValueError("limit_out_of_range")
    return value


def test_normalize_limit_rejects_zero() -> None:
    import pytest

    with pytest.raises(ValueError, match="limit_out_of_range"):
        normalize_limit(0)
```

外部 HTTP、数据库和模型调用通过接口或 mock 隔离；集成测试使用临时资源并清理。测试要检查结果、调用次数、超时、错误映射和副作用，而不只看“没有抛异常”。

## 8. 格式、类型和提交前检查

```bash
ruff format .
ruff check .
pytest -q
# 有类型检查时：mypy src
```

格式化减少无意义 diff；lint 发现明显错误；类型检查约束接口；测试验证行为。提交前检查 `git diff`，不要把 `.env`、缓存、构建物、密钥和本地数据库带进仓库。

## 9. README 最小内容

```text
项目解决什么问题
环境与 Python 版本
安装依赖
配置项和安全边界
运行命令
测试命令
目录结构
已知限制与排错入口
```

README 是运行合同，不是把代码逐行解释一遍；细节放模块文档和测试。

## 10. 进入 Agent 项目

Agent 项目至少把以下边界显式化：

- Provider、模型和工具配置可替换；
- 输入和模型输出经过 schema/业务校验；
- HTTP/工具调用有超时、有限重试和错误码；
- 日志有 task/trace ID 且脱敏；
- 测试能 mock 模型并验证工具轨迹；
- 运行命令、依赖和 `.env.example` 可复现。

示例项目中的 `Path(__file__).resolve().parent`、不可变配置对象和显式 `.env` 路径都只是实现细节，核心仍是“配置集中、依赖可复现、边界可测试”。

## 最小工程化清单

- 新建虚拟环境，不依赖全局包；
- 依赖有唯一来源并锁定版本；
- Secret 不进代码、Git、日志和测试样本；
- 入口、配置、业务、外部客户端和测试分层；
- 有格式、lint、类型（如适用）和测试命令；
- 失败能定位到输入、代码、依赖或环境。

下一步：[Python Agent 工程化补充](./04_Python%20Agent工程化补充.md)。
