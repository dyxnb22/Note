# Lecture 8：区块链扩容、支付通道、桥与 Rollup

来源：课程课件 `lecture8-L2-handout.pdf`（原 PDF 未随笔记入库，当前只保留整理稿。）

## 8.1 为什么需要 Layer 2

区块链的安全来自全球复制：每个全节点独立重执行每笔交易。这样验证能力强，但吞吐受最慢或最普通节点限制。Bitcoin 和 Ethereum L1 的吞吐远低于传统支付网络。

L2 把大部分执行搬到链下，把 L1 保留为最终裁判。合格的 L2 应保留：

1. **Public verifiability**：用户或观察者能重建和验证状态；
2. **Self-custody**：只有有效授权能移动资金；
3. **Censorship resistance**：运营者不能永久阻止用户 L1 退出。

支付通道和 Rollup 都是“链下做工作、链上防作弊”，但支付通道服务固定参与者和支付更新，Rollup 服务共享的账户、合约和开放用户集合。

## 8.2 Payment channel

Alice 和 Bob 若每天交易 200 次，可以：

1. 一笔 L1 funding/open 交易锁入资金；
2. 在链下交换双方签名的余额更新；
3. 一笔 L1 close/settlement 交易提交最终余额。

正常情况下，大量付款被压缩成两笔链上交易。每个 channel 有 open、use、close 三阶段。

### 8.2.1 如何让最新状态胜出

攻击者可能广播一个旧状态，里面自己余额更多。两类解决方式：

- **Incentive replacement**：新状态让接收者获得更多，旧状态没有吸引力；适合单向 Spilman channel；
- **Revocation**：旧状态被更新时，双方交换 revocation secret；若有人广播旧状态，对方可以在 delay 窗口内提交 justice transaction，拿走作弊方全部或大部分余额。

安全更新的顺序很重要：先为新状态交换并签名，再揭示旧状态的 revocation secret。这样任何中途掉线时，诚实方至少持有一个可安全退出的 commitment。广播被撤销状态时，广播者自己的输出被相对时间锁延迟，给对方提交罚没交易的机会。

Watchtower 代替用户持续监控 L1：它发现撤销状态后广播 justice transaction。支付通道是非托管的，但争议安全仍依赖有人在时间窗口内可用。

## 8.3 HTLC 与 Lightning 多跳支付

Alice 想通过 Bob、Caroline 把钱付给 Dave。若 Alice 先付款而 Bob 不转给 Caroline，Alice 会损失资金。因此每一跳必须原子化：要么所有跳都成功，要么都退款。

HTLC 同时使用哈希锁和时间锁：

```text
若在 deadline 前提供 R 且 H(R)=h -> 收款
否则 deadline 后付款方退款
```

Dave 生成秘密 R，只把 `h=H(R)` 给 Alice。每一跳使用相同 hash，但时间锁从接近接收者的一跳到发送者方向逐渐变长：`t_A > t_B > t_C`。Dave 揭示 R 后，Caroline 用它领取上游款，再向 Bob 展示，最后 Bob 向 Alice 展示。若 R 从未出现，所有 HTLC 超时退款。

Lightning 是由双向 channel 构成的图：路由受每一跳的余额、方向流动性、手续费和监控能力限制。它很适合即时、小额、固定参与者支付，但大量资本被锁在通道中，开放式共享状态因此引向 Rollup。

## 8.4 Bridge 的基本逻辑与风险

最简单的 lock-and-mint bridge：

1. 用户在源链锁定原生资产；
2. 目标链确认源链的锁定事件；
3. 目标链铸造等量 wrapped token；
4. 赎回时目标链销毁 wrapped token，源链释放原资产。

关键问题不是“有没有一个签名”，而是：目标链相信什么证据，且这个证据是否足够稳定。

信任模式从单一运营者、多签委员会、经济质押签名者到验证源链 headers/consensus 的 validating bridge。桥的安全上限受最弱被信任的 authority、共识和最终性约束。

### 8.4.1 跨链重组攻击

若源链先看到锁定、目标链铸币并最终确认，之后源链发生重组，把锁定交易移除，用户可能重新花源链原资产；目标链上的 wrapped token 仍存在，于是两份资产主张对应一份抵押，桥发生资不抵债。

防御方式：目标链验证源链共识、等待源链 deterministic finality，或在概率最终性链上等待保守的确认数量。没有最终性的源链不存在一个有限确认数能给绝对确定性，只能降低重组概率。

## 8.5 Rollup 的工作流

