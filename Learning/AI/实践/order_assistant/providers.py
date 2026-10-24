"""脚本化模型与非流式 Chat Completions 适配器。"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request


class ProviderError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


class ScriptedProvider:
    """按已收到的工具结果产生动作；不联网，也不模拟模型质量。"""

    def __init__(self, order_id: str):
        self.order_id = order_id
        self.calls = 0

    def decide(self, messages: list[dict], tools: list[dict]) -> dict:
        results = [
            json.loads(message["content"])
            for message in messages if message["role"] == "tool"
        ]
        observations = [item for item in results if item["status"] == "ok"]
        if not observations:
            name, arguments = "lookup_order", {"order_id": self.order_id}
        elif len(observations) == 1:
            name, arguments = "lookup_policy", {
                "status": observations[0]["data"]["status"],
            }
        else:
            order, policy = observations[0]["data"], observations[1]["data"]
            name, arguments = "submit_answer", {
                "order_id": order["order_id"],
                "status": order["status"],
                "can_request_cancellation": policy["can_request_cancellation"],
            }
        self.calls += 1
        return {
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": f"call_{self.calls}", "type": "function",
                "function": {
                    "name": name,
                    "arguments": json.dumps(arguments, ensure_ascii=False),
                },
            }],
        }


class CompatibleProvider:
    """仅支持普通文本消息与单个 function tool 调用。"""

    def __init__(self):
        self.url = os.getenv("LLM_CHAT_URL", "")
        self.key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "")
        if not all((self.url, self.key, self.model)):
            raise ProviderError("需要设置 LLM_CHAT_URL、LLM_API_KEY、LLM_MODEL")
        address = urllib.parse.urlsplit(self.url)
        if address.scheme != "https" or not address.netloc or address.username:
            raise ProviderError("LLM_CHAT_URL 必须是无内嵌凭证的 HTTPS 完整端点")
        self.opener = urllib.request.build_opener(NoRedirect())

    def decide(self, messages: list[dict], tools: list[dict]) -> dict:
        payload = {
            "model": self.model, "messages": messages, "tools": tools,
            "tool_choice": "required", "stream": False,
        }
        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            # 这是网络等待超时，不是整个 Agent 任务的统一期限。
            with self.opener.open(request, timeout=15) as response:
                body = json.load(response)
        except urllib.error.HTTPError as exc:
            raise ProviderError(f"模型服务返回 HTTP {exc.code}") from None
        except (OSError, ValueError):
            raise ProviderError("模型请求失败或响应不是有效 JSON") from None
        if not isinstance(body, dict):
            raise ProviderError("模型响应根节点必须是对象")
        choices = body.get("choices")
        if not isinstance(choices, list) or len(choices) != 1:
            raise ProviderError("本例要求响应包含一个 choice")
        choice = choices[0]
        if not isinstance(choice, dict) or choice.get("finish_reason") != "tool_calls":
            raise ProviderError("未取得完整工具提案；拒绝、截断和纯文本不会直接执行")
        message = choice.get("message")
        if not isinstance(message, dict) or message.get("role") != "assistant":
            raise ProviderError("模型消息结构不符合约定")
        if message.get("refusal"):
            raise ProviderError("模型拒绝了当前请求")
        supported = {"role", "content", "tool_calls", "refusal"}
        if any(value is not None for key, value in message.items() if key not in supported):
            raise ProviderError("响应含本例不支持的内容字段，需要扩展适配器")
        if message.get("content") is not None and not isinstance(message["content"], str):
            raise ProviderError("本例只支持文本 content")
        return {key: message.get(key) for key in ("role", "content", "tool_calls")}
