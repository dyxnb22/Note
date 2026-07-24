# Python 工程基础

这里放做 AI 应用之前必须打牢的 Python 工程基础。

总路线见：[Python → AI → Agent 学习地图](../00_Navigation/AI-Python-Agent学习地图.md)。

代码块约定：标为 `python` 的片段应能通过语法解析；标为 `text` 的内容是局部结构、命令输出或省略上下文的伪代码，不能直接复制运行。完整可运行链路优先放在 `实践/`。

## 文档

| 文档 | 内容 |
|------|------|
| `01_Python核心语法.md` | 语言基础、标准库、类型注解、async/await |
| `02_Python工程化.md` | 虚拟环境、依赖管理、配置、日志、测试 |
| `04_Python Agent工程化补充.md` | 把 Pydantic、asyncio、类型边界和稳定性连接到 Agent Runtime |
| `Python代码组织与设计模式.md` | Service/Client/Repository/Pipeline 架构模式 |
| `03_HTTP与API调用.md` | requests/httpx、超时、重试、客户端封装 |
| `FastAPI.md` | 路由、请求响应模型、依赖注入、服务化 |
| `错误与Debug.md` | 排错顺序、常见错误、最小复现 |

## 按场景选文档

**Python 零基础入门**
→ `01_Python核心语法.md` → `02_Python工程化.md` → `03_HTTP与API调用.md`

**有 Python 基础，直接做 AI 项目**
→ 先扫 `02_Python工程化.md`（虚拟环境 + 依赖管理）→ `04_Python Agent工程化补充.md`（Pydantic + asyncio + 类型边界）→ `03_HTTP与API调用.md`（httpx 异步调用）→ 进 `../Agent/01_LLM调用基础.md`

**需要把 Agent 做成 API 服务**
→ `FastAPI.md` → `Python代码组织与设计模式.md`（Service/Repository 分层）

**线上出了问题不会 debug**
→ `错误与Debug.md`

## 必读 vs 按需

| 文档 | 分类 | 说明 |
|------|------|------|
| `01_Python核心语法.md` | **必读**（Python 不熟时）| async/await 是 AI 应用的基础 |
| `02_Python工程化.md` | **必读** | 依赖管理、日志、测试，每个项目都要用 |
| `04_Python Agent工程化补充.md` | **Agent 前置** | 把 Python 能力落到数据边界、并发、重试和测试 |
| `03_HTTP与API调用.md` | **必读** | httpx 异步调用 LLM API 的前置 |
| `FastAPI.md` | 按需 | 需要服务化时读 |
| `Python代码组织与设计模式.md` | 按需 | 项目变复杂、需要重构时读 |
| `错误与Debug.md` | 按需 | 遇到难 debug 的问题时读 |

## 进入 Agent

完成 Python 基础和工程化后，进入 [AI Agent 工程知识库](../Agent/README.md)；完整路线见 [AI Agent 工程学习路线图](../Agent/00_学习路线图.md)。最小主线是：

`LLM 调用基础 → Tool Calling → Agent 架构与设计 → Context 工程 → 安全/验证 → Eval`

知识库问答再加 RAG 与知识系统；固定流程先看 Workflow 与编排，再按需使用 LangGraph；需要 API 交付时回到 FastAPI。

## 与 Agent/ 目录的边界

- Python 语言本身、工程规范、HTTP 调用 → 放这里
- Pydantic、asyncio、重试、类型边界等 Python 能力如何服务 Agent → 看 `04_Python Agent工程化补充.md`
- 一旦涉及 LLM、Agent、RAG、工具协议 → 放 `Agent/`

## 配套实践

- [Python 基础练习](./实践/Python基础练习/README.md)：只用于复习 Python 变量、类型、输出和条件判断，不属于 Agent 主线。
