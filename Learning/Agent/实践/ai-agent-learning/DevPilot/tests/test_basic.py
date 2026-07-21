"""DevPilot 测试"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from state import DevPilotState
from tools import (
    EXTENSION_MAP, DETECTION_MARKERS,
    set_active_languages, get_active_languages, grep_search
)


def test_state_initialization():
    """State 包含 languages 字段"""
    state = DevPilotState(
        messages=[{"role": "user", "content": "测试"}],
        task_type="bug_fix",
        repo_path=".",
        languages=["python", "java"],
        target_files=[],
        analysis_report="",
        diff="",
        approved=False,
        pr_number="",
        next_step="route",
    )
    assert state["task_type"] == "bug_fix"
    assert "python" in state["languages"]
    assert "java" in state["languages"]


def test_language_map():
    """验证语言映射表包含主流语言"""
    assert "python" in EXTENSION_MAP
    assert "java" in EXTENSION_MAP
    assert "javascript" in EXTENSION_MAP
    assert "go" in EXTENSION_MAP
    assert "c" in EXTENSION_MAP
    assert "cpp" in EXTENSION_MAP
    assert "rust" in EXTENSION_MAP


def test_set_languages():
    """验证语言切换"""
    set_active_languages(["python", "java"])
    langs = get_active_languages()
    assert "python" in langs
    assert "java" in langs


def test_grep_search():
    """验证 grep_search 能运行（不依赖具体结果）"""
    result = grep_search("def ", ".")
    assert isinstance(result, str)
    print(f"grep 返回长度: {len(result)}")



if __name__ == "__main__":
    test_state_initialization()
    test_language_map()
    test_set_languages()
    test_grep_search()
    print("所有测试通过!")
