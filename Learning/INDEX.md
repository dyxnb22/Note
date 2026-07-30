# Learning 总索引

这里是按“可复用知识”组织的长期学习库。课程、项目和资料只作为来源或案例，最终知识归入主题。

本页（`INDEX.md`）负责学习路线、目标导航和推荐阅读；目录结构、内容边界和维护规则见 [Learning README](./README.md)。

## 技术主线

```text
计算机基础 → 后端工程 → 系统设计 → AI 应用工程 → 案例验证 → 职业表达
```

金融、健康、历史与社会、Web3、写作与表达是并列的专题路线，不是技术主线的后续阶段。进入这些主题时直接使用对应索引，不需要先读完技术目录。

## 按目标进入

| 目标 | 入口 |
|---|---|
| 补计算机底座 | [CS](./CS/README.md) |
| 做 Java/Go/Rust 后端 | [Backend](./Backend/README.md) |
| 用 Go 做生产后端 | [Go 正式路线](./Backend/Go/README.md) → [Go 后端实战](./Backend/Go/05_Go后端项目实战.md) |
| 学 LLM 原理 | [AI](./AI/README.md) |
| 学 Python → AI → Agent | [学习地图](./00_Navigation/AI-Python-Agent学习地图.md) |
| 用 Rust 做 Agent Runtime | [Rust/Go 目标地图](./00_Navigation/Rust-Agent与Go后端学习地图.md) → [Rust Agent 工程化](./Backend/Rust/16_Rust%20Agent工程化.md) |
| 做 Agent、RAG、MCP | [Python](./Python/README.md) → [AI](./AI/README.md) → [Agent](./Agent/README.md) |
| 练系统设计 | [Backend/Architecture](./Backend/Architecture/README.md) |
| 看真实项目取舍 | [Case Studies](./Case_Studies/README.md) |
| 查术语、产品和技术资料 | [References](./References/README.md) |
| 准备面试和职业发展 | [Career](./Career/README.md) |
| 写 RFC、ADR、Runbook、复盘和困难沟通 | [专业技术文档与困难沟通](./Writing_and_Expression/05_Professional_Documents/专业技术文档与困难沟通.md) |
| 学金融与投资 | [Finance](./Finance/README.md) |
| 做金融实证与量化研究 | [金融进阶与实证研究](./Finance/15_Advanced_Practice/金融进阶与实证研究.md) |
| 管理健康与精力 | [Health and Energy](./Health_and_Energy/INDEX.md) |
| 建立长期电脑工作与恢复系统 | [长期工作健康与恢复](./Health_and_Energy/05_Sustainable_Work/长期工作健康与恢复.md) |
| 理解历史、制度和组织 | [History and Society](./History_and_Society/INDEX.md) |
| 理解计算机、AI 产业与数字社会 | [计算机、AI 产业与数字社会](./History_and_Society/05_Digital_Age/计算机AI产业与数字社会.md) |
| 学 Web3 机制和工程 | [Web3](./Web3/INDEX.md) |
| 学 Web3 高级工程与协议安全 | [Web3 高级工程与协议安全](./Web3/08_Advanced_Engineering/Web3高级工程与协议安全.md) |
| 学 TypeScript 工程 | [TypeScript](./TypeScript/README.md) |
| 补算法、证明、安全、编译与计算理论 | [CS 完整路线](./CS/README.md) |
| 学数据库系统原理 | [数据库系统原理](./Backend/Data/数据库系统原理.md) |
| 学性能、可观测性与 SRE | [生产系统工程](./Backend/Delivery/07_生产系统工程.md) |
| 学 ML 系统与模型交付 | [ML 系统与 MLOps](./AI/ML系统与MLOps.md) |
| 学数据工程与流处理 | [数据工程与流处理](./Backend/Data/数据工程与流处理.md) |
| 学云平台与 IaC | [云原生与 IaC](./Backend/Delivery/08_云原生与IaC.md) |
| 学重构与遗留系统演进 | [软件工程与演进式架构](./Backend/SoftwareEngineering.md) |
| 做系统故障实验 | [系统实验路线](./Case_Studies/System_Labs/README.md) |

## 如何使用这个索引

1. 第一次进入先读[知识地图](./00_Navigation/知识地图.md)，理解主题边界；需要判断事实可靠性时读[来源与证据](./00_Navigation/来源与证据.md)。
2. 从“按目标进入”中只选择一个当前目标，不把所有目录当成连续必修课。
3. 每个目标都按“主题正文 → 最小实践 → 故障或反例 → 证据记录 → 项目表达”形成闭环。

技术学习按目标选择路线：

- 通用软件系统： [CS](./CS/README.md) → [Backend](./Backend/README.md) → [系统实验](./Case_Studies/System_Labs/README.md)。
- Python、模型与 Agent 应用： [Python → AI → Agent 学习地图](./00_Navigation/AI-Python-Agent学习地图.md)。
- Go 生产后端与 Rust Agent Runtime： [Rust Agent 与 Go 后端学习地图](./00_Navigation/Rust-Agent与Go后端学习地图.md)。
- 项目和源码验证： [Case Studies](./Case_Studies/README.md) → [技术资料证据与复现工作流](./References/技术资料证据与复现工作流.md)。

金融、健康、历史与社会、Web3、写作与表达等专题，直接从上方目标表进入各自索引；它们各自维护先修关系、来源边界和实践方式。

## 内容边界

- 理论和方法进入主题文档；项目名称、源码结构和运行证据进入案例文档。
- 文档正文、README、源码和配置可以作为证据；视频不自动转写为已学习内容。
- “主题级提炼”“正文核验”“源码审计”“本地复现”分开记录，不混淆完成度。
- 每篇新增文档都应写清边界、失败场景、来源和相关主题。

## 文档状态

较短的文档不再仅凭字数判断质量；需要时用 frontmatter 明确它承担的工作：

- `type: concept / guide / reference / map / practice / case` 表示文档角色。
- `status: mature` 表示在该角色下已经闭环；速查表、地图和参考页可以短而成熟。
- `status: developing` 表示仍缺机制、反例、来源、运行结果或复盘证据，不应被当成定稿。
- 算法题卡和课程实验即使结论正确，未记录实现、测试或实验结果前仍保持 `developing`。

状态不是完成百分比。版本敏感内容还要单独记录 `last_verified`，并通过各模块的来源页重新核验。
