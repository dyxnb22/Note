#!/usr/bin/env python3
"""A tiny self-attention demo using only Python stdlib.

This file is intentionally small and explicit. It is not fast, but it helps you
see the actual math behind Attention(Q, K, V).
"""

from __future__ import annotations

import math


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def softmax(values: list[float]) -> list[float]:
    # Subtracting max improves numerical stability.
    max_value = max(values)
    exp_values = [math.exp(value - max_value) for value in values]
    total = sum(exp_values)
    return [value / total for value in exp_values]


def weighted_sum(weights: list[float], vectors: list[list[float]]) -> list[float]:
    result = [0.0 for _ in vectors[0]]
    for weight, vector in zip(weights, vectors):
        for index, value in enumerate(vector):
            result[index] += weight * value
    return result


def self_attention(tokens: list[str], embeddings: list[list[float]]) -> list[list[float]]:
    """Compute single-head self-attention.

    To keep the demo focused, Q/K/V are all equal to the input embeddings.
    Real models learn different projection matrices for Q, K, and V.
    """
    q_vectors = embeddings
    k_vectors = embeddings
    v_vectors = embeddings
    scale = math.sqrt(len(embeddings[0]))

    outputs: list[list[float]] = []
    for token, query in zip(tokens, q_vectors):
        scores = [dot(query, key) / scale for key in k_vectors]
        weights = softmax(scores)
        output = weighted_sum(weights, v_vectors)
        outputs.append(output)

        print(f"\nToken: {token}")
        print("Attention weights:")
        for other_token, weight in zip(tokens, weights):
            print(f"  {other_token}: {weight:.3f}")
        print(f"New representation: {[round(value, 3) for value in output]}")

    return outputs


def main() -> None:
    tokens = ["我", "喜欢", "学习", "大模型"]

    # Each token is represented by a tiny fake embedding.
    # In real LLMs, embeddings usually have thousands of dimensions.
    embeddings = [
        [0.9, 0.1, 0.0],
        [0.8, 0.2, 0.1],
        [0.1, 0.9, 0.7],
        [0.0, 1.0, 0.9],
    ]

    self_attention(tokens, embeddings)


if __name__ == "__main__":
    main()

