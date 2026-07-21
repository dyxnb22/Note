# Agent 学习路径

## 推荐学习顺序

### 01 Python 工程化模板

路径：`01_python_project_template`

你会学到：

- Python 项目基础结构
- `.env`、`.gitignore`、`requirements.txt`
- logging 的基本使用

运行：

```bash
cd 01_python_project_template
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

练习：

- 增加 `APP_ENV`
- 修改日志级别
- 增加一个新的配置项

### 02 HTTP API Client

路径：`02_http_api_client`

你会学到：

- HTTP GET/POST
- headers、timeout、status_code
- JSON 解析
- requests 和 httpx 的区别

运行：

```bash
cd 02_http_api_client
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

练习：

- 增加一个新的 httpbin API
- 模拟 timeout 异常
- 改成并发请求多个 URL

### 03 OpenAI CLI Chat

路径：`03_openai_cli_chat`

你会学到：

- OpenAI SDK
- messages 对话结构
- system/user/assistant 的区别
- 多轮上下文保存

运行：

```bash
cd 03_openai_cli_chat
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

练习：

- 增加 `/reset`
- 限制历史消息长度
- 修改 system prompt

### 04 Tool Calling Agent

路径：`04_tool_calling_agent`

你会学到：

- tool 函数
- tool schema
- 模型如何返回 tool_calls
- Python 如何执行工具

运行：

```bash
cd 04_tool_calling_agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

练习：

- 增加时间工具
- 增加城市参数校验
- 打印完整 tool_calls

### 05 Simple Agent Loop

路径：`05_simple_agent_loop`

你会学到：

- Agent Loop
- Tool / Observation / Final Answer
- 为什么 Agent 需要循环
- 为什么要设置最大循环次数

运行：

```bash
cd 05_simple_agent_loop
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

练习：

- 增加新工具
- 记录每轮工具调用
- 让 Agent 在失败时重试一次

### 06 FastAPI Agent Service

路径：`06_fastapi_agent_service`

你会学到：

- FastAPI
- Pydantic Request/Response
- Agent Service 分层
- CLI 和 API 服务的区别

运行：

```bash
cd 06_fastapi_agent_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

练习：

- 增加 `/health`
- 增加 `conversation_id`
- 把第 05 课 Agent Loop 接进服务

### 07 LangGraph Basic Workflow

路径：`07_langgraph_basic_workflow`

你会学到：

- State
- Node
- Edge
- compile 和 invoke

运行：

```bash
cd 07_langgraph_basic_workflow
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

练习：

- 增加分类节点
- 增加条件边
- 打印最终 State

### 08 LangGraph Tool Agent

路径：`08_langgraph_tool_agent`

你会学到：

- ToolNode
- Conditional Edge
- LangGraph 中的工具执行流程
- 图结构如何表达 Agent 流程

运行：

```bash
cd 08_langgraph_tool_agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

练习：

- 增加时间工具
- 支持更多城市
- 把模拟 planner 替换成真实 LLM

### 09 LangGraph Memory Agent

路径：`09_langgraph_memory_agent`

你会学到：

- messages 历史
- memory 结构化记忆
- Checkpointer
- thread_id

运行：

```bash
cd 09_langgraph_memory_agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

练习：

- 记住城市
- 记住职业
- 切换 thread_id 观察记忆隔离

### 10 RAG Agent Basic

路径：`10_rag_agent_basic`

你会学到：

- document loading
- chunking
- retrieval
- context injection
- LLM answer

运行：

```bash
cd 10_rag_agent_basic
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

练习：

- 增加新文档
- 调整 chunk size
- 把关键词检索升级为 embedding 检索

### 11 MCP Server

路径：`11_mcp_server`

你会学到：

- MCP 三种原语：Tool（有副作用）/ Resource（只读）/ Prompt（模板）
- 用 `@mcp.tool()` 把普通 Python 函数变成 MCP 工具
- 一个完整的 Note Manager MCP Server 实现

运行：

```bash
cd 11_mcp_server
pip install "fastmcp>=2.0"     # 可选，没有则以 Mock 模式运行
python main.py
```

练习：

- 增加 delete_note 工具
- 增加 `notes://by-tag/{tag}` Resource
- 把 MCP Server 连接到 Claude Desktop 使用

### 12 Claude API Agent

路径：`12_claude_api_agent`

你会学到：

- Anthropic SDK 原生调用（不绕 LangChain）
- Prompt Caching：System Prompt 缓存，成本降低 90%
- Streaming 流式输出
- Tool Use 原生 API 格式（理解 LangChain @tool 背后的格式）
- 多轮对话历史管理

运行：

```bash
cd 12_claude_api_agent
pip install anthropic python-dotenv
cp .env.example .env    # 填入 ANTHROPIC_API_KEY
python main.py
```

练习：

- 实现带 Prompt Caching 的 RAG（把文档注入缓存 System Prompt）
- 改造成带流式输出的 FastAPI 服务
- 实现成本统计（记录每次调用的 Token 用量）

## 学完后下一步

01-10 是基础，11-12 是 2025+ 的关键扩展。学完后：

1. **把 11（MCP Server）和 12（Claude API）结合**：
   用 Claude API + MCP 工具，构建自己的工具服务平台

2. **升级 devpilot**：
   - 把 devpilot 的 Fixer Agent 接入真实 LLM（配置 ANTHROPIC_API_KEY 即可）
   - 把代码搜索工具做成 MCP Server，让 Cursor 也能用

3. **个人知识库 RAG Agent**（agent-learning-projects 10 的升级版）：
   - 真实 Embedding（text-embedding-3-small）
   - 混合检索（向量 + BM25）
   - 引用来源输出

4. **生产化**：
   - FastAPI 封装 → 前端对话界面
   - LangSmith / 自建评估框架 → 持续监控 Agent 质量
