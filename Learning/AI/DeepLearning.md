# 深度学习：从参数更新到语言模型适配

深度学习用可微分模型建立输入与输出的关系，通过损失衡量误差，再沿梯度调整参数。理解一条完整的训练链路，比记住组件名更有用：数据如何变成张量、输出如何进入损失、哪些参数被更新、验证指标又说明什么。

## 张量、概率与梯度怎样连起来

一批样本排成矩阵 X，线性层计算 XW+b，激活函数引入非线性。矩阵维度表达样本、特征和输出的含义；即使广播允许计算，形状与语义不一致仍会优化错误目标。

分类模型常输出 logits，再经 Softmax 得到类别概率。熵描述分布的分散程度，KL 散度衡量两个分布的差异；这些量各有定义，不能都叫作“置信度”。输出概率也不自动具有校准后的正确率含义。

梯度指向损失在参数空间中局部上升最快的方向，梯度下降沿反方向走一小步。Adam 用历史梯度的一阶、二阶矩估计缩放更新，再做偏差修正；它仍需要合适的学习率、数据和损失。[Adam 原论文](https://arxiv.org/abs/1412.6980)

## 一次训练与一次验证

训练批次依次完成清梯度、前向、求损失、反向、更新。下面是流程伪代码，model、数据迭代器、优化器与 evaluate 需由具体任务定义；evaluate 负责在验证集汇总指标。

```pseudocode
for epoch in range(num_epochs):
    model.train()
    for batch in train_loader:
        optimizer.zero_grad()
        outputs = model(batch["input"])
        loss = loss_fn(outputs, batch["label"])
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        val_loss = evaluate(model, val_loader)
```

train/eval 控制 Dropout、BatchNorm 等模块的行为；no_grad 控制是否记录自动求导图，二者不是同一个开关。损失函数还决定输入约定，例如交叉熵通常直接接收 logits，不能无条件先加 Softmax。

训练损失下降而验证损失持续上升，是泛化变差的信号，但应先检查划分、预处理、评估模式和分布差异。正则、数据增强、早停与容量调整分别改变不同条件，不能看到曲线就只归因于模型大小。

## 从神经网络到自回归语言模型

Decoder-only 模型把 token 变成向量，注入位置信息，经过多层因果注意力与前馈网络，最后由语言模型头输出下一个 token 的 logits。因果掩码阻止当前位置读取未来 token，训练中的输入与标签也必须正确错位。

| 组件 | 保留的关系 | 需要区分的边界 |
|---|---|---|
| 多头注意力 | 每个位置与可见上下文的关系 | 掩码、头数与张量维度由架构决定 |
| 前馈网络 | 各位置的非线性特征变换 | 标准两层 MLP 与门控变体参数量不同 |
| 残差连接 | 把原表示加回子层结果 | 需要维度兼容，不能保证梯度永不消失 |
| LayerNorm | 按指定特征维度归一化 | 与按批次统计的 BatchNorm 语义不同 |
| Dropout | 训练时随机屏蔽部分激活 | 推理通常通过 eval 关闭 |

以标准多头注意力为例，d_model=4096、n_heads=32 时，每头维度为 128。分头后分别计算注意力，再拼接并投影；多查询或分组查询架构中的查询头与键值头数量可能不同，不能只套一个形状公式。

位置表示可以相加到嵌入，也可在注意力内部改变查询和键。RoPE 属于后者，不能理解为所有模型都使用同一套“token 加位置向量”。上下文外推效果还取决于训练长度、位置缩放与评估任务。

若普通 FFN 用 d→4d→d 两个矩阵，其参数约为 8d²；标准同宽 Q、K、V、输出投影约为 4d²。因此忽略偏置与其他组件时，FFN 在这两部分中约占三分之二，这不是所有 Transformer 总参数的固定比例。

## LoRA 改变的是更新空间

全参数微调更新基础权重；LoRA 冻结基础权重 W，用低秩矩阵表示增量。设 W 的形状为 m×n，可令 A 为 r×n、B 为 m×r，使 ΔW=(α/r)BA；A、B 的命名顺序可不同，关键是维度与乘法一致。

新增参数为 r(m+n)，原矩阵参数为 mn。方阵 m=n=d 时，缩减倍数为 d/(2r)，而非 d/r。例如 d=4096、r=8，原矩阵有 16,777,216 个参数，增量矩阵共有 65,536 个，比例为 256 倍。这个计算只比较所适配的一个权重矩阵，不代表整模型显存也减少 256 倍。

QLoRA 进一步以量化方式存储冻结的基础权重，并训练适配参数；激活、优化器状态、序列长度与批量仍消耗显存。Prompt Tuning 则训练输入侧的连续提示表示，更新位置与 LoRA 不同。方法选择应结合任务质量与资源实测，不能只按名称推断效果。

LoRA 影响的是添加适配器的模块与可训练参数集合。它并不自带知识检索、来源验证或事实更新机制，也不能仅据参数少就断言模型只学格式。是否记住任务信息、是否遗忘原能力，都需在独立样本上评估。[LoRA 原论文](https://arxiv.org/abs/2106.09685)

## 把模型加载与适配连接起来

下面两段在同一 Python 会话中顺序执行，需要安装兼容版本的 torch、transformers 与 peft，首次加载需要下载模型文件。这里演示加载与添加适配器，训练仍需另行构造输入、标签、掩码和批次。

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "openai-community/gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
base_model = AutoModelForCausalLM.from_pretrained(model_id)
```

GPT-2 的融合注意力投影名为 c_attn，并采用 Conv1D 的权重存储方向；不能照抄另一模型的 q_proj、v_proj 模块名。更换架构后应检查实际模块与所适配的权重形状。[GPT-2 文档](https://huggingface.co/docs/transformers/en/model_doc/gpt2)

```python
from peft import LoraConfig, TaskType, get_peft_model

config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["c_attn"],
    fan_in_fan_out=True,
    bias="none",
)
model = get_peft_model(base_model, config)
model.print_trainable_parameters()
```

fan_in_fan_out 与目标层的存储方向对应，α/r 是这里使用的默认缩放规则。可训练比例由目标层、秩、偏置与额外可训练模块共同决定，实际输出才是当前配置的结果。[PEFT LoRA 配置](https://huggingface.co/docs/peft/en/package_reference/lora)

一次实验应同时保存基础模型修订、适配器配置与权重、分词器、数据划分、随机种子、环境和验证指标。适配器必须与对应基础模型一起解释；只保存训练损失或一个权重文件，无法可靠比较实验。生成概率、解码和评估可继续对照[语言模型基础](LLM基础.md)。
