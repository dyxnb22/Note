# Lecture 7：Zero-Knowledge Proofs、SNARK、STARK 与实际应用

来源：课程课件 `lecture7-zkp-handout.pdf`（原 PDF 未随笔记入库，当前只保留整理稿。）

## 7.1 ZKP 的承诺

零知识证明允许 prover 向 verifier 证明自己知道某个秘密或完成了某个计算，而不泄露秘密本身。例如：证明年龄超过 18 而不交出身份证、证明账户余额足够而不公开余额、证明一百万笔交易执行正确而不要求每个节点全部重算。

形式上，一个 ZKP 协议需要三个性质：

1. **Completeness（完备性）**：诚实 prover 持有正确 witness 时，诚实 verifier 会接受；
2. **Soundness（可靠/健全性）**：没有正确 witness 的作弊 prover 只能以极小概率通过；
3. **Zero-knowledge（零知识性）**：verifier 除了“命题为真/证明者知道 witness”之外，不学到额外秘密。

## 7.2 交互式证明的直觉

Ali Baba 洞穴例子：洞穴有 A、B 两条路，中间有一扇只有知道魔法词才能打开的门。prover 随机走入一条，verifier 随机要求从 A 或 B 出来。知道魔法词的人总能满足；不知道的人每轮成功概率是 1/2，重复 100 轮后作弊概率约为 `2^-100`。

颜色盲朋友的例子同理：证明两球颜色不同，但不告诉哪一个是红色。Sudoku 协议通过随机打乱数字、只打开 verifier 指定的一行/列/宫，重复后让作弊者通过概率指数下降。图 3-coloring 则用随机颜色置换、承诺和随机边检查证明知道一个合法着色。

交互式协议的关键是：prover 必须先承诺，verifier 之后才随机挑战；不能看到挑战后再构造答案。

## 7.3 NP 完全性与普适性

NP 问题可以理解为：解可能难找，但给出解后容易验证。NP-complete 问题是最难的一类：任意 NP 问题都能多项式归约到它。图 3-coloring 是 NP-complete，因此对它构造 ZKP，就能通过归约给大量可验证命题构造 ZKP。

实际系统不直接把程序变成图，而是变成算术电路和多项式约束。课程的“普适性”结论是：能够被有效验证的计算，都可以被编码成一个证明系统能检查的关系。

## 7.4 Fiat-Shamir：去掉交互

区块链不适合每个验证者与 prover 往返多轮，因此需要 non-interactive proof。Fiat-Shamir 把 verifier 的随机 challenge 替换成承诺的哈希：

```text
interactive:       commitment -> random challenge -> response
Fiat-Shamir:       commitment -> c = H(commitment) -> response
```

任何人都可以重算哈希并验证响应。安全直觉是 prover 必须先固定 commitment，不能等看到 challenge 后才选择 commitment；哈希在随机 oracle 模型中提供不可预测 challenge。安全性从信息论随机性转为计算假设，依赖哈希函数安全。

## 7.5 Commitments 与多项式指纹

ZKP 经常是：先隐藏 witness，再生成 challenge，最后只打开足够信息。除了哈希承诺和 Pedersen 承诺，SNARK 使用 polynomial commitment。

Schwartz-Zippel 引理的直觉是：两个不同的低次数多项式只可能在有限多个点相等。如果把计算正确性编码成多项式恒等式，在一个随机点检查两者相等，错误多项式被误接受的概率极低。

KZG commitment 可以把多项式 `f(x)` 承诺成一个群元素，再证明 `f(5)=86` 而不公开整个多项式。一个群元素承诺和一次评估证明，使大计算可以被压缩为很小的对象；代价是配对曲线和 trusted setup。

## 7.6 Arithmetic circuit、R1CS 与 QAP

任意程序都可以拆成加法和乘法门。例如证明“我知道 x，使 `x^2+x=12`”：witness 是 x=3，电路先算 `w1=x×x`，再算 `(w1+x)×1=12`。

R1CS（Rank-1 Constraint System）把每个门写成：

```text
(A · s) × (B · s) = (C · s)
```

其中 s 是包含常数 1、私有 witness 和中间 wire 的向量。加法可以乘以 1 表示，常数也能表示，因此 R1CS 能表达任意算术电路。

电路规模决定 prover 成本：简单乘法只需很少约束，SHA-256 约数万约束，签名验证约数十万，完整 Ethereum 区块可能上千万，ML 推理可能上亿。关键不对称是：prover 很贵，verifier 可以很快。

R1CS 到 QAP 的思路：把每条约束插值为多项式，在约束点构造 `Z(x)`；所有约束成立，当且仅当某个多项式恒等式能被 Z(x) 整除。verifier 不检查所有点，而是在一个随机点检查，利用 Schwartz-Zippel 以极高概率发现错误。

