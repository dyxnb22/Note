# xfg-planet 迁移清单

源库：`/Users/diaoyuxuan/xfg-planet`，共 95 份 Markdown。目标库只维护归类后的主题、案例、参考和职业文档，不复制原目录结构。

## 处理规则

| 类型 | 做法 |
|---|---|
| 合并 | 进入已有主文档，删除重复背景、目录和讨论噪声 |
| 新建 | 没有合适主题时建立精简文档 |
| 案例 | 保留项目、PRD、源码和验证边界，回链主题 |
| 导航 | 只记录来源、覆盖和证据，不承载技术正文 |

## 目录归位

| 源目录 | 目标位置 | 处理 |
|---|---|---|
| `00-学习导航` | `INDEX.md`、`00_Navigation` | 合并导航、来源和进度 |
| `01-基础能力` | `CS`、`Backend` | 合并基础、DDD、调试、消息和分布式边界 |
| `02-AI应用范式` | `AI`、`Python Agent`、`Case_Studies/AI` | 主题归纳，项目单列案例 |
| `03-AI工程实践` | `Backend/Delivery`、`Python Agent`、`Case_Studies/AI` | 合并交付、部署和安全边界 |
| `04-系统设计与组件` | `Backend/Architecture`、`Backend/Data` | 提炼通用设计和 98 条场景索引 |
| `05-业务场景` | `Case_Studies/Backend` | 项目案例化，设计结论回链主题 |
| `06-源码与案例` | `Case_Studies/Source_Audits`、`Case_Studies/AI` | 保留源码链路、构建、测试和运行边界 |
| `07-工程化与部署` | `Backend/Delivery` | 合并 Docker、Linux、发布和运维入口 |
| `08-术语与参考` | `References` | 合并术语、技术小册、开源和科技资料 |
| `09-求职与职业` | `Career`、`Writing_and_Expression` | 提炼路线、招聘、成长和项目表达 |
| `99-归档` | 不迁移正文 | 仅保留源库归档边界 |

## 重点文件归位

| 源内容 | 目标主文档 |
|---|---|
| 课程清单、课程映射、学习进度 | [来源与证据](./来源与证据.md) |
| 基础能力知识、DDD、可靠性、消息与组件 | [DDD 与领域建模](../Backend/Architecture/DDD与领域建模.md)、[可靠性与一致性](../Backend/Architecture/可靠性与一致性.md) |
| 98 条场景索引与首批正文 | [场景方案库](../Backend/Architecture/场景方案库.md)、[场景逐项索引](../Backend/Architecture/场景逐项索引.md) |
| AI-MCP-Gateway、WaLiSSH、Agent/RAG | [AI 案例](../Case_Studies/AI/README.md) |
| 拼团、Redis 游戏、业务项目 | [业务案例](../Case_Studies/Backend/业务项目能力地图.md) |
| 源码阅读与逐文件审计 | [源码审计总览](../Case_Studies/Source_Audits/源码审计总览.md) |
| 产品文档、术语、小册、开源和科技资料 | [References](../References/README.md) |
| 招聘、职场材料和学习路线 | [Career](../Career/README.md) |

各级源 `README.md` 已折叠到目标目录入口；视频、图片占位、重复来源表和无法核验的外部内容不作为独立知识文档维护。原始材料仍保留在源库。
