# Python 工程基础

这里放做 AI 应用之前必须打牢的 Python 工程基础。

## 文档

| 文档 | 内容 |
|------|------|
| `Python.md` | 学习路径导航 |
| `Python核心语法.md` | 语言基础、标准库、类型注解、async/await |
| `Python工程化.md` | 虚拟环境、依赖管理、配置、日志、测试 |
| `Python Agent工程化补充.md` | 把 Pydantic、asyncio、类型边界和稳定性连接到 Agent Runtime |
| `Python代码组织与设计模式.md` | Service/Client/Repository/Pipeline 架构模式 |
| `HTTP与API调用.md` | requests/httpx、超时、重试、客户端封装 |
| `FastAPI.md` | 路由、请求响应模型、依赖注入、服务化 |
| `错误与Debug.md` | 排错顺序、常见错误、最小复现 |

## 按场景选文档

**Python 零基础入门**
→ `Python.md`（路径导航）→ `Python核心语法.md` → `Python工程化.md`

**有 Python 基础，直接做 AI 项目**
→ 先扫 `Python工程化.md`（虚拟环境 + 依赖管理）→ `Python Agent工程化补充.md`（Pydantic + asyncio + 类型边界）→ `HTTP与API调用.md`（httpx 异步调用）→ 进 `../Agent/LLM调用基础.md`

**需要把 Agent 做成 API 服务**
→ `FastAPI.md` → `Python代码组织与设计模式.md`（Service/Repository 分层）

**线上出了问题不会 debug**
→ `错误与Debug.md`

## 必读 vs 按需

| 文档 | 分类 | 说明 |
|------|------|------|
| `Python核心语法.md` | **必读**（Python 不熟时）| async/await 是 AI 应用的基础 |
| `Python工程化.md` | **必读** | 依赖管理、日志、测试，每个项目都要用 |
| `Python Agent工程化补充.md` | **Agent 前置** | 把 Python 能力落到数据边界、并发、重试和测试 |
| `HTTP与API调用.md` | **必读** | httpx 异步调用 LLM API 的前置 |
| `FastAPI.md` | 按需 | 需要服务化时读 |
| `Python代码组织与设计模式.md` | 按需 | 项目变复杂、需要重构时读 |
| `错误与Debug.md` | 按需 | 遇到难 debug 的问题时读 |

## 与 Agent/ 目录的边界

- Python 语言本身、工程规范、HTTP 调用 → 放这里
- Pydantic、asyncio、重试、类型边界等 Python 能力如何服务 Agent → 看 `Python Agent工程化补充.md`
- 一旦涉及 LLM、Agent、RAG、工具协议 → 放 `Agent/`
