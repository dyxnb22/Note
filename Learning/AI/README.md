# Learning/AI

这个目录是 AI 应用工程的**理论地基**，不追求算法推导深度，追求能支撑三件事：

1. **读懂论文和技术博客**：理解模型行为和设计决策背后的原理
2. **解释 LLM 工作原理**：能在面试中清楚讲清 tokenization、generation、fine-tuning、alignment
3. **为应用工程提供判断依据**：理解模型能力边界，才能做出合理的系统设计决策

三个主题目录的整体关系见：[Python → AI → Agent 学习地图](../00_Navigation/AI-Python-Agent学习地图.md)。

## 文档地图

| 文档 | 定位 | 适合什么时候看 |
|------|------|----------------|
| `LLM基础.md` | LLM 工作原理全链路：从 token 到 generation 到 alignment | 进入 AI 应用开发前必读；面试前复习 |
| `DeepLearning/` | 以 D2L 路线系统学习训练原理、CNN、RNN、Transformer、视觉与 NLP | 需要系统补模型训练基础时 |
| `DeepLearning.md` | 深度学习到 LLM 的工程桥接速览 | 想快速补训练循环、Transformer、LoRA 和 HuggingFace 时 |
| `AI工具与编程助手.md` | AI 编程工具的能力、边界、协作方式、风险 | 开始使用 AI Coding Agent 时；思考人机协作时 |

## 配套实践

- [LLM 课程实践](./实践/llm_learning/README.md)：00–11 课程，从深度学习和 Transformer 到 Agent、RAG、评测、微调、生产系统与研究方法。
- [DeepPath Lab](./实践/DeepPathLab/README.md)：以项目制方式从自动微分、线性模型、MLP 和 CNN 开始，逐步走向序列模型、Transformer 与 NLP。
- [Agent Runtime 实践](../Agent/实践/learn-claude-code/README.md)：s01–s20 课程，验证 Agent Loop、工具、Context、可靠性和 MCP。

## 与 xfg-planet 案例的连接

- [AI MCP Gateway](../Case_Studies/AI/AI-MCP-Gateway.md)：协议转换、JSON-RPC、Session 和工具治理。
- [WaLiSSH](../Case_Studies/AI/WaLiSSH.md)：工具化执行、Agent Loop、SSH 和安全边界。
- [Agent 脚手架与可编排 RAG](../Case_Studies/AI/Agent脚手架与可编排RAG.md)：Workflow、MCP、Skills、Session 和知识库配置。

## 与 Python / Agent 目录的边界

- 模型是什么、怎么工作、为什么这样设计 → 放这里
- Python 语言和服务工程 → 放 `Learning/Python/`
- 如何调用模型、如何构建 Agent、如何做 RAG → 放 `Learning/Agent/`
- 可运行的课程实验、样例输入和实验输出 → 放 `Learning/AI/实践/`
- 边界案例：context window 的原理（这里）vs 如何管理 context 窗口（Agent）

## 按场景选文档

**准备面试**
→ 必读 `LLM基础.md`（全篇，尤其是面试高频部分）
→ 按需按 `DeepLearning/README.md` 顺序学习
→ 然后去 `Agent/` 看工程应用文档

**开始做 AI 项目**
→ 先读 `LLM基础.md` 的 tokenization、context window、generation 参数章节
→ 再直接进 `Agent/01_LLM调用基础.md`

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
| context window 放哪里？ | 原理放这里（`LLM基础.md`）；如何在代码里管理放 `Agent/04_Context工程.md` |
| tokenization 放哪里？ | 放这里；tiktoken 的实际用法放 `Agent/04_Context工程.md` |
| fine-tuning 放哪里？ | 原理（LoRA 数学、训练流程）放这里；什么场景选 fine-tuning vs RAG 的工程判断放 [RAG](../Agent/RAG.md) |
| RAG 是理论还是工程？ | 检索与生成链路放 [RAG](../Agent/RAG.md)，来源、权限和版本治理放 [知识系统](../Agent/知识系统.md)；为什么 RAG 能减少幻觉的原理放 `LLM基础.md` |
