"""工具集：代码搜索 / Git 操作 / GitHub 操作 / 语言检测"""

import subprocess
import os
import glob as _glob

# ══════════════════════════════════════════════════════════════
#  语言 → 文件扩展名映射
# ══════════════════════════════════════════════════════════════

EXTENSION_MAP: dict[str, list[str]] = {
    "python":   [".py", ".pyi", ".pyx"],
    "java":     [".java", ".kt", ".kts", ".scala"],
    "javascript":[".js", ".jsx", ".mjs", ".cjs"],
    "typescript":[".ts", ".tsx"],
    "go":       [".go"],
    "rust":     [".rs"],
    "c":        [".c", ".h"],
    "cpp":      [".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx"],
    "ruby":     [".rb"],
    "php":      [".php"],
    "swift":    [".swift"],
    "csharp":   [".cs"],
    "shell":    [".sh", ".bash", ".zsh"],
    "sql":      [".sql"],
    "yaml":     [".yml", ".yaml"],
    "terraform":[".tf", ".tfvars"],
    "docker":   ["Dockerfile", "docker-compose.yml"],
}

# 项目标志文件 → 推断语言（用于自动检测）
DETECTION_MARKERS: dict[str, list[str]] = {
    "python":   ["requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "Pipfile", "poetry.lock"],
    "java":     ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle"],
    "javascript":["package.json"],
    "typescript":["tsconfig.json"],
    "go":       ["go.mod", "go.sum"],
    "rust":     ["Cargo.toml", "Cargo.lock"],
    "c":        ["Makefile", "CMakeLists.txt"],
    "cpp":      ["CMakeLists.txt", "conanfile.txt", "meson.build"],
    "ruby":     ["Gemfile", "Rakefile"],
    "php":      ["composer.json"],
    "swift":    ["Package.swift"],
    "csharp":   ["*.csproj", "*.sln"],
}

# ══════════════════════════════════════════════════════════════
#  当前会话的语言配置（模块级可变，grep 使用它）
# ══════════════════════════════════════════════════════════════

_active_languages: set[str] = set()
SKIP_DIRS = {
    "node_modules", "vendor", ".git", "__pycache__", "target",
    "build", "dist", "venv", ".venv", ".pytest_cache",
}


def _iter_files(repo_path: str):
    """遍历仓库文件，跳过依赖目录和构建产物。"""
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            yield os.path.join(root, filename)


def set_active_languages(langs: list[str]) -> list[str]:
    """设置当前会话的活跃语言，返回实际生效的列表"""
    global _active_languages
    valid = []
    for lang in langs:
        lang = lang.strip().lower()
        if lang in EXTENSION_MAP:
            valid.append(lang)
    _active_languages = set(valid) if valid else _detect_fallback()
    return sorted(_active_languages)


def get_active_languages() -> list[str]:
    return sorted(_active_languages or _detect_fallback())


# ══════════════════════════════════════════════════════════════
#  语言检测
# ══════════════════════════════════════════════════════════════


def _detect_fallback() -> set[str]:
    """无任何信息时的兜底：搜常见扩展名"""
    for marker in ["pyproject.toml", "pom.xml", "package.json", "go.mod", "Cargo.toml", "CMakeLists.txt"]:
        if os.path.exists(marker):
            for lang, markers in DETECTION_MARKERS.items():
                if marker in markers:
                    return {lang}
    return {"python", "java", "javascript", "typescript", "go", "c", "cpp"}


def detect_languages(repo_path: str = ".") -> str:
    """
    自动检测仓库使用的编程语言。扫描标志文件和源码扩展名。
    返回检测到的语言列表及判断依据。
    """
    results: dict[str, list[str]] = {}

    # 1. 扫描标志文件
    for lang, markers in DETECTION_MARKERS.items():
        for marker in markers:
            if marker.startswith("*."):
                pattern = os.path.join(repo_path, "**", marker)
                if _glob.glob(pattern, recursive=True):
                    results.setdefault(lang, []).append(f"文件通配: {marker}")
                    break
            elif os.path.exists(os.path.join(repo_path, marker)):
                results.setdefault(lang, []).append(f"标志文件: {marker}")
                break

    # 2. 扫描源码扩展名
    all_files = list(_iter_files(repo_path))
    for lang, exts in EXTENSION_MAP.items():
        if lang in results:
            continue
        for ext in exts:
            files = [path for path in all_files if path.endswith(ext)]
            if files:
                results.setdefault(lang, []).append(f"源码: {len(files)} 个 {ext} 文件")
                break

    if not results:
        return "无法自动检测语言。请用 /lang python,java,cpp 手动指定。"

    lines = []
    for lang, reasons in results.items():
        lines.append(f"  {lang}: {', '.join(reasons)}")

    # 自动设置为活跃语言
    lang_list = list(results.keys())
    set_active_languages(lang_list)

    return f"检测到 {len(results)} 种语言:\n" + "\n".join(lines)


def scan_languages(repo_path: str = ".") -> str:
    """查看当前仓库的语言配置和源码文件分布"""
    langs = get_active_languages()
    report = [f"活跃语言: {', '.join(langs)}", "", "源码文件统计:"]

    for lang in langs:
        exts = EXTENSION_MAP.get(lang, [])
        total = 0
        for ext in exts:
            total += sum(1 for path in _iter_files(repo_path) if path.endswith(ext))
        report.append(f"  {lang}: ~{total} 个文件 ({', '.join(exts)})")

    return "\n".join(report)


# ══════════════════════════════════════════════════════════════
#  Code Search（语言自适应）
# ══════════════════════════════════════════════════════════════


def grep_search(pattern: str, path: str = ".") -> str:
    """
    在代码库中搜索文本/正则(pattern)。
    自动限定当前活跃语言的源码文件，避免搜到 vendor/node_modules/二进制。
    """
    languages = get_active_languages()
    include_args: list[str] = []
    for lang in languages:
        for ext in EXTENSION_MAP.get(lang, []):
            if "/" not in ext and " " not in ext:
                include_args.extend(["--include", f"*{ext}"])

    if not include_args:
        # 全语言兜底
        for exts in EXTENSION_MAP.values():
            for ext in exts:
                include_args.extend(["--include", f"*{ext}"])

    exclude_args = [
        "--exclude-dir=node_modules",
        "--exclude-dir=vendor",
        "--exclude-dir=.git",
        "--exclude-dir=__pycache__",
        "--exclude-dir=target",
        "--exclude-dir=build",
        "--exclude-dir=dist",
    ]

    try:
        result = subprocess.run(
            ["grep", "-rn", *include_args, *exclude_args, pattern, path],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout.strip()
        if not output:
            return f"未找到匹配: {pattern} (已搜索 {', '.join(languages)} 文件)"
        lines = output.split("\n")[:40]
        return "\n".join(lines) + ("\n...(截断)" if len(output.split("\n")) > 40 else "")
    except FileNotFoundError:
        return "错误: grep 未安装"


def read_file(filepath: str, start_line: int = 1, end_line: int = 100) -> str:
    """读取文件内容。可指定行范围。"""
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
        selected = lines[start_line - 1 : end_line]
        return "".join(selected)
    except FileNotFoundError:
        return f"文件不存在: {filepath}"


def list_files(directory: str = ".", pattern: str = "*") -> str:
    """列出目录中的文件。pattern 如 '*.java'"""
    files = _glob.glob(os.path.join(directory, "**", pattern), recursive=True)
    # 过滤掉常见非源码目录
    files = [f for f in files if not any(
        skip in f.split(os.sep) for skip in SKIP_DIRS
    )]
    return "\n".join(files[:50]) + ("\n...(截断)" if len(files) > 50 else "")


# ══════════════════════════════════════════════════════════════
#  Git Operations
# ══════════════════════════════════════════════════════════════


def git_diff(filepath: str = "") -> str:
    cmd = ["git", "diff"]
    if filepath:
        cmd.append(filepath)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() or "(无改动)"


def git_status() -> str:
    result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
    return result.stdout.strip() or "(干净)"


def create_branch(branch_name: str) -> str:
    result = subprocess.run(
        ["git", "checkout", "-b", branch_name],
        capture_output=True, text=True
    )
    return result.stdout.strip() or result.stderr.strip()


# ══════════════════════════════════════════════════════════════
#  GitHub Operations
# ══════════════════════════════════════════════════════════════


def create_pr(title: str, body: str, base: str = "main") -> str:
    try:
        result = subprocess.run(
            ["gh", "pr", "create", "--title", title, "--body", body, "--base", base],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip() or result.stderr.strip()
    except FileNotFoundError:
        return "错误: 未安装 gh CLI"


def read_issue(issue_url: str) -> str:
    try:
        result = subprocess.run(
            ["gh", "issue", "view", issue_url, "--json", "title,body"],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return "错误: 未安装 gh CLI"


# ══════════════════════════════════════════════════════════════
#  汇总
# ══════════════════════════════════════════════════════════════

ALL_TOOLS = [
    grep_search, read_file, list_files,
    git_diff, git_status, create_branch,
    create_pr, read_issue,
    detect_languages, scan_languages,
]
