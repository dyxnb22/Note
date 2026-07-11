# BERT 预训练与微调

BERT 是 encoder-only Transformer，利用双向上下文表示文本。其经典预训练含 masked language modeling；下游任务通常在 `[CLS]` 表示或 token 表示上接轻量任务头，再整体微调。

与自回归 LLM 的关键差别：BERT 可同时看左右文，适合理解、匹配、分类和抽取；decoder-only 模型用因果 mask，适合生成。微调时应使用较小学习率、验证集早停并注意任务数据量。

`#bert #pretraining #fine-tuning`
