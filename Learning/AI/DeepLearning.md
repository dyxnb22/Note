# 深度学习基础

这篇文档的定位：**从深度学习快速桥接到 LLM 工程**，能支撑理解 LLM 模型行为、读懂大部分 NLP 论文、做 fine-tuning 实验。

不追求算法推导完整性，重点是建立正确的直觉和工程能力。需要按章节系统学习时，回到[动手学深度学习路线](./DeepLearning/README.md)；需要理解 Token、生成和对齐时，阅读[LLM 基础](./LLM基础.md)。

---

## 1. 数学基础（只补够用的部分）

### 线性代数

| 概念 | 在 DL/LLM 里的用途 |
|------|-------------------|
| 矩阵乘法 | 线性变换、attention 计算、embedding 查找 |
| 余弦相似度 | 向量语义相似度，RAG 检索核心 |
| 特征值/SVD | 理解 LoRA 低秩分解的直觉 |

### 概率统计

| 概念 | 在 LLM 里的用途 |
|------|----------------|
| Softmax | 把 logits 变成概率分布，token 采样基础 |
| KL 散度 | RLHF 中约束模型不偏离预训练分布 |
| Entropy | 衡量模型输出的不确定性 |

### 优化

梯度下降的直觉：
```
loss = 模型输出与正确答案的差距
梯度 = loss 对参数的偏导，指向 loss 上升最快的方向
更新参数 = 沿梯度反方向移动一小步（learning rate 控制步长）
```

**Adam 为什么好用**：自适应调整每个参数的学习率（高频梯度的参数步长小，低频的步长大），训练更稳定。

---

## 2. 神经网络基础

### 最小 PyTorch 训练循环

```python
for epoch in range(num_epochs):
for batch in train_loader:
    optimizer.zero_grad()          # 清空上一步梯度
    outputs = model(batch["input"])
    loss = loss_fn(outputs, batch["label"])
    loss.backward()                # 反向传播，计算梯度
    optimizer.step()               # 更新参数

val_loss = evaluate(model, val_loader)
```

### 关键组件

| 组件 | 作用 | 注意点 |
|------|------|--------|
| LayerNorm | 稳定训练，归一化每层激活值 | Transformer 标配，比 BatchNorm 更适合序列 |
| Dropout | 随机置零部分神经元，防过拟合 | 推理时要关闭（`model.eval()`） |
| 残差连接 | `output = F(x) + x`，避免梯度消失 | 深层网络必备 |
| 激活函数 | 引入非线性（ReLU, GeLU, SiLU） | LLM 多用 SwiGLU 变体 |

### 过拟合诊断

```
train loss ↓，val loss ↓ → 正常训练
train loss ↓，val loss ↑ → 过拟合，需要正则化或更多数据
train loss 不降 → 学习率/模型/数据有问题
train/val loss 都高 → 模型容量不够或数据太难
```

常见处理：更多数据或数据增强；减小模型规模；Dropout + Weight Decay；Early Stopping。

---

## 3. Transformer 架构

### 整体结构（Decoder-only）

```
Token IDs
  ↓
Embedding Layer（token + position）
  ↓
N × Transformer Block：
  - Multi-Head Self-Attention（+ Causal Mask）
  - Add & Norm（残差 + LayerNorm）
  - Feed-Forward Network（两层 MLP）
  - Add & Norm
  ↓
LM Head（linear → logits → softmax → token 概率）
```

### Position Encoding

Transformer 没有 RNN 的序列感，需要显式注入位置信息。现代 LLM 多用 **RoPE（Rotary Position Embedding）**：相对位置感知更强，外推能力更好。

### Feed-Forward Network

在 attention 之后，每个 token 独立过一个两层 MLP：

```
x → Linear(d_model → 4d_model) → GeLU → Linear(4d_model → d_model)
```

FFN 的参数量占 Transformer 总参数的大部分（约 2/3）。

