# Provider 适配与框架选型

> 递进路径：先分清 Provider、应用和 Runtime 的边界，再理解流式/结构化输出与图编排，最后回答框架选型和兼容性问题。

## Level 1｜Provider 与应用边界

1. 为什么 Agent 应该在 Provider SDK 外面增加 Adapter 层？
2. 一个内部统一的 `ModelResult` 至少应该包含哪些字段？
3. `messages`、Context、State 和调用元数据分别解决什么问题？
4. 为什么不能把某一家 Provider 的响应字段直接传到 Agent Runtime？
5. Streaming 只解决了什么问题？它没有解决什么问题？
6. JSON mode、结构化输出和业务语义校验之间是什么关系？
7. 为什么要记录 `request_id`、usage 和稳定的错误码？
8. 多模态输入接入时，Adapter 和业务层分别负责什么？

## Level 2｜运行机制与框架抽象

9. Provider 的 typed content block 如何归一化为内部 `ToolCall` 和 `ToolResult`？
10. `tool_call`、工具执行结果和最终文本在一次请求中的职责有什么不同？
11. 流式调用遇到断连、取消和重复事件时，系统如何保证结果一致？
12. 轻量 `while` Loop、显式 Workflow 和图编排分别适合什么场景？
13. 低代码 Agent 平台的价值和边界是什么？
14. 如何把 LangGraph 的 State、Node、Edge、Checkpoint 映射到通用 Agent Runtime？
15. 为什么生产环境不能只用内存 Checkpointer？
16. 图中的条件边应该如何设计，才能避免模型输出直接成为任意跳转？
17. `interrupt/resume` 怎样实现人工审批，而且恢复时不会绕过策略？
18. LangGraph 中共享 State、Reducer、子图和并行 Send 分别解决什么问题？

## Level 3｜选型与兼容性设计

19. 如何判断现有项目是否真的需要引入 Agent Framework？
20. 选择框架时如何权衡控制力、开发速度和运维成本？
21. 如何设计 Provider 替换，使业务代码不依赖某个模型厂商？
22. 模型、工具 Schema、Prompt 和 State Schema 升级时，兼容性应如何管理？
23. Adapter 层应该测试哪些异常和边界？
24. 为什么“框架节点数量”不能直接等同于“多 Agent 数量”？

## Level 4｜场景追问

25. 设计一个支持多 Provider、工具调用、流式输出和人工审批的 Agent Runtime，你会如何分层？
26. 一个简单问答项目逐渐加入循环、持久化、并行和恢复，你会在哪些信号出现后从 Loop 升级到图编排？
27. 如果切换 Provider 后工具调用频繁失败，你会从协议、Adapter、Prompt 还是模型能力哪一层开始定位？
28. 如果一个图编排系统上线后出现状态覆盖和恢复错乱，你会如何排查并改造？
