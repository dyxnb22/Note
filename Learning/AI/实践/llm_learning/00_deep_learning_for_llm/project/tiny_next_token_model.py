#!/usr/bin/env python3
"""A tiny trainable next-token model using only Python stdlib.

This is not a Transformer. It is a teaching bridge:
token -> parameters -> logits -> softmax -> cross entropy -> gradient descent.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict


CORPUS = "我 喜欢 学习 大模型 我 喜欢 写 代码 我 学习 Transformer"


def softmax(logits: list[float]) -> list[float]:
    max_logit = max(logits)
    exp_values = [math.exp(item - max_logit) for item in logits]
    total = sum(exp_values)
    return [item / total for item in exp_values]


def cross_entropy(probability: float) -> float:
    return -math.log(max(probability, 1e-12))


def build_dataset(text: str) -> tuple[list[str], list[tuple[int, int]]]:
    tokens = text.split()
    vocab = sorted(set(tokens))
    token_to_id = {token: index for index, token in enumerate(vocab)}
    pairs = [(token_to_id[a], token_to_id[b]) for a, b in zip(tokens, tokens[1:])]
    return vocab, pairs


def train(epochs: int = 500, learning_rate: float = 0.2) -> tuple[list[str], list[list[float]]]:
    vocab, pairs = build_dataset(CORPUS)
    size = len(vocab)
    random.seed(7)

    # weights[current_token][next_token] is the logit for predicting next_token.
    weights = [[random.uniform(-0.1, 0.1) for _ in range(size)] for _ in range(size)]

    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        gradients: dict[tuple[int, int], float] = defaultdict(float)

        for current_id, target_id in pairs:
            probs = softmax(weights[current_id])
            total_loss += cross_entropy(probs[target_id])

            # Gradient of softmax + cross entropy: probs - one_hot(target).
            for next_id, probability in enumerate(probs):
                gradients[(current_id, next_id)] += probability - (1.0 if next_id == target_id else 0.0)

        for (current_id, next_id), gradient in gradients.items():
            weights[current_id][next_id] -= learning_rate * gradient / len(pairs)

        if epoch in {1, 50, 100, 300, 500}:
            print(f"epoch={epoch:3d} loss={total_loss / len(pairs):.4f}")

    return vocab, weights


def predict(vocab: list[str], weights: list[list[float]], token: str) -> None:
    token_to_id = {item: index for index, item in enumerate(vocab)}
    current_id = token_to_id[token]
    probs = softmax(weights[current_id])
    ranked = sorted(zip(vocab, probs), key=lambda item: item[1], reverse=True)
    print(f"\nNext-token prediction for: {token}")
    for next_token, probability in ranked[:3]:
        print(f"  {next_token}: {probability:.3f}")


def main() -> None:
    vocab, weights = train()
    print(f"\nVocabulary: {vocab}")
    predict(vocab, weights, "我")
    predict(vocab, weights, "学习")


if __name__ == "__main__":
    main()

