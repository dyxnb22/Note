# 第五部分：Tutorial 6 —— PoS、Calldata 与安全/活性韧性

## 24. Proof of Stake

PoS 的典型流程：

1. **质押**：验证者锁定 collateral，作为安全押金；
2. **选择 proposer**：协议按质押权重和随机性选出区块提议者；
3. **验证和投票**：其他验证者检查签名、余额、nonce、gas 和状态转换，并对区块 attestation；
4. **最终化、奖励和惩罚**：收到足够有效票后区块进入链或被最终化；诚实者获得奖励，双签等恶意行为可能被 slash。

PoS 相比 PoW 的优点是能耗低；挑战是质押集中会导致权力集中，也要认真设计长程攻击、惩罚、密钥安全和退出机制。

## 25. Ethereum calldata 的可见性

### 25.1 当前调用中的函数

函数 F 在交易 T 执行时可以读取 T 的 calldata。Solidity 中可通过 msg.data，EVM 中可用 CALLDATASIZE、CALLDATALOAD、CALLDATACOPY。答案是 **Yes**。

### 25.2 后续交易中的函数

之后的交易 T_next 再调用同一个 F 时，msg.data 是 T_next 的 calldata，不能直接读取旧交易 T 的 calldata。答案是 **No, not directly**。

例外是：T 执行时主动把 calldata 存到了合约 storage，后来读取的是已经存储的状态，不是跨交易回溯读取历史执行上下文。

### 25.3 人类查看

公链上的交易 calldata 是公开数据。区块最终化后，人类可以通过全节点、RPC 或区块浏览器读取它。答案是 **Yes**，除非考虑加密应用层等额外隐私机制；Ethereum 基础 calldata 本身不保密。

## 26. Safety / Liveness resilience

设总节点数为 n，提交一个决定需要 q 个票。

### 26.1 Liveness resilience

攻击者控制 f 个节点并让它们完全不投票，剩下 n-f 个诚实节点仍需形成 quorum：

~~~text
n - f ≥ q
⇒ f ≤ n-q.
~~~

因此：

~~~text
f_l = n-q.
~~~

### 26.2 Safety resilience

两个大小为 q 的 quorum 在 n 个节点中至少相交：

~~~text
|Q_1 ∩ Q_2| ≥ 2q-n.
~~~

如果攻击者控制整个交集，就可以在两个冲突决定中重复投票。因此要保持安全，需要：

~~~text
f < 2q-n.
~~~

最大整数安全韧性是：

~~~text
f_s = 2q-n-1.
~~~

整体韧性为：

~~~text
f_overall = min(f_s, f_l)
          = min(2q-n-1, n-q).
~~~

### 26.3 最优 quorum

让两边尽量平衡：

~~~text
2q-n-1 = n-q
3q = 2n+1
q ≈ (2n+1)/3.
~~~

因为 q 必须是整数，实际选最接近的整数并比较 min(f_s,f_l)。

### 26.4 n=40，优先保证 f=15 的安全性

要求：

~~~text
2q-40-1 ≥ 15
2q ≥ 56
q ≥ 28.
~~~

最小整数 quorum 是 q=28。此时：

~~~text
f_l = 40-28 = 12.
~~~

也就是说，安全性可以承受 15 个对手，但活性只能承受 12 个节点不参与；若 13 个节点离线，只剩 27 个，不足以形成 28 票。高价值金融系统可以接受这种安全优先的停机风险，但必须用冗余、监控、运维演练和快速恢复来承担它。

---

