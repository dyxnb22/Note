# 09 LangGraph Memory Agent

## 项目目标

理解 Agent 的 Memory，以及 LangGraph State 如何帮助管理记忆。

## 你会学到什么

- `messages` 和 `memory` 的区别
- 短期记忆是什么
- State 如何保存结构化信息
- Checkpointer 如何按 `thread_id` 恢复状态

## 项目结构

```text
main.py   带记忆的 LangGraph Agent
```

## 如何运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 核心代码流程

第一轮用户说“我叫 Tom”，节点把 `name=Tom` 写入 `memory`。第二轮用户问“我叫什么”，同一个 `thread_id` 会恢复上一轮状态。

## 建议你修改的练习

- 让 Agent 记住城市
- 尝试换一个 `thread_id`
- 增加 `/reset` 清空 memory

## 常见问题

- 第二轮忘记名字：确认两次调用使用相同 `thread_id`
- memory 被覆盖：更新 dict 时要保留原有字段
