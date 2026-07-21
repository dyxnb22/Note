# 多 Agent 协作的边界与模式

多 Agent 不是能力叠加器。仅当任务可分解、子任务相对独立、并行收益超过协调成本，或需要不同工具/权限隔离时才使用；否则单 Agent 加明确 workflow 更稳定、更便宜。

## 常见模式

manager-worker：管理者拆解并汇总；planner-executor：计划与执行分离；reviewer：独立检查关键输出；swarm：多个同类候选后投票/选择。每个 agent 必须有输入契约、输出 schema、预算、工具白名单和终止条件。

## 共享状态与安全

默认传递压缩后的显式产物，不共享无限对话历史。写操作必须串行化或使用事务/幂等键；子 agent 不继承父 agent 的全部权限。协调者要处理超时、重复、冲突、低质量结果和递归派生。

## 评估

比较多 agent 与单 workflow 的端到端质量、成本、延迟和失败率。若没有可量化提升，应删掉协作层。

`#multi-agent #orchestration #workflow`
