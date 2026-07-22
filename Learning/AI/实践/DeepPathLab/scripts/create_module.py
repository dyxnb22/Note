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
    parser.add_argument(
        "--activate",
        action="store_true",
        help="Create the full working layout for the current module",
    )
    args = parser.parse_args()

    module_dir = args.root / "modules" / f"{args.number}_{slugify(args.title)}"
    module_dir.mkdir(parents=True, exist_ok=True)

    readme = f"""# {args.number} {args.title}

**Status: {"Current iteration" if args.activate else "Queued"}**

This module is part of DeepPath Lab and should become one independent learning project.

## Planned Project

Define the smallest runnable artifact that makes the module's core idea concrete.
"""

    if args.activate:
        readme += """
## Workflow

The active module uses the full working layout:

- Read the reference chapter
- Write original notes in `notes.md`
- Reproduce a baseline in `reproduce/`
- Implement the core idea in `from_scratch/`
- Run ablations in `experiments/`
- Summarize results in `report.md`
"""
    else:
        readme += """
The working folders (`notes.md`, `reproduce/`, `from_scratch/`, `experiments/`,
and `report.md`) are created only when the previous module has meaningful
progress. Use `--activate` when this module becomes the current iteration.
"""

    write_file(module_dir / "README.md", readme)

    if args.activate:
        for name in ("reproduce", "from_scratch", "experiments"):
            (module_dir / name).mkdir(exist_ok=True)

        notes = """# Notes

Record original notes, implementation questions, and observations for this
module. Do not copy the reference text.
"""

        report = """# Report

Record commands, measurements, failure cases, and conclusions for this module.
"""

        sub_readmes = {
            "reproduce/README.md": "# Reproduce\n\nAdd the baseline reproduction and its run notes.\n",
            "from_scratch/README.md": "# From Scratch\n\nAdd the smallest original implementation of the core idea.\n",
            "experiments/README.md": "# Experiments\n\nAdd ablations, diagnostics, and observations.\n",
        }

        write_file(module_dir / "notes.md", notes)
        write_file(module_dir / "report.md", report)
        for relative_path, content in sub_readmes.items():
            write_file(module_dir / relative_path, content)

    mode = "active scaffold" if args.activate else "scope card"
    print(f"Created {mode} at {module_dir}")


if __name__ == "__main__":
    main()
