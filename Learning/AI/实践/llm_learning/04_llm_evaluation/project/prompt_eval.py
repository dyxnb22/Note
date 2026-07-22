#!/usr/bin/env python3
"""Minimal prompt regression evaluation for LLM applications."""

from __future__ import annotations

import json
import os
import urllib.request


CASES = [
    {
        "question": "RAG 适合解决什么问题？",
        "must_include": ["检索", "外部知识"],
    },
    {
        "question": "Agent 调用工具时为什么需要权限控制？",
        "must_include": ["风险", "执行"],
    },
    {
        "question": "LoRA 为什么比全量微调省资源？",
        "must_include": ["低秩", "参数"],
    },
]


PROMPTS = {
    "short": "请用一句话回答问题。",
    "interview": "请用面试表达回答，先给结论，再解释原因，保持简洁准确。",
}


def call_llm(system_prompt: str, question: str) -> str:
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        # Mock output keeps this evaluation runnable without network/API spend.
        return f"{question} 的核心是检索外部知识、控制执行风险，并通过低秩参数适配减少训练成本。"

    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com").rstrip("/")
    model = os.environ["LLM_MODEL"]
    payload = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            "temperature": 0,
        }
    ).encode()
    request = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode())["choices"][0]["message"]["content"]


def score(answer: str, must_include: list[str]) -> float:
    hits = sum(1 for word in must_include if word in answer)
    return hits / len(must_include)


def main() -> None:
    for name, prompt in PROMPTS.items():
        total = 0.0
        print(f"\nPrompt: {name}")
        for case in CASES:
            answer = call_llm(prompt, case["question"])
            case_score = score(answer, case["must_include"])
            total += case_score
            print(f"- score={case_score:.2f} question={case['question']}")
            print(f"  answer={answer}")
        print(f"Average: {total / len(CASES):.2f}")


if __name__ == "__main__":
    main()
