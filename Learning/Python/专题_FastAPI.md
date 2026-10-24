# 专题：FastAPI

> FastAPI 用 Starlette 处理路由和中间件，用 Pydantic 校验、序列化数据。下面看路由、依赖、生命周期和响应模型；依赖 scope 的行为以 FastAPI 0.121.0+ 为背景。

## 应用与路由

FastAPI() 创建应用；`@app.get("/items")` 将下方函数注册为 GET 路由。POST、PUT、PATCH、DELETE 分别使用 app.post、app.put、app.patch、app.delete。

- 路径参数写进路径并带类型：`/users/{uid}`，类型转换和校验自动做；想限制取值范围用 `Path(ge=1)` 或 `Literal`。
- 参数来源由路径模板、类型注解和 Query / Body / Header 等声明决定。路径中的同名参数取自路径，普通标量通常取自查询字符串，Pydantic 模型通常取自请求体。显式指定来源或外部名称时，使用对应声明和 alias。
- `HTTPException(status_code, detail)` 抛出即返回对应状态码；自定义状态码用装饰器参数或 `Response`。
- 路由按注册顺序尝试匹配。如果固定路径可能与动态路径重叠，应先注册固定路径，避免请求进入不符合预期的处理函数。

```python
from typing import Annotated
from fastapi import FastAPI, Path, Query

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(
    item_id: Annotated[int, Path(ge=1)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return {"item_id": item_id, "limit": limit}
```

item_id 从路径取值，limit 从查询字符串取值。框架先把文本转成整数，再检查范围；item_id=0 不满足约束，会返回请求校验错误。

## 依赖注入

- `Depends(callable)` 让框架调用依赖函数，并把结果传给路由。依赖函数也可以通过 Depends 取得其他依赖函数的结果，由此形成**依赖树**。
yield 依赖在 yield 前准备资源，退出时执行清理。从 FastAPI 0.121.0 起，可以通过 Depends 的 scope 选择清理时机：

| scope | 清理时机 |
|---|---|
| request | 通常在响应发送后清理 |
| function | 可以在路由函数返回后、响应发送前清理 |

具体选择要结合所用版本，尤其要检查流式响应是否还需要这些资源。

```python
from typing import Annotated
from fastapi import Depends, FastAPI

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
```

