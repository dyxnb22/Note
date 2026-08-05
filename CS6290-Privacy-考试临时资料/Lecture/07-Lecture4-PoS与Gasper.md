# Lecture 4：Proof of Stake、BFT 基础与 Ethereum Gasper

来源：课程课件 `lecture4-pos-handout.pdf`（原 PDF 未随笔记入库，当前只保留整理稿。）

## 4.1 PoS 为什么出现

PoW 用电力和硬件竞争出块，PoS 把参与资格绑定到锁定资本。验证者质押资产，按 stake 获得提议和投票权；行为不当时可被 slash，抵押资产被销毁或罚没。

| 维度 | PoW | PoS |
|---|---|---|
| Sybil resistance | 算力 | 经济 stake |
| 参与成本 | 电力和硬件 | 锁定资本和运行节点 |
| 责任追踪 | 匿名算力，难处罚 | 签名投票，可证明并 slash |
| 最终性 | 通常概率性 | 可提供 BFT 确定性最终性 |

PoS 的核心不是“投票更公平”，而是把攻击成本从持续烧电转为可被没收的资本，从而获得经济问责和更低的能源消耗。课件把 Ethereum 从 PoW 切换到 PoS 的能耗下降描述为约 99.95%。

## 4.2 BFT 的 quorum 数学

每个共识协议都要保证：

- safety：不会最终确定两个冲突区块；
- liveness：最终能确定某个区块。

假设 `n=10`，最多 3 个恶意验证者。如果只要求过半（6 票），恶意验证者可以对 A 和 B 都投票，使两边分别凑够过半。解决方式是要求 **超过 2/3**：10 个节点至少需要 7 票。

两个大小为 q 的集合在 n 个元素中至少有 `2q-n` 个交集。对 `q > 2n/3`，交集大于 `n/3`；由于恶意节点最多 `f<n/3`，交集内至少有一个诚实节点。诚实节点不会同时签两个冲突区块，所以两个冲突 quorum 不能同时形成。

活性方面，若 3 个恶意节点拒绝投票，仍有 7 个诚实节点可以达到 7 票；若恶意节点达到或超过 `n/3`，系统可能卡住。`f<n/3` 同时是安全和活性的关键边界。

PoS 的 signed votes 还提供问责：如果两个冲突 quorum 都存在，签名交集能找出 double-sign 的验证者。检测和处罚要区分：

- `f<n/3`：协议安全，不应发生违规；
- `n/3 < f < 2n/3`：可能破坏 safety，但签名证据可以识别并 slash；
- `f>2n/3`：攻击者可能控制链，协议内处罚能力也可能被压制，只能依靠社会层 hard fork。

## 4.3 PBFT-style PoS

一个简化的 PoS BFT epoch 是：

```text
proposer 提议区块
       -> validators 签名投票
       -> stake > 2/3
       -> finalized
```

如果验证者对同一 epoch 的两个冲突区块签名，任何观察者都可以提交两份签名作为 fraud proof，链上合约验证后罚没其 stake。安全性不是依赖“验证者永远善良”，而是让错误行为留下不可否认的密码证据。

实际网络的验证者集合不断加入、退出、离线，且规模很大，因此采用随机委员会。委员会过小则更容易被集中攻击，过大则消息和带宽成本高。

## 4.4 CAP 与嵌套链

互联网规模的共识同时想要：开放加入、动态可用、快速确定性最终性。但网络分区时，两边若都继续处理并最终确认交易，就可能冲突；若等两边重新连接，系统可能停止。因此单一协议不能在所有条件下同时保证 dynamic availability 和 finality。

实际解决方法是**两条具有不同职责的链**：

- available chain：快速延伸，允许临时分叉和动态参与；
- finalized chain：慢一些，使用 BFT 检查点，提供安全最终性。

Finality gadget 把 BFT 最终性层叠加在 longest-chain/fork-choice 之上。Ebb-and-Flow 的直觉是：Flow 快速生成账本，Ebb 对某个快照投票；之后的新链必须从最近的 finalized checkpoint 延伸。

## 4.5 Fork choice：Longest Chain、GHOST 和 LMD-GHOST

