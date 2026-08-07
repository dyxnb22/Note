# 03 OpenAI CLI Chat

> **在它之前**：可先运行 [00 最小 Agent Loop 练习](../00_agent_mental_model/README.md) 预热；理论上先读 [LLM 调用基础](../../../../01_LLM调用基础.md)。本项目使用一种具体的 messages 风格 API 学习调用流程；不要把这里的字段当成所有 Provider 的通用格式。

## 项目目标

第一次真正调用 OpenAI SDK，理解 LLM 对话的基本结构。

## 你会学到什么

- 如何从 `.env` 读取 `OPENAI_API_KEY`
- `messages` 的作用
- `system`、`user`、`assistant` 的区别
- 如何保存多轮上下文

## 项目结构

```text
main.py           命令行聊天程序
.env.example     API Key 示例
requirements.txt OpenAI SDK
```

## 如何运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填写 OPENAI_API_KEY
python main.py
```

## 核心代码流程

用户输入后，程序把内容追加到 `messages`，调用 OpenAI Chat Completions API，再把模型回答也追加回 `messages`。

这一步还不是 Agent Loop：每次用户输入只调用一次模型，也没有工具执行。你现在只观察三件事：

```text
system  = 持久规则
user    = 当前任务
assistant = 模型返回的文本（下一轮作为历史）
```

Provider 返回对象中的 token 用量、请求编号和错误属于调用元数据，不需要追加进 `messages`。跨 Provider 的统一语义见 [LLM 调用基础](../../../../01_LLM调用基础.md)。

这里的 `messages` 是 Chat Completions 的练习格式，不是所有 Provider 的通用内部类型；跨 Provider 的消息语义和适配边界见 [LLM 调用基础](../../../../01_LLM调用基础.md)。

## 建议你修改的练习

- 修改 system prompt
- 限制最多保存最近 6 条消息
- 输入 `/reset` 清空上下文

## 常见问题

- 401：API Key 错误或没填
- 上下文越来越长：真实项目需要裁剪或总结历史
