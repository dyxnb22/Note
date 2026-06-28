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
<table header-row="true">
<tr>
<td>页面</td>
<td>只负责什么</td>
<td>不重复什么</td>
</tr>
<tr>
<td>Python核心语法</td>
<td>语言基础、标准库、类型注解基础</td>
<td>不讲项目结构和 CLI 工具封装</td>
</tr>
<tr>
<td>Python工程化</td>
<td>环境、依赖、配置、日志、测试、项目启动方式、简单 CLI 入口</td>
<td>不深入讲 Service / Client / Repository 等架构模式</td>
</tr>
<tr>
<td>HTTP与API调用</td>
<td>requests/httpx、timeout、retry、client 封装</td>
<td>不讲 OpenAI SDK 专属用法</td>
</tr>
<tr>
<td>OpenAI SDK与LLM调用</td>
<td>模型调用、多轮、stream、结构化输出</td>
<td>不展开完整 Tool Calling 执行循环</td>
</tr>
<tr>
<td>Tool Calling</td>
<td>工具 schema、tool_map、执行工具、安全边界</td>
<td>不讲 LangGraph 图编排</td>
</tr>
<tr>
<td>Agent基础架构</td>
<td>Agent Loop、State、Memory、Planning</td>
<td>不深入讲具体框架 API</td>
</tr>
<tr>
<td>RAG</td>
<td>chunk、embedding、retrieval、rerank、评估</td>
<td>不讲通用 HTTP 和 FastAPI 基础</td>
</tr>
<tr>
<td>LangGraph</td>
<td>StateGraph、Node、Edge、checkpoint、interrupt</td>
<td>不重复 Agent 基础概念太多</td>
</tr>
<tr>
<td>FastAPI</td>
<td>路由、请求响应模型、Depends、服务化</td>
<td>不讲 Agent 内部实现</td>
</tr>
<tr>
<td>Python代码组织与设计模式</td>
<td>Service、Client、Repository、Registry、Pipeline</td>
<td>不重复基础项目结构</td>
</tr>
<tr>
<td>错误与Debug</td>
<td>排错顺序、常见错误、最小复现</td>
<td>不替代各页面的具体概念学习</td>
</tr>
<tr>
<td>Prompt Engineering</td>
<td>prompt 结构、边界、输出格式</td>
<td>不讲 Python 语法和 API 细节</td>
</tr>
<tr>
<td>部署与上线</td>
<td>Docker、环境变量、日志、运行稳定性</td>
<td>不讲本地开发基础</td>
</tr>
<tr>
<td>项目实战</td>
<td>串联路线，分阶段做项目</td>
<td>不把所有理论重新讲一遍</td>
</tr>
</table>
## 子页面

- [[Python核心语法]]
- [[Python工程化]]
- [[HTTP与API调用]]
- [[FastAPI]]
- [[部署与上线]]
- [[错误与Debug]]
- [[Python代码组织与设计模式]]
