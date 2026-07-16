# Delivery

这里放把服务跑起来、交付出去、稳定维护时会用到的内容。

## 这个目录解决什么问题

- 本地代码如何安全协作和发布
- 服务如何打包、部署、启动、重启、回滚
- 线上出问题时怎么用 Linux 和日志先把现场看清
- 如何把“手工上线”逐步演进到“可重复交付”

## 主题

- [Git](/Users/diaoyuxuan/Documents/Notes/Learning/Backend/Delivery/Git.md)：版本控制、分支协作、冲突处理、回退
- [Linux 命令详解指南](/Users/diaoyuxuan/Documents/Notes/Learning/Backend/Delivery/Linux%20命令详解指南.md)：登录服务器后最常用的排查命令
- [Docker](/Users/diaoyuxuan/Documents/Notes/Learning/Backend/Delivery/Docker.md)：镜像、容器、Dockerfile、Compose
- [Kubernetes](/Users/diaoyuxuan/Documents/Notes/Learning/Backend/Delivery/Kubernetes.md)：Pod、Service、发布、探针、资源与弹性
- [部署与上线](/Users/diaoyuxuan/Documents/Notes/Learning/Backend/Delivery/部署与上线.md)：从单服务启动到可回滚上线
- [CI_CD](/Users/diaoyuxuan/Documents/Notes/Learning/Backend/Delivery/CI_CD.md)：自动构建、自动测试、自动发布

## 建议顺序

1. 先掌握 `Git`
2. 再熟悉 `Linux 命令详解指南`
3. 然后看 `Docker`
4. 再读 `部署与上线`
5. 最后补 `CI_CD`

## 边界

- 偏部署、运维、交付流程的内容放这里
- 偏服务本身的设计与拆分，放 `Architecture`
- 偏数据库、中间件使用方式，放 `Data`
