# 小林 Coding 与 JavaGuide 知识体系提炼

这份地图把小林 Coding 与 JavaGuide 的公开知识目录压缩成可检索的本地主题，并指向知识库中的主文档。它不复制原文，也不把站点目录当成另一套平行课程；遇到问题时先进入本地主题，再沿来源链接核对上下文和版本。

## 范围与证据边界

- 盘点日期：2026-08-20。
- “全部知识点”指两个站点公开导航和可访问文章中的主题节点、核心机制和工程边界，不等于逐段搬运原文。
- 只有课程名称、训练营介绍、视频或未公开正文的内容，只记录主题，不宣称完成正文核验。
- JavaGuide 的会员文章若正文不可见，只保留公开目录能确认的主题；小林 Coding 的训练营营销页不作为技术结论来源。
- 两站都未覆盖的 Agent/LLM 内容若进入题库，继续明确标注“通用补充”，不挂靠到两站名下。
- 版本敏感问题以题目所在文件的版本说明为准；本页只维护知识归属和来源入口。

## 一张图看完两站知识主干

```text
硬件与操作系统
  → 网络与 Web
  → 数据结构与算法
  → Java / Go / C++ / Python 工程
  → 数据库、缓存、搜索与消息
  → Spring、服务与安全
  → 分布式、高性能与高可用
  → 测试、交付、排障与求职
  → LLM、RAG、Agent、AI 系统与 AI Coding
```

## 计算机基础

| 主题 | 两站知识点提炼 | 本地归属 |
| --- | --- | --- |
| 计算机组成 | CPU 取指/译码/执行、流水线与分支预测；存储层次、局部性、缓存行、MESI 与伪共享；中断、DMA、浮点数和性能上限 | [计算机组成](../CS/01_计算机组成.md) |
| 操作系统 | 内核与系统调用；进程、线程、协程、调度和上下文切换；IPC、同步、死锁、futex；虚拟内存、缺页、回收与 OOM；文件系统、Page Cache、崩溃一致性 | [操作系统](../CS/05_OS.md) |
| 高性能 I/O | 阻塞/非阻塞、同步/异步；select/poll/epoll；LT/ET；Reactor/Proactor；零拷贝、软中断与 Linux 收包路径 | [操作系统](../CS/05_OS.md)、[网络](../CS/03_Network.md) |
| 网络分层 | OSI/TCP-IP、以太网、ARP、IP、ICMP、路由、NAT、DNS；一次 URL 请求的解析、连接、TLS、HTTP 和服务端链路 | [网络](../CS/03_Network.md)、[HTTP 与 Web](../CS/04_HTTP与Web协议.md) |
| TCP | 三次握手/四次挥手；序号、确认、重传、滑动窗口、流量/拥塞控制；半/全连接队列；粘包、Keepalive、TIME_WAIT；断电、进程崩溃和异常报文边界 | [网络](../CS/03_Network.md) |
| HTTP | 方法、状态码、缓存、Cookie/Session、HTTPS；HTTP/1.1 队头阻塞、HTTP/2 多路复用、HTTP/3/QUIC；RPC、WebSocket、SSE 的边界 | [HTTP 与 Web](../CS/04_HTTP与Web协议.md) |
| 数据结构 | 数组、链表、栈、队列、哈希、堆、树、图；红黑树、Trie、并查集、跳表、布隆过滤器、LRU | [数据结构](../CS/02_数据结构.md) |
| 算法 | 复杂度、排序、二分、双指针、滑动窗口、DFS/BFS、回溯、贪心、动态规划、TopK、字符串与链表边界 | [算法设计与复杂度](../CS/07_算法设计与复杂度.md)、[算法题目录](../CS/算法/README.md) |
| Linux 与 Shell | 文件、权限、进程、网络、磁盘、内存和文本处理命令；管道、重定向、Shell 脚本与线上证据链 | [Linux 命令](../Backend/Delivery/03_Linux%20命令详解指南.md) |

