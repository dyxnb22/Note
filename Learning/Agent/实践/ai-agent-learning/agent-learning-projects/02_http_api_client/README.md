# 02 HTTP API Client

## 项目目标

理解 HTTP API 调用，这是 Agent 调用外部工具的基础。

## 你会学到什么

- `requests` 同步请求
- `httpx` 异步请求
- GET、POST、headers、timeout
- `status_code`、`headers`、`json()`
- 基础异常处理

## 项目结构

```text
main.py             HTTP 示例入口
requirements.txt   requests/httpx/python-dotenv
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

程序先用 `requests.get()` 调用 httpbin 的 GET API，再用 `requests.post()` 发送 JSON，最后用 `httpx.AsyncClient` 演示异步请求。

## 建议你修改的练习

- 增加一个 `/headers` 请求
- 把 timeout 改成很小，观察异常
- 同时发起 3 个 async 请求

## 常见问题

- 网络失败：确认能访问 `https://httpbin.org`
- JSON 解析失败：确认 API 返回的是 JSON，不是 HTML 错误页
