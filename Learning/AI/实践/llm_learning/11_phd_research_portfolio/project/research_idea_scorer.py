#!/usr/bin/env python3
"""Score LLM research ideas for PhD application readiness."""

from __future__ import annotations


IDEAS = [
    {
        "name": "Agent tool-use robustness benchmark for Chinese workplace tasks",
        "novelty": 4,
        "feasibility": 5,
        "evaluation": 5,
        "phd_fit": 4,
    },
    {
        "name": "Train a frontier-scale MoE model from scratch",
        "novelty": 3,
        "feasibility": 1,
        "evaluation": 2,
        "phd_fit": 3,
    },
    {
        "name": "CoT length control for small reasoning models via preference data",
        "novelty": 4,
        "feasibility": 4,
        "evaluation": 4,
        "phd_fit": 5,
    },
]


WEIGHTS = {
    "novelty": 0.30,
    "feasibility": 0.25,
    "evaluation": 0.25,
    "phd_fit": 0.20,
}


def score(idea: dict[str, int | str]) -> float:
    return sum(float(idea[key]) * weight for key, weight in WEIGHTS.items())


def main() -> None:
    ranked = sorted(IDEAS, key=score, reverse=True)
    for idea in ranked:
        print(f"{score(idea):.2f} - {idea['name']}")
    print("\nPrefer ideas that are novel enough, feasible on your hardware, and easy to evaluate rigorously.")


if __name__ == "__main__":
    main()

