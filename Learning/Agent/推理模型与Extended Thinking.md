---
type: guide
status: mature
last_verified: 2026-07-30
---

# 推理模型与 Thinking 工程

这篇文档解决一个问题：**如何把模型的额外推理能力用于 Agent，并在质量、延迟、成本、工具连续性和可观测性之间做取舍**。

Provider 会用 reasoning、thinking、effort、mode 或 budget 等不同字段暴露能力。本页以稳定工程原则为主，以当前 Anthropic Thinking 和 OpenAI Responses 为接口例子；实际模型支持情况必须从[版本与来源](./版本与来源.md)重新核对。

## 1. 不要把可见 Thinking 当成原始思维链

推理模式允许模型在给出最终答案或决定下一次工具调用前进行额外计算。对应用而言，通常能观察到的是：最终文本、工具动作、推理 token 用量，以及 Provider 选择返回的推理摘要或加密状态。

```text
用户输入
  ↓
模型内部推理（可能不返回原文）
  ↓
推理摘要 / 加密状态（视 Provider 与配置而定）
  ↓
文本或工具调用
```

Anthropic 当前文档明确说明，`thinking` block 中可见文本是**推理摘要**，不是原始 chain of thought；最新模型还可能默认只返回空摘要和用于连续性的 `signature`。因此不要把摘要用于审计“模型究竟如何想”，也不要把它当成事实证据。真正可审计的仍是输入、动作、工具结果、最终结论和外部证据。

## 2. 两种控制方式

### Adaptive thinking：当前优先路径

支持 adaptive thinking 的 Claude 模型由模型结合任务难度决定是否思考及思考深度，再用 `effort` 调节整体投入。模型 ID 从配置读取，不写死在业务代码中：

```python
import os
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model=os.environ["ANTHROPIC_MODEL"],
    max_tokens=16000,
    thinking={"type": "adaptive", "display": "omitted"},
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": "分析这个故障并给出可验证的根因假设"}],
)
```

`display: "omitted"` 只是不返回可读摘要，不会取消内部推理或降低推理计费。需要开发调试时可在支持的模型上使用 `display: "summarized"`，但不要默认向最终用户展示。

### Manual extended thinking：旧模型兼容路径

部分旧模型只支持固定预算：

```python
thinking={"type": "enabled", "budget_tokens": 8000}
```

当前 Anthropic 文档将这种模式列为 legacy：在 4.6 系列上已弃用，在 4.7 及以后模型上会被拒绝。对仍支持它的模型，`budget_tokens` 最低为 1024、通常要小于 `max_tokens`，并且是目标预算而非严格用量。迁移时移除 `budget_tokens`，改为 adaptive thinking，并用 `output_config.effort` 调节投入。

OpenAI Responses 则使用 Provider 自己的 reasoning 配置；例如 GPT-5.6 的 `reasoning.effort` 与 `reasoning.mode` 是独立控制项。不要把 Anthropic 字段机械翻译到 OpenAI 请求中。

## 3. 成本与延迟模型

Thinking 的主要代价不是“多一个字段”，而是更多输出侧计算、首 token 延迟和长任务尾延迟。Anthropic 将内部 thinking token 计入输出 token，即使摘要被省略也照常计费；当前响应可通过 `usage.output_tokens_details.thinking_tokens` 观察内部推理用量。

评估时至少记录：

| 维度 | 记录方式 |
| --- | --- |
| 任务成功 | 固定评测集、明确通过条件 |
| 推理投入 | Provider 返回的 reasoning/thinking token 字段 |
| 延迟 | 首文本 token、总耗时、P95/P99 |
| 工具效率 | 调用次数、重复调用、无效调用、失败恢复 |
| 总成本 | 输入、缓存、推理、文本输出和工具成本分别计算 |

不要预设“最高 effort 一定最好”。从普通或中等配置建立基线，只在代表性任务上提高投入，寻找质量收益开始饱和的位置。

