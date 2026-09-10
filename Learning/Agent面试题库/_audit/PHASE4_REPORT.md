# Phase 4 — Duplicate Candidate Clustering

- Questions: **736**
- Candidate edges: **47**
- Review clusters: **38**

> Phase 4 只生成候选，不做删除/合并裁决。`13_跨主题综合题` 仅作为重复提示，默认不删。

## Candidate edges

| # | Score | A | B | Shared atoms | Hint only |
|---:|---:|---|---|---|---|
| 1 | 0.871 | `Q::09_工程化与系统设计/生产工程与系统设计.md::8` — 令牌桶、漏桶、固定窗口和滑动窗口如何选择？ | `Q::11_编码与后端/编码题与后端基础.md::15` — 实现令牌桶、漏桶或滑动窗口限流。 | BACK-001 | no |
| 2 | 0.871 | `Q::12_课程深化/02_代码Agent与ComputerUse/代码Agent与ComputerUse.md::1` — 一个代码 Agent 的最小工具集应该有哪些？ | `Q::12_课程深化/02_代码Agent与ComputerUse/代码Agent与ComputerUse.md::5` — 代码 Agent 的 Context 应该选择哪些内容？ | CODE-004 | no |
| 3 | 0.860 | `Q::08_评测与可观测/评测与可观测性.md::14` — 如何处理模型输出的随机性？ | `Q::08_评测与可观测/评测与可观测性.md::31` — 如何在模型输出随机的情况下做线上实验？ | EVAL-012 | no |
| 4 | 0.857 | `Q::05_Multi-Agent与Workflow/Multi-Agent与Workflow.md::9` — 如何设置子 Agent 的权限和能力边界？ | `Q::05_Multi-Agent与Workflow/Skill编排与协作面经补充.md::10` — 如何隔离被委托 Agent 的身份、数据和副作用权限？ | IDENT-001 | no |
| 5 | 0.856 | `Q::04_Tool与协议/Tool Calling与MCP.md::1` — Function Calling 的完整流程是什么？ | `Q::04_Tool与协议/Tool Calling与MCP.md::2` — Tool Calling 与普通函数调用有什么区别？ | SEC-001, TOOL-003 | no |
| 6 | 0.855 | `Q::03_Memory与状态/Memory与State.md::22` — 如何设计 State Schema 和状态版本？ | `Q::12_课程深化/03_Durable与生产运维/Durable与生产运维.md::17` — Prompt、模型、工具、策略、索引和 State Schema 应如何版本化？ | OPS-002, STATE-003 | no |
| 7 | 0.848 | `Q::05_Multi-Agent与Workflow/Multi-Agent与Workflow.md::7` — 如何避免多 Agent 之间重复劳动、循环调用和责任不清？ | `Q::05_Multi-Agent与Workflow/Skill编排与协作面经补充.md::9` — 如何避免多 Agent 因上下文复制、自然语言闲聊和反复确认而失控？ | MULTI-005 | no |
| 8 | 0.846 | `Q::12_课程深化/06_推理与模型行为/推理与模型行为.md::14` — 工具调用训练轨迹应该包含哪些成功和失败样本？ | `Q::12_课程深化/06_推理与模型行为/推理与模型行为.md::19` — 工具调用训练数据应有哪些安全要求？ | DATA-006 | no |
| 9 | 0.844 | `Q::05_Multi-Agent与Workflow/Loop控制与Harness面经补充.md::17` — Agent Loop 如何利用 KV Cache、请求批处理和结果缓存降低延迟？哪些缓存不能盲目复用？ | `Q::05_Multi-Agent与Workflow/Loop控制与Harness面经补充.md::23` — Agent Loop 中哪些结果可以复用，哪些不能？ | CACHE-001 | no |
| 10 | 0.841 | `Q::11_编码与后端/编码题与后端基础.md::32` — ClickHouse 有什么特性？适合什么场景？ | `Q::11_编码与后端/编码题与后端基础.md::33` — Kafka 和 ClickHouse 如何配合做事件分析？ | BACK-016 | no |
| 11 | 0.841 | `Q::12_课程深化/01_Provider与框架/Provider适配与框架选型.md::21` — Adapter 层应该测试哪些异常和边界？ | `Q::12_课程深化/01_Provider与框架/Provider适配与框架选型.md::33` — Provider Adapter 的契约测试至少要覆盖哪些情况？ | PROV-008 | no |
| 12 | 0.840 | `Q::08_评测与可观测/评测、轨迹与线上故障面经补充.md::1` — 离线评测与在线评测的目标、数据和反馈速度有什么区别？ | `Q::08_评测与可观测/评测与可观测性.md::38` — 离线评测、在线评测和生产监控分别回答什么问题？ | EVAL-014 | no |
| 13 | 0.839 | `Q::07_可靠性与安全/可靠性与安全.md::14` — 如何处理模型输出中的敏感信息？ | `Q::07_可靠性与安全/可靠性与安全.md::15` — 如何做敏感信息识别和脱敏？ | SEC-009 | no |
| 14 | 0.839 | `Q::08_评测与可观测/评测、轨迹与线上故障面经补充.md::7` — LLM-as-Judge 有哪些偏差？如何与规则、程序验证和人工评审组合？ | `Q::08_评测与可观测/评测与可观测性.md::10` — LLM-as-a-Judge 的优点、问题和改进方法是什么？ | EVAL-010 | no |
| 15 | 0.838 | `Q::12_课程深化/01_Provider与框架/Provider适配与框架选型.md::13` — 如何把 LangGraph 的 State、Node、Edge、Checkpoint 映射到通用 Agent Runtime？ | `Q::12_课程深化/01_Provider与框架/Provider适配与框架选型.md::17` — LangGraph 中共享 State、Reducer、子图和并行 Send 分别解决什么问题？ | PROV-009 | no |
| 16 | 0.835 | `Q::11_编码与后端/编码题与后端基础.md::37` — 如何设计可测试的 Agent 代码？ | `Q::11_编码与后端/编码题与后端基础.md::44` — 如何为 Agent 代码设计单测、Mock、回放测试和端到端评测？ | TEST-002 | no |
| 17 | 0.833 | `Q::12_课程深化/04_知识摄取与GraphRAG/知识摄取与GraphRAG.md::30` — 如何评估 GraphRAG 是否值得相对普通混合检索增加复杂度？ | `Q::12_课程深化/04_知识摄取与GraphRAG/知识摄取与GraphRAG.md::33` — 企业问题需要跨文档、多跳关系推理，你会如何证明 GraphRAG 比混合检索更适合？ | GRAPH-001 | no |
| 18 | 0.832 | `Q::05_Multi-Agent与Workflow/Skill编排与协作面经补充.md::1` — “一个 Agent × N 个 Skill”与“多个专用 Agent”的核心差异是什么？ | `Q::05_Multi-Agent与Workflow/Skill编排与协作面经补充.md::6` — Skill、Prompt、Tool、Workflow 和 Agent 的边界分别是什么？ | SKILL-001 | no |
| 19 | 0.830 | `Q::04_Tool与协议/Tool Calling与MCP.md::2` — Tool Calling 与普通函数调用有什么区别？ | `Q::12_课程深化/01_Provider与框架/Provider适配与框架选型.md::10` — `tool_call`、工具执行结果和最终文本在一次请求中的职责有什么不同？ | SEC-001, TOOL-003 | no |
| 20 | 0.824 | `Q::05_Multi-Agent与Workflow/Loop控制与Harness面经补充.md::18` — 如何设计 Loop Trace，使它既能解释决策，又能安全回放而不重复真实副作用？ | `Q::05_Multi-Agent与Workflow/Multi-Agent与Workflow.md::21` — 如何设计 Harness 的日志、Trace 和回放能力？ | REPLAY-001, TRACE-002 | no |
| 21 | 0.812 | `Q::01_基础架构/Agent基础与架构.md::13` — Planner、Executor、Critic、Router、Supervisor 分别负责什么？ | `Q::05_Multi-Agent与Workflow/Multi-Agent与Workflow.md::3` — Planner、Executor、Critic、Router、Supervisor 分别负责什么？ | MULTI-002 | no |
| 22 | 0.798 | `Q::01_基础架构/Agent基础与架构.md::2` — Agent 的执行流程是什么 | `Q::01_基础架构/Agent基础与架构.md::7` — Agent 系统最重要的设计部分是什么？ | LOOP-003, LOOP-008, SEC-001, STATE-001 | no |
| 23 | 0.791 | `Q::12_课程深化/01_Provider与框架/Provider适配与框架选型.md::20` — 模型、工具 Schema、Prompt 和 State Schema 升级时，兼容性应如何管理？ | `Q::12_课程深化/03_Durable与生产运维/Durable与生产运维.md::17` — Prompt、模型、工具、策略、索引和 State Schema 应如何版本化？ | OPS-002, STATE-003 | no |
| 24 | 0.773 | `Q::01_基础架构/Agent基础与架构.md::10` — Plan-and-Execute 与 ReAct 有什么区别？ | `Q::10_模型与推理/高频八股与手撕面经补充.md::13` — Plan-and-Execute 为什么可能减少长任务中的重复规划？它又会引入什么风险？ | LOOP-004, LOOP-009 | no |
| 25 | 0.767 | `Q::04_Tool与协议/Tool Calling与MCP.md::10` — 工具调用如何支持预览、审批、撤销和回滚？ | `Q::07_可靠性与安全/可靠性与安全.md::20` — 如何让用户预览、确认、撤销和回滚 Agent 动作？ | SEC-005, TOOL-006 | no |
| 26 | 0.762 | `Q::09_工程化与系统设计/生产工程与系统设计.md::18` — 如何做多租户架构和数据隔离？ | `Q::12_课程深化/03_Durable与生产运维/Durable与生产运维.md::11` — 如何设计多租户任务的并发、资源和状态隔离？ | CAP-001, SEC-004 | no |
| 27 | 0.754 | `Q::05_Multi-Agent与Workflow/Multi-Agent与Workflow.md::21` — 如何设计 Harness 的日志、Trace 和回放能力？ | `Q::08_评测与可观测/评测与可观测性.md::37` — 如何设计可回放且不泄露秘密的 Trace？ | REPLAY-001, TRACE-002 | no |
| 28 | 0.754 | `Q::12_课程深化/03_Durable与生产运维/Durable与生产运维.md::6` — Queue、Lease 和 Heartbeat 如何配合？ | `Q::12_课程深化/03_Durable与生产运维/Durable与生产运维.md::34` — 为什么恢复需要 Lease、Heartbeat 或 CAS？ | DUR-004 | no |
| 29 | 0.754 | `Q::03_Memory与状态/Memory与State.md::6` — Memory 与 RAG 的边界是什么？ | `Q::03_Memory与状态/Memory与State.md::9` — Memory 的读取时机如何设计？ | MEM-009, MEM-014 | no |
| 30 | 0.753 | `Q::03_Memory与状态/Memory与State.md::22` — 如何设计 State Schema 和状态版本？ | `Q::12_课程深化/03_Durable与生产运维/Durable与生产运维.md::27` — State Schema 或策略前向迁移后，为什么不能只回滚应用代码？ | OPS-002, STATE-003 | no |
| 31 | 0.749 | `Q::04_Tool与协议/Tool Calling与MCP.md::14` — 工具调用如何避免重复执行外部副作用？ | `Q::07_可靠性与安全/可靠性与安全.md::26` — 工具调用已经成功但前端断线了，重试前如何判断外部副作用是否已经发生？ | TOOL-001, TOOL-002 | no |
| 32 | 0.739 | `Q::03_Memory与状态/Memory与State.md::22` — 如何设计 State Schema 和状态版本？ | `Q::12_课程深化/03_Durable与生产运维/Durable与生产运维.md::35` — 如何处理状态 Schema 或执行策略升级后的旧任务？ | OPS-002, STATE-003 | no |
| 33 | 0.739 | `Q::10_模型与推理/高频八股与手撕面经补充.md::20` — 如何用程序验证和 LLM 评审共同判断一条 Agent 轨迹是否成功？ | `Q::12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md::6` — 为什么程序验证优先于 LLM Judge？ | EVAL-010, TEST-002 | no |
| 34 | 0.737 | `Q::03_Memory与状态/Memory与State.md::22` — 如何设计 State Schema 和状态版本？ | `Q::12_课程深化/01_Provider与框架/Provider适配与框架选型.md::20` — 模型、工具 Schema、Prompt 和 State Schema 升级时，兼容性应如何管理？ | OPS-002, STATE-003 | no |
| 35 | 0.727 | `Q::07_可靠性与安全/可靠性与安全.md::9` — 什么是 Prompt Injection？直接注入和间接注入有什么区别？ | `Q::07_可靠性与安全/可靠性与安全.md::31` — Prompt Injection 为什么不能只靠更强的 System Prompt 防御？ | SEC-007 | no |
| 36 | 0.725 | `Q::04_Tool与协议/Tool Calling与MCP.md::20` — 什么是 MCP？它解决了什么问题？ | `Q::04_Tool与协议/Tool Calling与MCP.md::24` — MCP 有什么优点和短板？ | MCP-001 | no |
| 37 | 0.722 | `Q::08_评测与可观测/评测与可观测性.md::33` — 如何为 Agent 设置 SLO、SLA 和安全指标？ | `Q::12_课程深化/03_Durable与生产运维/Durable与生产运维.md::15` — Agent 的 SLI/SLO 不应只监控哪些 HTTP 指标？ | OBS-003 | no |
| 38 | 0.715 | `Q::04_Tool与协议/Tool Calling与MCP.md::7` — 工具返回过大时如何截断、分页或摘要？ | `Q::09_工程化与系统设计/系统设计与取舍面经补充.md::9` — 工具返回超长结果时，如何做剪裁、摘要、分页和后续追问？ | TOOL-005 | no |
| 39 | 0.704 | `Q::04_Tool与协议/Tool Calling与MCP.md::22` — MCP Server 如何设计？工具、资源和 Prompt 如何组织？ | `Q::12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md::19` — MCP Server 中 Tool、Resource、Prompt 的边界是什么？ | MCP-002 | no |
| 40 | 0.701 | `Q::08_评测与可观测/评测与可观测性.md::24` — 如何回放一次历史 Agent 运行？ | `Q::12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md::5` — 一条可重放的 Agent 记录至少包含什么？ | REPLAY-001, TRACE-002 | no |
| 41 | 0.679 | `Q::09_工程化与系统设计/系统设计与取舍面经补充.md::1` — 面试时如何用一条因果链讲清 Agent 项目，而不是先背技术栈？ | `Q::13_跨主题综合题/新增题簇_Agent与AI后端.md::9` — 如何把一个 RAG/Agent 项目讲出业务价值，而不是只讲调用了模型？ | PROJECT-001 | yes |
| 42 | 0.676 | `Q::01_基础架构/Agent基础与架构.md::29` — 设计一个客服 Agent：哪些步骤用 Workflow，哪些步骤交给 Agent？ | `Q::05_Multi-Agent与Workflow/Multi-Agent与Workflow.md::2` — Workflow 与 Agent 的边界是什么？ | LOOP-002 | no |
| 43 | 0.676 | `Q::03_Memory与状态/Memory与State.md::24` — 进程崩溃后如何从 Checkpoint 恢复？ | `Q::03_Memory与状态/Memory与State.md::32` — 长任务运行到一半进程崩溃，如何判断哪些工具副作用已经发生，再从 Checkpoint 恢复？ | DUR-002, STATE-006, TOOL-002 | no |
| 44 | 0.672 | `Q::05_Multi-Agent与Workflow/Skill编排与协作面经补充.md::1` — “一个 Agent × N 个 Skill”与“多个专用 Agent”的核心差异是什么？ | `Q::12_课程深化/07_实时交互与产品/实时交互与产品.md::18` — Tool、Skill 和 MCP Server 的边界是什么？ | SKILL-001 | no |
| 45 | 0.584 | `Q::01_基础架构/Agent基础与架构.md::2` — Agent 的执行流程是什么 | `Q::01_基础架构/Agent基础与架构.md::9` — Agent Loop 在什么条件下继续执行、什么条件下结束？ | LOOP-003, LOOP-008, LOOP-011 | no |
| 46 | 0.472 | `Q::06_RAG与知识库/RAG与检索.md::27` — 知识系统处理更新、删除和权限变化时，在线检索侧需要额外做什么？ | `Q::12_课程深化/04_知识摄取与GraphRAG/知识摄取与GraphRAG.md::7` — 知识系统如何处理更新、删除、重命名和权限变化？ | INGEST-002 | no |
| 47 | 0.405 | `Q::03_Memory与状态/Memory与State.md::6` — Memory 与 RAG 的边界是什么？ | `Q::03_Memory与状态/Memory与State.md::7` — Memory 与普通数据库、缓存和日志的边界是什么？ | MEM-014 | no |
