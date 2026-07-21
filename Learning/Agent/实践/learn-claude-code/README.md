# learn-claude-code 课程实践

这里是 `Learning/Agent` 的代码实验区。理论笔记负责解释概念、边界和生产化注意事项；本目录负责运行、观察和修改最小实现。

这里是 `learn-claude-code` 当前 `s01-s20` 课程的本地学习快照。保留课程代码和运行所需的配套文件，不复制项目说明文档，避免理论内容分叉；如果以后需要更新，可从 [GitHub 上游仓库](https://github.com/shareAI-lab/learn-claude-code) 重新同步。

## 如何运行

```bash
cd "/Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Agent/实践/learn-claude-code"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env` 填入可用的 `ANTHROPIC_API_KEY` 和 `MODEL_ID` 后，在本目录下运行某个实验：

```bash
python s01_agent_loop/code.py
python s02_tool_use/code.py
```

课程代码通常使用当前工作目录作为 Agent 的工作区，运行时应保持在本目录；实验产生的 `.memory/`、`.tasks/`、`.mailboxes/`、`.transcripts/` 等状态文件也会落在这里。不要把真实密钥提交到 Notes。

## 理论—实践对应关系

| 课程 | 实践入口 | 主要对应笔记 |
|---|---|---|
| s01 | [Agent Loop](./s01_agent_loop/code.py) | [Agent 架构与设计](../../Agent架构与设计.md) |
| s02 | [Tool Use](./s02_tool_use/code.py) | [Tool Calling](../../Tool%20Calling.md) |
| s03 | [Permission](./s03_permission/code.py) | [安全与可控性](../../安全与可控性.md) |
| s04 | [Hooks](./s04_hooks/code.py) | [安全与可控性](../../安全与可控性.md) |
| s05 | [Todo Write](./s05_todo_write/code.py) | [Agent 架构与设计](../../Agent架构与设计.md) |
| s06 | [Subagent](./s06_subagent/code.py) | [Agent 架构与设计](../../Agent架构与设计.md) |
| s07 | [Skill Loading](./s07_skill_loading/code.py) | [Context 工程](../../Context工程.md) |
| s08 | [Context Compact](./s08_context_compact/code.py) | [Context 工程](../../Context工程.md) |
| s09 | [Memory](./s09_memory/code.py) | [Memory 与状态管理](../../Memory与状态管理.md) |
| s10 | [System Prompt](./s10_system_prompt/code.py) | [Context 工程](../../Context工程.md) |
| s11 | [Error Recovery](./s11_error_recovery/code.py) | [LLM 调用基础](../../LLM调用基础.md) |
| s12 | [Task System](./s12_task_system/code.py) | [Durable Execution 与分布式可靠性](../../Durable%20Execution与分布式可靠性.md) |
| s13 | [Background Tasks](./s13_background_tasks/code.py) | [Durable Execution 与分布式可靠性](../../Durable%20Execution与分布式可靠性.md) |
| s14 | [Cron Scheduler](./s14_cron_scheduler/code.py) | [Durable Execution 与分布式可靠性](../../Durable%20Execution与分布式可靠性.md) |
| s15 | [Agent Teams](./s15_agent_teams/code.py) | [Workflow 与 LangGraph](../../Workflow与LangGraph.md) |
| s16 | [Team Protocols](./s16_team_protocols/code.py) | [Workflow 与 LangGraph](../../Workflow与LangGraph.md) |
| s17 | [Autonomous Agents](./s17_autonomous_agents/code.py) | [Workflow 与 LangGraph](../../Workflow与LangGraph.md) |
| s18 | [Worktree Isolation](./s18_worktree_isolation/code.py) | [代码 Agent 基础设施](../../代码%20Agent%20基础设施.md) |
| s19 | [MCP Plugin](./s19_mcp_plugin/code.py) | [MCP 与工具协议](../../MCP与工具协议.md) |
| s20 | [Comprehensive Harness](./s20_comprehensive/code.py) | [Agent 架构与设计](../../Agent架构与设计.md) |

## 测试

当前复制了与 `s01-s20` 代码直接相关的测试：

```bash
pytest -q tests
```

测试是学习用的底线检查，不等同于完整 Agent Eval。完成每一章后，建议再按照对应理论笔记中的验收问题，记录一次轨迹、失败模式和改进结果。
