# Case Studies

这里保存用于验证知识的业务、AI、产品和源码案例。案例文档回答“项目怎么做、证据在哪里、哪些结论可以迁移”，不替代主题文档。

PRD 的共用分析方法见[产品文档与需求分析](../Product_and_Decision/产品文档与需求分析.md)，具体项目仍放在案例文档中。

## 业务案例

- [业务案例索引](./Backend/README.md)：从共同能力地图进入拼团交易与 Redis 轻量状态两个深化案例。

## AI 案例

- [AI MCP Gateway](./AI/AI-MCP-Gateway.md)：协议转换、工具治理和分布式 Session。
- [WaLiSSH](./AI/WaLiSSH.md)：SSH 工具化、Agent Loop、凭证保护和服务端边界。
- [Agent 脚手架与可编排 RAG](./AI/Agent脚手架与可编排RAG.md)：Workflow、MCP、Skills、Session 和动态 Agent。

## 源码审计

源码审计按“入口 → 模块 → 核心链路 → 配置/测试 → 运行边界”记录；索引与阅读方法见 [Source Audits](./Source_Audits/README.md)。

- [开源项目能力索引](./开源项目能力索引.md)：把项目经验映射到可迁移能力。

## 系统实验

- [系统实验路线](./System_Labs/README.md)：小型数据库、解释器、Raft、HNSW、性能/SLO、ML 交付、三语言服务对照和数据流处理。

## 使用方式

先读主题文档，再用案例验证设计；看到项目中的特殊实现时，区分“通用模式”和“项目约束”，不要把单个仓库的取舍当成通用规则。

现有五个业务与 AI 案例均已补充深化实验：用状态机、并发/乱序、故障注入、权限测试、评测数据集和证据矩阵，把“代码中存在”与“已经运行验证”分开。
