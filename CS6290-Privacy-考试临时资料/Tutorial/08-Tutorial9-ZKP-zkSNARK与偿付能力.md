# 第八部分：Tutorial 9 —— ZKP、zk-SNARK 与 Proof of Solvency

## 37. ZKP、NIZK、ZK-SNARK 的关系

层次关系可以记为：

~~~text
ZK-SNARK ⊂ NIZK ⊂ ZKP
~~~

- **ZKP**：最广义的零知识证明，可能交互；证明者让验证者相信自己知道 witness，同时不泄露 witness。核心性质是 completeness、soundness/proof of knowledge、zero-knowledge。
- **NIZK**：非交互零知识证明，证明者发送一份 proof，验证者独立检查；可能依赖 CRS/可信设置。
- **ZK-SNARK**：一种具体的 NIZK，强调 succinct（证明短、验证快）和 argument of knowledge（通常是计算安全，而非无条件/统计安全）。

注意“proof”和“argument”的术语区别：argument 通常只要求计算能力受限的攻击者不能伪造；这正适合复杂电路和区块链验证，但安全性依赖计算假设。

## 38. 简化版交易所 Proof of Solvency

### 38.1 目标

交易所希望证明：链上资产 Assets 足以覆盖所有客户负债，但不公开每个客户的余额。

设客户余额为 bal_i。把叶子定义为客户数据，构造 Merkle tree，根为 R，总负债：

~~~text
B = Σ_i bal_i.
~~~

交易所发布 public statement (R,B)，并用 zk-SNARK 证明自己知道 witness：

~~~text
{(bal_i, Π_i)}_(i=1)^n
~~~

其中 Π_i 是叶子到 R 的 Merkle proof。电路检查：

1. 所有 bal_i 的和等于公开的 B；
2. 每个 Π_i 确实把对应叶子连到 R。

任何人验证 proof 并检查 B≤Assets。客户私下收到自己的 (bal_i,Π_i)，验证余额是否正确以及叶子是否属于 R。

技术细节：题目把叶子 0 设成随机 256-bit 数，是为了让树叶数为 2 的幂时有一个不代表客户的填充叶；真实设计中叶子还必须包含唯一身份和版本/快照信息。

### 38.2 Attack A：相同余额的叶子复用

若 Alice 和 Bob 的余额都为 x，恶意交易所只放一个值为 x 的叶子，然后把同一叶子证明发给两人。SNARK 中 x 只被求和一次，但真实负债是：

~~~text
x(Alice) + x(Bob) = 2x.
~~~

两人都能验证自己的余额和 Merkle proof，因此都不会投诉；他们不知道两个人共享了同一个叶子。

### 38.3 Mitigation B：叶子绑定唯一客户

把叶子改成：

~~~text
Leaf_i = H(clientID_i || bal_i)
~~~

或 H(username_i,bal_i)。即使余额相同，不同客户 ID 也会产生不同叶子；电路和求和必须对所有不同客户记录分别计数。

### 38.4 Attack C：恶意客户 Eve 与交易所串通

交易所可以直接把 Eve 的记录从树中省略：

1. 只用诚实客户构造根 R'；
2. 只计算诚实客户的总负债 B'；
3. 生成对 (R',B') 有效的 SNARK；
4. 给诚实客户发送正确余额和路径；
5. Eve 不投诉，因为她在串通。

若 Eve 的余额占一半，公开 B' 就可能只有真实总负债的一半，但所有诚实客户的个人验证都通过。这个例子说明：

> 有效 proof 只证明公开 statement 为真；它不自动证明 statement 覆盖了现实世界中的所有客户。

### 38.5 Mitigation D：绑定客户集合和数量

除了 (R,B)，还要绑定客户集合或客户数量 N，并让电路证明：

- 所有叶子是 H(clientID_i,bal_i)；
- ID 互不重复；
- 叶子数量等于公开/外部承诺的 N；
- 每个有效客户都被纳入快照。

但只公开“交易所声称 n=100”还不够，因为交易所可以声称 n=50。因此 N 应来自外部可核验的客户注册表、审计快照、签名客户集合承诺或其他公开约束。n 解决的是“无声遗漏”；唯一 ID 解决的是“重复计数/叶子复用”。

---

