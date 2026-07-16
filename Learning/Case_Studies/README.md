# Case Studies

这里保存用于验证知识的业务、AI、产品和源码案例。案例文档回答“项目怎么做、证据在哪里、哪些结论可以迁移”，不替代主题文档。

产品文档案例统一放在 [产品文档与需求分析](../References/产品文档与需求分析.md)，避免同一套 PRD 同时出现在参考层和案例层。

## 业务案例

- [拼团交易平台](./Backend/拼团交易平台.md)：交易、营销、库存、支付、组队和补偿。
- [Redis 轻量游戏状态](./Backend/Redis轻量游戏状态.md)：轻量状态建模、Redis 生命周期和双语言实现边界。
- [业务项目能力地图](./Backend/业务项目能力地图.md)：支付、营销、抽奖、IM 和外卖项目的共同骨架。

## AI 案例

- [AI MCP Gateway](./AI/AI-MCP-Gateway.md)：协议转换、工具治理和分布式 Session。
- [WaLiSSH](./AI/WaLiSSH.md)：SSH 工具化、Agent Loop、凭证保护和服务端边界。
- [Agent 脚手架与可编排 RAG](./AI/Agent脚手架与可编排RAG.md)：Workflow、MCP、Skills、Session 和动态 Agent。

## 源码审计

源码审计按“入口 → 模块 → 核心链路 → 配置/测试 → 运行边界”记录，统一入口见 [源码审计总览](./Source_Audits/源码审计总览.md)。

## 使用方式

先读主题文档，再用案例验证设计；看到项目中的特殊实现时，区分“通用模式”和“项目约束”，不要把单个仓库的取舍当成通用规则。
