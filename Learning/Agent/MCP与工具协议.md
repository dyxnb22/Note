# MCP 与工具协议

这篇文档解决一个问题：**MCP 是什么，什么时候用它，什么时候直接写 SDK 调用**。

---

## 1. MCP 解决什么问题

### 没有 MCP 时的痛点

每个工具都要单独适配：

```
AI App → 自己写 Notion SDK 调用
AI App → 自己写 GitHub SDK 调用
AI App → 自己写文件系统接口
AI App → 自己写数据库 SDK

每个工具：不同 API 风格、不同鉴权方式、不同错误格式
```

当工具多了，集成成本按线性增长，而且每个应用都要重复做这些工作。

### MCP 的核心价值

```
AI App / MCP Client → MCP Protocol → MCP Server → Tool / Resource / Prompt
```

MCP（Model Context Protocol）是 Anthropic 提出的开放协议，定义了 AI 应用和工具之间的标准通信格式。

**价值不在于"让模型更聪明"，而在于**：
- 工具实现一次，可被任意 MCP Client 使用
- AI 应用不用关心每个工具的具体 SDK
- 生态里工具可以复用（社区 MCP Server 库）

---

## 2. MCP 的三种能力

| 能力 | 含义 | 示例 |
|------|------|------|
| **Tools** | AI 可以调用的函数 | `search_github_issues()`, `create_file()` |
| **Resources** | AI 可以读取的数据 | `file://project/README.md`, `db://users` |
| **Prompts** | 预定义的 prompt 模板 | `code_review_prompt`, `summarize_template` |

Tools 是最常用的，Resources 和 Prompts 是补充能力。

---

## 3. MCP Server 实现

用官方 SDK 实现一个简单的 MCP Server：

```python
## pip install mcp

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
import mcp.server.stdio

app = Server("my-tools-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
"""声明这个 Server 提供哪些工具"""
return [
    Tool(
        name="search_docs",
        description="搜索项目文档。输入关键词，返回相关文档片段。",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词",
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回结果数量，默认 5",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    ),
]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
"""处理工具调用"""
if name == "search_docs":
    query = arguments["query"]
    top_k = arguments.get("top_k", 5)

## 实际的搜索逻辑
    results = await search_vector_store(query, top_k)

    return [
        TextContent(
            type="text",
            text=f"找到 {len(results)} 条相关文档：\n\n" +
                 "\n\n".join([r["content"] for r in results]),
        )
    ]

raise ValueError(f"未知工具: {name}")

## 启动 Server（stdio 模式，供 Claude Desktop 等使用）
async def main():
async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
    await app.run(
        read_stream,
        write_stream,
        InitializationOptions(server_name="my-tools", server_version="0.1.0"),
    )
```

---

## 4. MCP Client 实现

