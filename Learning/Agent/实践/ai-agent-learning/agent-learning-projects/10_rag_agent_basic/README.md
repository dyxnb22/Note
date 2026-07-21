# 10 RAG Agent Basic

## 项目目标

理解 RAG 的基本流程：读取文档、切分 chunk、检索相关内容、注入上下文、生成回答。

## 你会学到什么

- 什么是 RAG
- 为什么不能把所有文档直接塞给 LLM
- chunk 是什么
- retrieval 是什么
- context injection 是什么

## 项目结构

```text
docs/agent_notes.md   本地知识库
main.py               RAG 示例
```

## 如何运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

默认不调用 OpenAI。如果要启用真实模型：

```env
USE_OPENAI=true
OPENAI_API_KEY=your_api_key_here
```

## 核心代码流程

程序读取 `docs/*.md`，切分成 chunk，根据问题做关键词检索，把相关 chunk 作为上下文。如果启用 OpenAI，就把上下文注入 prompt 生成回答。

## 建议你修改的练习

- 增加一篇新的 Markdown 文档
- 调整 `chunk_size`
- 把关键词检索改成 embedding 检索

## 常见问题

- 回答不准：关键词检索很简单，后续可升级向量检索
- 上下文太长：减少 `top_k` 或缩小 chunk
