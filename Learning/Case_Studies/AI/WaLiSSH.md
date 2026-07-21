# WaLiSSH：SSH 工具化的运行时 Agent

WaLiSSH 把 SSH 连接、命令执行和 SFTP 文件传输封装为服务端工具，再由 Agent 根据意图选择工具。可迁移的重点是“先建立可靠工具，再增加模型自主决策”。

## 分层

```text
Tauri/React/TypeScript 客户端
          ↓
API/Trigger → App 用例 → Case: 意图识别 / ReAct
          ↓
Domain: Agent / SSH 抽象
          ↓
Infrastructure: JSch / SFTP / LLM / 持久化
```

客户端负责交互和展示；服务端持有凭证、执行能力和审计权，避免把服务器信息或危险动作直接暴露给客户端。

## 演进顺序

1. 验证 SSH Session 和认证。
2. 抽象命令执行，定义超时、输出截断和错误模型。
3. 引入 ReAct/Agent Loop，让模型选择受约束的工具。
4. 增加 SFTP、长任务、记忆和异步反馈。

顺序本身是工程经验：模型不应先于工具可靠性和执行边界。

## 安全边界

- 密码、私钥和主机密钥加密存储，不能作为普通明文列。
- 工具参数由服务端 schema 校验；危险命令需要权限、预览/确认、超时、取消和审计。
- Agent 输出不是执行权限；实际执行必须经过服务端策略和资源授权。
- 长任务要有 Session、进度、结果持久化、重试和人工终止。

## 证据边界

已核对服务端 Maven 多模块、README、提交演进、Agent/SSH 领域包、配置和测试入口；SSH、模型 API、MCP 等外部依赖未在本机联调。课程视频和课程帖中不可读的图片内容不纳入结论。

相关：[Agent 架构与设计](../../Agent/Agent架构与设计.md)、[安全与可控性](../../Agent/安全与可控性.md)。

来源：`xfg-planet/02-AI应用范式/Agent与工作流/WaLiSSH-智能体知识提炼.md`、`06-源码与案例/源码阅读/WaLiSSH-服务端源码阅读.md`。
