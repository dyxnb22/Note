# 词嵌入：Word2Vec、GloVe 与子词

词嵌入将离散 token 映射为稠密向量，使相似上下文的词靠近。Word2Vec 通过预测上下文/中心词学习表示；负采样降低全词表 softmax 的成本。GloVe 结合全局共现统计。

词级词表难处理罕见词和形态变化；子词嵌入将词拆为更小单元，是 BPE/WordPiece 等现代 tokenizer 的思想基础。向量相近反映训练语料中的共现，不等于逻辑等价或无偏见。

`#word2vec #glove #subword`
