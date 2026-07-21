# 08 LangGraph Tool Agent

## 项目目标

理解 LangGraph 中如何组织 Tool Calling Agent。

## 你会学到什么

- ToolNode 的作用
- Conditional Edge 的作用
- 工具调用为什么适合用图结构表达
- Planner、Tool、Final Answer 的分工

## 项目结构

```text
main.py   LangGraph Tool Agent
```

## 如何运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 核心代码流程

`planner` 模拟模型生成 tool calls，`ToolNode` 执行工具，`final_answer` 汇总工具观察结果。

## 建议你修改的练习

- 增加一个 `get_current_time` 工具
- 把 planner 换成真实 LLM
- 尝试支持多个城市

## 常见问题

- 工具没有执行：检查 AIMessage 里是否真的有 `tool_calls`
- 路由没走到 ToolNode：检查条件边返回值是否是 `"tools"`
