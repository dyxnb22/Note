# Python代码组织与设计模式
这一页不是传统“设计模式大全”，而是整理 Python / Agent / FastAPI / RAG 项目里最常见、最实用的代码组织方式。目标是从“看懂语法”过渡到“看懂项目为什么这样拆”。

## 1. 为什么需要代码组织

小脚本可以一个文件写完，但项目变大后会遇到：业务逻辑、API 调用、工具调用、配置、日志全部混在一起，导致不好测试、难 Debug、也不容易替换模型或外部服务。

好的代码组织应该做到：

- 每个文件职责清楚。
- 路由层不要堆业务逻辑。
- 外部 API 调用集中封装。
- 工具函数有白名单注册表。
- 复杂流程能被拆成多个步骤。

## 2. 常见分层

```plain text
app/
├── main.py          # 程序入口，创建 FastAPI app 或 CLI 入口
├── config.py        # 配置读取
├── schemas.py       # 请求/响应/State 数据结构
├── services.py      # 业务服务
├── clients.py       # 外部 API client
├── tools.py         # Agent 工具函数
├── graph.py         # LangGraph 编排
├── memory.py        # 记忆或 checkpoint
└── logger.py        # 日志
```

粗略分工：

- `main.py`：负责启动，不堆业务逻辑。
- `config.py`：负责配置。
- `schemas.py`：负责数据结构。
- `clients.py`：负责和外部系统通信。
- `services.py`：负责编排业务流程。
- `tools.py`：放可被 Agent 调用的动作。
- `graph.py`：放 LangGraph 节点和边。

## 3. Service 模式

Service 负责业务流程，不直接关心 HTTP 细节，也不直接关心页面展示。

```text
class AgentService:
def __init__(self, llm_client, tool_registry):
    self.llm_client = llm_client
    self.tool_registry = tool_registry

def answer(self, question: str) -> str:
## 1. 构造 messages
## 2. 调用 LLM
## 3. 如果有工具调用，执行工具
## 4. 返回最终答案
    return "answer"
```

FastAPI 路由里只调用 service：

```text
@app.post("/chat")
def chat(req: ChatRequest) -> ChatResponse:
answer = agent_service.answer(req.message)
return ChatResponse(answer=answer)
```

好处：路由函数很薄，Service 可以单独测试，CLI、FastAPI、定时任务都能复用同一个 Service。

## 4. Client 模式

Client 封装外部系统调用，例如 OpenAI、Notion、GitHub、向量数据库、天气 API。

```text
class WeatherClient:
def __init__(self, base_url: str, api_key: str):
    self.base_url = base_url
    self.api_key = api_key

def get_weather(self, city: str) -> dict:
    return {"city": city, "temperature": "26°C"}
```

业务代码只调用：

```python
weather = weather_client.get_weather("香港")
```

好处：timeout、headers、认证统一管理；替换 API 提供商更容易；也更容易 mock 测试。

## 5. Repository 模式

Repository 负责数据读写。常用于数据库、文件、向量库、Notion 页面。

```text
class NoteRepository:
def search(self, query: str) -> list[dict]:
    ...

def save(self, note: dict) -> None:
    ...
```

Service 不需要知道数据到底存在 Markdown、Notion、SQLite 还是向量库里。

## 6. Registry / tool_map 模式

Tool Calling 里最重要的组织方式之一就是注册表。

```text
def get_weather(city: str) -> dict:
return {"city": city, "temperature": "26°C"}

def get_current_time() -> dict:
return {"time": "2026-05-19T10:00:00"}

tool_map = {
"get_weather": get_weather,
"get_current_time": get_current_time,
}
```

执行工具：

```text
def run_tool(name: str, args: dict) -> dict:
tool = tool_map.get(name)
if tool is None:
    return {"error": f"unknown tool: {name}"}
return tool(**args)
```

不要用：

```python
eval(name)(**args)  # 危险，不可控
```

Registry 的价值：白名单控制、方便列出所有工具、方便加权限、日志和错误处理。

## 7. Factory 模式

Factory 负责创建对象，尤其是对象创建过程比较复杂时。

```text
def create_llm_client(settings: Settings):
return OpenAI(api_key=settings.openai_api_key)
```

或者：

```text
def create_vector_store(kind: str):
if kind == "chroma":
    return ChromaStore()
if kind == "memory":
    return InMemoryStore()
raise ValueError(f"unknown vector store: {kind}")
```

好处：创建逻辑集中管理；替换实现更容易；测试时可以换成 fake client。

## 8. Pipeline 模式

Pipeline 把流程拆成多个连续步骤。RAG、Agent、数据清洗都常见。

```text
def run_rag_pipeline(question: str) -> str:
query = rewrite_query(question)
chunks = retrieve(query)
context = build_context(chunks)
answer = call_llm(question, context)
return answer
```

对应 RAG：

```plain text
question → rewrite_query → retrieve → build_context → call_llm → answer
```

好处：每一步可以单独测试，出错时容易定位，后续也可以把步骤搬进 LangGraph。

## 9. Adapter 模式

Adapter 用来统一不同外部系统的接口。

```text
class OpenAIAdapter:
def chat(self, messages: list[dict]) -> str:
    ...

class DeepSeekAdapter:
def chat(self, messages: list[dict]) -> str:
    ...
```

业务层只依赖统一接口：

```text
def ask_model(client, messages: list[dict]) -> str:
return client.chat(messages)
```

好处：模型提供商可以换，但业务代码不用到处改。

## 10. Dependency Injection 依赖注入

依赖注入就是：不要在函数内部偷偷创建所有对象，而是从外面传进来。

不推荐：

```text
def answer(question: str) -> str:
client = OpenAI()
return client.responses.create(...)
```

推荐：

```text
def answer(question: str, llm_client) -> str:
return llm_client.ask(question)
```

FastAPI 里的 `Depends` 就是依赖注入的一种形式。

## 11. 如何判断该不该抽象

- 只有一个地方用：先写函数。
- 两三个地方重复：考虑抽函数。
- 有状态、配置、多个方法：考虑类。
- 要替换实现：考虑接口 / Protocol / Adapter。
- 要管理很多同类能力：考虑 Registry。
- 流程有多个稳定步骤：考虑 Pipeline 或 LangGraph。

## 12. Agent 项目推荐组合

FastAPI 项目：

```plain text
FastAPI route → AgentService → LLM Client → Tool Registry → Tool Functions → Repository / External Client
```

LangGraph 项目：

```plain text
graph.py → nodes.py → state.py → tools.py → services.py → clients.py
```

RAG 项目：

```plain text
RAGService → Retriever → VectorStore Repository → LLM Client → Answer Builder
```

## 复习清单

- 能解释 Service 和 Client 的区别。
- 能解释为什么 Tool Calling 要用 tool_map / Registry。
- 能把一个大函数拆成 Pipeline。
- 能说出 Repository 解决什么问题。
- 能解释 Factory 什么时候有用。
- 能判断什么时候不需要抽象。
- 能把 FastAPI route 写薄，把业务逻辑放到 Service。
