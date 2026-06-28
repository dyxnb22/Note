# Redis

# 数据结构

<details>
<summary>Redis 常见数据类型和应用场景</summary>
	Redis 常见数据类型可以分为基础类型和扩展类型。

	基础类型：
	- String：缓存对象、计数器、分布式锁、共享 Session。
	- Hash：对象缓存、购物车、用户信息。
	- List：简单消息队列、最新列表、栈/队列。
	- Set：去重、点赞、抽奖、共同关注、交并差集。
	- Zset：排行榜、延迟队列、按分数排序的场景。

	扩展类型：
	- Bitmap：签到、在线状态、布尔状态统计。
	- HyperLogLog：海量 UV、去重计数，牺牲少量精度换低内存。
	- GEO：附近的人、门店距离、地理位置查询。
	- Stream：消息队列，支持消息 ID、消费组、ACK，比 List 更适合队列场景。
</details>

<details>
<summary>Redis 底层有哪些核心数据结构</summary>
	核心底层结构包括 SDS、dict、listpack、quicklist、skiplist、intset。Redis 会在省内存和操作效率之间做权衡：小对象优先紧凑结构，数据变大后转成更适合查询和修改的结构。
</details>

<details>
<summary>String 使用什么存储？为什么不用 C 字符串</summary>
	Redis String 底层主要使用 SDS。它能 O(1) 获取长度、支持二进制安全、减少缓冲区溢出，并通过空间预分配和惰性释放减少频繁内存重分配。
</details>

<details>
<summary>Hash、List、Set、Zset 底层如何实现</summary>
	- Hash：小对象时可能使用 listpack，变大后转成哈希表。
	- List：Redis 3.2 之后主要由 quicklist 实现，本质上是双向链表 + 紧凑列表。
	- Set：如果元素都是整数且数量少，可能用 intset；否则使用哈希表。
	- Zset：通常由跳表 + 哈希表共同实现，既支持按 member 查分数，也支持按 score 排序。
</details>

---

# 线程模型

<details>
<summary>Redis 为什么快</summary>
	Redis 快主要因为：
	- 基于内存操作。
	- 数据结构高效。
	- 命令执行主流程单线程，减少锁竞争和切换。
	- 使用 I/O 多路复用。
	- RESP 协议简单。
	- 后台线程处理 fsync、lazyfree 等耗时任务。
</details>

<details>
<summary>Redis 单线程指的是什么？哪些地方用了多线程</summary>
	Redis 单线程通常指命令解析、命令执行、数据读写主流程由主线程串行执行。
	但 Redis 并不是整个进程只有一个线程：有 BIO 线程、lazyfree 线程，Redis 6.0 还引入了 I/O 多线程处理网络读写。
</details>

<details>
<summary>什么是 I/O 多路复用</summary>
	I/O 多路复用允许 Redis 用一个线程同时监听多个 socket，把“哪个连接准备好了”这件事交给操作系统通知。常见实现依赖 `select`、`poll`、`epoll`、`kqueue` 等机制。这样 Redis 不必为每个连接都创建一个线程，也能高效处理大量并发连接。
</details>

---

# 事务和原子性

<details>
<summary>Redis 如何保证原子性</summary>
	单条命令由主线程串行执行，天然具备原子性。多条命令需要 Lua 脚本或 `MULTI/EXEC` 事务；其中 Lua 更适合读-判-写必须整体原子的场景。
</details>

<details>
<summary>Redis 事务能保证原子性吗</summary>
	Redis 事务能保证命令排队后连续执行，但没有传统数据库的完整回滚语义。执行时某条命令失败，其他命令仍会继续执行。
</details>

<details>
<summary>为什么 Lua 脚本常用于 Redis 事务场景</summary>
	因为 Lua 脚本会在 Redis 中一次性串行执行，整个脚本过程不会被其他命令打断，非常适合实现“读取条件 -> 判断 -> 更新写入”这种需要整体原子性的逻辑。
</details>

---

# 持久化

<details>
<summary>Redis 持久化方式有哪些</summary>
	主要有 RDB、AOF、混合持久化。
	RDB 适合备份和快速恢复，但两次快照之间可能丢数据。
	AOF 数据更完整，但文件通常更大，恢复也可能更慢。
</details>

<details>
<summary>RDB 和 AOF 有什么区别</summary>
	- RDB：按时间点做快照，恢复快、文件紧凑，但数据可能回退到上一次快照。
	- AOF：按写命令追加日志，数据更完整，可配置 `everysec` 等策略，但文件更大，恢复时需要重放。
	- 混合持久化：结合两者优点，通常先写 RDB 头部，再追加增量 AOF。
</details>

<details>
<summary>AOF 重写是什么</summary>
	AOF 重写不是简单地把旧 AOF 文件压缩，而是根据当前内存中的数据，生成一份“能恢复到当前状态的最简命令集”，从而减小 AOF 文件体积。
</details>

---

# 过期删除和内存淘汰

