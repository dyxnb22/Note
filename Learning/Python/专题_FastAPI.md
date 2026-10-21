# 专题：FastAPI

> FastAPI 使用 Starlette 处理路由和中间件，并结合 Pydantic 完成数据校验与序列化。本专题介绍路由、依赖、生命周期和响应模型等机制。

## 应用与路由

FastAPI() 创建应用；`@app.get("/items")` 将下方函数注册为 GET 路由。POST、PUT、PATCH、DELETE 分别使用 app.post、app.put、app.patch、app.delete；这些是独立方法，不是一个带斜线的方法名。

- 路径参数写进路径并带类型：`/users/{uid}`，类型转换和校验自动做；想限制取值范围用 `Path(ge=1)` 或 `Literal`。
- 参数来源由路径模板、类型注解和 Query / Body / Header 等声明共同决定。路径中的同名参数来自路径，普通标量参数通常来自查询字符串，Pydantic 模型通常作为请求体；需要显式指定来源或外部名称时，使用对应声明及 alias。
- `HTTPException(status_code, detail)` 抛出即返回对应状态码；自定义状态码用装饰器参数或 `Response`。
- 路由按注册顺序尝试匹配。如果固定路径可能与动态路径重叠，应先注册固定路径，避免请求进入不符合预期的处理函数。

```python
from typing import Annotated
from fastapi import FastAPI, Path, Query
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/items/{item_id}")
def read_item(
    item_id: Annotated[int, Path(ge=1)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return {"item_id": item_id, "limit": limit}


with TestClient(app) as client:
    response = client.get("/items/2?limit=3")
    assert response.json() == {"item_id": 2, "limit": 3}
    assert client.get("/items/0").status_code == 422
```

item_id 从路径取值，limit 从查询字符串取值；框架将文本转换为整数，再检查范围。这里 TestClient 在进程内发送请求，不需要启动监听端口的服务器。

## 依赖注入

- `Depends(callable)` 注入依赖；依赖也是函数，可以再依赖其他依赖，形成**依赖树**，框架按需解析。
- yield 依赖将准备与清理包围在一次依赖使用范围内；现代版本的退出时机受 Depends 的 scope 影响，请求作用域通常在响应发送后退出，函数作用域可在路由返回后更早退出。应结合版本与流式响应需要选择。

```python
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


# 教学用会话替身，只展示生命周期，不连接数据库。
class Session:
    closed = False

    def close(self):
        self.closed = True


sessions = []


def get_session():
    session = Session()
    sessions.append(session)
    try:
        yield session
    finally:
        session.close()


app = FastAPI()


@app.get("/status")
def status(session: Annotated[Session, Depends(get_session)]):
    return {"closed": session.closed}


with TestClient(app) as client:
    assert client.get("/status").json() == {"closed": False}
assert sessions[0].closed is True
```

- 同一个请求内，同一个依赖默认**只解析一次**并缓存；要每次解析传 `Depends(fn, use_cache=False)`。
- 测试时，通过 `app.dependency_overrides` 将依赖函数替换为测试实现。这样可以控制输入和失败场景，不必修改依赖内部的数据库调用。
- 依赖适合解析身份和检查入口权限。与具体资源、租户或状态相关的授权，需要在拥有这些信息的位置检查，避免其他调用路径绕过约束。

## 生命周期

- 新代码通常用 `lifespan` 上下文管理器管理启动与关闭。较早的 `on_event` 生命周期注册方式已被弃用，迁移时按项目使用的版本核对：

```python
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient() as client:
        app.state.client = client
        yield  # 离开时由 async with 清理客户端


app = FastAPI(lifespan=lifespan)

from fastapi.testclient import TestClient

with TestClient(app):
    assert not app.state.client.is_closed
assert app.state.client.is_closed
```

- **应用级资源**(HTTP 客户端、连接池)在启动创建、关闭释放，存 `app.state`；请求级资源(DB 会话)放 `yield` 依赖。通常复用应用级客户端以利用连接池；如果必须临时创建，正确使用 with/async with 仍可清理，并非“新建就必然泄漏”。

## 同步端点与异步端点