### Multi-Head Attention 维度

```
d_model = 总维度（如 4096）
n_heads = head 数量（如 32）
d_head = d_model / n_heads = 每个 head 的维度（= 128）
每个 head 独立计算 attention，最后 concat 再线性变换
```

---

## 4. 微调技术

### 全参数微调 vs PEFT

| 方法 | 更新参数 | 显存需求 | 适合场景 |
|------|---------|---------|---------|
| Full Fine-tuning | 全部 | 极高（需要梯度） | 大厂资源 |
| LoRA | 低秩适配矩阵 | 低 | 大多数自定义场景 |
| QLoRA | 量化 base + LoRA | 更低 | 消费级 GPU |
| Prompt Tuning | 虚拟 token 的 embedding | 极低 | 参数极少场景 |

### LoRA 原理

```
原始权重 W（冻结，不更新）
新增：W_new = W + ΔW = W + A·B

A: (d_model × r)，B: (r × d_model)，rank r << d_model

训练时只更新 A 和 B，参数量 = 2 × d_model × r
相比全参数微调，参数量减少 d_model/r 倍（通常 r=8~64）
```

**关键限制**：LoRA 只影响添加了 adapter 的层；不能从根本上增加模型不具备的知识；主要用于风格调整、格式适配、特定领域行为微调。

### 实验记录规范

做 fine-tuning 实验，至少记录：

```
实验名称：
基础模型：
任务：
数据集（大小 / 来源 / 质量说明）：
超参数（lr, batch_size, epoch, rank, alpha）：
训练 loss 曲线（截图或数字）：
Validation 指标（metric + 数值）：
显存用量：
失败点 / 观察到的问题：
结论：
```

不记录实验细节 = 重跑不可复现 = 白做。

---

## 5. HuggingFace 生态

### 最常用的入口

```python
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

## 最简单的方式
pipe = pipeline("text-generation", model="gpt2")
result = pipe("Tell me about", max_new_tokens=50)

## 手动加载（更灵活）
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b")
model = AutoModelForCausalLM.from_pretrained(
"meta-llama/Llama-2-7b",
torch_dtype=torch.float16,
device_map="auto",  # 自动分配到可用 GPU
)
```

### PEFT + LoRA 基础用法

```python
from peft import get_peft_model, LoraConfig, TaskType

lora_config = LoraConfig(
task_type=TaskType.CAUSAL_LM,
r=16,           # rank
lora_alpha=32,  # scaling factor
lora_dropout=0.1,
target_modules=["q_proj", "v_proj"],  # 要加 LoRA 的层
)

model = get_peft_model(base_model, lora_config)
model.print_trainable_parameters()
## 通常显示 < 1% 参数可训练
```

---

## 6. 面试自测

---

## D2L 系统学习入口

本页保留为深度学习概念总览；若要按“动手学深度学习”的实践路线学习，请从 [DeepLearning/README.md](DeepLearning/README.md) 开始。

建议顺序：预备知识 → 线性网络 → MLP → 深度学习计算 → CNN → RNN/Seq2Seq → 注意力与 Transformer → 优化与性能 → CV/NLP。每完成一个模块，都应运行最小实验、修改一个超参数并记录现象。

与 `LLM基础.md` 的边界：本目录解释模型训练与架构基础；`LLM基础.md` 聚焦现代大语言模型的 token、生成、对齐与应用边界。

- [ ] 能解释反向传播的流程（梯度是什么、怎么流）
- [ ] 能说清楚 Dropout 的作用和推理时要关闭的原因
- [ ] 能解释 LoRA 的原理（低秩矩阵、只更新 adapter、原始权重冻结）
- [ ] 能说清楚 train loss / val loss 的几种典型曲线代表什么
- [ ] 能解释为什么 Transformer 需要 Position Encoding
- [ ] 能说出 LayerNorm 和 BatchNorm 的区别（序列长度不固定，BatchNorm 不适合）