<details>
<summary>过期删除策略和内存淘汰策略有什么区别</summary>
	过期删除解决 TTL 到期后何时删除；内存淘汰解决内存达到 `maxmemory` 后如何腾空间。前者看 TTL，后者看内存是否已满。
</details>

<details>
<summary>Redis 的过期删除策略有哪些</summary>
	主要结合三种思想：
	- 定时删除：到期就删，但成本高。
	- 惰性删除：访问时发现过期才删。
	- 定期删除：周期性随机抽查部分 key 删除。

	Redis 实际上主要使用“惰性删除 + 定期删除”的组合。
</details>

<details>
<summary>Redis 的内存淘汰策略有哪些</summary>
	常见有：
	- `noeviction`
	- `allkeys-lru`
	- `volatile-lru`
	- `allkeys-lfu`
	- `volatile-lfu`
	- `allkeys-random`
	- `volatile-random`
	- `volatile-ttl`

	生产里常见是 `allkeys-lru` 或 `allkeys-lfu`。
</details>

---

# 高可用和集群

<details>
<summary>Redis 主从同步中的全量同步和部分同步怎么实现</summary>
	全量同步通过 `PSYNC` 触发，主库 `BGSAVE` 生成 RDB 发给从库，再补发缓冲期间的增量命令。部分同步依赖 replication id、offset 和 `repl_backlog_buffer` 补发缺失数据。
</details>

<details>
<summary>哨兵模式解决了什么问题</summary>
	Sentinel 主要解决主从架构下的高可用问题：监控主从节点、自动故障转移、通知客户端新的主节点地址。但它不负责数据分片。
</details>

<details>
<summary>Redis Cluster 是怎么分片的</summary>
	Redis Cluster 通过 16384 个 hash slot 分片，不是一致性哈希。key 先做 CRC16，再对 16384 取模，落到对应 slot，由不同 master 节点负责。
</details>

<details>
<summary>Redis Cluster 和哨兵模式有什么区别</summary>
	- 哨兵模式：解决高可用，不做数据分片。
	- Cluster：既解决高可用，也做分片扩展。

	如果数据量不大，只是想避免单点故障，哨兵就够了；如果单机内存或吞吐不够，需要水平拆分，才考虑 Cluster。
</details>

---

# 缓存设计

<details>
<summary>如何保证 Redis 和 MySQL 缓存一致性</summary>
	常见模式是 Cache Aside：读时先查缓存，未命中再查数据库并回填；写时先更新数据库，再删除缓存。需要配合重试、延迟双删、binlog 订阅等机制，保证最终一致。
</details>

<details>
<summary>缓存雪崩、击穿、穿透是什么？怎么解决</summary>
	雪崩是大量 key 同时失效或 Redis 故障；击穿是单个热点 key 过期；穿透是请求不存在的数据。常见手段包括随机 TTL、互斥锁、空值缓存、布隆过滤器、限流和多级缓存。
</details>

<details>
<summary>为什么会有大 key 和热 key 问题</summary>
	- 大 key：单个 key 对应 value 非常大，删除、迁移、网络传输、主从同步都容易带来抖动。
	- 热 key：某个 key 访问量极高，可能把单个 Redis 节点打成瓶颈。

	处理思路：
	- 大 key：拆分、异步删除、结构优化。
	- 热 key：本地缓存、多副本、读写分离、预热、限流。
</details>

---

# 分布式锁

<details>
<summary>Redis 分布式锁怎么实现</summary>
	最基础做法是：

	```bash
	SET lock_key unique_value NX PX 30000
	```

	含义：
	- `NX`：只有 key 不存在时才设置成功。
	- `PX 30000`：设置过期时间，避免死锁。
	- `unique_value`：标识锁的持有者，释放时需要校验，避免误删别人的锁。
</details>

<details>
<summary>为什么释放锁时要用 Lua 脚本</summary>
	因为“先判断 value 再删除 key”如果分两条命令执行，中间可能被别的线程插入，导致误删。Lua 脚本能保证校验和删除的原子性。
</details>

---

# 高频简答

<details>
<summary>Redis 和 MySQL 分别适合什么场景</summary>
	MySQL 更适合持久化、强一致、复杂查询和事务型数据；Redis 更适合高并发缓存、计数器、排行榜、会话、热点数据和轻量消息场景。它们通常是配合关系，而不是替代关系。
</details>

<details>
<summary>Redis 为什么不用红黑树而用跳表做 Zset</summary>
	跳表实现简单，支持范围查询、插入删除效率稳定，也更适合和哈希表组合使用。Redis 更强调工程实现简单和性能足够稳定，而不是单纯追求理论最优。
</details>

<details>
<summary>面试中怎么一句话概括 Redis</summary>
	Redis 是一个基于内存的高性能键值数据库，支持多种数据结构，具备缓存、持久化、主从复制、高可用和集群能力，常用于高并发场景下的缓存、计数、排行、分布式锁和消息处理。
</details>
