# LLM 基础

本页负责模型原理正文；按题目复习见 [AI 面试题库](./面试题库/README.md)。Provider、Tool、State、RAG 应用和 Agent Loop 进入 [Agent 面试题库](../Agent面试题库/README.md)。

这篇文档解决一个问题：**作为 AI 应用工程师，你需要理解 LLM 到底是怎么工作的**。

不是为了训练模型，而是为了：
- 理解模型能做什么、不能做什么
- 做出合理的系统设计决策
- 在面试中清楚解释 tokenization、generation、alignment、fine-tuning

## 配套实践

| 主题 | 实践入口 |
|---|---|
| Token、Transformer 与注意力 | [self_attention_demo.py](./实践/llm_learning/00_transformer_foundation/project/self_attention_demo.py) |
| SFT、LoRA 与推理 | [prepare_sft_dataset.py](./实践/llm_learning/05_finetune_and_inference/project/prepare_sft_dataset.py) |
| MoE、MLA 与 KV Cache 估算 | [architecture_budget_estimator.py](./实践/llm_learning/07_open_llm_deepseek_study/project/architecture_budget_estimator.py) |
| DPO 与推理模型 | [tiny_dpo_loss.py](./实践/llm_learning/09_alignment_reasoning_research/project/tiny_dpo_loss.py) |

实践代码用于建立直觉和验证流程；模型规格、API 限制和训练配置仍应以具体 Provider/框架文档为准。

---

## 1. 从文本到 Token

### Tokenization 是什么

模型不直接处理字符，也不处理单词，而是处理 **token**。

```
"I love Hong Kong" → ["I", " love", " Hong", " Kong"]
"不可思议" → ["不", "可思", "议"]（根据词表不同）
"ChatGPT" → ["Chat", "G", "PT"]
```

主流方法是 **BPE（Byte-Pair Encoding）**：从字符出发，不断合并高频字符对，直到达到词表大小。

### 关键数字感知

> 这里的 token 比例、词表大小、Context Window 和模型名称只用于建立数量级直觉，不是永久不变的产品规格。实际开发前请按具体模型和日期核对 Provider 文档。

- GPT-4 词表约 100K token
- 英文大约 1 token ≈ 0.75 词
- 中文约 1 个汉字 = 1-2 token（效率比英文低）
- 1K token ≈ 750 英文词 ≈ 500 中文字

### 为什么 Tokenization 对工程重要

1. **成本计量单位**：API 按 token 计费，不按字符或词
2. **Context Window 以 token 计**：128K token ≠ 128K 汉字
3. **数字、代码的 token 效率**：`127.0.0.1` 可能被切成 5-7 个 token
4. **奇怪的 token 边界可能引发问题**：如 `2024-01-01` 被切断导致日期理解偏差

---

## 2. 从 Token 到 Embedding

每个 token 被映射为一个高维向量（**embedding**），向量空间里语义相近的词距离近。

```
token ID → embedding 层 → 浮点向量（如 d=4096）
```

**余弦相似度**是衡量语义相近度的常用方法：

```python
similarity = dot(a, b) / (norm(a) * norm(b))
## 值域 [-1, 1]，越接近 1 越相似
```

RAG 的向量检索、语义搜索的基础都是 embedding 相似度。

---

## 3. Transformer 核心机制

### Self-Attention：每个 token 从其他 token 那里收集信息

直觉：序列里的每个 token，根据当前上下文，重新计算自己应该是什么表示。

```
Q（Query）= 我想找什么信息
K（Key）  = 我有什么信息可被找到
V（Value）= 真正被取走的信息

Attention(Q, K, V) = softmax(QK^T / √d_k) · V
```

面试回答结构：
1. 输入 token 的 embedding
2. 三次线性变换分别得到 Q、K、V
3. Q 和所有 K 做点积，除以 √d 避免数值过大，softmax 得到注意力权重
4. 用权重对 V 做加权求和，得到新的表示
5. Multi-Head Attention 让模型从多个子空间同时学习不同类型的关系

### 为什么是 Decoder-only

主流生成式 LLM（GPT、Claude、Llama 等）都是 Decoder-only 架构：

```
输入前文 token → 预测下一个 token → 把新 token 接回去 → 继续预测
```

**Causal Mask**：训练时每个 token 只能看到它自己及它左边的 token，防止"未来信息泄露"。

### KV Cache

推理时，历史 token 的 K 和 V 可以缓存，不用每次重新计算：

```
没有 KV Cache：每步生成都重算所有历史 token 的 K/V → O(n²) 复杂度
有 KV Cache：只计算新 token 的 K/V，历史的复用 → 显著加速
```

**工程意义**：长 context 场景下 KV Cache 是内存和延迟的主要来源，是 context window 有硬限制的原因之一。

---

## 4. 生成过程与采样参数

### Autoregressive 生成

```
[System + User] → Logits（词表大小的分数）→ Softmax → 概率分布 → 采样 → next token → 接回去 → 继续
```

