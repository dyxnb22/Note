#!/usr/bin/env python3
"""Create a new DeepPath Lab module scaffold."""

from __future__ import annotations

import argparse
from pathlib import Path


def slugify(name: str) -> str:
    cleaned = []
    for char in name.lower():
        if char.isalnum():
            cleaned.append(char)
        elif char in {" ", "-", "&", "/"}:
            cleaned.append("_")
    slug = "".join(cleaned)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("number", help="Module number, for example 05")
    parser.add_argument("title", help="Module title, for example Sequence Models")
    parser.add_argument(
        "--root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Repository root",
    )
    args = parser.parse_args()

    module_dir = args.root / "modules" / f"{args.number}_{slugify(args.title)}"
    module_dir.mkdir(parents=True, exist_ok=True)
    for name in ("reproduce", "from_scratch", "experiments"):
        (module_dir / name).mkdir(exist_ok=True)

    readme = f"""# {args.number} {args.title}

This module is part of DeepPath Lab.

## Workflow

- Read the reference chapter
- Write original notes in `notes.md`
- Reproduce a baseline in `reproduce/`
- Implement the core idea in `from_scratch/`
- Run ablations in `experiments/`
- Summarize results in `report.md`
"""

    notes = """# Notes

Write original notes here.
"""

    report = """# Report

Summarize the module work, experiments, and takeaways here.
"""

    sub_readmes = {
        "reproduce/README.md": "# Reproduce\n\nStore baseline reproductions here.\n",
        "from_scratch/README.md": "# From Scratch\n\nImplement the core ideas here.\n",
        "experiments/README.md": "# Experiments\n\nStore ablations and diagnostics here.\n",
    }

    write_file(module_dir / "README.md", readme)
    write_file(module_dir / "notes.md", notes)
    write_file(module_dir / "report.md", report)
    for relative_path, content in sub_readmes.items():
        write_file(module_dir / relative_path, content)

    print(f"Created module scaffold at {module_dir}")


if __name__ == "__main__":
    main()
