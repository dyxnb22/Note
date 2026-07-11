# 推理模型与 Extended Thinking

这篇文档解决一个问题：**什么是推理模型（Reasoning Model），如何在 Agent 里正确使用 Extended Thinking，以及它和普通 LLM 调用的本质区别**。

2025 年以来，Claude 3.7 Sonnet 和 Claude 4 系列让"让模型先想再说"成为主流工程选项。

---

## 1. 什么是 Extended Thinking

普通调用：模型直接输出 → 你看到的就是全部。

Extended Thinking：模型先在内部生成一段"思考链"（thinking tokens），再基于这段思考给出最终回答。

```
[用户输入]
    ↓
[Thinking Block]   ← 模型内部推理，可以很长
    ↓
[Text Block]       ← 最终回答，基于 thinking 推导出来
```

**关键认知**：thinking tokens 是模型真正的推理过程，不是 system prompt 里的 chain-of-thought 提示词技巧。模型自主决定在 thinking 里写什么，你无法控制也无法注入。

---

## 2. API 用法

### 基础调用

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000,   # 最多允许用多少 token 来思考
    },
    messages=[{"role": "user", "content": "解决这道数学竞赛题：..."}],
)

for block in response.content:
    if block.type == "thinking":
        print("[THINKING]", block.thinking[:200], "...")   # 内部推理
    elif block.type == "text":
        print("[ANSWER]", block.text)                      # 最终回答
```

### budget_tokens 的含义

```python
# budget_tokens = 允许用于 thinking 的最大 token 数
# 实际消耗可能更少（模型认为不需要那么多）
# 最小值：1024
# 推荐范围：5000-16000（复杂任务），1024-3000（简单分类）

thinking={"type": "enabled", "budget_tokens": 8000}

# 关闭 thinking（等同于不传）
thinking={"type": "disabled"}
```

### 读取 response

```python
response = client.messages.create(...)

# response.content 是 block 列表，顺序固定：thinking → text
# 有时可能有多个 text block（工具调用场景）

thinking_text = ""
final_answer = ""

for block in response.content:
    if block.type == "thinking":
        thinking_text = block.thinking
    elif block.type == "text":
        final_answer += block.text
```

---

## 3. 成本结构

Extended Thinking 的 token 计费和普通调用**不同**：

```
普通调用：
  input_tokens  × 输入单价
  output_tokens × 输出单价

Extended Thinking：
  input_tokens         × 输入单价      ← 你发给模型的内容
  thinking_tokens      × 输出单价      ← 模型生成的思考过程（按输出计费！）
  output_tokens        × 输出单价      ← 最终回答

usage.input_tokens    → 你的 prompt
usage.output_tokens   → thinking_tokens + text_tokens（合计）
```

**注意**：`budget_tokens` 是上限，不是必须消耗的量。你设 budget=16000，模型只用了 3000，你只付 3000。

```python
# 读取实际消耗
print(response.usage.input_tokens)    # prompt token
print(response.usage.output_tokens)   # thinking + text 总计
# Anthropic API 目前不分别暴露 thinking vs text token 数
# 可以通过计算 len(thinking_text) 估算
```

**成本估算**（claude-sonnet-4-6，2026 年参考）：

| 场景 | budget_tokens | 典型实际 thinking | 额外成本 |
|------|-------------|-----------------|---------|
| 简单推理 | 2000 | 500-800 | 低 |
| 数学证明 | 8000 | 4000-7000 | 中 |
| 复杂多步规划 | 16000 | 10000-15000 | 高 |

---

## 4. Streaming 与 Extended Thinking

长 thinking 必须用 streaming，否则等待时间很长且容易超时：

```python
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 8000},
    messages=[{"role": "user", "content": user_input}],
) as stream:
    current_block_type = None

    for event in stream:
        if hasattr(event, "type"):
            if event.type == "content_block_start":
                current_block_type = event.content_block.type
                if current_block_type == "thinking":
                    print("\n[thinking...]", end="", flush=True)
                elif current_block_type == "text":
                    print("\n[answer] ", end="", flush=True)

            elif event.type == "content_block_delta":
                if current_block_type == "thinking" and hasattr(event.delta, "thinking"):
                    # thinking 内容，可选择不显示给用户
                    pass
                elif current_block_type == "text" and hasattr(event.delta, "text"):
                    print(event.delta.text, end="", flush=True)
```

**工程实践**：对用户展示"正在思考..."的动画，thinking 内容通常不直接展示（太长，且是内部推理）。

---

## 5. 在 Tool Use 循环里使用（Interleaved Thinking）

Extended Thinking 和 Tool Use 组合时有特殊行为：模型的 thinking blocks **必须原样传回**下一轮，不能省略。

```python
messages = [{"role": "user", "content": "帮我分析这个代码库的问题并给出修复方案"}]

