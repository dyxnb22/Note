# Agent 面试题库

这里按 Agent 知识类别整理，方便逐类刷题，不把所有问题堆在一篇笔记里。

## 推荐刷题顺序

1. [[00_复习路线与答题模板]]、[[00_主题速答卡]]
2. [[01_基础架构/Agent基础与架构]]
3. [[02_Prompt与上下文/Prompt与Context Engineering]]、[[03_Memory与状态/Memory与State]]
4. [[04_Tool与协议/Tool Calling与MCP]]、[[05_Multi-Agent与Workflow/Multi-Agent与Workflow]]
5. [[06_RAG与知识库/RAG与检索]]
6. [[07_可靠性与安全/可靠性与安全]]、[[08_评测与可观测/评测与可观测性]]
7. [[09_工程化与系统设计/生产工程与系统设计]]、[[10_模型与推理/模型与推理基础]]
8. [[11_编码与后端/编码题与后端基础]]
9. [[12_课程深化/README]]：刷完主线后，按课程特有方向补充 Provider、代码 Agent、生产运维、知识治理、跨 Agent、推理、实时交互和项目表达。
10. [[13_跨主题综合题/新增题簇_Agent与AI后端]]：集中练习 AI 后端、RAG 安全、平台取舍、SRE 和项目表达。
11. 各主分类下标注“面经高频补充”的子题单：集中刷近期面经和公开题库提炼的 Loop、Harness、Skill、评测、系统设计及高频八股。

## 知识分类

- [[01_基础架构/Agent基础与架构]]：Agent 定义、生命周期、ReAct、规划、路由和架构选型。
- [[02_Prompt与上下文/Prompt与Context Engineering]]：Prompt、Context Engineering、查询改写和上下文压缩。
- [[03_Memory与状态/Memory与State]]：短期/长期/任务记忆、State、Checkpoint 和恢复。
- [[04_Tool与协议/Tool Calling与MCP]]：Function Calling、Tool、MCP、A2A 和工具治理。
- [[05_Multi-Agent与Workflow/Multi-Agent与Workflow]]：多 Agent、Workflow、Supervisor、Harness 和并行协作；另有 [[05_Multi-Agent与Workflow/Loop控制与Harness面经补充]]、[[05_Multi-Agent与Workflow/Skill编排与协作面经补充]]。
- [[06_RAG与知识库/RAG与检索]]：文档处理、混合检索、Rerank、评测和知识更新。
- [[07_可靠性与安全/可靠性与安全]]：幻觉、死循环、Prompt Injection、沙箱、权限和人工接管。
- [[08_评测与可观测/评测与可观测性]]：指标、数据集、Badcase、Trace、回归和线上监控；另有 [[08_评测与可观测/评测、轨迹与线上故障面经补充]]。
- [[09_工程化与系统设计/生产工程与系统设计]]：并发、流式、限流、队列、部署、成本和高可用；另有 [[09_工程化与系统设计/系统设计与取舍面经补充]]。
- [[10_模型与推理/模型与推理基础]]：Transformer、Attention、KV Cache、SFT、RL 和推理优化；另有 [[10_模型与推理/高频八股与手撕面经补充]]。
- [[11_编码与后端/编码题与后端基础]]：手撕题、数据库、Redis、消息系统和后端系统设计。
- [[12_课程深化/README]]：从原课程拆出的进阶专题，按递进层次继续刷题。
- [[13_跨主题综合题/新增题簇_Agent与AI后端]]：新增的 AI 后端、RAG 安全、平台取舍、SRE 与项目表达题。

## 权威归属与去重规则

- 通用模型结构、训练算法、推理基础和模型版本：回到 [AI/LLM 基础](../AI/LLM基础.md) 与 [AI 面试题库](../AI/面试题库/README.md)；本库只保留 Agent 对模型行为、路由、预算和适配的差异。
- 通用数据库、缓存、消息、系统设计和交付：分别以 [Backend/Data](../Backend/Data/README.md)、[Backend/Architecture](../Backend/Architecture/README.md) 和 [Backend/Delivery](../Backend/Delivery/README.md) 为主文档；本库只保留 Agent 的状态、工具、幂等、权限和评测连接。
- Python/Go/Java/Rust 的语言实现：进入对应语言题库；Agent 页面不重复完整语言教程，只补模型/工具/状态与该语言的组合边界。
- 同一问题需要同时出现在两个入口时，主入口写完整答案，桥接入口只保留差异点和链接；基础评测题与 `12_课程深化` 的实验/发布门禁也按这个层级区分。

## 答案形式

每道题的答案都已直接放在题目下方，按“题目 → 答案 → 下一题”的顺序阅读，不再维护独立答案目录。

原有 `Learning/Agent/面试` 目录已移除，内容统一迁移到本题库。