AI 应用作为 MCP Client，连接到 MCP Server：

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def use_mcp_tools():
server_params = StdioServerParameters(
    command="python",
    args=["my_mcp_server.py"],
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
## 初始化
        await session.initialize()

## 列出可用工具
        tools = await session.list_tools()
        print("可用工具:", [t.name for t in tools.tools])

## 调用工具
        result = await session.call_tool(
            "search_docs",
            arguments={"query": "RAG 实现", "top_k": 3},
        )
        print("结果:", result.content[0].text)
```

---

## 5. 与 Claude Desktop 集成

Claude Desktop 是最常用的 MCP Client，配置方式：

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
"my-tools": {
  "command": "python",
  "args": ["/path/to/my_mcp_server.py"],
  "env": {
    "DATABASE_URL": "postgresql://localhost/mydb"
  }
},
"filesystem": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/workspace"]
}
  }
}
```

配置后，Claude Desktop 里的 Claude 就能使用这些工具。

---

## 6. MCP 与直接 SDK 调用的比较

| 维度 | 直接 SDK 调用 | MCP |
|------|-------------|-----|
| 集成成本 | 每次都要写适配代码 | 一次实现，多处使用 |
| 复杂度 | 低（就是函数调用） | 高（需要 Server 进程） |
| 可复用性 | 只在当前应用使用 | 任意 MCP Client 可用 |
| 调试难度 | 直接 | 需要了解协议和进程通信 |
| 适合场景 | 单一应用、快速迭代 | 工具需要被多个 AI 应用共享 |

**结论**：
- 如果只是给自己的应用加工具，直接写函数 + Tool Calling schema 更简单
- 如果工具需要被多个 AI 应用使用（Claude Desktop + 你自己的 app + 团队其他 AI 工具），才值得做成 MCP Server
- 如果使用社区现有的 MCP Server（如文件系统、GitHub、Notion），直接作为 Client 使用即可

---

## 7. 自建工具协议时要考虑什么

如果团队要在 MCP 之外自建工具协议：

| 考量 | 问题 |
|------|------|
| Schema 格式 | 和 OpenAI function calling 格式兼容吗？ |
| 版本管理 | 工具 API 升级时如何兼容旧的调用方 |
| 鉴权 | 工具调用如何携带用户身份 |
| 错误格式 | 失败时返回什么格式，模型能理解吗 |
| 超时与限速 | 工具慢了怎么办，调用频率有限制吗 |
| 审计 | 谁在什么时候调用了什么工具 |

MCP 已经处理了这些问题，自建协议时要确认有没有更好的理由不用它。

---

## 8. 工程深度：Transport、Auth、版本兼容

### Transport 形态

MCP 支持两种传输方式，使用场景不同：

| Transport | 形态 | 适合 |
|-----------|------|------|
| **stdio** | Server 是子进程，通过标准输入输出通信 | 本地工具（文件系统、本地数据库）；Claude Desktop 集成 |
| **SSE / HTTP** | Server 是独立 HTTP 服务，通过 Server-Sent Events 推送 | 远程服务；多 Client 共享；需要认证的场景 |

```python
## SSE 模式启动（替代 stdio）
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette

sse = SseServerTransport("/messages")

async def handle_sse(request):
async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
    await app.run(streams[0], streams[1], app.create_initialization_options())

starlette_app = Starlette(routes=[Route("/sse", endpoint=handle_sse)])
```

### Auth / User Identity 传递

MCP Server 收到工具调用时，通常需要知道"谁在调用"：

```python
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
## 从 arguments 或 request context 里取 user token
user_token = arguments.get("_auth_token")  # 一种约定

if name == "query_user_data":
## 用 token 验证权限再执行
    user = await verify_token(user_token)
    if not user.has_permission("read_data"):
        return [TextContent(type="text", text="权限不足")]
    ...
```

**实践注意**：MCP 协议本身不规定认证方式。常见做法：
- stdio 模式：Server 是本地子进程，信任本地调用者
- SSE/HTTP 模式：Client 在建连时传 Bearer Token，Server 验证；或在 arguments 里约定传 auth context

### Capability Discovery 与版本兼容

`list_tools()` 就是 capability discovery 的机制——Client 启动时拉取工具列表，不需要 hardcode。版本兼容靠工具描述和 schema：

```python
@app.list_tools()
async def list_tools() -> list[Tool]:
return [
    Tool(
        name="search_docs",
        description="v2: 支持 filters 参数（v1 不支持）",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "filters": {"type": "object", "description": "可选，v2 新增"},
            },
            "required": ["query"],
        },
    ),
]
```

向后兼容原则：新增字段设为 optional；不要修改已有字段含义；重大变更用新工具名（`search_docs_v2`）。

### 为什么团队内部工具平台会偏向协议层

当团队有多个 AI 应用（客服 Agent、代码 Agent、分析 Agent）都需要访问同一套工具（内部知识库、CRM、权限系统）时：

```
没有协议层：
  客服 Agent → 自己写 CRM 集成
  代码 Agent → 自己写 CRM 集成（重复）
  分析 Agent → 自己写 CRM 集成（重复）

有协议层（MCP）：
  CRM MCP Server ← 客服 Agent
             ← 代码 Agent
             ← 分析 Agent
```

工具集成逻辑收敛到 Server 端，权限控制、审计、错误处理统一维护，每个 AI 应用只需要做 Client 调用。这是团队规模增长后自然演化的方向。

---

## 9. 高频社区 MCP Server

| Server | 用途 |
|--------|------|
| `@modelcontextprotocol/server-filesystem` | 文件系统读写 |
| `@modelcontextprotocol/server-github` | GitHub 操作 |
| `@modelcontextprotocol/server-postgres` | PostgreSQL 查询 |
| `@modelcontextprotocol/server-brave-search` | 网络搜索 |
| `@modelcontextprotocol/server-puppeteer` | 浏览器自动化 |

---

## 10. MCP 工具的企业级治理

当 Agent 系统集成了多个外部 MCP Server 时，不能无条件信任所有 Server 提供的工具：

**工具命名约定**：

```
mcp__{server_name}__{tool_name}

示例：
  mcp__github__create_pull_request
  mcp__jira__create_issue
  mcp__filesystem__write_file
```

这个命名约定让 Agent 和审计系统能区分"内置工具"和"MCP 工具"，并知道工具来自哪个 Server。

**allowlist 控制哪些 MCP Server 可以连接**：

```python
MCP_ALLOWLIST = {
    "filesystem": {
        "allowed_tools": ["read_file", "list_dir"],  # 只允许读，不允许写
        "trusted": True,
    },
    "github": {
        "allowed_tools": ["get_pr", "list_issues", "create_comment"],
        "write_tools": ["create_pr", "push_branch"],  # 写操作需要 Grant
        "trusted": False,  # 外部服务，内容视为 untrusted
    },
}

def assemble_tool_pool(active_mcp_sessions: dict) -> list[dict]:
    """每次 LLM 调用前重新组装工具池"""
    tools = list(BUILTIN_TOOLS)  # 内置工具
    for server_name, session in active_mcp_sessions.items():
        config = MCP_ALLOWLIST.get(server_name, {})
        mcp_tools = session.list_tools()
        for tool in mcp_tools:
            if tool.name in config.get("allowed_tools", []):
                # 重命名为 mcp__{server}__{tool} 格式
                tools.append(rename_tool(tool, f"mcp__{server_name}__{tool.name}"))
    return tools
```

**写操作的 Grant 门控**：

```python
def execute_mcp_tool(tool_name: str, args: dict, context: ExecutionContext) -> str:
    server, tool = parse_mcp_tool_name(tool_name)  # "github", "create_pr"
    config = MCP_ALLOWLIST[server]

    if tool in config.get("write_tools", []):
        # 写操作：必须有有效的 Grant
        grant = context.find_grant(action=tool_name, proposal=args)
        if not grant or not consume_grant(grant.id, proposal=args):
            return "Error: 写操作需要人工审批 Grant"

    # 执行工具，但把结果视为 untrusted（可能含 prompt injection）
    result = session.call_tool(tool, args)
    return redact_secrets(result)  # 脱敏后返回
```

---

## 11. Streamable HTTP Transport（版本化协议示例）

MCP 的远程传输规范和 SDK 会随版本演进。本节用 Streamable HTTP 展示远程 Server 的设计思路；端点、会话、流式响应和安全要求在实际实现前应以[官方 Transports 规范](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)及对应 SDK 文档为准。下面的 FastAPI 代码是教学示意，不是可直接复制的完整协议实现：

```
旧方式（SSE）：
  Client → POST /messages    ← 发送请求
  Client ← GET /sse          ← 监听服务器推送（两个端点）

新方式（Streamable HTTP）：
  Client ↔ POST /mcp         ← 单一端点，支持流式响应
  支持：普通 HTTP response + 流式 SSE response（同一端点）
```

**Server 实现（FastAPI）**：

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("my-server")
app = FastAPI()

@mcp.tool()
async def search_docs(query: str) -> str:
    results = await vector_store.search(query)
    return json.dumps(results)

# Streamable HTTP 端点
@app.post("/mcp")
async def handle_mcp(request: Request):
    body = await request.json()

    # 判断是否需要流式响应
    if body.get("method") in ["tools/call"] and body.get("stream"):
        async def generate():
            async for chunk in mcp.handle_streaming(body):
                yield f"data: {json.dumps(chunk)}\n\n"
        return StreamingResponse(generate(), media_type="text/event-stream")

    # 普通 HTTP 响应
    result = await mcp.handle(body)
    return result

# Client 连接
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def connect_remote_server():
    async with streamablehttp_client("https://my-server.com/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool("search_docs", {"query": "退款政策"})
```

**与 stdio 的选择**：本地进程用 stdio（简单、低延迟）；远程服务用 Streamable HTTP（支持网络部署、多客户端）。

---

## 12. MCP Authorization（OAuth / 版本化示例）

远程 MCP Server 通常需要把 OAuth、Bearer Token、scope 和资源访问控制组合起来。本节代码只演示认证边界；发现流程、元数据、token audience 和客户端注册等细节应以[官方 Authorization 规范](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)为准：

```python
# MCP Server 端：声明 OAuth 配置
from mcp.server.auth import OAuthProvider

oauth_config = {
    "issuer": "https://auth.mycompany.com",
    "authorization_endpoint": "https://auth.mycompany.com/oauth/authorize",
    "token_endpoint": "https://auth.mycompany.com/oauth/token",
    "scopes_supported": ["mcp:read", "mcp:write", "mcp:admin"],
}

# Server 验证 Bearer Token
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)) -> dict:
    token = credentials.credentials
    # 验证 JWT token
    payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
    return payload

