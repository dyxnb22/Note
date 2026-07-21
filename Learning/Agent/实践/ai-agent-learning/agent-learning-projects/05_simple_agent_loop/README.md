# 05 Simple Agent Loop

## 项目目标

不依赖框架，手写一个最小 Agent Loop。

## 你会学到什么

- Agent 和普通 ChatBot 的区别
- Tool、Observation、Final Answer 的关系
- 为什么 Agent 需要循环
- 为什么要限制最大循环次数

## 项目结构

```text
main.py   手写 Agent Loop
```

## 如何运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## 核心代码流程

用户输入后，模型决定是否调用工具。程序执行工具并把 Observation 放回 `messages`。模型看到 Observation 后继续推理，直到输出 Final Answer。

## 建议你修改的练习

- 把最大循环次数从 3 改成 5
- 增加一个 `search_note` 工具
- 打印每轮 tool call，观察 Agent 思考路径

## 常见问题

- 无限调用工具：必须设置最大循环次数
- 工具参数错误：加强工具 schema 和 description