- 同一个请求内，同一个依赖默认**只解析一次**并缓存；要每次解析传 `Depends(fn, use_cache=False)`。
- 测试时，通过 `app.dependency_overrides` 将依赖函数替换为测试实现。这样可以控制输入和失败场景，不必修改依赖内部的数据库调用。
- 依赖可以解析身份、检查入口权限。订单归属和状态约束放在取得业务数据的位置检查，HTTP 以外的调用路径也须经过这些检查。

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
```

- **应用级资源**（HTTP 客户端、连接池）启动时创建，存入 `app.state`，关闭时释放。请求级 DB 会话放在 `yield` 依赖中。临时创建的客户端用 with/async with 管理，退出代码块时清理。

## 同步端点与异步端点

- `async def` 端点在事件循环上运行；耗时阻塞 I/O 会妨碍该循环中的其他任务调度，应使用异步接口或将阻塞操作交给有并发上限的线程池。
- 同步路由通常由线程池执行。它不会直接占用事件循环执行阻塞操作，但仍受线程池容量限制；任务较多时可能等待可用线程。
- 调用异步库（httpx.AsyncClient、async SQLAlchemy）的端点使用 `async def`；只用同步库时，可以写 `def`。普通同步代码直接调用异步函数，只会得到协程对象。跨线程或事件循环调用时，要明确怎样调度和等待。异步路由中的同步阻塞操作，也可以交给线程。
- 线程池排队时，一起看等待时间、活跃任务和下游延迟。瓶颈在下游时，扩大线程池可能只会增加下游压力。

## 错误处理

不同错误由不同位置处理：

| 情况 | 常见处理 |
|---|---|
| 未捕获的 ValueError 等内部异常 | 返回 500 |
| 抛出 HTTPException | 返回指定的状态码 |
| 请求输入校验失败 | 通常返回 422 |
| 内部处理或响应校验失败 | 按服务端错误排查，不能归为请求输入校验失败 |
- 用 `@app.exception_handler(MyError)` 注册处理器，将业务异常映射成**统一错误体**(稳定 `code` + 供人阅读的 `message` + 可选 `request_id`)，不要向客户端暴露堆栈、SQL 和内部字段。
- 默认的请求校验错误响应通常在 `detail` 中包含结构化错误列表。具体字段受框架版本和自定义错误处理器影响。
- 自定义错误体返回前，过滤原始输入中可能携带的敏感信息。
- `debug=True` 会在响应里返回堆栈，只能用于本地。

## 中间件

- 用 `@app.middleware("http")` 或继承 `BaseHTTPMiddleware`，可以为请求统一注入 `request_id`、记录日志、计时或做简单限流。
- 中间件在调用下游前处理请求，在下游返回后处理响应，适合通用计时和日志。需要路由参数或依赖组合时，通常用依赖更方便。认证放进中间件后，仍需单独配置路由依赖声明和 OpenAPI 安全说明。
- 中间件中的耗时操作会增加所有经过它的请求的延迟。只服务于某个路由的处理，应放到该路由或相应依赖中。
- 流式响应、上下文传播或性能有精确要求时，可以编写纯 ASGI 中间件；使用 `BaseHTTPMiddleware` 时，针对这些需求核对限制并验证行为。

## 响应模型与 OpenAPI

- `response_model=` 定义响应结构，框架据此过滤未声明字段并序列化。没有显式设置时，可以使用框架支持的返回类型注解；框架不会根据每次返回的值临时猜结构。没有有效输出约束时，要自行检查敏感字段。
- `response_model_exclude_none` 控制是否排除值为 None 的字段，`response_model_by_alias` 控制是否使用字段别名输出，例如 camelCase 名称。
- `response_model` 也用于生成 OpenAPI schema。修改字段名或删除字段可能破坏现有客户端，应先评估兼容性，再确定迁移或版本策略。
- /docs、/redoc 和 /openapi.json 是不同入口；`docs_url=None` 只关闭 Swagger UI。需同时关闭其他入口时，再配置 `redoc_url=None`、`openapi_url=None`。
- 直接返回 Response 或其子类（如 StreamingResponse）时，框架不会再按 response_model 校验和过滤其内容；输出格式与字段范围由返回响应的代码负责。

## 测试

- 同步接口测试可以使用 `TestClient(app)`，它基于 HTTPX。
- 异步测试可以用 `httpx.AsyncClient` 配合 `ASGITransport` 直接调用应用，无需监听端口。客户端需要设置测试用的 `base_url`；应用的启动和关闭仍需单独管理。
- 覆盖依赖：测试替身通过 `dependency_overrides` 注入，测试结束清理(`app.dependency_overrides.clear()`)。
- 生命周期在 `TestClient` 的上下文管理器里触发，测试启动/关闭逻辑要显式包 `with TestClient(app) as client:`。
- 契约测试：在测试中检查关键端点生成的 OpenAPI 定义（`app.openapi()`），避免无意改坏已有接口。

## 常见陷阱

- `BackgroundTasks` 在响应后执行进程内任务，不提供持久化保证。重要任务需要可靠存储与调度时，应使用持久化任务队列。
- 同一请求内可复用的同一依赖默认使用缓存。需要重新执行时可按场景设置 use_cache=False；循环中逐条检查资源权限，通常应显式调用相应逻辑，避免误以为依赖会为每条数据自动重跑。
- `app.state` 是应用内共享的可变对象。多个请求可能同时读写其中的数据，更新时要处理并发竞争。
- CORS、信任代理头(`--proxy-headers`)、请求体大小限制要在入口显式配置，默认值不一定符合生产预期。

## 串起路由、依赖与事务

取消请求依次经过“认证依赖取得当前用户 → Pydantic 校验版本 → 业务层检查范围和状态 → 存储事务提交 → 响应模型组织输出”。更换认证来源时，仍要保留业务层的资源和状态检查。

测试这条路径时，只替换需要隔离的依赖，保留输入模型和资源授权检查，确认不同身份与订单状态对应的响应。

## 参考资料

- [FastAPI 响应模型](https://fastapi.tiangolo.com/tutorial/response-model/)
- [FastAPI 错误处理](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [yield 依赖与 scope](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)
- [HTTPX ASGI 生命周期](https://www.python-httpx.org/advanced/transports/#asgi-startup-and-shutdown)
