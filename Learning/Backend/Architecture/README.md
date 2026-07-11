# Architecture

这里放系统层面的设计和扩展问题。

## 这个目录解决什么问题

- 单机方案为什么会撑不住
- 系统拆开后会出现哪些一致性、可用性和治理问题
- 面试里的系统设计题应该按什么顺序回答
- 真正上线后怎么做高可用、限流、降级、重试和容灾

## 主题

- [系统设计](/Users/diaoyuxuan/Documents/Notes/Learning/Backend/Architecture/系统设计.md)：设计题答题框架和典型场景
- [分布式](/Users/diaoyuxuan/Documents/Notes/Learning/Backend/Architecture/分布式.md)：CAP、分布式锁、事务、RPC、注册中心
- [高可用与服务治理](/Users/diaoyuxuan/Documents/Notes/Learning/Backend/Architecture/高可用与服务治理.md)：超时、重试、幂等、限流、熔断、降级、容灾

## 建议顺序

1. 先看 `系统设计`
2. 再看 `分布式`
3. 最后补 `高可用与服务治理`

## 边界

- 偏数据库、缓存、MQ 本身的细节放 `Data`
- 偏部署、发布、CI/CD、上线运维放 `Delivery`
- 偏服务拆分、流量治理、容灾和一致性取舍放这里