出块更快时，网络传播来不及，普通最长链会产生更多 orphan block。GHOST（Greedy Heaviest Observed Sub-Tree）不只看一条最长路径，而是看子树累计权重，选择最重子树。

LMD-GHOST（Latest Message Driven GHOST）把权重换成验证者最新 attestation 的 stake：

1. 从 genesis 或最近 justified checkpoint 开始；
2. 收集每个验证者最新投票；
3. 在每个分叉处计算各分支得到的最新 stake；
4. 选择更重分支，重复直到叶子。

LMD-GHOST 提供快速 fork choice 和动态可用，但它本身不提供最终性，仍需要 Casper FFG。

## 4.6 Gasper：Ethereum 的两个部分

Gasper = `LMD-GHOST + Casper FFG`。

- slot 约 12 秒：一个 proposer 提出区块，委员会 attestation；
- epoch 包含 32 个 slot，约几分钟；
- LMD-GHOST 选择当前可用链的 head；
- Casper FFG 对 epoch checkpoint 投票并提供最终性。

### 4.6.1 Attestation 的双重作用

一个 validator 的签名 attestation 同时：

1. 作为 LMD-GHOST 的 fork-choice 权重；
2. 作为 Casper FFG 的 source-target checkpoint 投票。

协议按 stake 加权，而不是简单按验证者数量加权；若每个验证者的有效 stake 相同，两者在直觉上才相同。

### 4.6.2 Proposed、Justified、Finalized

- **Proposed**：刚提出，没有足够投票，容易被 fork 替换；
- **Justified**：某个 source-target checkpoint 得到超过 2/3 stake，一轮支持；仍可能出现竞争 checkpoint；
- **Finalized**：连续两轮 linked justification，前一个 checkpoint 最终确定；反转通常要求 double voting 或 surround voting，而这些是可 slash 的。

Casper FFG 的两个 slash 条件：

1. **Double voting**：同一 epoch 对两个不同 target 投票；
2. **Surround voting**：后一个 vote 的 source-target 区间包围早先的区间。

在网络延迟、验证者离线时可能无法达到 2/3，从而 liveness 停滞；inactivity leak 逐渐减少离线者的有效 stake，直到在线集合重新能形成 quorum。

课件还讨论 ex ante reorg：攻击者提前知道未来 proposer 排班，可能故意隐藏早期区块、之后释放更长链抢走 MEV。proposer boost 等规则给新发布的区块临时额外权重，降低此类重组概率。

## 4.7 委员会与随机性

不能让约九十万验证者每 12 秒全部投票，因此每个 epoch 随机打乱验证者，把每人分到某一个 slot 的 committee。随机选择必须不可预测、不可偏置、公开可验证、持续可用。

若仅用 `H(block_number, public_key)` 选择，攻击者可以反复生成密钥进行 key grinding。Ethereum 的 RANDAO 让多个 proposer 提交随机贡献并 XOR 混合，但最后揭示者有轻微 bias：它可以选择不揭示，代价是失去奖励。VDF 被提出作为未来更强的随机性方案。

若攻击者 stake 比例低于 1/3，随机委员会越大，其在委员会中超过 1/3 的概率越小。课件以约数万规模的委员会说明为什么大委员会能让抽样比例集中到总体 stake 比例附近。

## 4.8 现代 PoS 议题

- **MEV**：proposer 可以从交易排序获利；
- **PBS（Proposer-Builder Separation）**：builder 负责构造高价值区块，validator 选择最高出价的 builder 并提议；
- **Intent-based trading**：用户表达“用 1 ETH 换最多 USDC”，solver 竞争给出最优执行，减少公开 mempool 中的可抢跑信息；
- **L2 rollups**：在链下执行、在 L1 提交数据和状态承诺；
- **EIP-4844/Danksharding 方向**：为 Rollup 提供临时 blob 数据空间，降低 L2 发布批量数据的成本；blob 不像永久 storage 一样长期保存，但在数据可用窗口内可被验证和重建；
- **EIP-1559**：base fee 根据需求调整并销毁，priority fee 给 proposer。

---