开发者不会总是手写 R1CS。Circom 是类似 JavaScript 的电路 DSL，Noir 接近 Rust 风格，Cairo 面向 STARK，Halo2 是 Rust 库；它们把约束编写、编译和证明系统连接起来。更高层的 zkVM（如 RISC-V/Rust 路线）允许开发者写较普通的程序，再由 VM 产生执行证明，降低了 ZK 应用开发门槛，但通常会付出更大的电路和证明成本。SnarkJS 等工具负责生成/验证 Groth16 或 PLONK proof，proving-as-a-service 则把昂贵的证明计算外包。

## 7.7 SNARK

SNARK 的含义：

- **S**uccinct：证明很小；
- **N**on-interactive：一次消息；
- **A**rgument：对计算能力受限攻击者的计算安全保证；
- **R** of Knowledge：证明者必须知道 witness。

常见流程：

```text
程序
 -> arithmetic circuit/R1CS
 -> QAP/PLONK constraints
 -> prover 计算并承诺
 -> 输出 proof
 -> verifier 根据 public inputs 快速验证
```

### 7.7.1 Trusted setup

许多 SNARK 需要生成秘密参数 τ，并公开 τ 的幂相关群元素。若有人保留 τ（toxic waste），可能伪造不真实命题的证明。因此需要 multi-party ceremony：每人加入随机秘密，处理参数后删除自己的秘密；只要至少一个参与者诚实删除，最终秘密就未知。

- **Groth16**：约 192 字节、验证快，但每个电路需要单独 setup；
- **PLONK**：通用 setup，一次 ceremony 可支持许多电路，证明略大；
- **Halo2/IPA**：通过不同承诺结构支持更少 trusted setup 的递归证明。

递归 SNARK 把“验证另一个证明”也放入电路，能够把很多步骤压缩成一个证明，用于 light client、proof aggregation 和 rollup-of-rollups。

## 7.8 STARK、FRI 与 Bulletproofs

STARK（Scalable Transparent ARgument of Knowledge）不需要 trusted setup，基于哈希，具有后量子安全倾向，但证明比 Groth16 大得多，验证也略慢。

FRI 是 STARK 的多项式低次数测试：prover 把多项式值放入 Merkle tree，verifier 随机抽样，逐轮折半多项式度数，证明其“接近低次数”。它不依赖配对曲线，适合透明和后量子取舍。

Bulletproofs 不需要 trusted setup，证明大小对数级，适合范围证明；但验证通常是线性级，不适合大规模通用计算。

| 系统 | Setup | Proof | Verify | 适合 |
|---|---|---:|---:|---|
| Groth16 | 每电路 | 很小 | 很快 | 最小证明、Zcash |
| PLONK | 通用 | 较小 | 快 | 可升级电路、zkSync |
| STARK | 无 | 较大 | 中等 | 透明、后量子、Starknet |
| Bulletproofs | 无 | 对数级 | 线性级 | 范围证明、Monero |

不存在绝对最好的系统；选择取决于证明大小、setup 信任、量子安全、证明时间、验证时间和应用是否频繁改电路。

## 7.9 应用

### 7.9.1 Zcash

Zcash 的 shielded pool 把 note 的金额、所有者和随机数承诺到 Merkle tree。花费时 prover 证明：

- 我知道树中某个有效 note；
- note 金额足够；
- Merkle 路径正确；
- 我生成了正确的 nullifier。

nullifier 公开用于阻止双花，但不告诉大家具体花费了哪个 note。新 note 可以给 Bob 7 个单位，剩余 3 个给 Alice，而 sender、receiver、金额和具体旧 note 不公开。

### 7.9.2 Tornado Cash

存款者生成 `(nullifier, secret)`，承诺 `cm=H(nullifier||secret)` 加入固定面额的 Merkle tree。取款时，用 ZKP 证明自己知道某个树中承诺对应的秘密，并公开 nullifier；合约拒绝重复 nullifier。因为证明不透露路径，观察者无法把取款链接到某笔存款。

### 7.9.3 ZK-Rollup

L2 执行大量交易，prover 生成一个“这一批状态转移全部正确”的证明，L1 只验证该证明并更新状态根。它把执行成本转移到链下，用几毫秒级证明验证替代重执行，且没有 optimistic rollup 的长挑战期。

### 7.9.4 私有合约与更广泛应用

Aztec、Aleo、Penumbra 等方向尝试对任意合约输入、状态和执行结果做隐私保护。ZKP 还可用于：

- zkBridge：证明另一条链的共识或区块有效，减少对签名委员会的信任；
- zkML：证明某个模型确实对某输入运行并得到某输出；
- zkTLS：证明网页内容来自 TLS 会话；
- zkEmail：在不公开邮件正文的情况下证明邮件来源或属性；
- zkPassport/zkKYC：证明身份属性而不交出完整证件。

开发抽象从手写电路、Circom/Noir 等 DSL 发展到 SP1、RISC Zero 等 zkVM，使普通程序更容易被编译成可证明计算。

---
