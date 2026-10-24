# LLM 基础

LLM 把文本编码成 Token 序列，通过向量表示和 Transformer 计算上下文，再逐步生成后续 Token。训练改变参数，推理使用已经确定的参数；采样、上下文长度和推理实现共同影响输出行为与成本。

从这个计算过程出发，可以进一步理解模型何时需要外部知识、为何会出现无依据回答，以及适配方法各自改变了什么。检索与业务接入见[模型与应用边界](./专题_模型与应用边界.md)，执行、工具和状态见[Agent 系统全景](../Agent/00_01_Agent系统全景.md)。

## 从文本到 Token

### 词表与 Token 序列

Tokenizer 按词表和编码规则把文本转换为 Token ID。一个 Token 可能对应一个词、词的一部分、字符或字节片段，具体划分取决于所用 tokenizer。

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

## 从 Token 到 Embedding

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

## Transformer 核心机制

### Self-Attention：每个 token 从其他 token 那里收集信息

直觉：序列里的每个 token，根据当前上下文，重新计算自己应该是什么表示。

```
Q（Query）= 我想找什么信息
K（Key）  = 我有什么信息可被找到
V（Value）= 真正被取走的信息

Attention(Q, K, V) = softmax(QK^T / √d_k) · V
```

一次自注意力计算按以下过程展开：
1. 输入 token 的 embedding
2. 三次线性变换分别得到 Q、K、V
3. Q 和所有 K 做点积，除以 √d 避免数值过大，softmax 得到注意力权重
4. 用权重对 V 做加权求和，得到新的表示
5. Multi-Head Attention 让模型从多个子空间同时学习不同类型的关系

### 位置表示与 RoPE

注意力根据内容计算 token 间关系，还需要位置信息区分顺序。绝对位置把位置表示加入输入；相对位置直接刻画距离；RoPE 对 Q/K 做与位置相关的旋转，使点积包含相对位置信息。不同模型可能使用不同方案。

位置表示不保证任意长文本都有效：训练长度、外推方法、注意力成本和 KV Cache 容量仍会约束效果。更完整的结构见 [注意力与 Transformer](./DeepLearning/09_注意力与Transformer/注意力与Transformer.md)。

### Encoder 与 Decoder 的任务边界

| 架构 | 信息访问方式 | 常见任务 |
|---|---|---|
| Encoder-only | 在给定输入中双向聚合上下文 | 表示、分类、匹配 |
| Decoder-only | 用因果掩码根据前缀预测后续 token | 自回归生成 |
| Encoder-Decoder | 编码输入，再由解码器关注编码结果和输出前缀 | 翻译、摘要与条件生成 |

这些是结构及常见用途，任务也可通过不同建模方式实现，不能把用途当成结构的唯一限制。

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

### MoE：稀疏激活与路由

MoE（Mixture of Experts）把每层的单个 FFN 换成一组专家和一个路由器。每个 token 只激活 top-k 个专家：

```
总参数：N 个专家的全部权重（决定显存占用）
激活参数：每个 token 实际用到的 k 个专家（决定算力消耗）
```

- **路由（Router）**：对 token 打分选 top-k 专家，通常带 softmax/归一化和权重加权。
- **专家容量（Expert Capacity）**：限制单个专家一次最多接收多少 token，超出的 token 被丢弃或走残旁路，防止热点专家溢出。
- **负载均衡（Load Balancing）**：辅助损失鼓励 token 均匀分布到各专家，避免少数专家过载、其余闲置；训练不稳定常与路由坍缩（token 挤向少数专家）有关。
- **共享专家（Shared Expert）**：部分实现额外挂一个始终激活的专家承载通用知识，减少路由专家间的冗余。

**工程含义**：MoE 用更低算力买到更大总参数，代价是显存按总参数付、专家并行引入 all-to-all 通信、批处理和调度复杂度上升。能力不等于"参数量 ÷ 激活比"的线性换算，要以目标任务评测为准。

---

## 生成过程与采样参数

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

## 预训练 → SFT → RLHF → 对齐

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

### RL 算法族：PPO 与 GRPO

PPO 在 RLHF 里同时维护四个模型：策略（actor）、价值（critic）、奖励（reward）和参考（reference，用于 KL 约束）。critic 估计优势基线，clip 目标限制单步更新幅度，训练稳但显存和计算开销大。

GRPO（Group Relative Policy Optimization）用"组内相对奖励"替代 critic：

```
同一 prompt 采样 G 个回答 → 各自打分
优势 = (r_i − 组均值) / 组标准差
用 PPO 式的裁剪目标 + KL 约束更新策略
```

- 省掉 value model，显存和训练成本明显下降，适合奖励可程序化验证的任务（RLVR：数学、代码、格式约束）。
- 代价：基线质量取决于组大小 G；奖励稀疏或组内得分接近时，优势估计方差大，需要加大 G 或改奖励设计。
- 与 DPO 的关系：DPO 是离线、无 RL 循环的偏好优化；GRPO 是在线 RL，仍需要采样和验证器。

### 熵坍塌：策略分布过度集中

