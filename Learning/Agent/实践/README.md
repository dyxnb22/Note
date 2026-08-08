# Agent 实践

这里集中放 `Learning/Agent` 的可运行代码。理论、边界和生产化判断仍维护在上级目录的章节笔记中，实践目录只保留代码、项目 README、配置示例和测试。

完整的 Python → AI → Agent 学习顺序和实践选择见：[学习地图](../../00_Navigation/AI-Python-Agent学习地图.md)。

## 三条实践路线

- [ai-agent-learning](./ai-agent-learning/README.md)：默认只走 `03–05` 的 Provider SDK、Tool Calling 和 Agent Loop；Python/HTTP 不熟时补 `01–02`，想先看固定轨迹时选 `00`，需要服务化或具体分支时再进入 `06–12`。
- [learn-claude-code](./learn-claude-code/README.md)：s01–s20，重点学习 Agent Harness 的工具、权限、Hook、Context、Memory、Task、后台任务、团队、Worktree 和 MCP 机制。
- [rust-agent-runtime](./rust-agent-runtime/README.md)：在已懂 Agent Loop 后，用 Rust 验证 Tool Registry、预算、取消、Trace、Provider Adapter、受限执行与恢复。

## 目录结构

```text
实践/
├── ai-agent-learning/       # 00–12 主学习路线
│   ├── agent-learning-projects/  # 逐步项目
│   ├── langgraph-advanced/      # 框架专项
│   └── DevPilot/                # 综合项目
├── learn-claude-code/       # s01–s20 Harness 实验
└── rust-agent-runtime/      # Rust Runtime/Harness 实现分支
```

新增同语言、同目标实践优先归入已有路线。只有语言运行模型或验证目标明显不同，才在此层建立新目录；Rust 分支保留是因为它验证所有权、Trait、Async、受限进程和单二进制交付，而不是复制 Python 课程。

## 选择建议

第一次系统学习 Agent：先完成 `ai-agent-learning/agent-learning-projects/03–05`。`00` 是可选预热，`01–02` 是 Python/HTTP 补充，`06` 只在需要服务化时进入；随后按真实目标选择 `07–09` 的 LangGraph/Memory、`10` 的 RAG 或 `11` 的 MCP。

已经能调用模型并写过基础 Agent：从 `learn-claude-code` 选择与当前问题对应的实验（例如 s03 权限、s07–s08 Context、s12–s14 长任务、s18 Worktree、s19 MCP），不需要把 s01–s20 再完整重做；也可以直接用 `ai-agent-learning/DevPilot` 做综合项目。

希望用 Rust 做 Agent：先完成基础 Agent Loop，再学习 Rust 01–12 中的目标章节，最后进入 `rust-agent-runtime`；完整顺序见 [Rust Agent 与 Go 后端学习地图](../../00_Navigation/Rust-Agent与Go后端学习地图.md)。

三套实践都属于教学代码。运行前检查依赖和 Provider 文档，涉及文件写入、外部命令、MCP Server 或真实模型时，先阅读对应理论章节的安全和验证要求。

## 代码注释与证据约定

实践代码不要求逐行翻译语法，但以下边界必须有注释或 README 说明：

- 输入来自模型/用户时，说明校验、解析和拒绝策略。
- 调用网络、工具或文件时，说明超时、取消、权限、幂等和资源关闭。
- 使用 Mock、脚本模型或简化算法时，明确它与生产实现的差异。
- 每个可运行入口记录命令、依赖版本、预期输出和未验证边界。

测试通过只证明对应测试覆盖的行为；没有运行记录的代码块统一视为示例，不写成“已验证”。
