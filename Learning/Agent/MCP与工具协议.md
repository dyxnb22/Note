# MCP 与工具协议

MCP（Model Context Protocol）解决的是**宿主与外部工具/资源之间的复用和发现**，不是 Agent Loop，也不是业务授权。

> **学习位置**：完成 Tool Calling、Context、安全和基础 Workflow 后阅读。
>
> **职责边界**：本文负责 MCP 的层次、能力、Transport、Client/Server、认证边界、版本和治理；工具合同见 [Tool Calling](./02_Tool%20Calling.md)，渐进式能力目录见 [Skills](./Skills与渐进式披露.md)，外部 Server 的威胁见 [安全与可控性](./08_安全与可控性.md)。

## 1. 三个层次不要混淆

| 名称 | 解决的问题 | 作用范围 |
|---|---|---|
| Function/Tool Calling | 模型如何提出一次结构化动作 | 一次模型调用与应用执行器 |
| MCP | Client 如何发现并调用跨宿主的工具/资源/Prompt | 应用与 MCP Server 之间 |
| Skill | 如何按需加载一组能力说明、流程和脚本 | Context/能力组织层 |

MCP Server 只是提供能力的进程或服务；它返回的工具描述和结果仍是不可信输入，Client 还要做 allowlist、schema、权限、超时、审计和结果脱敏。

## 2. MCP 的三种能力

- **Tools**：可调用动作，可能有副作用；需要 schema、权限和执行状态。
- **Resources**：可读取的数据或资源；需要 URI、访问控制、版本和缓存策略。
- **Prompts**：可复用的提示模板；不能绕过宿主的系统规则和工具权限。

有些版本/实现还包含采样、Roots、通知和进度等能力。先确认 Client/Server 的协议版本和协商结果，不要把某个 SDK 的类型名当成永久标准。

## 3. 基本交互

```text
Client 启动/连接 Server
  → initialize / capability negotiation
  → tools/list、resources/list 或 prompts/list
  → Host 根据任务和策略筛选可见能力
  → 模型提出 tool call
  → Client 校验、授权并发送 tools/call
  → Server 返回结果
  → Client 脱敏、限长、标记来源后回填 Context
```

模型通常看不到“某个 Server 可以做什么”这一事实的全部细节；Host 决定哪些能力进入本轮 schema。Server 也不能因为被发现就获得宿主的全部身份和网络权限。

## 4. Server 与 Client 的最小边界

Server 应声明稳定名称、版本、能力和 schema，并在自己的边界内校验参数、身份、资源和副作用。Client 应负责：

1. 连接、初始化和能力协商；
2. Server/工具来源与版本 allowlist；
3. schema、超时、并发、结果大小和取消；
4. actor/tenant/resource/operation 的业务授权；
5. 审批、幂等、审计和 Trace；
6. 将结果标记为外部数据，不让其成为新的系统指令。

```text
MCP Client ≠ 直接信任 MCP Server
MCP Auth ≠ 业务授权
tools/list ≠ 允许模型使用所有工具
tools/call 成功 ≠ 业务副作用已被证明完成
```

## 5. Transport 与部署

| Transport | 特点 | 适合 |
|---|---|---|
| stdio | 本地进程、边界简单 | Desktop、CLI、受控本地工具 |
| Streamable HTTP | 远程服务、可流式/会话化 | 团队或云端共享 Server |
| 历史 SSE 形态 | 旧实现兼容 | 只在迁移旧系统时核对 |

Transport 只解决消息传输，不自动解决网络出口、租户隔离、凭证传递、限流或副作用。远程 Server 应有独立身份、TLS、超时、重试、审计和网络 allowlist。

## 6. Auth、身份和授权

认证确认“谁连接了 Server”；业务授权还要确认“这个 actor 能否对这个 resource 执行这个 operation”。调用链至少传递或服务端恢复：

```text
actor_id / tenant_id / task_id / agent_id
  → MCP Client
  → Server 身份验证
  → 业务 policy 检查
  → 工具执行和审计
```

不要把长期用户 token 直接放进模型 Context 或工具描述。使用短期、最小 scope 的凭证；Fallback、转发和异步 Worker 都要重新检查数据边界。完整身份与租户治理见 [Agent 身份与数据治理](./Agent身份与数据治理.md)。

## 7. 能力发现与版本兼容

能力目录需要版本化：

- Server/工具稳定 ID 和版本；
- 输入/输出 schema 版本；
- 权限、资源类型和副作用标记；
- 变更后重建模型可见工具目录；
- 旧 Client 的兼容、拒绝和回滚路径。

工具描述变化会改变模型选择，不能只当作普通文案修改；应进入 Tool/Eval 回归。大量工具先做域/Skill 路由，见 [Tool Calling](./02_Tool%20Calling.md)。

## 8. 供应链与结果处理

接入外部 Server 前检查：来源、版本/digest、依赖、权限声明、网络访问、凭证范围和更新通知。工具描述可能包含注入，工具结果也可能包含注入或 Secret：

```text
Server result
  → 大小限制 / schema 验证
  → Secret/PII 脱敏
  → 来源标签（外部数据，不是指令）
  → actor/tenant 过滤
  → Trace 与 Context
```

Server 不能通过工具描述诱导 Host 绕过 policy，也不能把“查到的结果”当作宿主已授权的事实。

## 9. Sampling 与 Server 回调模型

某些协议实现允许 Server 请求 Host 代为调用模型。它会把信任边界扩大到 Server：

- Host 必须显式允许，不能默认接受；
- Prompt、资源和模型参数经过策略/预算检查；
- 结果按同样规则脱敏、审计和评测；
- Server 不应借 sampling 获得用户秘密或无限模型预算。

如果只是应用内部工具调用，直接 Function Calling 通常更简单；需要跨应用共享、独立部署或由多个宿主发现时，再考虑 MCP。

## 10. 与其他方案怎么选

| 需求 | 优先方案 |
|---|---|
| 单个应用自己的函数 | 直接 Tool Calling |
| 固定业务流程 | Workflow + 内部工具 |
| 多个 Host 复用一个工具服务 | MCP |
| 工具很多、正文和流程按需加载 | MCP + Skills |
| 跨产品委托另一个 Agent | A2A/跨 Agent 协议 |

MCP 不会自动提供多 Agent 协作、可靠恢复、评测或安全合规；这些能力回到对应主文档。

## 11. 确实需要跨客户端工具时检查

如果工具只服务一个应用，停留在普通 Tool Calling 即可。确实需要多个 Host 复用工具服务时，再用当前 MCP 项目检查：

1. Client 能协商能力、列出工具并调用；
2. 每次调用都校验 actor/tenant/resource；
3. Server 结果不会被当作系统指令；
4. 超时、取消、未知工具和过大结果有明确错误；
5. Server 升级后工具 schema 变化能触发回归和回滚；
6. 能解释何时直接函数比 MCP 更简单。

实践：[MCP Server](./实践/ai-agent-learning/agent-learning-projects/11_mcp_server/README.md)、[learn-claude-code s19](./实践/learn-claude-code/s19_mcp_plugin/code.py)。

## 官方来源

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [MCP Authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
- [MCP Transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)