- `async def` 端点跑在事件循环上；在其中执行耗时阻塞 I/O 会阻碍该事件循环的任务调度；不能因此概括为整个多进程服务只能处理一个请求。
- 同步路由通常由线程池执行。它不会直接占用事件循环执行阻塞操作，但仍受线程池容量限制；任务较多时可能等待可用线程。
- 选型：端点里是异步库(httpx.AsyncClient、async SQLAlchemy)就 `async def`；只有同步库就 `def`；同步函数直接调用异步函数只得到协程对象，不会完成异步操作；跨线程或事件循环的桥接需明确设计。异步路由需要使用同步阻塞库时，可考虑在线程中执行。
- 调整线程池前，先观察等待时间、活跃任务和下游延迟。容量不足可能导致排队，但扩大线程池也可能将压力转移给下游。

## 错误处理

- 未捕获的 `ValueError` 等变成 500；`HTTPException` 变成对应状态码；请求输入校验失败通常是 422；内部或响应校验失败不属于这一请求错误路径。
- 用 `@app.exception_handler(MyError)` 注册处理器，把业务异常映射成**统一错误体**(稳定 `code` + 人类可读 `message` + 可选 `request_id`)，不要把堆栈、SQL、内部字段泄漏给客户端。
- 默认的请求校验错误响应通常在 `detail` 中包含结构化错误列表。具体字段受框架版本和自定义错误处理器影响。
- 对外接口应明确错误格式，并检查是否包含不应暴露的输入或内部信息。
- `debug=True` 会在响应里返回堆栈，只能用于本地。

## 中间件

- `@app.middleware("http")` 或继承 `BaseHTTPMiddleware` 做请求级横切：注入 `request_id`、统一日志、计时、简单限流。
- 中间件可以在调用下游应用前处理请求，并在下游返回后处理响应。通用计时、日志适合放在这里；需要路由参数或依赖组合的逻辑通常更适合依赖。中间件也能处理认证，但不会自动成为路由的依赖声明或 OpenAPI 安全说明。
- 中间件里做耗时操作会加在所有请求上；重活下放路由或依赖。
- 需要精确控制流式响应、上下文传播或性能时，可以编写纯 ASGI 中间件。使用 `BaseHTTPMiddleware` 前，应了解其限制并验证相关行为。

## 响应模型与 OpenAPI

- `response_model=` 声明响应结构：做**输出过滤**(只暴露声明字段)和序列化；省略时可从有效的返回类型注解推导，不是按实际返回值动态推断。未设置有效输出约束时需检查敏感字段。
- 常用开关：`response_model_exclude_none`、`response_model_by_alias`(对外 camelCase 契约)。
- `response_model` 也用于生成 OpenAPI schema。修改字段名或删除字段可能破坏现有客户端，应先评估兼容性，再确定迁移或版本策略。
- /docs、/redoc 和 /openapi.json 是不同入口；`docs_url=None` 只关闭 Swagger UI。需同时关闭其他入口时，再配置 `redoc_url=None`、`openapi_url=None`。
- 直接返回 Response 或其子类（如 StreamingResponse）时，框架不会再按 response_model 校验和过滤其内容；输出格式与字段范围由返回响应的代码负责。

## 测试

- 同步接口测试可以使用 `TestClient(app)`，它基于 HTTPX。
- 异步测试可以用 `httpx.AsyncClient` 配合 `ASGITransport` 直接调用应用，无需监听端口。客户端需要设置测试用的 `base_url`；应用的启动和关闭仍需单独管理。
- 覆盖依赖：测试替身通过 `dependency_overrides` 注入，测试结束清理(`app.dependency_overrides.clear()`)。
- 生命周期在 `TestClient` 的上下文管理器里触发，测试启动/关闭逻辑要显式包 `with TestClient(app) as client:`。
- 契约测试：对关键端点断言 OpenAPI schema(`app.openapi()`)，防止无意识的破坏性变更。

## 常见陷阱

- `BackgroundTasks` 在响应后执行进程内任务，不提供持久化保证。重要任务需要可靠存储与调度时，应使用持久化任务队列。
- 同一请求内可复用的同一依赖默认使用缓存。需要重新执行时可按场景设置 use_cache=False；循环中逐条检查资源权限，通常应显式调用相应逻辑，避免误以为依赖会为每条数据自动重跑。
- `app.state` 是应用级共享可变对象，写并发安全的代码。
- CORS、信任代理头(`--proxy-headers`)、请求体大小限制要在入口显式配置，默认值不一定符合生产预期。

## 参考资料

- [FastAPI 响应模型](https://fastapi.tiangolo.com/tutorial/response-model/)
- [FastAPI 错误处理](https://fastapi.tiangolo.com/tutorial/handling-errors/)

- [yield 依赖与 scope](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)
- [HTTPX ASGI 生命周期](https://www.python-httpx.org/advanced/transports/#asgi-startup-and-shutdown)