### 关键采样参数

| 参数 | 作用 | 典型值 | 工程建议 |
|------|------|--------|----------|
| `temperature` | 平滑/锐化概率分布。越高越随机，越低越确定 | 0-2 | 结构化输出用 0；创意类用 0.7-1.0 |
| `top_p` | 从累积概率达到 p 的 token 中采样（nucleus sampling） | 0.9-0.95 | 比 temperature 更平滑 |
| `top_k` | 只从概率最高的 k 个 token 中采样 | 40-100 | 较少单独使用 |
| `max_tokens` | 最大生成 token 数 | 视任务 | 不设或设太大 = 浪费 cost |
| `stop` | 遇到这些 token 立即停止 | `["\n", "###"]` | 结构化场景常用 |

### temperature=0 的实际含义

并不是完全确定性，而是 argmax（总取概率最高的 token）。相同 prompt + temperature=0 通常得到相同结果，但不是保证（模型服务可能有并发差异）。

---

## 5. 预训练 → SFT → RLHF → 对齐

### 预训练（Pretraining）

在海量文本上做 next-token prediction。

```
目标：给定前文，预测下一个 token
数据：互联网文本、书籍、代码等
结果：模型学到语言结构、世界知识、推理模式
```

这个阶段产生的模型叫 **Base Model**，它很强但不听指令。

### 指令微调（SFT，Supervised Fine-tuning）

在 `(instruction, response)` 对上继续训练，让模型学会"怎么按指令格式回答"。

### RLHF（Reinforcement Learning from Human Feedback）

1. 训练一个 **Reward Model**：人类对不同回答打分
2. 用强化学习（PPO）让生成模型最大化 Reward Model 的分数
3. 同时保持与预训练分布不要偏离太远（KL 散度约束）

现代替代方案：**DPO（Direct Preference Optimization）**——直接用偏好对数据训练，不需要显式 RM。

### 对齐的实际含义

对齐 ≠ 模型更聪明，而是：拒绝有害请求、诚实标注不确定性、遵从人类意图而不是字面指令。

**工程含义**：对齐过的模型有 safety filter，在特定话题上会拒绝，这是设计，不是 bug。

---

## 6. Fine-tuning / RAG / Prompt 三种适配路径

| 方法 | 解决什么问题 | 代价 | 适合场景 |
|------|-------------|------|---------|
| **Prompt 工程** | 调整模型行为、给上下文 | 几乎无额外成本 | 大多数任务的第一选择 |
| **RAG** | 注入外部知识 / 私有数据 | 检索系统工程成本 | 知识库问答、私有文档 |
| **Fine-tuning (LoRA/QLoRA)** | 改变模型风格/专业能力/输出格式 | GPU + 数据标注成本高 | 特定领域、风格一致性要求极高 |
| **Full fine-tuning** | 从根本上改变模型行为 | 极高 | 大厂才做 |

**选择顺序**：先 Prompt → 不够再 RAG → 仍不够再 Fine-tuning。

### LoRA 原理简介

不修改预训练权重，而是在部分层旁边添加低秩矩阵：

```
W_new = W_pretrained + A · B   （A 和 B 是低秩矩阵，rank << d）
训练时只更新 A 和 B
```

优势：参数量小（相比全参数减少 90%+）、显存需求低。
限制：只影响有 adapter 的层；不能根本改变模型知识，只能微调行为。

---

## 7. Hallucination：为什么发生，怎么缓解

### 为什么 LLM 会幻觉

LLM 的本质是：**在训练分布上预测最可能的下一个 token**，不是检索事实。

当模型对某个问题没有可靠知识时，它仍然会生成"听起来合理"的内容。

具体原因：训练数据里该知识不存在或冲突；问题涉及具体数字/日期/人名；prompt 隐含了错误前提；长 context 中早期信息被"遗忘"。

### 缓解策略

| 策略 | 原理 | 适用场景 |
|------|------|---------|
| RAG | 把正确事实放进 context | 知识库问答 |
| 要求模型引用来源 | 迫使模型定位到 context 里的内容 | 文档问答 |
| Grounding check | 让另一个模型验证回答是否有原文支持 | 高准确率场景 |
| temperature=0 | 减少随机性（不能消除幻觉） | 结构化任务 |
| 结构化输出 | 限制输出格式，减少自由发挥空间 | 信息抽取 |

**关键认知**：幻觉不是可以完全消除的 bug，而是这类模型的固有属性。系统设计要把它当成已知约束来应对。

---

## 8. Context Window 与长文档处理

### Context Window 不是固定知识

不同模型、版本和接口支持的窗口会变化，运行前应查 Provider 官方模型页，并把实际限制写入项目配置。不要根据系列名称猜窗口，也不要把“最大可输入 token”误当作长文档都能被同等可靠利用。

### 长 Context 的实际问题

- **Lost in the middle**：模型对 context 开头和结尾更敏感，中间的内容容易被忽略
- **成本线性增长**：token 越多，每次调用越贵
- **延迟增长**：TTFT（Time to First Token）随 context 增长

