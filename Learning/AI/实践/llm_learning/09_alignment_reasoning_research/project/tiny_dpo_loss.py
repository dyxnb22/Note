#!/usr/bin/env python3
"""A tiny numerical DPO loss demo.

DPO compares how much more the policy prefers a chosen answer than a rejected
answer, relative to a reference model. This script uses fake log-probabilities
so the core idea is visible without training a real LLM.
"""

from __future__ import annotations

import math


def log_sigmoid(x: float) -> float:
    return -math.log1p(math.exp(-x))


def dpo_loss(
    policy_chosen_logp: float,
    policy_rejected_logp: float,
    reference_chosen_logp: float,
    reference_rejected_logp: float,
    beta: float = 0.1,
) -> float:
    policy_margin = policy_chosen_logp - policy_rejected_logp
    reference_margin = reference_chosen_logp - reference_rejected_logp
    return -log_sigmoid(beta * (policy_margin - reference_margin))


def main() -> None:
    examples = [
        {
            "name": "policy already prefers chosen",
            "policy_chosen": -1.0,
            "policy_rejected": -3.0,
            "reference_chosen": -1.5,
            "reference_rejected": -2.0,
        },
        {
            "name": "policy weakly prefers rejected",
            "policy_chosen": -2.8,
            "policy_rejected": -1.2,
            "reference_chosen": -1.5,
            "reference_rejected": -2.0,
        },
    ]

    for item in examples:
        loss = dpo_loss(
            item["policy_chosen"],
            item["policy_rejected"],
            item["reference_chosen"],
            item["reference_rejected"],
        )
        print(f"{item['name']}: loss={loss:.4f}")

    print("\nLower loss means the policy preference margin better matches the chosen-over-rejected preference.")


if __name__ == "__main__":
    main()

