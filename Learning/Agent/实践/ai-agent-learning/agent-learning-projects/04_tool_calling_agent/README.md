# 04 Tool Calling Agent

## 项目目标

理解 Tool Calling：模型决定调用工具，程序执行工具，再把结果交回模型。

## 你会学到什么

- tool 函数
- tool schema
- `tool_calls`
- 工具结果如何返回给模型
- 最终自然语言回复如何生成

## 项目结构

```text
main.py           Tool Calling 完整流程
.env.example     OpenAI API Key 示例
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

第一次请求把工具 schema 发给模型。模型如果需要工具，会返回 `tool_calls`。Python 根据 `tool_calls` 执行 `get_weather()`，再把工具结果作为 `tool` 消息发回模型生成最终回答。

## 建议你修改的练习

- 增加一个 `get_current_time` 工具
- 增加一个未知城市的处理
- 让用户从命令行输入城市

## 常见问题

- 模型没调用工具：检查 tool description 是否清楚
- JSON 解析失败：检查模型返回的 arguments 是否是合法 JSON
