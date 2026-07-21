"""DevPilot 入口。

这是最终项目的 MVP CLI。它演示的是 Agent 工程闭环：
1. 自动检测语言；
2. Router 判断任务类型；
3. Analyzer 搜索代码；
4. Fixer 生成建议级 diff；
5. Human 审批；
6. Reviewer 审查；
7. PR Creator 输出 PR 草稿。
"""

import os
import sys
from pprint import pprint

from langchain_core.messages import HumanMessage
from langgraph.types import Command

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph import build_graph
from tools import detect_languages, get_active_languages, scan_languages, set_active_languages


HELP = """命令:
  /lang java,python,go   手动指定分析语言
  /lang auto             重新自动检测语言
  /lang                  查看当前语言配置
  /scan                  扫描仓库源码文件分布
  /thread <id>           切换对话线程
  /help                  查看帮助
  /quit                  退出"""


def _print_state_summary(values: dict) -> None:
    """展示最重要的中间结果，避免把完整 State 全部刷屏。"""
    print(f"\n[任务类型] {values.get('task_type', '?')}")
    print("\n[分析报告]")
    print((values.get("analysis_report") or "(无)")[:1200])
    print("\n[建议级 Diff]")
    print((values.get("diff") or "(无)")[:1200])


def _print_final_messages(values: dict) -> None:
    messages = values.get("messages", [])
    if not messages:
        return

    print("\n[最终输出]")
    for message in messages[-2:]:
        content = getattr(message, "content", "")
        if content:
            print(content[:1200])
            print("-" * 50)


def main():
    print("╔══════════════════════════════════════╗")
    print("║     DevPilot - 代码分析与修改建议助手  ║")
    print("╚══════════════════════════════════════╝")
    print()

    repo_path = os.getcwd()
    print("[启动] 自动检测仓库语言...")
    print(detect_languages(repo_path))
    print()

    app = build_graph()
    current_thread = "default"

    print("输入需求，例如：修复 login 函数的空值问题")
    print("输入 /help 查看命令列表")
    print()

    while True:
        try:
            user_input = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见!")
            break

        if not user_input:
            continue

        if user_input == "/quit":
            break

        if user_input == "/help":
            print(HELP)
            continue

        if user_input == "/scan":
            print(scan_languages(repo_path))
            continue

        if user_input == "/lang":
            print(f"当前语言: {', '.join(get_active_languages())}")
            continue

        if user_input.startswith("/lang "):
            arg = user_input[6:].strip()
            if arg == "auto":
                print(detect_languages(repo_path))
            else:
                langs = [lang.strip() for lang in arg.split(",")]
                print(f"[已切换] 活跃语言: {', '.join(set_active_languages(langs))}")
            continue

        if user_input.startswith("/thread "):
            current_thread = user_input.split(maxsplit=1)[1]
            print(f"[已切换到线程: {current_thread}]")
            continue

        config = {"configurable": {"thread_id": current_thread}}
        languages = get_active_languages()

        print(f"\n[语言: {', '.join(languages)}] 开始分析...")

        for event in app.stream(
            {
                "messages": [HumanMessage(content=user_input)],
                "repo_path": repo_path,
                "languages": languages,
                "task_type": "",
                "target_files": [],
                "analysis_report": "",
                "diff": "",
                "approved": False,
                "pr_number": "",
                "next_step": "route",
            },
            config=config,
        ):
            if "__interrupt__" in event:
                print("\n[等待人工审批]")
                pprint(event["__interrupt__"][0].value)
            else:
                print(f"[节点完成] {next(iter(event.keys()))}")

        values = app.get_state(config).values
        _print_state_summary(values)

        decision = input("\n批准进入 Reviewer? (y/n): ").strip().lower()
        approved = decision == "y"

        for event in app.stream(Command(resume={"approved": approved}), config=config):
            print(f"[节点完成] {next(iter(event.keys()))}")

        values = app.get_state(config).values
        if approved:
            _print_final_messages(values)
        else:
            print("[已拒绝] 流程结束，未进入 Reviewer。")

        print("\n" + "-" * 50)


if __name__ == "__main__":
    main()
