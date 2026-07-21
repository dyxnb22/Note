#!/usr/bin/env python3
"""A tiny production-style LLM gateway using only Python stdlib."""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


CACHE: dict[str, dict[str, str]] = {}
RATE_LIMIT: dict[str, list[float]] = {}


def allow_request(client: str, limit: int = 20, window_seconds: int = 60) -> bool:
    now = time.time()
    history = [item for item in RATE_LIMIT.get(client, []) if now - item < window_seconds]
    if len(history) >= limit:
        RATE_LIMIT[client] = history
        return False
    history.append(now)
    RATE_LIMIT[client] = history
    return True


def cache_key(message: str) -> str:
    return hashlib.sha256(message.encode("utf-8")).hexdigest()


def call_model(message: str) -> str:
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        return f"[mock] 你问的是：{message}。生产网关应包含重试、缓存、限流、日志和安全检查。"

    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    payload = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a concise LLM engineering assistant."},
                {"role": "user", "content": message},
            ],
            "temperature": 0.2,
        }
    ).encode()
    request = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())["choices"][0]["message"]["content"]


class Handler(BaseHTTPRequestHandler):
    def _json(self, status: int, data: dict[str, object]) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802 - http.server uses this method name.
        if self.path != "/chat":
            self._json(404, {"error": "not_found"})
            return

        client = self.client_address[0]
        if not allow_request(client):
            self._json(429, {"error": "rate_limited"})
            return

        try:
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size).decode("utf-8"))
            message = str(payload.get("message", "")).strip()
            if not message:
                self._json(400, {"error": "message_required"})
                return

            key = cache_key(message)
            if key in CACHE:
                self._json(200, {"answer": CACHE[key]["answer"], "cached": True})
                return

            answer = call_model(message)
            CACHE[key] = {"answer": answer}
            print(json.dumps({"event": "chat", "client": client, "chars": len(message)}, ensure_ascii=False))
            self._json(200, {"answer": answer, "cached": False})
        except (json.JSONDecodeError, urllib.error.URLError, TimeoutError) as exc:
            self._json(500, {"error": "llm_gateway_error", "detail": str(exc)})


def main() -> None:
    port = int(os.getenv("PORT", "8088"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"LLM gateway listening on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()

