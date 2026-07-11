# FastAPI
FastAPI 是 Python 里非常适合做 API 服务的 Web 框架。对 Agent 项目来说，它通常负责把本地能力包装成 HTTP 接口，例如聊天接口、文件上传、RAG 查询、Tool 执行、流式输出。

## 1. FastAPI 在这条路线里的位置

```plain text
Python 基础
→ Python 工程化
→ HTTP/API 调用
→ OpenAI SDK
→ FastAPI 对外提供接口
→ RAG / Agent / LangGraph 作为后端能力
```

FastAPI 解决的是“把 Python 能力变成服务”的问题。它不负责替你做 RAG、Agent 或部署，而是把这些能力通过 HTTP 暴露出去。

## 2. 安装与最小应用

```bash
python -m pip install fastapi uvicorn  # fastapi 是框架，uvicorn 是 ASGI 服务器
uvicorn main:app --reload              # main:app = main.py 文件里的 app 对象
## --reload 表示开发模式热重载，代码保存后自动重启；正式部署一般不用
```

```python
## main.py
from fastapi import FastAPI

app = FastAPI(title="Agent API")  # 创建 FastAPI 应用对象

@app.get("/health")               # 注册 GET /health 路由
def health():
return {"status": "ok"}       # 返回 dict，会自动转成 JSON
```

访问：

- `http://127.0.0.1:8000/health`：健康检查接口。
- `http://127.0.0.1:8000/docs`：Swagger 文档，可以直接测试接口。
- `http://127.0.0.1:8000/redoc`：另一种文档展示。

## 3. GET / POST 接口

GET 通常用于查询，POST 通常用于提交数据或触发动作。

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
## 请求体模型：前端 POST JSON 时必须包含 message 字段
message: str

class ChatResponse(BaseModel):
## 响应体模型：后端返回的数据应该包含 answer 字段
answer: str

@app.get("/items/{item_id}")
def get_item(item_id: int, q: str | None = None):
## item_id 来自路径：/items/123
## q 来自 query：/items/123?q=python
return {"item_id": item_id, "q": q}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
## req 是经过 Pydantic 校验后的对象
return ChatResponse(answer=f"你说的是：{req.message}")
```

请求示例：

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好"}'
```

## 4. Pydantic 数据模型

Pydantic 用来做请求校验、类型转换、响应结构定义和文档生成。

```python
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
query: str = Field(min_length=1, description="用户问题")
## min_length=1 表示不能为空字符串

top_k: int = Field(default=5, ge=1, le=20)
## default=5 默认值是 5
## ge=1 表示 >= 1
## le=20 表示 <= 20

class SearchResult(BaseModel):
title: str
content: str
score: float
```

好处：

- 请求字段自动校验。
- 类型不对会自动返回 422 错误。
- 自动生成 API 文档。
- 前后端联调时字段更清楚。

## 5. Request / Response 数据来源

常见数据来源：

- path 参数：`/items/{item_id}`。
- query 参数：`?q=python`。
- body：POST JSON。
- header：认证、trace id、客户端信息。

```python
from fastapi import Header, HTTPException

@app.get("/me")
def me(authorization: str | None = Header(default=None)):
## Header(default=None) 表示从请求头里读取 Authorization
if not authorization:
    raise HTTPException(status_code=401, detail="Missing Authorization")
return {"ok": True}
```

`HTTPException` 会直接返回 HTTP 错误响应，不会继续往下执行。

## 6. async API

如果接口里有网络请求、数据库查询、LLM 调用、RAG 检索，通常适合 `async def`。

```python
import httpx

@app.get("/external")
async def external():
async with httpx.AsyncClient(timeout=10.0) as client:
## await 表示等待 HTTP 请求完成；等待期间事件循环可以处理其他请求
    response = await client.get("https://httpbin.org/get")
    response.raise_for_status()
    return response.json()
```

注意：

- `async def` 里不要调用长时间阻塞的同步代码。
- 同步 CPU 密集任务会卡住事件循环。
- 调 LLM / HTTP / DB 时优先使用异步客户端。

## 7. 依赖注入 Depends

依赖注入用来复用认证、配置、数据库连接、service 对象。

```python
from fastapi import Depends, HTTPException

class Settings:
api_key: str = "demo"

def get_settings() -> Settings:
## 真实项目里这里会读取 .env / config.py
return Settings()

def verify_token(token: str | None = None):
## 真实项目里 token 应该来自 Header 或 Cookie
if token != "secret":
    raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/secure")
def secure(
_: None = Depends(verify_token),
settings: Settings = Depends(get_settings),
):
return {"api_key_configured": bool(settings.api_key)}
```

真实项目里常见依赖：

- `get_settings()`。
- `get_db()`。
- `get_current_user()`。
- `get_llm_client()`。
- `get_vector_store()`。
