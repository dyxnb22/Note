# 云原生与 IaC

本篇在 Docker、Kubernetes 和 CI/CD 之上，覆盖云资源、身份、网络、Terraform、GitOps、服务网格、多集群和成本治理。

## 1. 云资源责任边界

先理解共享责任模型：云厂商负责哪些物理/托管层，用户仍负责身份、网络、配置、数据、应用与备份。

托管服务降低部分运维，但不会自动解决 Schema、容量、权限、灾备和成本。

## 2. 账户与环境

生产、测试和开发使用独立账户/项目与权限边界。统一：

- 命名、标签和负责人。
- 区域与数据驻留。
- 日志与审计汇聚。
- 预算和配额。
- Break-glass 紧急访问。

不要只用 VPC 或 Namespace 假设完成强隔离。

## 3. IAM

主体包括人、服务和自动化流水线。优先短期凭证与工作负载身份，避免长期 Access Key。

权限设计：

- 默认拒绝。
- 最小 Action/Resource/Condition。
- 区分部署身份和运行身份。
- 高风险操作审批与 MFA。
- 定期 Access Review。
- 审计未使用权限和异常调用。

## 4. 云网络

理解 VPC/VNet、子网、路由表、安全组、NACL、NAT、负载均衡、Private Endpoint 和 DNS。

设计时区分：

- 公网入口。
- 应用层。
- 数据层。
- 管理平面。
- 出站访问。

默认禁止不必要的东西向和出站流量。网段规划预留集群、跨网络和未来扩容，避免地址重叠。

## 5. Terraform 基础

IaC 把期望资源写成可 Review、可重复的声明。Terraform 工作流：

```text
format/validate → plan → review → apply
→ observe → drift detection
```

State 包含敏感资源信息，需要远程加密存储、锁和最小权限。不能手工修改 State 作为日常流程。

## 6. Module

Module 封装稳定资源组合，暴露最小输入和输出。避免一个“万能 Module”包含大量布尔开关。

版本化 Module，升级前查看 Plan 和迁移说明。Provider 版本和 Lock File 进入版本控制。

## 7. Drift 与导入

控制台手工修改会造成 Drift。紧急修改后应尽快回写代码并 Review。

接管已有资源时先 Import/声明并确保 Plan 不产生意外销毁，再逐步标准化。

## 8. CI/CD 与 IaC

Pull Request 自动执行 Validate、Lint、安全扫描和 Plan；Apply 使用受保护环境和短期身份。

高风险变更包括删除、替换、网络、IAM、数据库和状态后端，需要额外审批和备份验证。

## 9. GitOps

GitOps 用 Git 中声明状态驱动集群控制器持续 Reconcile。优点是审计、回滚和 Drift 可见。

Secret 不能明文放 Git；使用加密 Secret 或外部 Secret 管理。Git 回滚配置不一定回滚数据库和外部副作用。

## 10. Gateway 与服务网格

Ingress/Gateway 处理南北向路由；Service Mesh 处理服务间身份、策略、遥测和流量。

网格会增加代理资源、证书、升级和排障层次。若只需要少量 TLS/Trace 能力，不应为“云原生”标签盲目引入。

## 11. 多集群与多区域

先明确目标：

- 故障隔离。
- 地域延迟。
- 法规与数据驻留。
- 独立发布。
- 容量。

多集群需要统一身份、配置、版本、服务发现、数据复制和故障切换。应用多活但数据库单区，通常仍不是完整多活。

## 12. 灾备

定义 RPO/RTO、故障范围和切换负责人。备份跨账户/区域保存并定期恢复。

演练包括 DNS、证书、Secret、镜像、配置、数据库、队列和第三方回调，不只启动备用集群。

## 13. 可观测性

统一资源、集群和应用标签，使成本、日志、指标和 Trace 能关联服务版本与负责人。

控制平面审计、IAM、网络流日志和应用事件进入集中但受权限保护的证据链。

## 14. FinOps

成本按团队、服务、环境和业务指标分配。关注：

- 闲置资源和过高 requests。
- 存储生命周期和快照。
- 跨区/公网传输。
- 日志与指标高基数。
- 预留/按需/抢占实例取舍。
- 单位业务成本。

降低成本不能破坏可靠性余量和恢复能力。

## 15. 安全

镜像签名、Admission Policy、Secret 管理、Runtime Policy、网络隔离、主机加固和供应链共同构成防线。

禁止公开控制面、特权工作负载和无审计紧急权限。

## 最小项目

使用 Terraform 和 GitOps 部署一个 Kubernetes API：

1. 建立网络、IAM 和集群。
2. 配置工作负载身份与 Secret。
3. PR 输出 Plan，受控 Apply。
4. GitOps 部署 Canary。
5. 接入成本和可观测性。
6. 模拟区域故障并按 Runbook 恢复。

## 验收清单

- 云账户、网络、身份和环境隔离明确。
- IaC State、Plan、Apply 和 Drift 受控。
- GitOps 与数据库迁移边界清楚。
- 多集群/多区域有数据和流量故障模型。
- 成本可归属且不牺牲 SLO。

## 来源与验证边界

资源语义以使用的云平台、Terraform Provider、Kubernetes/Gateway/GitOps 工具官方文档为准。IAM、网络和托管服务默认值可能变化，生产变更必须审阅 Plan 并在隔离环境验证。

## 导航与关联

- [模块入口：Delivery](./README.md)
- 同一路线：[生产系统工程](./07_生产系统工程.md) · [Agent 部署与生产化](../../Agent/12_部署与生产化.md)

`#cloud-native #terraform #iac #gitops #iam`