### 处理策略

| 策略 | 原理 | 代价 |
|------|------|------|
| 截断（固定窗口） | 只取最近 N token | 可能丢失重要信息 |
| 摘要压缩 | 让 LLM 将历史压缩成摘要 | 会损失细节 |
| RAG 替代全文 | 只检索相关片段放入 context | 需要好的检索 |
| 重要信息置顶 | 把最关键的内容放 system prompt | 手动设计成本 |

---

## 9. 推理优化基础

| 技术 | 作用 | 工程意义 |
|------|------|---------|
| **量化（Quantization）** | 用 INT8/INT4 替代 FP32，减少显存和计算量 | 推理速度快，精度略降 |
| **KV Cache** | 缓存历史 token 的 K/V，避免重算 | 长 context 推理的关键优化 |
| **Continuous Batching** | 同时处理多个请求，利用 GPU 并行 | vLLM 等推理框架的核心 |
| **Speculative Decoding** | 小模型草稿 + 大模型验证 | 降低延迟 |
| **Prompt Caching** | 缓存 system prompt 的 KV | 重复 system prompt 场景省 cost |

---

## 9.1 Attention 的最小数值检查（Python 标准库）

先用小矩阵验证公式，再依赖深度学习框架。下面的实现只为建立直觉，不包含训练、mask 和高效矩阵库。

```python
import math


def attention(query, key, value):
    # QK^T 衡量每个 Query 对各 Key 的相关性。
    scores = [
        [sum(q_i * k_i for q_i, k_i in zip(q, k)) / math.sqrt(len(q)) for k in key]
        for q in query
    ]
    weights = []
    for row in scores:
        # 每行独立 softmax；减去最大值避免指数溢出。
        maximum = max(row)
        exps = [math.exp(score - maximum) for score in row]
        total = sum(exps)
        weights.append([item / total for item in exps])
    return [
        [sum(weight * value_j for weight, value_j in zip(row, column)) for column in zip(*value)]
        for row in weights
    ]
```

验证时检查每行权重和为 1、输入维度不匹配会明确失败，并与框架实现对同一随机输入做数值对照。教学实现不能直接用于生产推理；生产还要处理 causal mask、padding、精度、批量和显存。

## 10. 面试高频问法与回答模板

**Q：解释 Self-Attention 的工作原理**

> Self-Attention 让序列中的每个 token 能够根据当前上下文动态地从其他 token 那里收集信息。具体来说，输入经过三次线性变换得到 Q、K、V。Q 和所有 K 做点积计算相似度，除以 √d 做缩放防止梯度消失，再过 softmax 得到注意力权重，最后对 V 做加权求和。Multi-Head Attention 同时在多个子空间做这个过程，让模型能从不同角度理解 token 关系。

**Q：为什么 LLM 会幻觉，有哪些缓解方法**

> LLM 的本质是 token 预测器，不是事实检索系统。当遇到训练数据里缺失的知识时，它仍会生成看起来合理的内容。缓解策略主要有三类：一是 RAG，把正确事实放进 context；二是约束输出，让模型引用原文、声明不确定性；三是系统层验证，用 grounding check 或事实核验步骤。没有办法完全消除，要在系统设计层面把它当成已知约束处理。

**Q：Fine-tuning、RAG、Prompt Engineering 怎么选**

> 这三种方法解决不同层次的问题。Prompt Engineering 最便宜，先用；RAG 解决私有知识和事实接地问题；Fine-tuning 改变模型的风格、格式偏好或专业能力。选择顺序是先 Prompt，不够再 RAG，仍不够再考虑 Fine-tuning。Fine-tuning 的成本和复杂度远高于其他两种，不要轻易跳到它。

**Q：KV Cache 是什么，对工程有什么影响**

> KV Cache 是推理时缓存历史 token 的 Key 和 Value，避免每步生成都重算。工程含义：长 context 的主要内存瓶颈来自 KV Cache；context window 有硬上限的原因之一是 KV Cache 的内存消耗随序列长度线性增长；Prompt Caching 本质是把 system prompt 的 KV Cache 持久化跨请求复用。

---

## 来源与验证边界

- Vaswani et al., *Attention Is All You Need*：Transformer 与 Self-Attention 的原始论文。
- Hugging Face Course：Tokenization、Transformer、微调和推理的实践入口。
- PyTorch 文档：张量、Autograd、训练和推理 API。

模型结构、上下文长度、量化能力和 Provider 参数会随版本变化；本文的公式和教学代码用于建立机制直觉，具体模型规格与 API 以锁定版本文档和本地实验为准。

## 何时回到本页

当当前项目需要解释 tokenization、embedding、attention、generation、采样参数、对齐方法、幻觉、KV Cache，或需要在 Prompt、RAG 和 Fine-tuning 之间选型时，再打开对应章节。做 Agent 应用不需要把这些主题预先全部复习一遍。
