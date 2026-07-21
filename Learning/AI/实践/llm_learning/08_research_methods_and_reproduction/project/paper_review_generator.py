#!/usr/bin/env python3
"""Generate a research-style paper review template."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def slugify(title: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-") or "paper"


def build_template(title: str) -> str:
    return f"""# Paper Review: {title}

## 1. Citation

- Title:
- Authors:
- Venue / Year:
- Link:

## 2. One-Sentence Summary

Write one sentence that captures the paper's central contribution.

## 3. Problem

What concrete problem does this paper solve?

## 4. Motivation

Why did prior methods fail or remain insufficient?

## 5. Method

Describe the method in your own words. Avoid copying the abstract.

## 6. Key Equations or Algorithms

List only the equations or algorithm steps needed to reimplement the idea.

## 7. Experiments

- Datasets:
- Baselines:
- Metrics:
- Main result:

## 8. Ablations

Which ablations prove the method is actually responsible for the gain?

## 9. Limitations

Where might the paper fail? What assumptions are fragile?

## 10. Reproduction Plan

- Minimal dataset:
- Minimal baseline:
- Expected metric:
- Compute requirement:
- Failure risks:

## 11. New Research Ideas

Write 3 possible extensions. At least one should be small enough for a 2-week experiment.
"""


def main() -> None:
    title = " ".join(sys.argv[1:]) or "Untitled LLM Paper"
    output = Path(__file__).with_name(f"{slugify(title)}.md")
    output.write_text(build_template(title), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()