## 4. Streaming 不是可选的性能装饰

复杂推理可能长时间没有最终文本。流式处理能避免连接层无反馈，也能分别展示任务状态和最终答案。若 `display` 为 `omitted`，应用通常只会收到 thinking block 的签名而没有 `thinking_delta`；这不代表模型没有思考。

```pseudocode
with client.messages.stream(..., thinking={"type": "adaptive", "display": "omitted"}) as stream:
    for event in stream:
        update_latency_metrics(event)
        if event is text_delta:
            send_to_user(event.text)
```

用户界面应显示“正在分析/正在调用工具”等诚实状态，不伪装成逐字展示模型内部思维。

## 5. Tool Use 中的连续性

对 Anthropic Messages API，在一次工具调用回合中返回工具结果时，必须把模型此前生成的 `thinking` 和 `tool_use` blocks **完整、原样**传回。签名承担连续性，修改、重排或只保留可见摘要都可能导致请求失败或推理断裂。

```pseudocode
messages.append({"role": "assistant", "content": response.content})
messages.append({"role": "user", "content": tool_results})
next_response = client.messages.create(messages=messages, ...)
```

这个要求是 Provider 协议，不是所有 Agent 的普遍消息格式。OpenAI Responses 使用 typed Items，并通过 `previous_response_id`、Conversations 或手工回传 output Items 维持状态；实现时分别遵守对应协议。

无论 Provider 如何设计，都应保证：工具副作用幂等、回放不会重复执行危险动作、超时可取消、失败可定位，且高风险动作在模型推理之外还有确定性的权限与审批门禁。

## 6. 什么时候值得开启

适合：多假设诊断、复杂代码分析、证明与算法设计、长链规划、需要结合多次工具结果的任务。通常不值得：简单分类、字段提取、格式转换、固定 FAQ 和延迟极敏感的高吞吐路径。

决策流程：

1. 先定义普通调用的质量、延迟和成本基线。
2. 只对失败主要来自“缺少多步推理”的任务开启 thinking。
3. 比较不同 effort / mode，而不是凭感觉选最高档。
4. 若瓶颈来自缺数据、坏工具、错误 schema 或权限失败，先修系统；增加推理不会补齐缺失证据。
5. 用路由按任务难度选择配置，并保留降级与超时策略。

## 7. 常见错误

- 把 thinking 摘要当成原始思维链或合规审计记录。
- 把 legacy `budget_tokens` 示例当成所有当前 Claude 模型的接口。
- 在工具回合中删除、修改或重排必须回传的 thinking blocks。
- 只看平均质量，不记录 reasoning token、尾延迟和工具调用放大。
- 对简单任务全部开启最高 effort，或用“多想”掩盖数据、工具和流程缺陷。
- 在不同 Provider 间复用同一消息格式和参数名。

## 8. 评测练习

选 20 个包含简单、困难和工具型任务的小数据集，对普通、低/中/高推理投入分别记录通过率、首 token、总耗时、推理 token、工具次数和成本。然后写出一条可执行路由规则，并用留出集验证它没有只记住样本。

## 官方来源

- [Anthropic Thinking 概览](https://platform.claude.com/docs/en/build-with-claude/thinking)
- [Anthropic Extended Thinking（legacy 与迁移）](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
- [OpenAI Reasoning 指南](https://developers.openai.com/api/docs/guides/reasoning)
- [OpenAI 最新模型指南](https://developers.openai.com/api/docs/guides/latest-model)

核对日期：2026-07-30。模型支持、默认值、用量字段和计费方式均需在上线前重新核验。

## 导航与关联

- [模块入口：AI Agent 工程知识库](./README.md)
- 同一路线：[Agent 运维与事故响应](./Agent运维与事故响应.md) · [模型行为与工具调用训练](./模型行为与工具调用训练.md)

`#agent #reasoning #thinking #evaluation`
