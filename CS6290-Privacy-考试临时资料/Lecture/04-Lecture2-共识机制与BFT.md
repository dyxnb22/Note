# Lecture 2：共识机制、BFT 与现代区块链共识

## 2.1 什么是共识

共识是让多个独立参与者在没有中央裁判的情况下，对一个值、一个决定或一段有序日志达成一致，即使其中一些参与者有故障、撒谎，网络还可能延迟或分区。

最基本的三个性质：

1. **Agreement**：任意两个诚实节点不会决定不同值；
2. **Validity**：决定的值必须符合协议，通常来源于某个诚实节点的提议；
3. **Termination**：所有诚实节点最终都会决定。

没有 Agreement 就会出现冲突；没有 Validity，协议可以永远输出一个固定的无意义值；没有 Termination，攻击者可以让系统永远等待。

## 2.2 Byzantine Generals、故障模型与网络模型

Byzantine Generals Problem 把问题表述为：将军只能发消息，但其中一些可能是叛徒；忠诚将军必须统一攻击或撤退。叛徒指挥官可以向不同将军发送相反命令，忠诚节点必须交叉验证并最终一致。

映射到区块链：

| 将军问题 | 区块链 |
|---|---|
| 将军 | 节点/验证者 |
| 指挥官 | leader/proposer |
| 忠诚将军 | honest node |
| 叛徒 | Byzantine node |
| 信使 | 网络消息 |
| 命令 | 区块或交易顺序 |

故障由弱到强：crash（停止）、omission（选择性丢消息）、Byzantine（任意恶意行为，包括向不同节点发送矛盾信息）。

故障容忍边界：

- Crash Fault Tolerance（CFT）：通常要求 `f < n/2`；Paxos、Raft 属于这一类；
- Byzantine Fault Tolerance（BFT）：通常要求 `f < n/3`，即 `n >= 3f+1`；PBFT、HotStuff、Tendermint 属于这一类。

网络模型：同步网络有已知延迟上界；纯异步网络延迟无上界，FLP 结果说明在一个异步系统中，即使只有一个 crash fault，也无法同时保证确定性共识的安全和活性；部分同步模型假设存在一个未知的 Global Stabilization Time，之后延迟有界，是多数实际 BFT 协议的模型。

## 2.3 CAP、Safety 与 Liveness

CAP 的三个词是：

- Consistency：读到一致状态；
- Availability：请求总能得到响应；
- Partition tolerance：网络分裂时仍能工作。

网络分区发生时，系统通常只能在“一致但可能停止”（CP）和“继续响应但可能暂时分叉”（AP）之间取舍。传统 BFT 更偏 CP：无法形成足够 quorum 时宁可停止；Nakamoto consensus 更偏 AP：继续出块，但分叉在之后收敛。

- **Safety**：坏事不会发生，例如两个冲突交易都被最终确认；
- **Liveness**：好事最终发生，例如合法交易不会永远被卡住。

这不是简单的“哪个协议更好”，而是不同网络和故障条件下的设计选择。

## 2.4 Byzantine Broadcast 与 SMR

Byzantine Broadcast 是单次协议：一个 leader 有输入值，所有诚实节点必须对同一值输出。交叉转发可以在 `f < n/3` 下帮助节点发现 leader 给出了矛盾值。Dolev-Strong 在同步网络中使用 `f+1` 轮签名链，允许更高的 Byzantine 容忍度，但依赖同步假设。

现实系统不是只决定一次，而是持续处理交易。因此需要 **State Machine Replication（SMR）**：所有副本对一个不断增长的命令日志达成一致，然后按相同顺序执行状态机。安全性意味着诚实节点日志一致且互为前缀；活性意味着客户端提交的合法交易最终出现在日志中。

## 2.5 PBFT：经典的许可型 BFT

PBFT 假设一个固定、已知身份的验证者集合，`n=3f+1` 时容忍 `f` 个 Byzantine 节点。其角色包括 primary、backup 和 client。

三阶段：

1. **Pre-prepare**：primary 提出区块或请求顺序；
2. **Prepare**：副本广播并确认自己看到的提议；
3. **Commit**：足够副本锁定决定，保证 view change 后不会换成冲突决定；
4. 客户端收集足够数量的匹配回复。

两个大小为 `2f+1` 的 quorum 必然有足够交集，其中至少有诚实节点，因此两个冲突决定不能都提交。