来源入口：[小林 Coding《图解网络》](https://xiaolincoding.com/network/)、[《图解系统》](https://xiaolincoding.com/os/)、[JavaGuide 计算机基础](https://javaguide.cn/cs-basics/)。

## 语言、运行时与构建

| 主题 | 两站知识点提炼 | 本地归属 |
| --- | --- | --- |
| Java 基础 | 类型、String、equals/hashCode、泛型、异常、反射、注解、序列化、代理、SPI、BigDecimal、Unsafe、Lambda/Stream 与语法糖 | [Java 题库](../Backend/Java/面试题库/README.md) |
| Java 集合 | List/Set/Map/Queue 选型；ArrayList、LinkedList、HashMap、ConcurrentHashMap 等实现、扩容、冲突和并发边界 | [集合与容器](../Backend/Java/面试题库/03_集合与容器.md) |
| Java I/O | 字节/字符流、BIO/NIO/AIO、Buffer/Channel/Selector、文件与网络 I/O、序列化边界 | [IO 与网络编程](../Backend/Java/面试题库/02_IO与网络编程.md) |
| Java 并发 | 线程状态、线程池、volatile、synchronized、CAS/Atomic、AQS、Lock、ThreadLocal、并发集合和 CompletableFuture | [并发与 JUC](../Backend/Java/面试题库/05_并发与JUC.md) |
| JVM | 内存区域、对象与引用、类文件/类加载器/双亲委派、GC 与参数、OOM/泄漏/StackOverflow、诊断工具；Java 8 至 25 的版本差异按需核对 | [JVM](../Backend/Java/面试题库/04_JVM.md) |
| Maven/Gradle | 坐标、依赖图、生命周期、插件、多模块和私服；Gradle Task/Plugin、初始化/配置/执行阶段、Wrapper 与可复现构建 | [Maven 与 Gradle](../Backend/Java/面试题库/16_Maven.md) |
| Go | 类型、接口、切片/Map、Goroutine/Channel/Context、GC、网络服务、测试、性能和生产边界 | [Go 题库](../Backend/Go/面试题库/README.md) |
| C++ | 指针/引用/const/static；编译链接；对象模型、虚函数；值类别和移动语义；STL、智能指针、内存管理、新特性和问题排查 | [C++ 题库](../Cpp/面试题库/01_语言、内存与工程.md) |
| Python | 对象模型、迭代/生成、装饰器、GIL、进程/线程/协程、asyncio、包测试、FastAPI/ASGI 和自动化测试 | [Python 题库](../Python/面试题库/README.md) |

来源入口：[小林 Coding 面试题](https://xiaolincoding.com/interview/)、[小林 Coding C++ 面试题](https://xiaolincoding.com/interview/cpp.html)、[JavaGuide 后端知识体系](https://javaguide.cn/home.html)、[JavaGuide Gradle 核心概念](https://javaguide.cn/tools/gradle/gradle-core-concepts.html)。

## 数据库、缓存、搜索与消息

| 主题 | 两站知识点提炼 | 本地归属 |
| --- | --- | --- |
| 数据库原理 | 关系模型、SQL 执行、索引、事务、隔离级别、锁、MVCC、日志、复制、分片和恢复 | [数据库系统原理](../Backend/Data/数据库系统原理.md) |
| MySQL | 一条 SQL 的执行链路；InnoDB 页/行；B+Tree、联合索引和索引失效；EXPLAIN、慢 SQL；Buffer Pool、redo/undo/binlog；事务、MVCC、锁、主从和分库分表 | [MySQL](../Backend/Data/MySQL.md)、[SQL](../Backend/Data/SQL.md) |
| Redis | String/Hash/List/Set/Zset/Bitmap/HyperLogLog/Stream；SDS、哈希、压缩结构、跳表；过期/淘汰；RDB/AOF；复制、哨兵、Cluster；分布式锁和缓存故障 | [Redis](../Backend/Data/Redis.md) |
| MongoDB | 文档模型、索引、复制集、分片、事务和适用边界 | [MongoDB](../Backend/Data/MongoDB.md) |
| Elasticsearch | 倒排索引、分词、Mapping、查询、深分页、分片副本、写入/查询优化、生命周期和集群排障 | [搜索与 Elasticsearch](../Backend/Data/搜索与Elasticsearch.md) |
| 消息队列 | 解耦、异步、削峰；可靠投递、幂等、顺序、重试、死信和积压；Kafka/RocketMQ/RabbitMQ 模型与选型 | [消息队列](../Backend/Data/消息队列.md) |
| 进程内事件队列 | Disruptor 的 RingBuffer、Sequence/Sequencer、事件处理链、等待策略，以及低延迟与 CPU 占用、阻塞下游之间的取舍 | [消息队列](../Backend/Data/消息队列.md#disruptor-与消息中间件是什么关系) |

来源入口：[小林 Coding《图解 MySQL》](https://xiaolincoding.com/mysql/)、[《图解 Redis》](https://xiaolincoding.com/redis/)、[JavaGuide 数据库目录](https://javaguide.cn/home.html#%E6%95%B0%E6%8D%AE%E5%BA%93)、[JavaGuide Disruptor](https://javaguide.cn/high-performance/message-queue/disruptor-questions.html)。

## Java Web、软件工程与安全

| 主题 | 两站知识点提炼 | 本地归属 |
| --- | --- | --- |
| Spring | IoC/AOP、Bean 生命周期、循环依赖、代理、事务传播/隔离/自调用、MVC、常用注解和设计模式 | [Spring 题库](../Backend/Java/面试题库/09_Spring核心.md) |
| Spring Boot | 自动配置、条件装配、启动流程、配置绑定、Web 线程模型、异常处理、监控和生产排障 | [Spring Web 与 Boot](../Backend/Java/面试题库/10_SpringWeb与Boot.md) |
| MyBatis/JPA/JDBC | 参数绑定、映射、一级/二级缓存、批处理、N+1、事务边界和数据访问选型 | [Java 数据访问](../Backend/Java/面试题库/08_Java数据访问.md) |
| API 与实时推送 | REST、版本/分页/错误合同；轮询、长轮询、SSE、WebSocket 的连接、重连和状态边界 | [API 与事件契约](../Backend/Architecture/09_API与事件契约.md)、[HTTP 与 Web](../CS/04_HTTP与Web协议.md) |
| 软件工程 | 命名、重构、单元测试、代码审查、设计模式、技术债、ADR 和演进式架构 | [软件工程与演进式架构](../Backend/SoftwareEngineering.md) |
| 认证授权 | Session、JWT、OAuth/OIDC、SSO、RBAC/ABAC、对象级权限、多租户和审计 | [认证、授权与多租户](../Backend/Architecture/认证、授权与多租户.md) |
| 数据与输入安全 | 加密/哈希、参数校验、注入、XSS/CSRF/CORS/SSRF、上传、敏感词、脱敏和秘密管理 | [应用安全](../Backend/Architecture/应用安全.md)、[安全与治理](../Security_and_Governance/README.md) |
| 定时任务 | 单机调度、分布式抢占、幂等、错过执行、并发执行、补偿、对账和可观测性 | [任务、消息与补偿](../Backend/Architecture/05_任务、消息与补偿.md) |

来源入口：[JavaGuide 系统设计](https://javaguide.cn/system-design/)、[SSO 单点登录](https://javaguide.cn/system-design/security/sso-intro.html)、[数据脱敏](https://javaguide.cn/system-design/security/data-desensitization.html)、[Web 实时消息推送](https://javaguide.cn/system-design/web-real-time-message-push.html)。

## 分布式、高性能与高可用

| 主题 | 两站知识点提炼 | 本地归属 |
| --- | --- | --- |
| 分布式基础 | 故障模型、CAP/BASE、一致性模型、复制、Quorum、逻辑时钟、分片和一致性哈希 | [分布式系统基础](../Backend/Architecture/03_分布式.md) |
| 共识与协调 | 拜占庭故障与崩溃故障；Paxos、Raft、ZAB、Gossip；选主、日志复制、元数据、锁和注册发现 | [分布式系统基础](../Backend/Architecture/03_分布式.md)、[分布式协调](../Backend/Architecture/分布式协调.md) |
| RPC 与网关 | 序列化、服务发现、负载均衡、超时、重试、幂等、Deadline、错误合同；API Gateway 的路由、认证、限流和观测 | [分布式系统基础](../Backend/Architecture/03_分布式.md)、[网关与接口治理](../Backend/Architecture/06_网关、接口治理与SDK.md) |
| 分布式组件 | ZooKeeper、Dubbo、分布式 ID/锁/事务/配置中心的用途与边界 | [分布式协调](../Backend/Architecture/分布式协调.md)、[可靠性与一致性](../Backend/Architecture/04_可靠性与一致性.md) |
| 数据扩展 | 读写分离、分库分表、SQL 优化、深分页、冷热分离和数据迁移 | [MySQL](../Backend/Data/MySQL.md)、[系统设计](../Backend/Architecture/01_系统设计.md) |
| 流量与分发 | DNS/四层/七层/客户端负载均衡；CDN 缓存与回源；一致性哈希和热点处理 | [系统设计](../Backend/Architecture/01_系统设计.md)、[HTTP 与 Web](../CS/04_HTTP与Web协议.md) |
| 高可用 | 冗余、故障转移、隔离、超时、有限重试、限流、熔断、降级、背压、容灾、压测和恢复演练 | [高可用与服务治理](../Backend/Architecture/高可用与服务治理.md) |
| 系统设计题 | 秒杀、订单超时、短链、上传、排行榜、Feed、消息、缓存、支付和高并发服务的需求、容量、数据、故障与取舍 | [系统设计](../Backend/Architecture/01_系统设计.md)、[场景方案库](../Backend/Architecture/08_场景方案库.md) |

来源入口：[JavaGuide 分布式](https://javaguide.cn/distributed-system/)、[高性能](https://javaguide.cn/high-performance/)、[高可用](https://javaguide.cn/high-availability/)、[数据冷热分离](https://javaguide.cn/high-performance/data-cold-hot-separation.html)、[小林 Coding 系统设计面试题](https://xiaolincoding.com/interview/systemdesign.html)。

## 测试、交付与线上排障

| 主题 | 两站知识点提炼 | 本地归属 |
| --- | --- | --- |
| 业务测试 | 从需求、角色、状态机、规则和故障路径设计用例；等价类、边界值、判定表、状态迁移和探索式测试 | [后端测试体系](../Backend/Testing.md) |
| 自动化测试 | Java/Python 测试框架、分层自动化、测试数据、环境隔离、Mock/Stub/Fake、失败证据和 CI 门禁 | [后端测试体系](../Backend/Testing.md)、[Python 工程与 Web](../Python/面试题库/02_工程与Web.md) |
| 性能测试 | 容量模型、工作负载、基线/阶梯/突发/稳定性测试；吞吐、P95/P99、错误率、资源、瓶颈和恢复 | [后端测试体系](../Backend/Testing.md)、[生产系统工程](../Backend/Delivery/07_生产系统工程.md) |
| Git | 工作区/暂存区/提交、分支、合并/rebase、冲突、撤销和协作边界 | [Git](../Backend/Delivery/01_Git.md) |
| Docker | 镜像层、容器、网络、存储、Dockerfile、Compose、资源/权限和排障 | [Docker](../Backend/Delivery/04_Docker.md) |
| CI/CD 与生产 | 可复现构建、门禁、部署、灰度、回滚、Kubernetes、日志/Metrics/Trace、SLI/SLO、容量和事故响应 | [Delivery](../Backend/Delivery/README.md) |

来源入口：[小林 Coding 测试开发面试全攻略](https://xiaolincoding.com/interview/test_dev.html)、[业务测试](https://xiaolincoding.com/interview/business_testing.html)、[性能测试](https://xiaolincoding.com/interview/performance_testing.html)、[JavaGuide 单元测试](https://javaguide.cn/system-design/basis/unit-test.html)。

## AI、RAG、Agent 与 AI Coding

| 主题 | JavaGuide 公开知识点提炼 | 本地归属 |
| --- | --- | --- |
| LLM 机制 | Token、Embedding、Attention、位置编码、上下文窗口、采样、KV Cache、量化、训练/对齐和推理成本 | [LLM 基础](../AI/LLM基础.md)、[AI 面试题库](../AI/面试题库/README.md) |
| 模型 API | 结构化输出、Function/Tool Calling、流式、限流、错误分类、重试、成本和 Provider 适配 | [Agent 题库](../Agent面试题库/README.md) |
| Agent | ReAct、规划、执行、反思、状态、记忆、Workflow/Graph/Loop、Skill、MCP、Harness 和多 Agent | [Agent 题库](../Agent面试题库/README.md) |
| RAG | 文档解析/切分、Embedding、向量索引、混合检索、Rerank、上下文组装、知识更新、GraphRAG 和评测 | [RAG 与检索](../Agent面试题库/06_RAG与知识库/RAG与检索.md)、[知识摄取与 GraphRAG](../Agent面试题库/12_课程深化/04_知识摄取与GraphRAG/知识摄取与GraphRAG.md) |
| AI 系统 | LLM 网关、安全、Prompt Injection、权限、可观测、Eval、缓存、降级、成本、语音与实时交互 | [生产工程与系统设计](../Agent面试题库/09_工程化与系统设计/生产工程与系统设计.md)、[实时交互与产品](../Agent面试题库/12_课程深化/07_实时交互与产品/实时交互与产品.md) |
| AI Coding | IDE 与 CLI Agent；指令文件、Context/Memory、Skill/Hook、任务拆分、Spec、验证、沙箱和多 Agent 协作 | [AI 工具与编程助手](../AI/AI工具与编程助手.md) |
| 项目表达 | 知识库问答、研究、客服、代码与 OnCall Agent 的架构、指标、失败案例、安全和取舍 | [Agent 实践与项目表达](../Agent面试题库/12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md)、[AI 案例](../Case_Studies/AI/README.md) |

来源入口：[JavaGuide AI 应用开发](https://javaguide.cn/ai/)、[AI 编程实战指南](https://javaguide.cn/ai-coding/)、[小林 Coding Agent 项目](https://xiaolincoding.com/project/agent_info.html)、[Agent 面试题纲](https://xiaolincoding.com/project/xiaolinnote.html)。小林 Coding 的项目页只支持确认项目主题；未公开源码或正文不据此推断实现细节。

## 求职、面试与学习方法

两站相关内容可压缩为四个动作：按岗位 JD 建能力矩阵；用题目暴露缺口而不是无差别背诵；项目表达必须给出问题、约束、方案、指标、失败和复盘；简历中的每个技术名词都应能接受原理、边界和故障追问。学习顺序不应被网站目录绑死，当前项目和目标岗位决定优先级。

本地归属：[Career](../Career/README.md)、[Java 复习路线](../Backend/Java/面试题库/00_复习路线与答题模板.md)、[Agent 复习路线](../Agent面试题库/00_复习路线与答题模板.md)。来源入口：[小林 Coding 学习和面试心得](https://xiaolincoding.com/cs_learn/)、[JavaGuide 面试准备目录](https://javaguide.cn/home.html#%E9%9D%A2%E8%AF%95%E5%87%86%E5%A4%87)。

## 使用与维护规则

1. 新看到一篇文章时，先在本页找到主题归属；本地已有主文档就补缺口，不复制一份同名笔记。
2. 只有新机制、新边界、新反例或版本变化才进入正文；纯例题和重复表述留在来源页。
3. 重要修订在对应题目附近附直接来源；本页只负责覆盖证明，不替代逐题来源。
4. 每次站点目录大幅调整后，先更新盘点日期和映射，再决定是否新增内容。
5. “目录出现”只证明主题存在；“正文核验”才能支持具体结论；“项目页存在”不能证明源码实现或性能指标。
