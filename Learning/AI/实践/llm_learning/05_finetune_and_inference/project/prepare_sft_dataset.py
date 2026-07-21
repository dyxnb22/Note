#!/usr/bin/env python3
"""Prepare a tiny SFT dataset and LoRA config draft."""

from __future__ import annotations

import json
import re
from pathlib import Path


EXAMPLES = [
    {
        "instruction": "解释 RAG 的核心流程",
        "answer": "RAG 的核心是先把问题用于检索外部知识，再把相关上下文交给模型生成答案。",
    },
    {
        "instruction": "解释 Agent 工具调用为什么要做确认",
        "answer": "因为模型输出不等于可信执行计划，确认步骤可以拦截删除、支付、发消息等高风险动作。",
    },
    {
        "instruction": "解释 LoRA 为什么省显存",
        "answer": "LoRA 冻结原模型参数，只训练小规模低秩矩阵，因此训练参数量和优化器状态都更少。",
    },
]


def rough_token_count(text: str) -> int:
    """A rough estimator: Chinese chars and English words are counted separately."""
    return len(re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9_]+", text))


def to_chat_record(example: dict[str, str]) -> dict[str, list[dict[str, str]]]:
    return {
        "messages": [
            {"role": "system", "content": "你是一个准确、简洁的大模型面试教练。"},
            {"role": "user", "content": example["instruction"]},
            {"role": "assistant", "content": example["answer"]},
        ]
    }


def main() -> None:
    out_dir = Path(__file__).parent
    dataset_path = out_dir / "sft_dataset.jsonl"
    config_path = out_dir / "lora_config.json"

    records = [to_chat_record(item) for item in EXAMPLES]
    with dataset_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    token_total = sum(rough_token_count(message["content"]) for record in records for message in record["messages"])
    config = {
        "method": "LoRA",
        "base_model": "choose-a-small-instruct-model-for-your-machine",
        "r": 8,
        "alpha": 16,
        "dropout": 0.05,
        "target_modules": ["q_proj", "v_proj"],
        "estimated_training_tokens": token_total,
        "note": "This is a config draft for learning; real training needs a framework such as PEFT/Transformers.",
    }
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote {dataset_path}")
    print(f"Wrote {config_path}")
    print(f"Rough token count: {token_total}")


if __name__ == "__main__":
    main()