PBFT 提供快速确定性最终性，但消息复杂度高、leader 可成为攻击目标、适合几十到约百个已知节点，不适合任何人都能免费加入的公有链。

## 2.6 无许可网络的 Sybil 问题与 Nakamoto consensus

BFT 的票数假设每个节点身份有意义。若创建身份免费，攻击者可以创建一万个假节点，轻易形成多数，这就是 Sybil attack。因此无许可协议必须把投票权绑定到稀缺资源：

- PoW：算力和电力；
- PoS：锁定的加密货币资本。

PoS 还需要防范两类课件特别指出的攻击：**nothing-at-stake** 是验证者可以几乎无成本地给多个分叉投票；slashing 让这种 equivocation 变得昂贵。**Long-range attack** 则利用旧验证者退出后仍掌握旧私钥的事实，在很久以前的历史上重写一条“看起来有足够签名”的链；weak subjectivity checkpoint 要求新节点通过一个近期可信检查点同步，而不是只凭远古签名判断当前链。

Bitcoin 的 Nakamoto consensus 将 PoW、最长累计工作量链、区块奖励和手续费组合起来。用户通常等待 k 个确认；k 越大，攻击者需要追赶的区块越多，反转概率大致指数下降。控制超过 50% 算力时攻击者可以持续领先，构成 51% 风险。

PoW 的优点是开放、动态、经过多年验证；缺点是能源高、出块慢、最终性概率化。PoS 试图保留开放性，同时用 stake 作为投票权和可罚没的抵押物。

## 2.7 现代 BFT 与 DAG

- **Tendermint**：Propose -> Prevote -> Precommit -> Commit，面向 PoS 链，提供 stake-weighted 投票和快速最终性。
- **HotStuff**：用 threshold signature 聚合投票，通信复杂度从 PBFT 的二次量级降低到线性量级；通过连续 3 个区块的链式规则提交前一个区块。
- **Ethereum Gasper**：Casper FFG 负责最终性，LMD-GHOST 负责 fork choice。
- **Avalanche/Snowball**：不依赖单一 leader，而是反复随机抽样少量节点；当抽样结果反复偏向同一个值时，置信度逐步累积并最终收敛。
- **DAG-based consensus**：多个区块并行引用多个父节点，Narwhal/Tusk、Mysticeti 等把数据传播和排序解耦，获得更高吞吐和更低延迟，但复杂度更高。

最终性类型：

| 类型 | 含义 | 例子 |
|---|---|---|
| Deterministic | 达到条件后数学上不可逆，除非破坏假设 | PBFT、Tendermint |
| Probabilistic | 反转概率随确认增长而下降 | Bitcoin PoW |
| Hybrid | 快速链加 BFT 检查点 | Ethereum PoS |

## 2.8 MEV、审查、分叉与治理

**MEV（Maximal Extractable Value）** 是区块提议者或 searcher 通过重排、插入、删除交易而获得的额外价值。典型 sandwich：攻击者先买入抬价，受害者以更差价格交易，攻击者再卖出。

**Censorship resistance** 不是共识自动保证的。验证者可以选择不包含某些交易，可能出于利润、监管或政治原因。研究方向包括 inclusion lists、加密 mempool、PBS、fair ordering。

Flashbots/MEV-Boost 是把交易搜索、区块构建和区块提议分开的实际方向之一：searcher 寻找可提取机会，builder 组装区块，proposer 在验证有效性的前提下选择出价。它可以减少单个验证者独占 MEV 的能力，但没有消除 MEV 本身。

分叉：软分叉兼容旧节点，硬分叉不兼容并可能形成两条链。BCH 因区块大小争议从 Bitcoin 分叉，是技术选择会带来经济和治理后果的案例。Ethereum Merge 则说明，经过充分测试和社区协调，复杂共识切换可以无停机完成。

治理的基本冲突是：开发者希望改进技术，验证者希望盈利，用户希望稳定和低费。Bitcoin 依靠 BIP 和较慢的社会共识；Ethereum 依靠 EIP 和核心开发者协调；某些链采用链上代币投票。

共识的后续研究还包括 trustless bridge、MEV 抑制、后量子签名、Rollup 和 **data availability sampling（DAS）**。DAS 的目标是让节点只随机抽样检查 blob 数据，就能以高概率发现数据不可用，从而在不要求每个节点下载全部数据的情况下提高可扩展性。

---

