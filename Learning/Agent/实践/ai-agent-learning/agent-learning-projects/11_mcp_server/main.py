"""
第 11 课：构建你自己的 MCP Server

学习目标：
1. 理解 MCP Server 的完整生命周期；
2. 掌握 Resources（资源）和 Tools（工具）的区别；
3. 理解如何把已有的 Python 函数"MCP 化"。

MCP 三种原语：
  - Tool：AI 模型可以调用的函数（有副作用，例如搜索、计算、写文件）
  - Resource：AI 模型可以读取的内容（只读，例如文档、配置、状态）
  - Prompt：预定义的提示词模板（帮助用户快速启动特定任务）

运行（有 fastmcp）：
    pip install "fastmcp>=2.0"
    python main.py

运行（无依赖，Mock 模式）：
    python main.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

try:
    from fastmcp import FastMCP
    HAS_FASTMCP = True
except ImportError:
    HAS_FASTMCP = False

# ---------------------------------------------------------------------------
# 业务逻辑（与 MCP 完全无关）
# ---------------------------------------------------------------------------

# 模拟一个简单的笔记系统
_notes: dict[str, dict] = {}


def _add_note_impl(title: str, content: str, tags: list[str] | None = None) -> dict:
    note_id = f"note_{len(_notes) + 1:03d}"
    _notes[note_id] = {
        "id": note_id,
        "title": title,
        "content": content,
        "tags": tags or [],
        "created_at": datetime.now().isoformat(),
    }
    return {"id": note_id, "message": f"笔记已保存：{title}"}


def _search_notes_impl(query: str) -> list[dict]:
    results = []
    for note in _notes.values():
        if query.lower() in note["title"].lower() or query.lower() in note["content"].lower():
            results.append({"id": note["id"], "title": note["title"], "preview": note["content"][:100]})
    return results


def _get_stats_impl() -> dict:
    tag_counts: dict[str, int] = {}
    for note in _notes.values():
        for tag in note["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    return {
        "total_notes": len(_notes),
        "tags": tag_counts,
        "latest": max(_notes.values(), key=lambda n: n["created_at"])["title"] if _notes else None,
    }


# ---------------------------------------------------------------------------
# MCP Server（有 fastmcp 才注册）
# ---------------------------------------------------------------------------

if HAS_FASTMCP:
    mcp = FastMCP("Note Manager MCP Server", version="1.0.0")

    # --- Tools（有副作用）---

    @mcp.tool()
    def add_note(title: str, content: str, tags: list[str] | None = None) -> str:
        """添加一条新笔记。title 是标题，content 是内容，tags 是可选标签列表。"""
        result = _add_note_impl(title, content, tags)
        return json.dumps(result, ensure_ascii=False)

    @mcp.tool()
    def search_notes(query: str) -> str:
        """在笔记库中搜索，返回标题或内容包含 query 的笔记列表。"""
        results = _search_notes_impl(query)
        if not results:
            return f"未找到包含 '{query}' 的笔记。"
        return json.dumps(results, ensure_ascii=False, indent=2)

    # --- Resources（只读）---
    # Resource 的 URI 格式：scheme://path
    # AI 模型可以"读取"这些资源，但不会修改它们

    @mcp.resource("notes://stats")
    def get_stats() -> str:
        """返回笔记库统计信息（总数、标签分布、最新笔记）。"""
        return json.dumps(_get_stats_impl(), ensure_ascii=False, indent=2)

    @mcp.resource("notes://all")
    def list_all_notes() -> str:
        """列出所有笔记的标题和 ID。"""
        return json.dumps(
            [{"id": n["id"], "title": n["title"]} for n in _notes.values()],
            ensure_ascii=False, indent=2
        )

    # --- Prompts（提示词模板）---

    @mcp.prompt()
    def summarize_notes(topic: str) -> str:
        """生成一个总结指定主题笔记的 Prompt 模板。"""
        return f"""请搜索关于 "{topic}" 的所有笔记，然后：
1. 列出找到的笔记标题
2. 总结核心观点
3. 指出各笔记之间的联系
4. 提出后续学习建议"""


# ---------------------------------------------------------------------------
# Mock 演示
# ---------------------------------------------------------------------------

def demo_without_mcp():
    print("=== 第 11 课：MCP Server（Mock 模式）===")
    print("[注意] 未安装 fastmcp，以 Mock 模式演示")
    print("       安装：pip install 'fastmcp>=2.0'")
    print()

    # 演示 Tool 调用
    print("--- Tool: add_note ---")
    r1 = _add_note_impl("MCP 学习笔记", "MCP 是 Anthropic 的开放工具协议", ["mcp", "ai"])
    print(f"  → {r1}")

    r2 = _add_note_impl("LangGraph 实践", "StateGraph 是 LangGraph 的核心", ["langgraph", "agent"])
    print(f"  → {r2}")

    print("\n--- Tool: search_notes ---")
    results = _search_notes_impl("mcp")
    print(f"  搜索 'mcp' → {results}")

    print("\n--- Resource: notes://stats ---")
    stats = _get_stats_impl()
    print(f"  → {stats}")

    print("""
--- MCP 三种原语对比 ---

  Tool      有副作用的操作       add_note / search_notes
            AI 模型"调用"它      类比：REST API POST/GET
            返回值给 AI 模型

  Resource  只读数据源           notes://stats / notes://all
            AI 模型"读取"它      类比：REST API GET（只读）
            通常是配置、状态、文档

  Prompt    提示词模板           summarize_notes
            帮用户快速启动任务   类比：代码里的函数模板

用法经验：
  - 查询、计算、写操作 → Tool
  - 配置、文档、状态监控 → Resource
  - 常用任务模板 → Prompt
""")


if __name__ == "__main__":
    if HAS_FASTMCP:
        print("启动 Note Manager MCP Server（stdio 模式）...")
        mcp.run()
    else:
        demo_without_mcp()