while True:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        thinking={"type": "enabled", "budget_tokens": 8000},
        tools=tools,
        messages=messages,
    )

    # 把完整的 response.content（含 thinking blocks）追加到 messages
    # 关键：不能只追加 text blocks，thinking blocks 也必须保留
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason == "end_turn":
        break

    if response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "user", "content": tool_results})
        # 下一轮继续，模型会在新的 thinking block 里回顾之前的推理
```

**为什么必须保留 thinking blocks**：模型在后续轮次里需要参考之前的推理过程，省略 thinking blocks 会导致行为不一致（模型自引用失效）。

---

## 6. 何时用 Extended Thinking

**适合场景：**

```
✓ 数学推导、逻辑证明、算法设计
✓ 多步骤规划（需要分析依赖关系再执行）
✓ 复杂代码 debug（需要假设-验证推理）
✓ 法律/合规分析（需要逐条推演）
✓ 安全漏洞分析
✓ 需要模型"自我质疑"的场景（发现第一个答案可能有问题）
```

**不适合（成本高收益低）：**

```
✗ 简单问答、FAQ
✗ 格式转换、数据提取
✗ 创意写作（thinking 对创意帮助有限）
✗ 高吞吐/低延迟场景
✗ 已经有明确 step-by-step prompt 的场景
```

### 决策树

```
任务是否需要多步推理、条件分支或自我验证？
    否 → 普通调用（省钱省时）
    是 ↓
响应质量对 budget_tokens 是否敏感？
    先用 2000 测试，再看是否需要更多
    一般规律：budget ≥ 实际问题所需思考量的 1.5x
```

---

## 7. 与 OpenAI o1/o3 的对比

| 维度 | Claude Extended Thinking | OpenAI o1/o3 |
|------|------------------------|--------------|
| thinking 可见性 | 可以读取 thinking 内容 | thinking 内容不暴露 |
| budget 控制 | `budget_tokens` 精细控制 | 只能选 low/medium/high |
| 与 tool use 结合 | 支持（interleaved thinking）| 支持（o1 有限制，o3 更完整）|
| streaming | 支持 | o1 支持，o3 支持 |
| 成本控制 | 可精细，按实际 thinking token 计费 | 按 effort 级别定价 |
| 适合场景 | 需要结合工具的复杂推理 | 纯推理、数学竞赛 |

**工程选择**：如果任务需要 tool use + 推理，Anthropic 的实现更完整（thinking blocks 在多轮 tool use 中持久化）。

---

## 8. 常见错误

```python
# 错误 1：budget_tokens 太小
thinking={"type": "enabled", "budget_tokens": 100}
# → 模型被迫在极短 thinking 里完成推理，质量下降
# 正确：最小 1024，复杂任务建议 ≥ 4000

# 错误 2：多轮对话时丢掉 thinking blocks
messages.append({
    "role": "assistant",
    "content": [b for b in response.content if b.type == "text"],  # 错！
})
# 正确：
messages.append({"role": "assistant", "content": response.content})  # 保留全部 blocks

# 错误 3：在 streaming 里漏掉 thinking delta 导致内容丢失
# thinking delta 的字段名是 event.delta.thinking（不是 .text）
# 如果你要拼接完整 thinking 内容，需要单独处理

# 错误 4：对所有任务都开 extended thinking
# 简单任务的 thinking 收益 ≈ 0，但成本 x2-x5
# 应该按任务类型路由（见 §6）
```

---

## 9. 面试高频

**Q：Extended Thinking 和普通 Chain-of-Thought prompt 有什么区别？**

> CoT prompt 是你在 system prompt 里让模型"一步步思考"，模型的推理过程出现在 output 里，直接被用户看到。Extended Thinking 是模型在 API 层面有一个单独的 thinking block，推理过程在返回给用户的 text 之前完成，thinking token 按输出计费但和最终回答分离。核心区别是：CoT 的推理过程会占用 context 窗口，Extended Thinking 的 thinking blocks 也在 context 里，但可以被模型自己在后续轮次引用，质量更稳定，也更难被 prompt injection 干扰（thinking 内容不暴露给外部）。

**Q：什么场景下 Extended Thinking 会显著提升质量？**

> 主要是需要"多假设比较"或"自我验证"的任务：数学推导（模型在 thinking 里可以试错再给最终答案）、复杂 debug（逐步缩小问题范围）、多步骤规划（先在 thinking 里排序依赖再输出计划）。对于简单问答、格式转换，thinking 基本没有帮助，反而增加成本和延迟。

**Q：budget_tokens 设多少合适？**

> 没有通用答案，需要实验。经验规则：先用 2000 跑基线，如果质量不够再加到 8000，看质量曲线是否还在提升。通常存在一个"饱和点"，超过这个点再加 budget 质量提升微乎其微。建议在 eval 集上找到这个饱和点再固定下来。复杂数学/推理题通常需要 8000-16000，一般分析任务 2000-4000 够用。
