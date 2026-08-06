# Kubernetes

Kubernetes（K8s）是容器编排平台，负责容器的调度、服务发现、滚动发布、自动修复和弹性伸缩。

## 核心组件

| 组件 | 作用 |
| --- | --- |
| kube-apiserver | 集群统一入口，校验请求并读写集群状态 |
| etcd | 保存 Kubernetes 资源和集群元数据，基于 Raft 保证一致性 |
| scheduler | 为未绑定节点的 Pod 选择合适 Node |
| controller-manager | 持续比较期望状态与实际状态并执行修复 |
| kubelet | Node 上的代理，负责 Pod 生命周期、探针和状态上报 |
| kube-proxy | 为 Service 维护转发规则 |
| CoreDNS | 提供集群内 DNS 服务发现 |

## Pod、Deployment、Service 分别解决什么问题？

- Pod 是最小调度单位，内含一个或多个共享网络、存储和生命周期的容器。
- Deployment 通过 ReplicaSet 管理无状态 Pod 副本，支持滚动更新、扩缩容和回滚。
- Service 为一组标签匹配的 Pod 提供稳定访问入口，并屏蔽 Pod IP 变化。
- StatefulSet 适合需要稳定身份和持久存储的有状态服务；DaemonSet 保证每个指定 Node 运行一个 Pod；Job/CronJob 适合一次性或定时任务。

## 创建 Pod 的流程是什么？

客户端请求先到 apiserver，apiserver 校验后把对象写入 etcd；scheduler 选择 Node，kubelet 监听到绑定结果后调用容器运行时创建容器和网络/卷，并把状态回报给 apiserver。

## liveness、readiness、startup 探针有什么区别？

- `livenessProbe`：判断进程是否仍然健康，失败通常触发重启。
- `readinessProbe`：判断是否可以接收流量，失败时从 Service 后端摘除，不重启容器。
- `startupProbe`：给启动慢的应用预留启动时间，成功前可抑制 liveness/readiness 的误判。

探测方式常见有 Exec、HTTP GET 和 TCP。探针要检查应用自身状态，外部依赖短暂故障不应直接导致容器被误杀。

## Service 常见类型是什么？

- `ClusterIP`：集群内部访问，默认类型。
- `NodePort`：在每个 Node 暴露端口，适合简单外部访问。
- `LoadBalancer`：借助云厂商负载均衡暴露服务。
- `Ingress`：按域名、路径把 HTTP/HTTPS 请求路由到多个 Service，通常由 Ingress Controller 实现。

## Kubernetes 如何滚动发布和回滚？

Deployment 更新 Pod 模板后逐步创建新 ReplicaSet、减少旧副本，避免一次性中断服务。通过 `maxSurge` 控制额外新副本数，`maxUnavailable` 控制更新期间最多不可用副本数；发布前应配 readiness 探针，避免未就绪 Pod 提前接流量。异常时回滚到历史 ReplicaSet，并结合发布状态和业务探针确认结果。

## 资源配置和配置管理怎么做？

- `requests` 用于调度时预留资源，`limits` 限制容器最大使用量；CPU 超限通常被限速，内存超限可能触发 OOMKill。
- ConfigMap 保存普通配置，Secret 保存敏感配置；Secret 仍需配合权限控制和外部密钥管理，不能把它当作天然加密保险箱。
- HPA 根据 CPU、内存或自定义指标调整副本数；扩容前要确认镜像、数据库和下游依赖也能承受流量。

## 调度

Scheduler 先过滤不满足条件的 Node，再对候选节点评分。影响调度的因素包括：

- requests 与可分配资源。
- nodeSelector、Node Affinity。
- Pod Affinity/Anti-Affinity。
- Taint 与 Toleration。
- Topology Spread Constraint。
- Priority 与 Preemption。

requests 过低会造成节点过度装箱和运行时争抢；过高会造成资源闲置和 Pending。应以实际使用分布和故障余量校准。

## 集群网络

Kubernetes 网络模型通常要求每个 Pod 拥有可路由 IP，Pod 间不依赖显式 NAT。CNI 插件负责创建网络接口、地址分配和路由/隧道。

需要区分：

- Pod IP：生命周期短。
- Service ClusterIP：稳定虚拟入口。
- Ingress/Gateway：七层路由。
- NetworkPolicy：限制允许的网络流量；未安装支持它的网络插件时可能不生效。

排障顺序：DNS → Service/EndpointSlice → Pod readiness → NetworkPolicy → CNI 路由 → 应用监听地址。

## 存储

- Volume：Pod 内容器共享的存储挂载。
- PV：集群存储资源。
- PVC：工作负载对存储的声明。
- StorageClass：动态供给策略。
- CSI：存储插件接口。

有状态服务还要考虑访问模式、拓扑绑定、快照、扩容、备份和故障转移。PVC 存在不代表数据已备份。

## RBAC 与工作负载身份

RBAC 由 Role/ClusterRole 和 RoleBinding/ClusterRoleBinding 组合。ServiceAccount 为 Pod 提供工作负载身份。

原则：

- 默认拒绝、最小权限。
- 避免给普通工作负载绑定 `cluster-admin`。
- 不把长期 Token 烘焙进镜像。
- 限制读取 Secret、创建 Pod、Exec 和端口转发等高风险权限。
- 审计控制面关键操作。

## 弹性与中断

HPA 扩副本，VPA 调整资源建议或配置，Cluster Autoscaler 扩节点。弹性依赖完整链路：

```text
指标及时 → 扩容决策 → 节点容量 → 镜像拉取
→ Pod 启动 → readiness 通过 → 下游可承载
```

PodDisruptionBudget 约束自愿中断期间的可用副本，但不能防止节点突然故障。优雅终止需要处理 SIGTERM、停止接流量、完成或转移在途任务，并在超时后退出。

## 可观测性

至少采集：

- 控制面和节点健康。
- Pod 重启、Pending、OOMKill 和驱逐。
- requests/limits 与实际使用。
- Deployment 发布进度。
- Service 延迟、错误率和吞吐。
- 事件、审计日志和应用 Trace。

不要只根据 Pod Running 判断服务可用；还要验证 readiness 和业务 SLI。

## 故障排查顺序

1. `kubectl get` 确认资源状态和期望副本。
2. `describe` 查看调度、探针、拉镜像和挂载事件。
3. 查看当前及上一次容器日志。
4. 检查资源限制、OOM、节点压力和驱逐。
5. 检查 Service、EndpointSlice、DNS 和 NetworkPolicy。
6. 对比最近发布、配置、Secret 和数据库迁移。
7. 必要时进入临时调试容器，不直接修改生产容器状态。

## Kubernetes 最小实践

部署一个带数据库依赖的 API：

- 配置 requests/limits 与三类探针。
- 使用 ConfigMap、Secret 和 ServiceAccount。
- 配置滚动发布、PDB 与 HPA。
- 加入 NetworkPolicy。
- 模拟 Pod 崩溃、节点中断和错误配置。
- 记录发现证据、恢复步骤和回滚条件。

## 导航与关联

- 同一路线：[日志与可观测性](./日志与可观测性.md) · [部署与上线](./05_部署与上线.md)
