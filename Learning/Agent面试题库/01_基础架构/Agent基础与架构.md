# Agent 基础与架构

> 递进路径：先判断边界，再讲运行时，最后完成架构设计和场景取舍。

## Level 1｜基础认知：是什么，为什么需要

1. 什么是 Agent？与普通 LLM Chat、Workflow、RPA 和传统后端服务有什么区别？
2. Agent 的最小闭环是什么？
3. 一次 Agent 请求从用户输入到最终回答经过哪些阶段？
4. Agent 如何理解任务、制定计划、调用工具、观察结果并结束任务？
5. Agent 的自主性体现在哪里？自主性越强一定越好吗？
6. 什么场景适合 Agent，什么场景应该使用确定性的 Workflow？
7. Agent 系统中哪些部分应该由模型决定，哪些部分应该由代码决定？
8. Agent Framework、Agent Runtime 和 Agent Application 有什么区别？
9. 如何从 Demo 演进到生产级 Agent？
10. Agent 系统最重要的设计部分是什么？

## Level 2｜原理机制：如何运行，如何结束

11. ReAct 是什么？Reasoning、Action、Observation 如何循环？
12. Agent Loop 在什么条件下继续执行、什么条件下结束？
13. Plan-and-Execute 与 ReAct 有什么区别？
14. Reflection、Critic、Self-Consistency 分别解决什么问题？
15. Router 模式是什么？如何设计路由条件和兜底分支？
16. Planner、Executor、Critic 分别负责什么？
17. 如何让 Agent 判断任务已经完成？
18. 如何避免每一步重新规划导致路径震荡？
19. 如何避免 Agent 重复调用同一个工具？
20. 如何处理计划执行到一半发现前提不成立的情况？
21. 长任务应该一次性规划还是边执行边规划？为什么？
22. 如何为 Agent 设置最大步数、超时、Token 和成本预算？

## Level 3｜设计取舍：如何选型，如何拆分

23. 单 Agent、多 Agent、Agent + Workflow 如何选型？
24. Master + Sub-Agent 架构的优点和问题是什么？
25. 多 Agent 拆分的依据是什么？如何决定任务边界？
26. 多 Agent 相比单 Agent 增加了哪些通信、状态和调度成本？
27. 如何设计一个客服 Agent、搜索 Agent、数据分析 Agent 或代码 Agent？
28. 如果让你从零设计一个企业级 Agent 平台，模块如何拆分？
29. Agent 如何支持暂停、恢复、取消、人工接管和重新执行？
30. 如何设计 Agent 的状态机？
31. 如何让长任务跨进程、跨机器持续运行？
32. 如何处理 Agent 运行中模型、工具、数据库或网络故障？
33. Agent 如何进行模型路由和多模型 Fallback？
34. Agent 如何接入已有业务系统而不破坏原有流程？
35. 如何从业务目标反推 Agent 的能力边界和成功标准？

## Level 4｜场景追问：把架构落到真实业务

36. 设计一个客服 Agent：哪些步骤用 Workflow，哪些步骤交给 Agent？
37. 设计一个 Coding Agent：如何处理仓库读取、命令执行、测试和失败恢复？
38. 设计一个数据分析 Agent：如何保证模型不能跳过计算直接编造结论？
39. 如果单 Agent 已经能完成任务，什么证据能证明拆成多 Agent 值得？
40. 如果线上任务偶发卡死，你会优先检查 Loop、State、工具还是外部依赖？为什么？
