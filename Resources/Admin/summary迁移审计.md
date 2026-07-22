# summary 迁移审计

源目录：`/Users/diaoyuxuan/Desktop/summary`

处理原则：以 `Learning` 中已有主题笔记为主，不复制原目录结构；只合并源笔记中独有且可复用的文字内容，删除重复背景、旧版本误导和命令堆砌。源目录中的图片不迁移到 Notes，图中知识只在必要时改写为文字。

## 逐文件状态

| 源文件 | 目标位置 | 状态 | 处理说明 |
| --- | --- | --- | --- |
| `Java.md` | `Learning/Backend/Java/Java.md`、`Java集合.md` | 已合并 | 补入 API/SPI、类初始化顺序、`assert`；其余基础和集合内容目标笔记已覆盖。 |
| `JUC.md` | `Learning/Backend/Java/JUC.md` | 已合并 | 补入守护线程、未捕获异常；锁、JMM、线程池等目标笔记更完整。 |
| `JVM.md` | `Learning/Backend/Java/JVM.md` | 已覆盖 | 目标笔记已覆盖对象分配、TLAB、GC、类加载、OOM 和诊断；源文件中的图片和旧表述不保留。 |
| `MySQL.md` | `Learning/Backend/Data/MySQL.md` | 已合并 | 补入 DECIMAL/FLOAT/DOUBLE、视图/存储过程/触发器、管理命令和删除风险；理论主体目标笔记已覆盖。 |
| `Redis.md` | `Learning/Backend/Data/Redis.md` | 已覆盖 | 目标笔记已覆盖持久化、事务、数据结构、集群、缓存问题和实战方案。 |
| `Spring.md` | `Learning/Backend/Java/Spring.md` | 已覆盖 | IoC、AOP、事务、生命周期、循环依赖和扩展点目标笔记已更系统。 |
| `SpringBoot.md` | `Learning/Backend/Java/Spring.md` | 已覆盖 | 自动配置、Starter、注解和跨域内容已归入 Spring 主文档。 |
| `SpringMVC.md` | `Learning/Backend/Java/Spring.md` | 已覆盖 | 请求流程、组件和注解已归入 Spring MVC 章节。 |
| `SpringCloud.md` | `Learning/Backend/Java/Spring.md`、`Learning/Backend/Architecture/分布式.md` | 已筛选 | 只保留微服务、网关、注册发现和服务治理共性；Eureka/Zuul/Ribbon/Hystrix 等旧技术不作为当前主线重复维护。 |
| `MyBatis.md` | `Learning/Backend/Java/Spring.md` | 已覆盖 | 配置、映射、缓存、插件、事务和运行原理已归入 MyBatis 章节。 |
| `Network.md` | `Learning/CS/Network.md` | 已覆盖 | HTTP、TCP、DNS、TLS、I/O 和网络排障目标笔记已更完整。 |
| `Nginx.md` | `Learning/CS/Network.md` | 已合并 | 补入请求匹配、Master/Worker、被动故障探测和 502/503/504 排障；不迁移图片和零散配置问答。 |
| `OS.md` | `Learning/CS/OS.md` | 已覆盖 | 进程、内存、文件系统、中断、I/O 多路复用和零拷贝目标笔记已覆盖。 |
| `Linux.md` | `Learning/Backend/Delivery/Linux 命令详解指南.md` | 已覆盖 | 命令内容目标笔记已更完整。 |
| `数据结构.md` | `Learning/CS/数据结构.md`、`Learning/CS/算法/` | 已覆盖 | 基础概念和算法题型已有对应主题笔记。 |
| `计算机组成.md` | `Learning/CS/计算机组成.md` | 已合并 | 补入补码溢出、IEEE 754、RISC/CISC、流水线冒险和校验码能力边界；图示改为文字。 |
| `设计模式.md` | `Learning/Backend/Java/设计模式.md` | 已覆盖 | 目标笔记已按变化点、模式边界和落地场景重写，优于源文件的逐模式速记。 |
| `Kafka.md` | `Learning/Backend/Data/消息队列.md` | 已覆盖 | Kafka 核心模型、性能、分区、ISR、ACK 和 Rebalance 已覆盖；源文件的图片和空标题不保留。 |
| `RabbitMQ.md` | `Learning/Backend/Data/消息队列.md` | 已合并 | 补入交换器选择、Publisher Confirm、持久化、手动 ACK、幂等、重试和死信。 |
| `ZooKeeper.md` | `Learning/Backend/Architecture/分布式.md` | 已覆盖 | 注册中心、ZAB、角色和分布式协调已有更完整主题；源文件仅保留少量重复介绍。 |
| `Docker.md` | `Learning/Backend/Delivery/Docker.md` | 空文件，跳过 | 目标笔记已有完整 Docker 内容，源文件没有正文。 |
| `Netty.md` | `Learning/CS/Network.md` | 空文件，跳过 | 目标笔记已有 Netty 线程模型、拆包和性能章节，源文件没有正文。 |
| `Tomcat.md` | `Learning/Backend/Java/Tomcat.md` | 空文件，跳过 | 目标笔记已有 Tomcat 层次、线程、Servlet 和集群章节，源文件没有正文。 |

