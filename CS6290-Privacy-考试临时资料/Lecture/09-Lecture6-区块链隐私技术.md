# Lecture 6：区块链隐私、混币、环签名与保密交易

来源：课程课件 `lecture6-privacy-handout.pdf`（原 PDF 未随笔记入库，当前只保留整理稿。）

## 6.1 透明性陷阱：公开账本不等于隐私

银行通常不把所有客户交易公开；Bitcoin 却永久公开输入、输出、金额和时间。地址只是 pseudonym，不是 anonymity。只要某个地址通过交易所 KYC、捐款页面、社交账号或网络层被连接到现实身份，历史交易图就可能被回溯分析。

隐私的重要性包括：

- 个人在被监视时会自我审查；
- 机构知道一切而个人无法观察机构，形成权力不对称；
- 企业不希望竞争对手看到供应商价格、工资、并购或交易策略；
- fungibility 要求同单位价值尽量可互换，否则来自“污染地址”的 1 BTC 可能比干净的 1 BTC 更难使用。

隐私不是“帮助违法”的同义词，而是对个人控制信息和减少不对称监视的保护。

隐私谱系可以从透明到完全私密：

```text
透明 -> 伪名 -> 不可链接 -> 金额保密 -> sender/receiver/amount 全部隐藏
Ethereum   Bitcoin   CoinJoin   Confidential Tx   Monero/Zcash
```

## 6.2 区块链怎样泄露信息

常见 chain analysis 启发式：

1. **Common-input ownership**：同一交易中的多个输入通常由同一用户控制；
2. **Change detection**：一个输出是整齐的支付额，另一个是新地址和不规则找零，则后者可能属于付款者；
3. 时间、金额、地址类型和重复使用模式；
4. 与 KYC 交易所、ENS 名称、NFT、DAO 投票等外部数据交叉。

Ethereum 的账户模型让同一地址长期参与 DeFi、授权、NFT 和治理，通常比 Bitcoin 新 UTXO 的使用模式更容易形成完整身份画像。

网络层也会泄露：监控首个广播节点、ISP 连接、恶意 spy nodes 和 mempool 时间，可以推测交易来源 IP。链上隐私与网络隐私是两个正交问题，需要分别使用 coin control、Dandelion++、Tor/I2P/VPN 等方法。

## 6.3 Mixing：打乱交易图

中心化 mixer 让用户把钱交给服务，服务把多人的钱重新分配。优点是简单，缺点是服务商知道完整映射，可能被盗、没收或跑路。

**CoinJoin** 让所有参与者共同签署一个交易：例如 3 个输入各 0.1 BTC，输出是 3 个顺序随机的 0.1 BTC。服务商不能单方面盗走资金，因为每个参与者都必须签名。

CoinJoin 的局限：

- 等额输出是必要条件，否则金额可匹配；
- 参与者需要同时在线协调；
- 时间、输入输出顺序和找零可能泄露；
- 单轮 anonymity set 有限，重复混合也可能遭 intersection attack；
- “toxic change” 会把混合前的身份链回去。

PayJoin 让付款者和收款者都贡献输入，打破“所有输入属于同一人”的启发式，更像普通支付，代价是协议协调复杂。

## 6.4 Commitment schemes：隐藏内容但承诺不会改

### 6.4.1 Hash commitment

两阶段：

```text
commit: c = H(m || r)
reveal: 发布 m,r，验证 H(m||r)=c
```

随机数 r 防止别人枚举低熵消息。性质：

- hiding：从 c 看不出 m；
- binding：发布后不能换成另一个 m' 仍匹配 c。

### 6.4.2 Pedersen commitment

在椭圆曲线群中，用两个没有已知离散对数关系的生成元 g、h：

```text
C(v,r) = vG + rH
```

它隐藏 v 且有加法同态：

```text
C(v1,r1) + C(v2,r2) = C(v1+v2, r1+r2)
```

因此验证者可以确认输入金额之和等于输出金额之和，却不看到每个金额。

### 6.4.3 Merkle membership

Merkle proof 可以证明“某个承诺在树中”，但如果直接公开路径，可能暴露元素是哪一个。再叠加 ZKP，就能证明“我知道树中的某个元素”而不公开索引，这为 Zcash 和 Tornado Cash 做准备。

## 6.5 Stealth addresses：隐藏收款方关联

地址复用会公开 Bob 的总收入、付款人和支出。Stealth address 让 Bob 发布一个 meta-address，付款者为每次支付派生一次性地址。

简化的 ECDH 过程：Bob 发布 scan key `S=sG` 和 spend key `B=bG`；Alice 选随机 `r`，发布 `R=rG`，计算共享秘密 `k=H(rS)`，把资金送到：

```text
P = kG + B
```

Bob 用自己的 `s` 计算 `H(sR)` 得到同一 k，从而识别并使用 P。旁观者没有 s，无法把多次 P 链接到 Bob。

