# Learning/AI

这个目录是 AI 应用工程的**理论地基**，不追求算法推导深度，追求能支撑三件事：

1. **读懂论文和技术博客**：理解模型行为和设计决策背后的原理
2. **解释 LLM 工作原理**：能在面试中清楚讲清 tokenization、generation、fine-tuning、alignment
3. **为应用工程提供判断依据**：理解模型能力边界，才能做出合理的系统设计决策

## 文档地图

| 文档 | 定位 | 适合什么时候看 |
|------|------|----------------|
| `LLM基础.md` | LLM 工作原理全链路：从 token 到 generation 到 alignment | 进入 AI 应用开发前必读；面试前复习 |
| `DeepLearning.md` + `DeepLearning/` | 以 D2L 路线学习训练原理、CNN、RNN、Transformer、视觉与 NLP | 需要系统补模型训练基础时 |
| `AI工具与编程助手.md` | AI 编程工具的能力、边界、协作方式、风险 | 开始使用 AI Coding Agent 时；思考人机协作时 |

## 与 Python Agent 目录的边界

- 模型是什么、怎么工作、为什么这样设计 → 放这里
- 如何调用模型、如何构建 Agent、如何做 RAG → 放 `Learning/Python Agent/`
- 边界案例：context window 的原理（这里）vs 如何管理 context 窗口（Python Agent）

## 按场景选文档

**准备面试**
→ 必读 `LLM基础.md`（全篇，尤其是面试高频部分）
→ 按需按 `DeepLearning/README.md` 顺序学习
→ 然后去 `Python Agent/Agent/` 看工程应用文档

**开始做 AI 项目**
→ 先读 `LLM基础.md` 的 tokenization、context window、generation 参数章节
→ 再直接进 `Python Agent/Agent/LLM调用基础.md`

**补 LLM 理论短板**
→ 顺序读：`DeepLearning/README.md` → `LLM基础.md`
→ 侧重理解，不追求手推公式

**开始用 AI 编程工具**
→ 直接读 `AI工具与编程助手.md`，其余两篇可以之后补

## 必读 vs 按需

| 文档 | 分类 | 说明 |
|------|------|------|
| `LLM基础.md` | **必读** | 做 AI 应用工程的理论地基，面试高频来源 |
| `DeepLearning/` | 按需 | 需要系统理解训练过程、Transformer 或微调时读 |
| `AI工具与编程助手.md` | 按需 | 开始用 AI Coding Agent 时读 |

## 常见混淆边界

| 问题 | 答案 |
|------|------|
| context window 放哪里？ | 原理放这里（`LLM基础.md`）；如何在代码里管理放 `Python Agent/Context工程.md` |
| tokenization 放哪里？ | 放这里；tiktoken 的实际用法放 `Python Agent/Context工程.md` |
| fine-tuning 放哪里？ | 原理（LoRA 数学、训练流程）放这里；什么场景选 fine-tuning vs RAG 的工程判断放 `Python Agent/RAG与知识系统.md` |
| RAG 是理论还是工程？ | RAG 的工程实现放 `Python Agent/RAG与知识系统.md`；为什么 RAG 能减少幻觉的原理放 `LLM基础.md` |