## 删除前检查

- [x] 所有当前 Markdown 源文件都有目标去处或明确跳过原因。
- [x] 没有向 Notes 复制源目录图片。
- [x] 新增内容已检查重复的二级标题。
- [x] 源笔记中的明显过时或错误表述未直接迁移。
- [ ] 删除源目录前确认 `summary` Git 历史中是否还有需要保留的已删除文件。
- [ ] 删除源目录前确认用户不需要保留原始图片和未迁移的个人材料。

本审计只说明“知识迁移范围”，不代表源目录的 Git 历史、图片和未迁移个人材料可以自动恢复；删除前仍需完成最后两项确认。

## 源目录 Git 历史补查

工作区当前已删除、但仍存在于 `summary` 的 `HEAD` 中的文件也已检查：

- `Dubbo.md`、`mall.md`、`拆团营销.md`：空文件。
- `summary.md`、`性能优化.md`：只有目录或空白标题，没有可复用正文。
- `ElasticSearch.md`、`Git.md`：现有 `Learning/Backend/Data/搜索与Elasticsearch.md` 和 `Learning/Backend/Delivery/Git.md` 已明显更完整。
- `操作系统.md`、`计算机网络.md`、`高并发&多线程.md`：分别被 `CS/OS`、`CS/Network`、`Backend/Java/JUC` 覆盖。
- `算法.md`：现有 `Learning/CS/算法/` 已按题型拆分，结构和内容更适合作为主线。

因此，历史 Markdown 中没有发现尚未安置且值得恢复的独立主题；Git 历史本身、图片和个人项目材料仍属于源目录的可选归档内容，不再复制到 Notes。

## Desktop/Notes 迁移审计

源目录：`/Users/diaoyuxuan/Desktop/Notes`

该目录当前 Markdown 约 1,658 行，并包含约 79 张图片。图片不迁移；图片中的必要知识改写为文字。

| 源文件 | 目标位置 | 状态 | 处理说明 |
| --- | --- | --- | --- |
| `Javaweb.md` | `Learning/Backend/Java/Spring.md`、`Learning/Backend/Delivery/Maven.md` | 已精选合并 | 补入 Spring MVC 参数绑定、REST 接口约定、文件/配置/全局异常处理、MyBatis 动态 SQL；Maven 单独整理依赖、生命周期、多模块和私服。 |
| `MySQL.md` | `Learning/Backend/Data/MySQL.md` | 已精选合并 | 补入批量写入/导入边界和 InnoDB 一致性备份；索引、事务、锁和 SQL 优化主体已由目标笔记覆盖。 |
| `Redis.md` | `Learning/Backend/Data/Redis.md`、`Learning/Backend/Architecture/认证、授权与多租户.md` | 已精选合并 | 补入客户端与序列化策略、Token 续租拦截器边界；缓存、分布式锁、秒杀和队列主体已由目标笔记覆盖。 |
| `Untitled.md` | — | 跳过 | 仅有两行，无独立价值。 |
| 历史 `Git.md`、`Markdown.md`、`操作系统.md`、`计算机网络.md` 等 | 现有对应主题笔记 | 已检查/跳过 | Git、操作系统和网络已有更完整目标笔记；Markdown 为基础语法速记，不纳入当前主线。 |

本轮迁移仍不代表源目录可以立即删除：其中有 Git 历史、未提交状态、图片和未迁移个人材料。建议完成最终复核后再归档或删除。
