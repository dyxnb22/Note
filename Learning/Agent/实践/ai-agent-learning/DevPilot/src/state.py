"""共享 State 定义"""

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class DevPilotState(TypedDict):
    messages: Annotated[list, add_messages]

    task_type: str         # "bug_fix" | "feature" | "code_review"
    repo_path: str
    languages: list[str]   # ["python", "java", "c"] — 自动检测或手动指定
    target_files: list[str]
    analysis_report: str
    diff: str
    approved: bool
    pr_number: str
    next_step: str
