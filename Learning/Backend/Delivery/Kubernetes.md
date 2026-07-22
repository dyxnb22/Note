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
