# AI MCP Gateway

AI MCP Gateway 把普通 HTTP/RPC 接口转换成标准化 MCP 工具，并解决协议、Session、权限和分布式部署问题。它不是简单反向代理，而是一个带状态和治理能力的工具网关。

## 核心链路

```text
OpenAPI/业务接口
      ↓
协议解析与参数映射
      ↓
网关配置 → 工具元数据 → MCP Client 调用
      ↓
JSON-RPC / SSE / Streamable
      ↓
Session、鉴权、错误映射、审计
```

## 模块职责

- `api`：管理端、SSE、Streamable 的接口契约。
- `domain`：网关、协议、鉴权、LLM、Session 的模型和生命周期。
- `case`：SSE/Streamable 用例、Session 和消息处理。
- `infrastructure`：MyBatis、Redis/Redisson、HTTP 网关和协议数据访问。
- `trigger`：HTTP 控制器和 Redis Session 事件监听。
- `app`：Spring Boot、WebFlux/WebMVC、数据库、Redis、线程池和模型配置。

## Session 设计

本地内存保存活跃连接对象，Redis 保存可同步的会话元数据并发布节点事件。分布式部署要区分：

- 本地连接对象：不能简单跨节点共享。
- 会话元数据：可以持久化、同步和恢复。
- 节点归属：创建节点、访问时间、过期清理和删除事件。

客户端切换节点时，要么路由到创建节点，要么在新节点重建本地 Session。

## 协议与安全

- JSON-RPC 要统一请求、响应、错误和工具调用语义。
- SSE 与 Streamable 共用领域能力，但连接建立、请求头、流式响应和关闭语义分别适配。
- OpenAPI 解析按 path/query/header/body 等参数类型使用策略表，避免巨型条件分支。
- 工具发现、调用和配置分别授权；参数需要 schema 校验，危险工具需要二次确认、审计和取消。

## 审计边界

已核对源码、测试类、配置、Mapper、部署文档和核心调用链：306 个文件、224 个 Java 文件、18 个测试 Java 文件、5 个 Mapper XML；Maven JDK 17 构建成功。当前测试报告显示测试类未被执行（`Tests run: 0`），不能把构建成功当作测试通过。MySQL、Redis、LLM Provider、真实 MCP 客户端和云服务器未在本机联调。

相关：[网关、接口治理与 SDK](../../Backend/Architecture/网关、接口治理与SDK.md)、[MCP 与工具协议](../../Agent/MCP与工具协议.md)。

来源：`xfg-planet/02-AI应用范式/Tool与MCP/AI-MCP-Gateway-知识提炼.md`、`06-源码与案例/源码阅读/AI-MCP-Gateway-逐文件源码审计.md`。
