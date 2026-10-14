# 大模型学习路线与项目集

这个目录是一套从 Agent 入门到 LLM 工程精通的学习工程。前半部分服务于“能做 Agent/RAG 项目并找实习或初级岗位”，后半部分服务于“理解训练、评测、推理、部署、系统可靠性，能应对更深入的大模型工程岗位”。

## 推荐学习顺序

[学习计划](./00_learning_plan/学习计划.md) 维护阶段目标和产出标准；课程顺序：

- **基础**：[深度学习](./00_deep_learning_for_llm/学习文档.md) → [Transformer](./00_transformer_foundation/学习文档.md)
- **应用**：[Agent](./01_agent_basics/学习文档.md) → [RAG](./02_rag_knowledge_base/学习文档.md) → [工作流](./03_tool_calling_workflow/学习文档.md) → [评测](./04_llm_evaluation/学习文档.md)
- **工程与研究**：[微调推理](./05_finetune_and_inference/学习文档.md) → [生产系统](./06_production_llm_system/学习文档.md) → [开源 LLM](./07_open_llm_deepseek_study/学习文档.md) → [研究复现](./08_research_methods_and_reproduction/学习文档.md) → [对齐与推理](./09_alignment_reasoning_research/学习文档.md) → [可解释性](./10_interpretability_and_evaluation/学习文档.md) → [研究作品集](./11_phd_research_portfolio/学习文档.md)

复习问答见 [AI 面试题库](../../面试题库/README.md)。

## 运行环境

Mac 上推荐使用系统 Python 3.11+ 或 Homebrew 安装的 Python：

```bash
python3 --version
```

所有示例默认只依赖 Python 标准库。需要真实模型时，设置 OpenAI-compatible 环境变量即可：

```bash
export LLM_API_KEY="你的 key"
export LLM_BASE_URL="https://api.deepseek.com"
export LLM_MODEL="deepseek-chat"
```

如果不设置 API key，示例会走本地 mock 输出，方便先理解代码结构。

## 在 Notes 中的位置

这是 `Learning/AI` 下的课程实践快照：课程说明和可运行项目放在这里；模型原理以 `Learning/AI` 为准，Agent Runtime、工具治理和生产可靠性以 `Learning/Agent面试题库` 为准。阶段产物见学习计划，各课程目录保存代码与实验记录；不要复制成新的理论主文档。

工具调用工作流报告、SFT 数据集、LoRA 配置和论文模板是实验产物/示例，不是理论主文档；重新运行脚本可能重新生成或覆盖输出。
