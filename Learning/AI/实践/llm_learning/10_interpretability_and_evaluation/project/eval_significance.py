#!/usr/bin/env python3
"""Bootstrap confidence interval for paired LLM evaluation results."""

from __future__ import annotations

import random
from statistics import mean


# 1 means prompt B wins, 0 means prompt A wins, 0.5 means tie.
PAIRED_RESULTS = [1, 1, 0, 1, 0.5, 1, 0, 1, 1, 0.5, 1, 0, 1, 1, 1]


def bootstrap_interval(values: list[float], rounds: int = 5000) -> tuple[float, float, float]:
    random.seed(42)
    estimates = []
    for _ in range(rounds):
        sample = [random.choice(values) for _ in values]
        estimates.append(mean(sample))
    estimates.sort()
    lower = estimates[int(0.025 * rounds)]
    upper = estimates[int(0.975 * rounds)]
    return mean(values), lower, upper


def main() -> None:
    win_rate, lower, upper = bootstrap_interval(PAIRED_RESULTS)
    print(f"Prompt B estimated win rate: {win_rate:.3f}")
    print(f"95% bootstrap interval: [{lower:.3f}, {upper:.3f}]")
    print("If the interval is wide, collect more examples before claiming a real improvement.")


if __name__ == "__main__":
    main()

