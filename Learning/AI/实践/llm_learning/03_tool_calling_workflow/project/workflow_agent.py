#!/usr/bin/env python3
"""A small state-machine workflow for safer agent actions."""

from __future__ import annotations

import datetime as dt
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class WorkflowState:
    goal: str
    plan: list[str] = field(default_factory=list)
    approved: bool = False
    results: list[str] = field(default_factory=list)


def plan(goal: str) -> list[str]:
    """In a real system this node could call an LLM planner."""
    return [
        f"理解目标：{goal}",
        "列出 3 个可执行学习任务",
        "保存到本地 workflow_report.md",
    ]


def risk_check(steps: list[str]) -> bool:
    """Block dangerous actions before any tool execution."""
    blocked_words = {"删除", "清空", "支付", "发送邮件", "上传密钥"}
    text = "\n".join(steps)
    return not any(word in text for word in blocked_words)


def execute(state: WorkflowState) -> WorkflowState:
    report = Path(__file__).with_name("workflow_report.md")
    content = [
        "# Workflow Report",
        "",
        f"Time: {dt.datetime.now().isoformat(timespec='seconds')}",
        f"Goal: {state.goal}",
        "",
        "## Plan",
        *[f"- {step}" for step in state.plan],
        "",
        "## Suggested Tasks",
        "- 复习 Agent 工具调用循环并画出流程图。",
        "- 跑通 mini RAG 示例并替换成自己的笔记。",
        "- 为一个 prompt 准备 5 条评测样例。",
    ]
    report.write_text("\n".join(content) + "\n", encoding="utf-8")
    state.results.append(f"Saved report: {report}")
    return state


def run(goal: str) -> WorkflowState:
    state = WorkflowState(goal=goal)
    state.plan = plan(goal)
    state.approved = risk_check(state.plan)
    if not state.approved:
        state.results.append("Plan blocked by risk check.")
        return state
    return execute(state)


if __name__ == "__main__":
    final_state = run(" ".join(sys.argv[1:]) or "整理今天的大模型学习任务")
    print("Plan:")
    print("\n".join(f"- {step}" for step in final_state.plan))
    print("\nResults:")
    print("\n".join(f"- {item}" for item in final_state.results))