Silent Payments（BIP352）尝试不增加额外明显链上数据，代价是收款方需要扫描交易。Ethereum 的 EIP-5564 则使用 announcement contract 记录临时公钥，但有扫描和 gas 成本。

## 6.6 Ring signatures：隐藏发送者

普通签名告诉大家“Alice 签了”；环签名只证明“环中的某一个公钥签了”，而不告诉是哪个。签名者选择若干 decoy，给非真实成员生成看似合理的值，再为真实成员生成一个让整个环方程闭合的值。

环签名需要解决双花：

```text
key image I = x · H(P)
```

其中 x 是真实私钥，P 是对应公钥。I 对同一密钥确定且唯一，网络可以拒绝重复出现的 I；但从 I 很难反推出 P 或签名者。它实现了“可链接但不可识别”：知道同一私钥是否重复花费，却不知道是谁。

环越大，匿名集合越大，但交易更大、验证更慢，且 decoy 选择不当会被时间和年龄偏差分析。Monero 强制固定 ring size，而不是让用户自由选择一个显眼的小环。

## 6.7 Confidential Transactions：隐藏金额

用 Pedersen commitment 替代明文金额：

```text
输入 C(5,r_in)
输出 C(3,r1) + C(2,r2)
```

只要承诺满足加法关系，验证者可检查输入总和等于输出总和，不知道 5、3、2 的具体数字。

但 Pedersen 承诺允许数学上的负值。如果不限制范围，攻击者可以把 5 表示为 10 加 -5，账面平衡却凭空制造资产。因此必须附带 **range proof**，证明隐藏值是非负的 64-bit 数，即 `v ∈ [0,2^64)`。

Bulletproofs 是不需要 trusted setup 的高效范围证明，证明大小为对数级；Bulletproofs+ 进一步减少大小并改善批量验证。Mimblewimble 结合保密交易和 transaction cut-through：若 A -> B 与 B -> C 相互抵消，可只保留 A -> C 的必要承诺，减少区块链图，但牺牲脚本表达能力并需要交互式签名。

## 6.8 Monero 的隐私栈与取舍

Monero 默认组合三层：

| 隐藏内容 | 技术 |
|---|---|
| 谁发送 | Ring signatures |
| 发给谁 | Stealth addresses |
| 金额多少 | RingCT + Bulletproofs |

相比 opt-in 隐私，默认隐私让所有交易都看起来相似，匿名集合更大；但它带来更大交易、更高验证成本、交易供应量审计困难和交易所支持下降等问题。若密码学实现存在增发 bug，外部观察者可能无法通过公开供应量独立发现。

隐私并非一次性解决：旧版 ring size、decoy age bias、时间分析和 poisoned outputs 都曾削弱 Monero，说明隐私系统需要持续与分析机构进行攻防。

## 6.9 隐私与监管

Tornado Cash 用固定面额存款和 ZKP：存款时把承诺加入 Merkle tree，取款时证明“我知道树中的某个承诺对应的秘密”，只公开 nullifier 防止重复取款，不公开具体是哪笔存款。它引发了“能否制裁一段不可变开源数学代码”的法律与治理问题。

区块链不可变、全节点复制与 GDPR 的删除权、修改权、数据最小化原则存在冲突。把个人信息放链下、链上只存哈希或使用加密后删除密钥可以减轻问题，但不能完美证明历史数据不存在。

Privacy Pools 试图实现可合规的隐私：用户从一个 association set 中取款，并用 ZKP 证明自己的存款属于没有坏参与者的集合，而不公开具体存款。zkKYC、BBS+ selective disclosure、zkTLS 等方向都体现“只证明所需属性”的理念。

监管侧的 Travel Rule 要求虚拟资产服务商在达到规定金额的转账中传递发送者和接收者信息。它与完全公开的链上账本不同：前者是服务商之间的身份信息交换，后者是所有观察者都能看到的交易图。隐私设计因此出现一条“隐私旋钮”：从完全透明、选择性披露，到默认全隐私；目标不是把所有信息都公开或全部隐藏，而是在需要时证明合规属性。

## 6.10 本讲工具对比

| 工具 | 隐藏什么 | 核心信任方式 |
|---|---|---|
| CoinJoin | 交易图关联 | 多方共同签名 |
| Stealth address | 收款方关联 | ECDH 派生一次性地址 |
| Ring signature | 发送者身份 | decoy 环 |
| Pedersen/CT | 金额 | 同态承诺 |
| Bulletproofs | 金额范围合法性 | 无 trusted setup 的 ZK |
| ZKP | 关于隐藏数据的任意可验证事实 | 完整性、健全性、零知识 |

本讲的终点是：前面的工具各自隐藏一个维度；下一讲的 ZKP 让我们不只隐藏数据，还可以证明关于这些隐藏数据的复杂命题。

---
