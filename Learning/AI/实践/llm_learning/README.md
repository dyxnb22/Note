# 大模型学习路线与项目集

这个目录是一套从 Agent 入门到 LLM 工程精通的学习工程。前半部分服务于“能做 Agent/RAG 项目并找实习或初级岗位”，后半部分服务于“理解训练、评测、推理、部署、系统可靠性，能应对更深入的大模型工程岗位”。

## 推荐学习顺序

1. `00_learning_plan/学习计划.md`：总路线、时间安排、产出标准。
2. `00_deep_learning_for_llm/`：从深度学习、softmax、loss、next-token prediction 学起。
3. `00_transformer_foundation/`：从 token、embedding、self-attention、Transformer Block 学起。
4. `01_agent_basics/`：Agent 基础、工具调用、ReAct 思路。
5. `02_rag_knowledge_base/`：RAG 检索增强生成。
6. `03_tool_calling_workflow/`：多步骤工作流、状态机、确认式执行。
7. `04_llm_evaluation/`：Prompt 与 Agent 评测。
8. `05_finetune_and_inference/`：微调数据、LoRA、推理优化。
9. `06_production_llm_system/`：生产级 LLM 网关、缓存、重试、观测。
10. `07_open_llm_deepseek_study/`：开源 LLM 架构与 DeepSeek V3/R1 学习。
11. `08_research_methods_and_reproduction/`：论文精读、复现、ablation 和研究报告。
12. `09_alignment_reasoning_research/`：SFT、DPO、RL、reasoning model 和 CoT 研究。
13. `10_interpretability_and_evaluation/`：可解释性、评测、安全与鲁棒性。
14. `11_phd_research_portfolio/`：PhD 申请作品集、研究路线和选题筛选。
15. `大模型八股.md`：面试高频知识点。

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

这是 `Learning/AI` 下的课程实践快照：课程说明和可运行项目放在这里，模型原理以 `Learning/AI` 的理论笔记为准，Agent Runtime、工具治理和生产可靠性以 `Learning/Agent` 为准。不要把本目录的课程说明再复制成新的理论主文档。

| 课程 | 实践入口 | 对齐笔记 |
|---|---|---|
| 00 深度学习 | [tiny_next_token_model.py](./00_deep_learning_for_llm/project/tiny_next_token_model.py) | [DeepLearning](../../DeepLearning/README.md) |
| 00 Transformer | [self_attention_demo.py](./00_transformer_foundation/project/self_attention_demo.py) | [Transformer 从结构到实现](../../DeepLearning/09_注意力与Transformer/注意力与Transformer.md) |
| 01 Agent | [simple_agent.py](./01_agent_basics/project/simple_agent.py) | [Agent 架构与设计](../../../Agent/Agent架构与设计.md) |
| 02 RAG | [mini_rag.py](./02_rag_knowledge_base/project/mini_rag.py) | [RAG](../../../Agent/RAG.md)、[知识系统](../../../Agent/知识系统.md) |
| 03 Workflow | [workflow_agent.py](./03_tool_calling_workflow/project/workflow_agent.py) | [Workflow 与编排](../../../Agent/Workflow与编排.md)、[LangGraph](../../../Agent/LangGraph.md) |
| 04 评测 | [prompt_eval.py](./04_llm_evaluation/project/prompt_eval.py) | [Agent Eval 实验方法](../../../Agent/Agent%20Eval实验方法.md) |
| 05 微调与推理 | [prepare_sft_dataset.py](./05_finetune_and_inference/project/prepare_sft_dataset.py) | [LLM 基础](../../LLM基础.md) |
| 06 生产系统 | [llm_gateway.py](./06_production_llm_system/project/llm_gateway.py) | [部署与生产化](../../../Agent/部署与生产化.md) |
| 07 开源 LLM | [architecture_budget_estimator.py](./07_open_llm_deepseek_study/project/architecture_budget_estimator.py) | [LLM 基础](../../LLM基础.md) |
| 08 研究复现 | [paper_review_generator.py](./08_research_methods_and_reproduction/project/paper_review_generator.py) | [LLM 学习计划](./00_learning_plan/学习计划.md) |
| 09 对齐与推理 | [tiny_dpo_loss.py](./09_alignment_reasoning_research/project/tiny_dpo_loss.py) | [LLM 基础](../../LLM基础.md) |
| 10 可解释性与评测 | [eval_significance.py](./10_interpretability_and_evaluation/project/eval_significance.py) | [Agent Eval 实验方法](../../../Agent/Agent%20Eval实验方法.md) |
| 11 研究作品集 | [research_idea_scorer.py](./11_phd_research_portfolio/project/research_idea_scorer.py) | [项目表达与面试](../../../Agent/项目表达与面试.md) |

课程中的 `workflow_report.md`、`sft_dataset.jsonl`、`lora_config.json` 和论文模板是实验产物/示例，不是理论主文档；重新运行脚本可能覆盖它们。
