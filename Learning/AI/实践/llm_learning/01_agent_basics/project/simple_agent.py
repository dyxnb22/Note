#!/usr/bin/env python3
"""A tiny ReAct-style agent that runs on macOS with only Python stdlib."""

from __future__ import annotations

import ast
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


NOTE_FILE = Path(__file__).with_name("agent_notes.txt")


@dataclass
class Tool:
    name: str
    description: str
    run: Callable[[str], str]


def safe_calculate(expression: str) -> str:
    """Evaluate simple arithmetic without exposing Python builtins."""
    expression = expression.strip()
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.USub,
        ast.Constant,
    )
    tree = ast.parse(expression, mode="eval")
    if not all(isinstance(node, allowed_nodes) for node in ast.walk(tree)):
        raise ValueError("Only simple arithmetic is allowed.")
    return str(eval(compile(tree, "<calculator>", "eval"), {"__builtins__": {}}, {}))


def current_time(_: str) -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def save_note(text: str) -> str:
    """Append notes locally so the example has a real side effect."""
    NOTE_FILE.write_text((NOTE_FILE.read_text() if NOTE_FILE.exists() else "") + text + "\n")
    return f"Saved note to {NOTE_FILE}"


TOOLS = {
    "calculator": Tool("calculator", "Calculate arithmetic expressions.", safe_calculate),
    "time": Tool("time", "Get current local time.", current_time),
    "note": Tool("note", "Save a short note to a local text file.", save_note),
}


def call_llm(messages: list[dict[str, str]]) -> str:
    """Call an OpenAI-compatible chat API, or use a deterministic mock."""
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        return mock_model(messages[-1]["content"])

    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    payload = json.dumps({"model": model, "messages": messages, "temperature": 0}).encode()
    request = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode())
        return data["choices"][0]["message"]["content"]


def mock_model(user_input: str) -> str:
    """A tiny rule-based stand-in so the agent is runnable without paid APIs."""
    if user_input.startswith("Observation:"):
        observation = user_input.removeprefix("Observation:").split("Give final answer.", 1)[0].strip()
        return json.dumps({"final": f"工具执行结果：{observation}"}, ensure_ascii=False)
    if any(ch.isdigit() for ch in user_input) and any(op in user_input for op in "+-*/"):
        expression = "".join(ch for ch in user_input if ch in "0123456789+-*/(). %")
        return json.dumps({"tool": "calculator", "input": expression}, ensure_ascii=False)
    if "时间" in user_input or "time" in user_input.lower():
        return json.dumps({"tool": "time", "input": ""}, ensure_ascii=False)
    if "记录" in user_input or "note" in user_input.lower():
        return json.dumps({"tool": "note", "input": user_input}, ensure_ascii=False)
    return json.dumps({"final": "我会先判断任务是否需要工具；这个问题可以直接回答。"}, ensure_ascii=False)


def agent(user_input: str) -> str:
    tool_text = "\n".join(f"- {tool.name}: {tool.description}" for tool in TOOLS.values())
    system = (
        "You are a small tool-using agent. "
        "Reply with JSON only: either {\"tool\":\"name\",\"input\":\"...\"} "
        "or {\"final\":\"answer\"}.\nAvailable tools:\n"
        + tool_text
    )
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user_input}]

    for _ in range(3):
        raw = call_llm(messages)
        try:
            action = json.loads(raw)
        except json.JSONDecodeError:
            return f"Model returned non-JSON output: {raw}"

        if "final" in action:
            return action["final"]

        tool = TOOLS.get(action.get("tool", ""))
        if not tool:
            return f"Unknown tool: {action}"

        try:
            observation = tool.run(action.get("input", ""))
        except Exception as exc:  # Keep tool failures visible to the model/user.
            observation = f"Tool error: {exc}"
        messages.append({"role": "assistant", "content": raw})
        messages.append({"role": "user", "content": f"Observation: {observation}. Give final answer."})

    return "Reached max agent steps."


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "帮我计算 12 * 8 + 6"
    print(agent(query))
