# 06 FastAPI Agent Service

## 项目目标

理解如何把 Agent 包装成后端 API 服务。

## 你会学到什么

- FastAPI 基础
- Pydantic Request/Response Model
- Agent Service 分层
- 异常处理和日志

## 项目结构

```text
app/agent_service.py   Agent 业务函数
app/config.py          配置
main.py                FastAPI 入口
```

## 如何运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

测试：

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"香港天气怎么样？"}'
```

## 核心代码流程

客户端请求 `/chat`，FastAPI 用 Pydantic 校验 JSON，调用 `run_agent()`，最后返回结构化 JSON。

## 建议你修改的练习

- 增加 `conversation_id`
- 增加 `/health`
- 把 `run_agent()` 替换成第 05 项目的 Agent Loop

## 常见问题

- 422：请求 JSON 不符合模型
- 端口占用：换成 `uvicorn main:app --port 8001`
