# HTTP与API调用
这一页专门整理 Python 如何调用外部 HTTP API。后面 OpenAI SDK、RAG、Tool Calling，本质上都离不开 HTTP 请求、超时、错误处理和 JSON 解析。

## 1. HTTP 调用的完整链路

```plain text
构造 URL / 参数 / headers / body
→ 发送请求
→ 获得响应 status_code / headers / body
→ 判断是否成功
→ 解析 JSON
→ 处理超时、网络错误、状态码错误
```

必须掌握：

- `GET`：查询数据。
- `POST`：提交数据、创建资源、触发动作。
- `headers`：认证、内容类型、客户端信息。
- `params`：URL 查询参数。
- `json`：请求体 JSON。
- `timeout`：防止一直卡住。
- `raise_for_status()`：把 4xx / 5xx 变成异常。

## 2. requests：同步 HTTP

适合脚本、小工具、同步程序。

```python
import requests

response = requests.get(
    "https://httpbin.org/get",             # 请求地址
    params={"name": "Tom", "age": 18},   # query 参数，会拼到 URL 后面
    headers={"User-Agent": "python-client"}, # 请求头
    timeout=10,                            # 最多等待 10 秒
)

print(response.status_code)                # HTTP 状态码，例如 200
print(response.headers.get("Content-Type")) # 响应头
print(response.text)                       # 原始响应文本

response.raise_for_status()                # 如果是 4xx / 5xx，抛出 HTTPError
data = response.json()                     # 把 JSON 响应转成 dict/list
print(data)
```

GET 参数会变成：

```plain text
https://httpbin.org/get?name=Tom&age=18
```

POST JSON：

```python
payload = {
    "name": "Tom",
    "age": 18,
}

response = requests.post(
    "https://httpbin.org/post",
    json=payload,       # requests 会自动序列化成 JSON，并设置 Content-Type
    timeout=10,
)

response.raise_for_status()
print(response.json())
```

## 3. requests 标准错误处理

真实项目不要只写 happy path，要处理常见失败。

```python
import requests


def fetch_json(url: str) -> dict:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.Timeout:
        # 请求超过 timeout 时间还没完成
        print("请求超时")

    except requests.HTTPError as e:
        # 状态码是 4xx / 5xx
        print(f"HTTP 状态码错误：{e}")

    except requests.RequestException as e:
        # requests 的网络相关异常基类，例如连接失败、DNS 失败
        print(f"网络请求失败：{e}")

    except ValueError:
        # response.json() 解析失败，说明响应不是合法 JSON
        print("响应不是合法 JSON")

    return {}
```

## 4. httpx：同步 + 异步 HTTP

`httpx` 是更现代的 HTTP 客户端，既支持同步也支持异步。FastAPI / Agent 项目里更常用。

<table header-row="true">
<tr>
<td>能力</td>
<td>requests</td>
<td>httpx</td>
</tr>
<tr>
<td>同步请求</td>
<td>支持</td>
<td>支持</td>
</tr>
<tr>
<td>异步请求</td>
<td>不支持</td>
<td>支持</td>
</tr>
<tr>
<td>连接复用</td>
<td>可用但不突出</td>
<td>`Client / AsyncClient` 更清晰</td>
</tr>
</table>

同步写法：

```python
import httpx

with httpx.Client(
    base_url="https://httpbin.org",
    timeout=10.0,
    headers={"User-Agent": "my-agent"},
) as client:
    response = client.get("/get", params={"name": "Tom"})
    response.raise_for_status()
    print(response.json())
```

异步写法：

```python
import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("https://httpbin.org/get")
        response.raise_for_status()
        print(response.json())

asyncio.run(main())
```