RL 训练后期策略熵快速下降，模型几乎总输出同一模式，探索与多样性消失。常见诱因：奖励被"钻空子"（reward hacking）、KL 约束太弱、数据或目标覆盖不足，正确 token 的概率被风格化套路挤占。

| 环节 | 做法 |
|------|------|
| 识别 | 监控策略熵曲线；输出多样性指标（distinct-n、重复率）；pass@k 与 pass@1 的差距拉大；长尾/新题成功率退化 |
| 缓解 | 熵奖励/熵正则；加强 KL 到参考模型的约束；扩数据与任务覆盖；修奖励定义，减少可被套路刷分的空间 |

**关键认知**：熵不是越低越好，也不是越高越好——训练要在"收敛到高分模式"和"保留探索与泛化"之间取舍；只看平均 reward 或 loss 会错过坍塌，必须看分布层面的指标。

### DPO 与偏好对

DPO 使用被偏好与被拒绝的回答对，直接优化策略相对参考策略的偏好关系，通常不需要另外拟合一个显式奖励模型或执行在线强化学习循环。它仍依赖偏好数据覆盖和标注质量，不能据流程简化推断一定优于其他方法。

预训练学习通用分布，SFT 用目标示例教任务与格式，偏好优化调整回答选择倾向。每一阶段都需要固定基座、数据、模板和评测切片，检查能力遗忘、事实性、格式和安全。

### 对齐的实际含义

对齐 ≠ 模型更聪明，而是：拒绝有害请求、诚实标注不确定性、遵从人类意图而不是字面指令。

**工程含义**：对齐过的模型有 safety filter，在特定话题上会拒绝，这是设计，不是 bug。

---

## Fine-tuning / RAG / Prompt 三种适配路径

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

## Hallucination：为什么发生，怎么缓解

### 为什么 LLM 会幻觉

模型根据上下文预测后续Token的概率分布。生成过程本身不负责核验每个陈述是否与外部事实一致。

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

系统需要评估无依据回答，并为重要结论保留来源核对和失败处理。减少采样随机性或约束格式，不能代替事实检查。

---

## Context Window 与长文档处理

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

## 推理优化基础

| 技术 | 作用 | 工程意义 |
|------|------|---------|
| **量化（Quantization）** | 用 INT8/INT4 替代 FP32，减少显存和计算量 | 推理速度快，精度略降 |
| **KV Cache** | 缓存历史 token 的 K/V，避免重算 | 长 context 推理的关键优化 |
| **Continuous Batching** | 同时处理多个请求，利用 GPU 并行 | vLLM 等推理框架的核心 |
| **Speculative Decoding** | 小模型草稿 + 大模型验证 | 降低延迟 |
| **Prompt Caching** | 缓存 system prompt 的 KV | 重复 system prompt 场景省 cost |

### 量化：GPTQ 与 AWQ 在做什么

权重量化不是简单四舍五入（RTN）。两种主流后训练量化（PTQ）思路：

| 方法 | 核心思路 | 特点 |
|------|---------|------|
| **GPTQ** | 逐层量化，用近似二阶信息（Hessian）估计量化误差，并把误差"补偿"到未量化的权重上 | 压缩率高的同时控制精度损失；需要校准数据 |
| **AWQ** | 用激活统计找出对输出影响大的"显著通道"，量化前对通道做缩放保护它们 | 不做反向传播，对激活分布敏感的模型更稳；常配合混合精度保留关键层 |

两者都依赖校准数据分布、位宽/分组粒度（如 g128）和 kernel 支持；换模型、换数据分布后结论不能照搬。量化精度还要和 KV Cache 量化、kernel 融合、batch 大小一起看——权重显存降了不代表整体延迟和吞吐按比例改善，必须用目标任务的困惑度、格式遵从和长尾表现验证。

### 投机解码：草稿-验证循环

小 Draft 模型一次提出 k 个 token，大 Target 模型一次前向并行验证这 k 个 token，再用修改后的拒绝采样决定接受多少——数学上保证最终输出分布与 Target 单独生成一致：

```
Draft 连猜 k 个 token → Target 并行验证 → 接受前缀 + 从首个被拒位置用 Target 修正
接受率越高，一次 Target 前向"产出"的 token 越多
```

- 收益来源：把逐 token 的 Target 串行生成，变成"一次验证多个 token"，生成阶段延迟下降。
- 收益不明显的情况：Draft 与 Target 分布差异大（接受率低）、输出很短、请求主要耗在 prefill 或工具等待、大 batch 服务下验证并行度已被占用。
- 工程上要测：接受率、端到端 P95、显存开销（多养一个 Draft/多份缓存），而不是只看 Decode 吞吐。

---

## Attention 的最小数值检查（Python 标准库）

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

## 从模型机制到应用设计

Tokenizer 决定输入计量，注意力与位置表示决定上下文处理，训练与适配决定任务行为，采样和推理实现共同影响质量、延迟与成本。应用还需要检索、工具执行、状态和权限，这些职责由程序承担。

模型与应用的连接见 [模型与应用边界](./专题_模型与应用边界.md)。Agent 的执行过程、工具合同和恢复机制继续见 [Agent 系统全景](../Agent/00_01_Agent系统全景.md)。
