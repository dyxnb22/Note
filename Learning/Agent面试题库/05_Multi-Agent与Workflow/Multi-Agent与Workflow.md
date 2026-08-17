# Multi-Agent、Workflow 与 Harness

> 递进路径：先建立单 Agent 基线，再决定是否拆分，随后处理通信、约束和故障传播。

## Level 1｜基础认知：什么时候需要多 Agent

1. 单 Agent、多 Agent、Agent + Workflow 如何选型？
2. 多 Agent 相比单 Agent 的收益和代价是什么？
3. Master + Sub-Agent 架构如何设计？
4. Planner、Executor、Critic、Router、Supervisor 分别负责什么？
5. 多 Agent 拆分的依据是什么？如何决定任务边界？
6. 什么场景适合多 Agent，什么场景只是增加复杂度？
7. Workflow 与 Agent 的边界是什么？
8. Workflow 的优点和问题是什么？
9. 如何让 Workflow 中的某一步具备 Agent 的灵活性？
10. 如何避免多 Agent 之间重复劳动、循环调用和责任不清？

## Level 2｜原理机制：Agent 如何协作

11. 多 Agent 如何通信？消息、共享状态、黑板和事件总线分别有什么特点？
12. 多 Agent 如何共享 State？如何处理状态一致性和并发写入？
13. 如何控制 Agent 并发量？
14. 哪些子任务适合并行，哪些必须串行？
15. 并行 Agent 的结果如何合并？冲突如何解决？
16. 一个 Agent 如何把任务委派给另一个 Agent？
17. 如何设置子 Agent 的权限和能力边界？
18. 子 Agent 失败时，父 Agent 如何重试、降级和接管？
19. 如何让多 Agent 任务支持取消、暂停、恢复和重放？
20. 多 Agent 并发会产生哪些性能问题？

## Level 3｜工程约束：Harness 如何把模型变得可控

21. 什么是 Harness？它如何约束和增强模型？
22. Harness 与 Skill、Prompt、Tool、CLI 的关系是什么？
23. Harness 如何降低幻觉？
24. 如何通过 Harness 强制 Agent 先取数据、再执行分析、最后生成结论？
25. 如何防止模型跳过工具调用、假装执行或伪造结果？
26. 如何让 Agent 的每个关键步骤都可验证？
27. 如何设计模型不可绕过的权限边界？
28. 如何把确定性校验、重试和人工确认插入 Agent Loop？
29. 如何设计 Harness 的日志、Trace 和回放能力？
30. 如何评估增加 Harness 后的收益和额外成本？

## Level 4｜场景追问：从单 Agent 演进到多 Agent

31. 一个研究任务包含检索、分析、写作三个阶段，你会选择 Workflow、Supervisor 还是多个独立 Agent？
32. 两个子 Agent 对同一个事实给出冲突结论，父 Agent 如何判断、合并或升级人工？
33. 多 Agent 的平均效果提升了，但延迟和成本翻倍，如何判断是否值得上线？
34. 如果子 Agent 经常重复调用同一个工具，应该修改拆分、通信协议、Harness 还是 Prompt？
