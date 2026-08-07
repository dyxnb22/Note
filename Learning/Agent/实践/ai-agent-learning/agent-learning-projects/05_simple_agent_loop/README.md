# 05 Simple Agent Loop

> **在它之前**：完成 [04 Tool Calling Agent](../04_tool_calling_agent/README.md)。本项目把一次工具调用改造成有限循环；先不引入 LangGraph，直接观察状态如何变化。

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

可以把每轮写成状态转移：

```text
messages + tools
  → ModelResult(tool_calls 或 final text)
  → tool_calls: 执行并追加 Observation，回到下一轮
  → final text: 检查停止条件并结束
  → 超过 3 轮: budget_exhausted
```

这里的“推理”只表示模型根据当前输入选择下一步；不要把它理解成程序能够读取模型的原始思维链。实际系统还要加参数校验、权限、超时、幂等和成功证据。

## 建议你修改的练习

- 把最大循环次数从 3 改成 5
- 增加一个 `search_note` 工具
- 打印每轮 tool call，观察 Agent 工具轨迹（不是模型的内部思维链）

## 常见问题

- 无限调用工具：必须设置最大循环次数
- 工具参数错误：加强工具 schema 和 description

示例中的计算工具只用于演示，不能用 `eval()` 执行不可信输入；如果扩展它，应使用白名单解析器或受限沙箱。
