"""DevPilot 的 Agent 节点实现。

设计原则：
1. 每个节点职责单一，方便单独替换成 LLM；
2. LLM 是可选的 —— 有 API Key 就用真实 LLM，没有就降级到规则 Mock；
3. 输出是“修改建议”，不直接改用户文件，避免误操作。

LLM 优先级：ANTHROPIC_API_KEY > OPENAI_API_KEY > DEEPSEEK_API_KEY > Mock
"""

import os
import re
from pathlib import Path

from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from state import DevPilotState
from tools import get_active_languages, grep_search, list_files, read_file, scan_languages

# ---------------------------------------------------------------------------
# LLM 工厂（懒加载，只有真正用到时才导入）
# ---------------------------------------------------------------------------


def _get_llm(max_tokens: int = 2048):
    """尝试获取可用的 LLM 客户端，全部不可用时返回 None。"""
    from dotenv import load_dotenv
    load_dotenv()

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")

    try:
        if anthropic_key:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(model="claude-sonnet-4-6", max_tokens=max_tokens)
    except ImportError:
        pass

    try:
        if openai_key:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=os.environ["OPENAI_MODEL"], max_tokens=max_tokens)
    except ImportError:
        pass

    try:
        if deepseek_key:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                api_key=deepseek_key,
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                max_tokens=max_tokens,
            )
    except ImportError:
        pass

    return None


def _latest_user_text(state: DevPilotState) -> str:
    """兼容 dict message 和 LangChain message 两种格式。"""
    message = state["messages"][-1]
    if isinstance(message, dict):
        return str(message.get("content", ""))
    return str(getattr(message, "content", ""))


def _first_user_text(state: DevPilotState) -> str:
    """取最初的用户需求，避免后续 AIMessage 覆盖任务语义。"""
    for message in state.get("messages", []):
        if isinstance(message, dict) and message.get("role") == "user":
            return str(message.get("content", ""))
        if getattr(message, "type", "") == "human":
            return str(getattr(message, "content", ""))
    return _latest_user_text(state)


def _extract_keywords(text: str) -> list[str]:
    """从用户需求中提取搜索关键词。

    这里故意用简单规则，方便学习。后续可以替换成 LLM 关键词提取。
    """
    words = re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}|[\u4e00-\u9fff]{2,}", text)
    stop_words = {"修复", "新增", "实现", "问题", "代码", "功能", "帮我", "一下"}
    keywords = [word for word in words if word not in stop_words]
    return keywords[:5] or ["def", "class", "TODO"]


def _paths_from_grep(output: str) -> list[str]:
    """从 grep_search 的输出中提取文件路径。"""
    paths: list[str] = []
    for line in output.splitlines():
        if ":" not in line:
            continue
        path = line.split(":", 1)[0]
        if path and Path(path).exists() and path not in paths:
            paths.append(path)
    return paths


def _display_path(path: str, repo_path: str) -> str:
    """把绝对路径转成更适合展示的仓库相对路径。"""
    try:
        return str(Path(path).resolve().relative_to(Path(repo_path).resolve()))
    except ValueError:
        return path


# ---------------------------------------------------------------------------
# Router Agent
# ---------------------------------------------------------------------------


def router(state: DevPilotState) -> dict:
    """判断任务类型：bug 修复、功能开发或代码审查。"""
    task = _latest_user_text(state)

    if any(word in task for word in ["审查", "review", "检查"]):
        task_type = "code_review"
    elif any(word in task for word in ["新增", "实现", "添加", "feature"]):
        task_type = "feature"
    else:
        task_type = "bug_fix"

    return {
        "task_type": task_type,
        "messages": [AIMessage(content=f"Router 判断任务类型为：{task_type}")],
        "next_step": "analyze",
    }


# ---------------------------------------------------------------------------
# Analyzer Agent
# ---------------------------------------------------------------------------


def analyzer(state: DevPilotState) -> dict:
    """搜索代码库，定位可能相关的文件。"""
    repo_path = state.get("repo_path", ".")
    task = _first_user_text(state)
    keywords = _extract_keywords(task)

    search_blocks: list[str] = []
    target_files: list[str] = []

    for keyword in keywords:
        output = grep_search(keyword, repo_path)
        search_blocks.append(f"### 关键词：{keyword}\n{output}")
        for path in _paths_from_grep(output):
            if path not in target_files:
                target_files.append(path)

    if not target_files:
        # 搜不到时给出源码文件兜底，避免后续节点没有上下文。
        listed = list_files(repo_path, "*")
        target_files = [line for line in listed.splitlines() if line][:8]

    report = "\n".join(
        [
            "## 分析报告",
            "",
            f"任务类型：{state.get('task_type', 'unknown')}",
            f"活跃语言：{', '.join(state.get('languages') or get_active_languages())}",
            "",
            "### 语言扫描",
            scan_languages(repo_path),
            "",
            "### 搜索关键词",
            ", ".join(keywords),
            "",
            "### 可能相关文件",
            "\n".join(
                f"- {_display_path(path, repo_path)}" for path in target_files[:12]
            ) or "- 暂未定位到文件",
            "",
            "### 搜索摘要",
            "\n\n".join(search_blocks[:3]),
        ]
    )

    return {
        "target_files": target_files[:12],
        "analysis_report": report,
        "messages": [AIMessage(content="Analyzer 已完成代码搜索和候选文件定位。")],
        "next_step": "fix",
    }


