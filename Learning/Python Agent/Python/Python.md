# Python 学习路径
这套页面按“先能读懂 Python 项目 → 再能写小工具 → 最后做 Agent 项目”的顺序整理。现在的重点不是把所有知识堆在一个页面，而是让每个页面职责清楚，减少重复。
## 推荐学习阶段
### 阶段 1：语言基础
先看 `Python核心语法`。
目标：能看懂变量、字符串、list/dict、函数、异常、文件、JSON、模块、async/await。
适合练习：小脚本、文件读写、JSON 处理。
### 阶段 2：Python 工程化
再看 `Python工程化`。
目标：理解项目为什么要有 `.venv`、`pyproject.toml`、`src/`、`__init__.py`、`python -m`、配置、日志、测试，以及如何把函数暴露成简单 CLI 命令。
适合练习：从 0 创建一个能运行的 Python package，再加一个 `sac ask ...` 或 `task add ...` 这样的命令入口。
### 阶段 3：外部 API 与 LLM
依次看：
1. `HTTP与API调用`
2. `OpenAI SDK与LLM调用`
3. `Tool Calling`
目标：能调用 HTTP API，能调用模型，能理解“模型生成工具调用，Python 真正执行工具”。
### 阶段 4：Agent 架构
依次看：
1. `Agent基础架构`
2. `RAG`
3. `LangGraph`
4. `MCP`
目标：理解 State、Tool、Memory、Agent Loop、RAG 检索、图编排和外部工具协议。
### 阶段 5：服务化、部署和实战
依次看：
1. `FastAPI`
2. `部署与上线`
3. `错误与Debug`
4. `Prompt Engineering`
5. `项目实战`
6. `Python代码组织与设计模式`
目标：把能力做成服务，能部署，能排错，能组织成可维护项目。
## 页面职责边界
| 页面 | 只负责什么 | 不重复什么 |
| --- | --- | --- |
| Python核心语法 | 语言基础、标准库、类型注解基础 | 不讲项目结构和 CLI 工具封装 |
| Python工程化 | 环境、依赖、配置、日志、测试、项目启动方式、简单 CLI 入口 | 不深入讲 Service / Client / Repository 等架构模式 |
| HTTP与API调用 | requests/httpx、timeout、retry、client 封装 | 不讲 OpenAI SDK 专属用法 |
| OpenAI SDK与LLM调用 | 模型调用、多轮、stream、结构化输出 | 不展开完整 Tool Calling 执行循环 |
| Tool Calling | 工具 schema、tool_map、执行工具、安全边界 | 不讲 LangGraph 图编排 |
| Agent基础架构 | Agent Loop、State、Memory、Planning | 不深入讲具体框架 API |
| RAG | chunk、embedding、retrieval、rerank、评估 | 不讲通用 HTTP 和 FastAPI 基础 |
| LangGraph | StateGraph、Node、Edge、checkpoint、interrupt | 不重复 Agent 基础概念太多 |
| FastAPI | 路由、请求响应模型、Depends、服务化 | 不讲 Agent 内部实现 |
| Python代码组织与设计模式 | Service、Client、Repository、Registry、Pipeline | 不重复基础项目结构 |
| 错误与Debug | 排错顺序、常见错误、最小复现 | 不替代各页面的具体概念学习 |
| Prompt Engineering | prompt 结构、边界、输出格式 | 不讲 Python 语法和 API 细节 |
| 部署与上线 | Docker、环境变量、日志、运行稳定性 | 不讲本地开发基础 |
| 项目实战 | 串联路线，分阶段做项目 | 不把所有理论重新讲一遍 |

## 子页面

- [[Python核心语法]]
- [[Python工程化]]
- [[HTTP与API调用]]
- [[FastAPI]]
- [[部署与上线]]
- [[错误与Debug]]
- [[Python代码组织与设计模式]]