```text
L1 deposit
   -> L2 sequencer 收集、排序交易
   -> L2 executor 执行并计算新 state root
   -> L1 接收 batch、数据和证明/断言
   -> L1 验证或等待挑战
```

sequencer 可以控制排序，但不应能创造无效状态或永久阻止退出。state root 是对状态的承诺；batch data 让别人能够重建状态。Merkle root 把一批交易绑定到一个精确状态，同时把 L1 费用分摊到很多 L2 交易。

Rollup 安全有三个相互独立的支柱：

1. **Data availability**：大家能否得到交易数据并重建状态；
2. **State integrity**：状态转移是否遵守规则；
3. **Censorship resistance**：用户能否强制包含交易或退出。

## 8.6 数据可用性

只发布 state root 很便宜，但它只承诺“某个状态”，不提供生成该状态所需的交易。若 sequencer withholding data，别人既不能重建账户状态，也不能制作退出证明或独立挑战。

数据对两件事都必要：

- 恢复与退出：用户需要知道余额和 Merkle path；
- 验证与挑战：watcher 需要重放交易，发现错误状态。

可选方案：

- Plasma：数据必要时由运营者提供，用户需监控；
- Validium/DAC：依赖委员会可用性；
- 标准 Rollup：把 calldata 或 blobs 放到 L1，信任最强但成本更高；
- 独立 DA layer：便宜，但增加对 DA 层的信任。

即便 validity proof 能证明转移正确，它也不能告诉用户隐藏在未发布数据中的余额，也不能让新 executor 继续运行。因此 proof correctness 与 data availability 是两个维度。

## 8.7 ZK-Rollup 与 Optimistic Rollup

### 8.7.1 ZK/validity rollup

executor 对旧状态和交易 batch 执行，计算新 root，生成 validity proof。L1 合约验证 proof：有效则接受新 root，无效则拒绝。证明把签名、旧 Merkle root 中读取的账户/存储值、执行规则和新 root 全部绑定起来。

prover 计算昂贵，但验证快速；证明和 L1 交易最终确认后不需要 fraud challenge window。

### 8.7.2 Optimistic rollup

运营者先提交 batch、state root 和 bond，协议“乐观地”假设它正确，开放通常约数天的挑战窗口。watcher 重执行公开数据，若发现错误，提交 fraud proof，协议通过并行二分定位错误步骤，罚没错误提议者。

二分（**bisection**）流程把 N 步争议分成两半，双方反复承诺中间状态哈希，每轮保留包含第一个分歧的一半；经过 `O(log N)` 轮后，L1 只需重执行一个步骤。挑战窗口不能太短，否则诚实 watcher 还没来得及发现错误，L1 资产就可能被错误 root 释放。

| 维度 | ZK Rollup | Optimistic Rollup |
|---|---|---|
| 正确性 | 先提供 validity proof | 默认正确，靠 fraud proof 挑战 |
| 信任假设 | sound proof system | 至少一个诚实 watcher |
| 提现 | L1 最终后较快 | 等挑战窗口结束 |
| 成本 | proof generation 重 | 正常情况轻，争议时复杂 |
| 数据 | 仍需公开以重建和退出 | 还需公开以重放和挑战 |

两者不是“隐私 vs 透明”的区别，而是如何证明状态完整性的区别。数据放不放 L1 又是另一条轴，不能用 validity proof 替代数据可用性。

## 8.8 抗审查与强制退出

若 sequencer 拒绝用户交易，用户需要 L1 escape hatch：

- **Forced inclusion**：把交易发到 L1 queue；若 sequencer 不处理，桥拒绝接受其后续 checkpoint；
- **On-chain exodus**：到达期限后冻结正常 rollup 活动，用户按最后一个可用状态退出。

这样 sequencer 可以延迟用户，但不能永久锁住资金。L1 仍然是权威结算层。

## 8.9 本讲总结构

| 设计 | 链下做什么 | L1 如何防作弊 | 用户如何退出 |
|---|---|---|---|
| 支付通道 | 签名余额更新 | revocation、justice tx | 广播最新安全 commitment |
| Lightning | 多跳 HTLC | hash/time lock | 超时退款或单方面关闭 |
| ZK Rollup | 批量执行共享状态 | validity proof | 验证后的 L1 withdrawal |
| Optimistic Rollup | 批量执行共享状态 | challenge/fraud proof | 等挑战窗口后提款 |
| Bridge | 跨链锁定和映射 | 验证源链证据和最终性 | 销毁映射资产并释放源资产 |

全课最后的统一模式是：

> 把普通工作移到链下，但必须把数据、状态承诺、正确性证明、争议处理和退出路径设计到让用户不必信任运营者。

---