@app.post("/mcp")
async def handle_mcp(request: Request, user: dict = Depends(verify_token)):
    # user 包含 sub（用户 ID）和 scopes
    if "mcp:write" not in user.get("scopes", []):
        raise HTTPException(status_code=403, detail="需要 mcp:write 权限")
    ...

# Client 端：使用 OAuth token
async def connect_with_oauth():
    token = await get_oauth_token(
        client_id="my-agent-app",
        scopes=["mcp:read"],
        auth_url="https://auth.mycompany.com/oauth/authorize",
    )
    async with streamablehttp_client(
        "https://my-server.com/mcp",
        headers={"Authorization": f"Bearer {token}"},
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
```

---

## 13. MCP Sampling — Server 回调 LLM

MCP 有一个不常见但重要的特性：Server 可以请求 Client 调用 LLM（Sampling）。

```
普通 Tool Use：Client（Agent）→ 调用工具 → Server 执行 → 返回结果

MCP Sampling：Server 执行工具时 → 发现需要 LLM 判断 → 请求 Client 调 LLM → 结果返回 Server
```

**用途**：Server 做 LLM 辅助决策（如判断检索到的内容是否相关），但不自己管理 API key——由 Client 代劳，Client 可以控制用哪个模型、费用怎么算。

```python
# Server 端：发起 sampling 请求
from mcp.types import SamplingMessage, CreateMessageRequestParams

@mcp.tool()
async def smart_search(query: str, context) -> str:
    raw_results = await search(query)

    # 请求 Client 用 LLM 过滤结果
    sampling_result = await context.session.create_message(
        CreateMessageRequestParams(
            messages=[
                SamplingMessage(
                    role="user",
                    content=f"以下哪些搜索结果和'{query}'最相关？\n{raw_results}"
                )
            ],
            max_tokens=512,
            model_preferences={"hints": [{"name": "claude-haiku"}]},  # 建议用便宜模型
        )
    )
    return sampling_result.content.text

# Client 端：需要实现 sampling handler
async def handle_sampling(params) -> str:
    # Client 决定用哪个模型、是否允许这个 sampling 请求
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",   # 用便宜模型做辅助判断
        messages=[{"role": m.role, "content": m.content.text} for m in params.messages],
        max_tokens=params.max_tokens,
    )
    return response.content[0].text
