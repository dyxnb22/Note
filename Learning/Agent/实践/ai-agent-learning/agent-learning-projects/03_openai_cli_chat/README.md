# 03 OpenAI CLI Chat

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

## 建议你修改的练习

- 修改 system prompt
- 限制最多保存最近 6 条消息
- 输入 `/reset` 清空上下文

## 常见问题

- 401：API Key 错误或没填
- 上下文越来越长：真实项目需要裁剪或总结历史