# ---------------------------------------------------------------------------
# Fixer Agent
# ---------------------------------------------------------------------------


def fixer(state: DevPilotState) -> dict:
    """基于分析报告生成建议级 diff。

    有 LLM Key → 读取目标文件内容，让 LLM 生成真实修改建议。
    无 LLM Key → 输出结构化 Mock diff，展示格式和流程。

    注意：输出是"建议"，不直接改文件，避免误操作。
    """
    task = _first_user_text(state)
    target_files = state.get("target_files", [])
    analysis = state.get("analysis_report", "")
    repo_path = state.get("repo_path", ".")

    llm = _get_llm()

    if llm and target_files:
        # 读取最相关的 1-2 个文件作为上下文
        file_contexts = []
        for path in target_files[:2]:
            content = read_file(path, start_line=1, end_line=60)
            rel = _display_path(path, repo_path)
            file_contexts.append(f"文件: {rel}\n```\n{content}\n```")

        prompt = f"""你是一个代码修改建议助手。

用户需求：{task}

代码分析报告摘要：
{analysis[:1500]}

相关文件内容：
{chr(10).join(file_contexts)}

请生成一个 unified diff 格式的修改建议。
要求：
1. 格式必须是标准 diff --git 格式
2. 只改最必要的地方，不要过度修改
3. 每个修改行都要有注释解释原因
4. 如果信息不足，输出分析说明而不是伪造 diff

只输出 diff 内容（或分析说明），不要其他废话。"""

        try:
            response = llm.invoke(prompt)
            diff = response.content if hasattr(response, "content") else str(response)
            mode = "LLM 生成"
        except Exception as e:
            diff = _mock_diff(task, target_files, repo_path)
            mode = f"LLM 调用失败({e})，降级到 Mock"
    else:
        diff = _mock_diff(task, target_files, repo_path)
        mode = "Mock（未配置 LLM Key）"

    return {
        "diff": diff,
        "messages": [AIMessage(content=f"Fixer [{mode}] 已生成建议级 diff，等待人工审批。")],
        "next_step": "approval",
    }


def _mock_diff(task: str, target_files: list, repo_path: str) -> str:
    """无 LLM 时输出的结构化占位 diff。"""
    file_hint = _display_path(target_files[0], repo_path) if target_files else "path/to/target_file.py"
    return "\n".join([
        "diff --git a/{0} b/{0}".format(file_hint),
        "--- a/{0}".format(file_hint),
        "+++ b/{0}".format(file_hint),
        "@@ -1,5 +1,8 @@",
        " # 现有代码（上下文行，不修改）",
        "-# TODO: 原逻辑需要结合分析报告进一步确认",
        "+# 建议修改：围绕用户需求补充实现或修复边界情况",
        f"+# 用户需求：{task[:80]}",
        "+# 提示：配置 ANTHROPIC_API_KEY 后，此处将由 LLM 生成真实修改建议",
        " # 下一步：人工确认后，把建议转成真实代码 patch",
    ])


# ---------------------------------------------------------------------------
# Human Approval
# ---------------------------------------------------------------------------


def approval_node(state: DevPilotState) -> dict:
    """人工审批节点。

    执行到这里会暂停。CLI 会展示分析报告和 diff，然后用 Command(resume=...)
    把 approved 结果传回来。
    """
    decision = interrupt(
        {
            "question": "是否批准进入 Reviewer？",
            "target_files": state.get("target_files", []),
            "diff_preview": state.get("diff", "")[:1000],
        }
    )
    approved = bool(decision.get("approved")) if isinstance(decision, dict) else False
    return {"approved": approved, "next_step": "review" if approved else "end"}


# ---------------------------------------------------------------------------
# Reviewer Agent
# ---------------------------------------------------------------------------


def reviewer(state: DevPilotState) -> dict:
    """审查建议 diff 的完整性和风险。"""
    target_files = state.get("target_files", [])
    suffixes = sorted({Path(path).suffix for path in target_files if Path(path).suffix})

    review = "\n".join(
        [
            "## Reviewer 审查结果",
            "",
            "结论：当前 diff 是建议级修改，不能直接视为可应用 patch。",
            "",
            "检查项：",
            "- 已基于搜索结果给出候选文件。",
            "- 已保留人工审批环节。",
            "- 尚未执行真实测试，需要人工把建议落到代码后再运行测试。",
            f"- 涉及文件类型：{', '.join(suffixes) if suffixes else '未知'}",
        ]
    )

    return {
        "messages": [AIMessage(content=review)],
        "next_step": "create_pr",
    }


# ---------------------------------------------------------------------------
# PR Creator Agent
# ---------------------------------------------------------------------------


def pr_creator(state: DevPilotState) -> dict:
    """生成 PR 标题和描述草稿。"""
    task = _first_user_text(state)
    target_files = state.get("target_files", [])
    repo_path = state.get("repo_path", ".")

    body = "\n".join(
        [
            "## 标题",
            f"DevPilot 建议：{task[:40]}",
            "",
            "## 描述",
            "- 根据用户需求完成代码搜索和候选文件定位。",
            "- 生成建议级 diff，等待人工转成真实代码修改。",
            "- Reviewer 已给出风险提示。",
            "",
            "## 候选文件",
            "\n".join(
                f"- {_display_path(path, repo_path)}" for path in target_files[:10]
            ) or "- 暂无",
        ]
    )

    return {
        "pr_number": "draft",
        "messages": [AIMessage(content=body)],
        "next_step": "end",
    }