```

**工程意义**：Sampling 让 MCP Server 可以构建"会思考"的工具，同时把 LLM 的控制权和成本留在 Client 端。

---

## learn-claude-code 对照：动态 MCP 工具池

s19 用 mock server 演示 MCP 的最小不变量：连接 Server、发现工具、给工具加 `mcp__server__tool` 命名空间，再把它们合并进内置工具池；s20 把这套动态工具池放回完整 Agent Loop。

这个实验特别适合补充本篇的协议细节：工具不是静态常量，连接状态、工具描述、权限标注和 prompt/cache 都会随 Server 变化。教学版只模拟 stdio 和 `tools/list`/`tools/call`，省略了多 Transport、OAuth、Server 反向通知、配置优先级和连接生命周期；这些部分不能从 mock 代码直接推断生产行为。对应实验：[s19_mcp_plugin/code.py](./实践/learn-claude-code/s19_mcp_plugin/code.py)、[s20_comprehensive/code.py](./实践/learn-claude-code/s20_comprehensive/code.py)。

## ai-agent-learning 配套实践

- [11 MCP Server](./实践/ai-agent-learning/agent-learning-projects/11_mcp_server/main.py)：用 FastMCP 实现 Note Manager，观察 Tool、Resource、Prompt 的边界。
- [LangGraph MCP 实验](./实践/ai-agent-learning/langgraph-advanced/06-mcp/mcp_server.py)：对照 MCP Server / Client 和 Mock 模式，理解外部工具如何进入 Agent 工具池。

实践代码适合学习协议和调用路径，不代表生产环境已经具备认证、租户隔离、生命周期管理和供应链治理。

## 附录：面试高频

**Q：MCP 是什么，解决什么问题？**

> MCP（Model Context Protocol）是 Anthropic 提出的开放协议，定义了 AI 应用和外部工具/数据源之间的标准通信格式。解决的问题是：每个工具都要单独适配，集成成本随工具数量线性增长，而且不同应用需要重复做同样的集成工作。有了 MCP，工具实现一次就能被任意 MCP Client 使用，AI 应用不需要关心每个工具的具体 SDK。

**Q：MCP 和直接 Tool Calling 有什么区别，什么时候用 MCP？**

> 直接 Tool Calling 是在你的 Python 程序里定义函数 + schema，模型调用后直接在同一进程里执行。MCP 是把工具封装成独立的 Server 进程，通过标准协议通信。如果工具只是你自己的应用在用，直接写函数 + schema 更简单；如果工具需要被多个 AI 应用共享（比如团队的内部知识库搜索，要给 Claude Desktop 用，也要给自己的 AI 应用用），做成 MCP Server 更合适。另外，现在有很多现成的社区 MCP Server（GitHub、文件系统、数据库等），可以直接作为 Client 使用，不用自己实现。
