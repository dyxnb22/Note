import asyncio
import os
from pathlib import Path
from typing import Any

import httpx
import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
BASE_URL = os.getenv("HTTPBIN_BASE_URL", "https://httpbin.org")


def sync_get_example() -> dict[str, Any]:
    """同步 GET 请求。

    HTTP API 是 Agent Tool 的基础：很多工具本质上就是调用一个外部 HTTP 服务，
    然后把 JSON 结果交给模型总结。
    """
    try:
        response = requests.get(
            f"{BASE_URL}/get",
            params={"topic": "agent"},
            headers={"X-Learning-Project": "02_http_api_client"},
            timeout=10,
        )
        print("GET status_code:", response.status_code)
        print("GET response header content-type:", response.headers.get("content-type"))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"error": str(exc)}


def sync_post_example() -> dict[str, Any]:
    """同步 POST 请求，演示 JSON body。"""
    try:
        response = requests.post(
            f"{BASE_URL}/post",
            json={"message": "hello api"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"error": str(exc)}


async def async_get_example() -> dict[str, Any]:
    """异步 GET 请求。

    httpx 支持 async/await。Agent 同时查多个工具时，异步可以减少等待时间。
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{BASE_URL}/get", params={"async": "true"})
            print("ASYNC GET status_code:", response.status_code)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        return {"error": str(exc)}


async def main() -> None:
    get_data = sync_get_example()
    post_data = sync_post_example()
    async_data = await async_get_example()

    # API 返回 JSON 很常见，因为 JSON 结构清晰，Python 可以直接转成 dict/list。
    print("sync get keys:", list(get_data.keys()))
    print("sync post json:", post_data.get("json"))
    print("async url:", async_data.get("url"))


if __name__ == "__main__":
    asyncio.run(main())
