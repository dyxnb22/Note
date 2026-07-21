#!/usr/bin/env python3
"""Conceptual estimators for dense vs MoE LLMs and KV cache growth."""

from __future__ import annotations


BYTES_PER_DTYPE = {
    "fp32": 4,
    "bf16": 2,
    "fp16": 2,
    "int8": 1,
    "int4": 0.5,
}


def params_memory_gb(params_billion: float, dtype: str = "bf16") -> float:
    return params_billion * 1_000_000_000 * BYTES_PER_DTYPE[dtype] / 1024**3


def kv_cache_gb(
    layers: int,
    context_tokens: int,
    kv_heads: int,
    head_dim: int,
    dtype: str = "bf16",
    batch_size: int = 1,
) -> float:
    # K and V are both cached, so multiply by 2.
    bytes_used = batch_size * layers * context_tokens * kv_heads * head_dim * 2 * BYTES_PER_DTYPE[dtype]
    return bytes_used / 1024**3


def main() -> None:
    print("Dense model parameter memory:")
    for params in [1.5, 7, 32, 70]:
        print(f"  {params:>4}B bf16 weights ~= {params_memory_gb(params):6.2f} GB")

    print("\nMoE intuition using DeepSeek-like public numbers:")
    total_params = 671
    activated_params = 37
    print(f"  Total parameters:     {total_params}B")
    print(f"  Activated per token:  {activated_params}B")
    print(f"  bf16 total weights:   {params_memory_gb(total_params):.2f} GB")
    print(f"  bf16 active compute:  roughly comparable to {activated_params}B active params per token")

    print("\nKV cache growth example:")
    for context in [4096, 32768, 128000]:
        cache = kv_cache_gb(layers=32, context_tokens=context, kv_heads=8, head_dim=128)
        print(f"  context={context:>6} tokens -> KV cache ~= {cache:6.2f} GB")

    print("\nTakeaway:")
    print("  MoE reduces active computation per token, while attention/KV design matters a lot for long context inference.")


if __name__ == "__main__":
    main()

