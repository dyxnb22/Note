# Learning/AI

这个目录提供 AI 与模型原理的按需参考，不是进入 Agent 前必须全部完成的理论课程。它主要支撑三件事：

1. **读懂论文和技术博客**：理解模型行为和设计决策背后的原理
2. **解释 LLM 工作原理**：能在面试中清楚讲清 tokenization、generation、fine-tuning、alignment
3. **为应用工程提供判断依据**：理解模型能力边界，才能做出合理的系统设计决策

三个主题目录的整体关系见：[Python → AI → Agent 学习地图](../00_Navigation/AI-Python-Agent学习地图.md)。

## 文档地图

| 文档 | 定位 | 适合什么时候看 |
|------|------|----------------|
| `LLM基础.md` | LLM 工作原理全链路：从 token 到 generation 到 alignment | 遇到模型原理问题或准备面试时查阅 |
| `面试题库/` | 模型、训练、推理和 AI 系统的问答题 | 需要按题目复习或准备模型相关面试时 |
| `DeepLearning/` | 以 D2L 路线系统学习训练原理、CNN、RNN、Transformer、视觉与 NLP | 需要系统补模型训练基础时 |
| `DeepLearning.md` | 深度学习到 LLM 的工程桥接速览 | 想快速补训练循环、Transformer、LoRA 和 HuggingFace 时 |
| `ML系统与MLOps.md` | 数据、实验、模型注册、推理服务、漂移、灰度与回滚 | 需要把训练结果做成可运营系统时 |
| `AI工具与编程助手.md` | AI 编程工具的能力、边界、协作方式、风险 | 开始使用 AI Coding Agent 时；思考人机协作时 |

通用数据科学的入口见 [数据科学](../Data_Science/README.md)：它补充问题定义、Python 数据分析、EDA、经典机器学习、特征泄漏、实验、时间序列和端到端项目；本目录继续负责深度学习与模型训练原理。

## 配套实践

- [LLM 课程实践](./实践/llm_learning/README.md)：00–11 课程，从深度学习和 Transformer 到 Agent、RAG、评测、微调、生产系统与研究方法。
- [DeepPath Lab](./实践/DeepPathLab/README.md)：以项目制方式从自动微分、线性模型、MLP 和 CNN 开始，逐步走向序列模型、Transformer 与 NLP。
- [Agent 实践与项目表达题](../Agent面试题库/12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md)：提炼 Agent Loop、工具、Context、可靠性和 MCP 的实践要点。

## 与 xfg-planet 案例的连接

- [AI MCP Gateway](../Case_Studies/AI/AI-MCP-Gateway.md)：协议转换、JSON-RPC、Session 和工具治理。
- [WaLiSSH](../Case_Studies/AI/WaLiSSH.md)：工具化执行、Agent Loop、SSH 和安全边界。
- [Agent 脚手架与可编排 RAG](../Case_Studies/AI/Agent脚手架与可编排RAG.md)：Workflow、MCP、Skills、Session 和知识库配置。

## 与 Python / Agent 目录的边界

- 模型是什么、怎么工作、为什么这样设计 → 放这里
- Python 语言和服务工程 → 放 `Learning/Python/`
- 如何调用模型、如何构建 Agent、如何做 RAG → 刷 `Learning/Agent面试题库/`
- 训练数据、实验追踪、模型注册、模型服务与漂移 → 放 `ML系统与MLOps.md`
- 可运行的课程实验、样例输入和实验输出 → 放 `Learning/AI/实践/`
- 边界案例：context window 的原理（这里）vs 如何管理 context 窗口（Agent）

## 按场景选文档

**准备面试**
→ 按岗位范围阅读 `LLM基础.md` 和 [AI 面试题库](./面试题库/README.md)，不默认扩展到全部深度学习章节
→ 按需按 `DeepLearning/README.md` 顺序学习
→ 然后去 `Agent面试题库/` 刷工程应用题

**开始做 AI 项目**
→ 直接进入 `Agent面试题库/01_基础架构/Agent基础与架构.md`
→ 遇到 tokenization、context window 或 generation 参数问题时，再回到 `LLM基础.md` 对应章节

**补 LLM 理论短板**
→ 顺序读：`DeepLearning/README.md` → `LLM基础.md`
→ 侧重理解，不追求手推公式

**开始用 AI 编程工具**
→ 直接读 `AI工具与编程助手.md`，其余两篇可以之后补

**把模型部署成生产服务**
→ `DeepLearning/` 或 `DeepLearning.md` → `ML系统与MLOps.md` → `Backend/Delivery/07_生产系统工程.md`

## 最小入口与按需分支

| 文档 | 分类 | 说明 |
|------|------|------|
| `LLM基础.md` | 核心参考 | Agent 应用不要求先通读；模型原理和面试问题出现时进入 |
| `面试题库/` | 问答复习 | 将模型原理、训练、推理和 AI 系统问题按题目集中复习 |
| `DeepLearning/` | 按需 | 需要系统理解训练过程、Transformer 或微调时读 |
| `ML系统与MLOps.md` | 按需 | 自己训练、注册、部署和监控模型时读 |
| `AI工具与编程助手.md` | 按需 | 开始用 AI Coding Agent 时读 |

这里没有全员必读清单。当前问题若是 Agent 应用，从 [Agent 面试题库](../Agent面试题库/README.md) 选择入口；只有自己训练模型时，才把 `DeepLearning/` 当作系统路线。

## 常见混淆边界

| 问题 | 答案 |
|------|------|
| context window 放哪里？ | 原理放这里（`LLM基础.md`）；如何在代码里管理刷 `Agent面试题库/02_Prompt与上下文/Prompt与Context Engineering.md` |
| tokenization 放哪里？ | 放这里；Context 的实际管理刷 `Agent面试题库/02_Prompt与上下文/Prompt与Context Engineering.md` |
| fine-tuning 放哪里？ | 原理（LoRA 数学、训练流程）放这里；模型行为训练的工程判断刷 [推理与模型行为](../Agent面试题库/12_课程深化/06_推理与模型行为/推理与模型行为.md) |
| RAG 是理论还是工程？ | 检索与生成链路刷 [RAG 与检索](../Agent面试题库/06_RAG与知识库/RAG与检索.md)，来源、权限和版本治理刷 [知识摄取与 GraphRAG](../Agent面试题库/12_课程深化/04_知识摄取与GraphRAG/知识摄取与GraphRAG.md)；为什么 RAG 能减少幻觉的原理放 `LLM基础.md` |
