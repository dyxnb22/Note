# Lecture 1B：Bitcoin 如何表示所有权、脚本与现代发展

## 1B.1 UTXO 不是账户余额，而是现金纸币

银行账本记录 `Alice: 5 BTC`。Bitcoin 不保存这样的账户余额，而保存一组 **Unspent Transaction Outputs（UTXO）**。每个 UTXO 是一笔带金额和花费条件的输出；谁能满足花费条件，谁就能消费它。

可以把 UTXO 想成现金纸币：你不能把一张 10 元纸币撕成 7 元，必须整张交出去，再收到 3 元找零。Bitcoin 也一样：输入 UTXO 必须整体消耗，交易输出再生成支付输出和找零输出。

```text
Alice 选择 0.3 BTC + 0.4 BTC = 0.7 BTC
支付 Bob                = 0.5 BTC
找零 Alice               = 0.19 BTC
手续费                   = 0.01 BTC
```

旧的两个 UTXO 从 UTXO set 删除，新的两个输出加入 UTXO set。不存在“币从地址移动到地址”的物理对象；账本状态只是旧输出被花掉、新输出被创建。

UTXO 标识为 `(txid, output_index)`。基本规则：

- 每个 UTXO 只能被花费一次；
- 每个输入必须引用一个存在且未花费的 UTXO；
- 输入总额必须不小于输出总额，差额是手续费；
- 一个交易可以合并多个输入，也可以拆成多个输出；
- 钱包保存的是私钥和地址信息，UTXO 在区块链上；钱包通过扫描或索引 UTXO 计算所谓“余额”。

优势是双花检查清晰、不同 UTXO 可以并行验证、使用新地址有隐私潜力。缺点是余额查询需要维护 UTXO set，跨交易共享状态困难，智能合约表达能力弱。

## 1B.2 Bitcoin Script：把 UTXO 锁起来

每个输出包含一个 **ScriptPubKey**，相当于锁；花费输入携带 **ScriptSig/witness**，相当于钥匙。节点把两者拼在一起，在栈式脚本引擎中执行：

```text
ScriptSig + ScriptPubKey -> TRUE 才允许花费
```

Bitcoin Script 有意不是图灵完备的，通常不支持任意循环。这样可以避免无限执行和许多拒绝服务问题，但代价是表达能力有限。

### 1B.2.1 P2PKH 的逐步执行

典型 P2PKH：

```text
ScriptSig:    <signature> <public_key>
ScriptPubKey: OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
```

执行过程：

1. 把签名和公钥压入栈；
2. `OP_DUP` 复制公钥；
3. `OP_HASH160` 计算复制公钥的哈希；
4. 与锁定脚本中的公钥哈希比较；
5. `OP_CHECKSIG` 检查签名是否对当前交易有效。

它同时证明“这是匹配的公钥”和“公钥对应的私钥确实签了这笔交易”。

### 1B.2.2 P2SH、多签与时间锁

P2SH 让付款者只看到赎回脚本的哈希：

```text
ScriptPubKey: HASH160 <hash(redeem_script)> EQUAL
ScriptSig:    <signatures> <redeem_script>
```

典型 2-of-3 多签要求三个公钥中任意两个签名。企业金库、托管、冷存储都可以使用。P2SH 把复杂脚本隐藏到真正花费时才揭示，减少地址复杂度。

Bitcoin Script 还支持：

- CLTV：绝对时间锁，某日期前不能花费；
- CSV：相对时间锁，UTXO 创建后必须等待若干区块；
- HTLC：知道满足 `H(secret)=h` 的秘密可以领取，否则超时退款；
- M-of-N multisig：多个密钥共同控制资金。

### 1B.2.3 Miniscript 与 Taproot

Miniscript 是 Script 的结构化子集。例如：

```text
Bob OR (Alice AND Carol) OR (Alice after six months)
```

可以被形式化表示、自动分析、组合和优化，降低手写脚本错误。

Taproot 把复杂花费条件放在一个 Merkleized tree 中，并优先使用 **key path**：如果参与者合作，就用聚合签名看起来像普通单签交易；只有合作失败时才揭示实际使用的 script path。这样既节省空间，也隐藏未使用的条件。

## 1B.3 Alice 向 Bob 支付的一笔完整交易

1. 钱包扫描 Alice 控制的 UTXO；
2. 选择输入并生成 Bob 的支付输出、Alice 的找零输出；
3. 对每个输入分别使用能解锁该 UTXO 的私钥签名；
4. 广播，节点验证签名、UTXO、金额；
5. 矿工按手续费率从 mempool 选择交易；
6. 交易进入区块，获得第一次确认；
7. 等待更多区块后，双花逆转的概率快速下降。

课件用 1、3、6 个区块分别表示低、中、高置信度；6 个确认是常见经验规则而不是数学上绝对的最终性。

## 1B.4 Bitcoin 的升级与生态

- **SegWit（2017）**：把 witness 从交易主体中分离，修复 transaction malleability，并提高有效区块容量；它也为 Lightning 提供了重要基础。
- **Taproot（2021）**：引入 Schnorr、MAST/脚本路径和更好的协作隐私。
- **P2WPKH/SegWit 原生地址**：把见证数据放在传统交易结构之外，减少交易重量并修复可塑性问题；
- **P2TR/Taproot 地址**：用 Schnorr key path 和 Merkleized script path 让合作花费看起来像普通单签，同时保留复杂回退条件。
- **Lightning Network**：把大量小额支付移到链下支付通道。
- **Ordinals/Inscriptions**：利用 witness 数据承载任意数据，形成 Bitcoin 上的 NFT 生态。
- **Taproot Assets**：在 Bitcoin/Lightning 上发行资产和稳定币的方向。
- **MuSig2**：把 N-of-N 的多个签名聚合成一个外观普通的签名。
- **FROST**：用分布式密钥生成实现阈值签名，避免单一可信 dealer。
- **Silent Payments**：用一个静态收款信息派生每笔唯一支付地址，改善收款方隐私。

## 1B.5 Bitcoin 隐私与安全挑战

Bitcoin 交易永久公开；地址不是现实身份，但交易图、KYC 交易所和地址复用可以把两者连接起来。提高隐私的工具包括 CoinJoin、Taproot、Lightning 的洋葱路由和 Silent Payments。

安全问题包括：

- 51% 攻击：等待确认、经济威慑；
- 双花：增加确认深度；
- Sybil：PoW 让创建身份不再免费；
- Eclipse：攻击者用恶意邻居隔离节点，解决办法是保持多样化连接。

软分叉向后兼容，旧节点仍可接受新规则下的区块；SegWit 和 Taproot 是例子。硬分叉不兼容，争议时可能形成两条链，例如 BCH 和 ETC。

Bitcoin 的 trilemma 选择是：

```text
去中心化 + 安全性  >  可扩展性
```

它牺牲了吞吐量，换取开放参与和较强的独立验证能力。扩容、量子安全、能源、监管和隐私是持续研究方向。

扩容研究还包括 Utreexo：用一个很小的 accumulator/根承诺替代节点本地保存完整 UTXO set，花费时附带成员证明；它把存储负担转化为证明和更新负担。stateless client 也沿着相似方向，让节点更多依赖状态证明而不是保存全部状态。

---

