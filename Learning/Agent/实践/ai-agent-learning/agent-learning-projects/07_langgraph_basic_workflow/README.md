# 07 LangGraph Basic Workflow

## 项目目标

第一次理解 LangGraph 的核心概念：State、Node、Edge、Graph、compile、invoke。

## 你会学到什么

- LangGraph 为什么用图表达 Agent 流程
- State 是什么
- Node 是什么
- Edge 是什么
- 为什么图结构适合 Agent Workflow

## 项目结构

```text
main.py   最小 LangGraph 工作流
```

## 如何运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 核心代码流程

`START -> receive_input -> generate_reply -> END`。第一个节点清洗输入，第二个节点生成回复。

## 建议你修改的练习

- 增加一个 `classify_intent` 节点
- 给 State 增加 `intent` 字段
- 尝试打印每个节点返回的 dict

## 常见问题

- State 字段缺失：`invoke()` 传入的初始 State 要包含需要读取的字段
- 节点名写错：`add_edge()` 里的节点名必须已经注册
