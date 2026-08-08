#!/usr/bin/env python3
"""Verify local Markdown links and fenced code blocks without changing notes."""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".obsidian", ".claudian"}


def markdown_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*.md")
        if not IGNORED_PARTS.intersection(path.relative_to(ROOT).parts)
    ]


def local_markdown_target(raw: str) -> str | None:
    target = raw.strip()
    if re.match(r"^(?:https?://|mailto:|obsidian:|data:|#)", target):
        return None

    # Markdown destinations may end with an optional quoted title.
    target = re.sub(r'''\s+["'][^"']*["']\s*$''', "", target)
    target = target.strip("<>").split("#", 1)[0]
    return unquote(target) or None


def main() -> int:
    notes = markdown_files()
    stems: dict[str, list[Path]] = defaultdict(list)
    for path in notes:
        stems[path.stem].append(path)

    problems: list[str] = []

    for path in notes:
        relative = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8", errors="replace")

        if text.count("`" * 3) % 2:
            problems.append(f"{relative}: unclosed ``` fence")
        if text.count("~" * 3) % 2:
            problems.append(f"{relative}: unclosed ~~~ fence")

        for raw in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", text):
            target = local_markdown_target(raw)
            if target is None:
                continue

            resolved = (path.parent / target).resolve()
            candidates = [resolved]
            if not resolved.suffix:
                candidates.append(resolved.with_suffix(".md"))
            if not any(candidate.exists() for candidate in candidates):
                problems.append(f"{relative}: missing link target: {raw}")

        for raw in re.findall(r"\[\[([^\]|#]+)", text):
            target = raw.strip()
            if "/" in target:
                resolved = (path.parent / unquote(target)).resolve()
                exists = resolved.exists() or resolved.with_suffix(".md").exists()
            else:
                exists = bool(stems.get(Path(target).stem))
            if not exists:
                problems.append(f"{relative}: missing wiki link target: [[{raw}]]")

    if problems:
        print("Notes verification failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print(f"Notes verification passed: {len(notes)} Markdown files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
