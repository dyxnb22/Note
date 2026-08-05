# Lecture 3A：Ethereum 基础、账户模型、EVM 与智能合约

来源：课程课件 `lecture3a-ethereum-fundamentals-handout.pdf`（原 PDF 未随笔记入库，当前只保留整理稿。）

## 3A.1 从 Bitcoin 到可编程平台

Bitcoin 主要解决货币转移；Ethereum 把区块链变成一个由所有节点共同执行的确定性计算平台。它支持：

- 账户和余额；
- 持久化存储；
- 合约代码；
- 合约之间的组合调用；
- 任何可表达为 EVM 程序的规则。

Bitcoin Script 主要是每个 UTXO 独立执行的条件。它没有跨交易持久状态。Ethereum 的核心改变是有一个持续存在的 world state。

## 3A.2 Ethereum 三层结构与账户

可以把系统分成：

1. **Consensus layer**：PoS 验证者决定区块顺序和最终性；
2. **Execution/compute layer**：EVM 按交易执行代码；
3. **State layer**：保存账户余额、nonce、代码和 storage。

Ethereum 有两种账户：

### EOA（Externally Owned Account）

- 由私钥控制；
- 没有代码和持久存储；
- 可以主动发起交易；
- nonce 记录已发送交易数量，防止 replay。

### Contract Account

- 地址由创建者和 nonce 派生；
- 由部署后的 bytecode 控制；
- 有持久化 storage；
- 不能像 EOA 一样主动发起交易，只能被交易或其他合约调用。

两者都有余额，区别在于控制方式是私钥还是代码。

## 3A.3 Ethereum 交易

交易字段包括：

- sender/signature：身份和授权；
- receiver：EOA、合约地址或合约创建占位；
- value：发送的 wei；
- data：部署 bytecode 或函数 calldata；
- gas limit：最多允许消耗的计算预算；
- fee 参数；
- nonce：必须和发送者当前 nonce 匹配。

三类常见交易：

1. value transfer：向 EOA 转 ETH；
2. contract creation：receiver 为空/特殊值，data 是初始化代码；
3. contract invocation：receiver 是合约地址，data 是函数选择器和参数。

交易通过以下检查才有效：余额足以覆盖 value 与最大 gas；nonce 正确；签名有效。nonce 防止相同交易重复执行，也强制同一 EOA 的交易有顺序。

## 3A.4 Gas、确定性和交易执行

EVM 对每个操作设定 gas 成本。粗略示例：ADD 很便宜，SLOAD 读取 storage 更贵，SSTORE 写入持久状态更贵。手续费可写为：

```text
fee = gasUsed × gasPrice
```

gas limit 是上限；实际未使用的 gas 退回，执行超过预算则交易 revert，已消耗 gas 通常不退。

EIP-1559 将费用分成：

```text
total fee = base fee + priority fee
```

base fee 根据区块需求调整并被销毁；priority fee 是给 proposer 的小费。销毁 base fee 能抑制验证者自己塞垃圾交易，并在需求高时给 ETH 带来通缩压力。

所有节点必须得到同一个状态，因此执行必须确定性：交易按区块内位置严格顺序执行，不能依赖节点各自调用外部 API 或未定义的随机数。`block.timestamp`、`block.number` 是所有节点看到的区块环境，但不是安全的随机源。

一笔交易可以触发多个内部合约调用；所有调用在同一交易的原子上下文中执行。如果最终 revert，状态修改整体回滚，但已消耗的 gas 仍然会被计费。

调用类型：

- internal call：同一合约内部调用；
- external call：向另一个合约发送消息，`msg.sender` 会变化；
- `delegatecall`：执行外部代码，但使用调用者的 storage 和上下文，常用于库和可升级代理，也因此要求 storage layout 严格匹配。

receipt 记录 status、gas used、logs 和合约创建地址。事件日志是便宜的外部索引信号，不等于合约 storage。

## 3A.5 Bitcoin UTXO 与 Ethereum account 对比

| 维度 | Bitcoin UTXO | Ethereum Account |
|---|---|---|
| 状态 | 未花费输出集合 | 账户余额、nonce、代码、storage |
| 防重放 | UTXO 只能花一次 | nonce |
| 并行验证 | 相对容易 | 共享状态使并行更难 |
| 合约 | 受限脚本 | 通用 EVM |
| 隐私 | 新地址有一定帮助 | 长期账户和 DeFi 交互更易链接 |

Ethereum 的 block header 还承诺 state root 和 receipts root。state root 是账户状态树的根，使轻客户端能用短证明验证状态，而不必从 genesis 重放所有交易。

节点保存量也有取舍：archival node 保存完整历史，适合区块浏览器和分析；pruned/full node 主要保存当前状态和验证所需数据；light client 只保存很少数据并依赖证明。应用通常由前端 UI、链上合约逻辑和区块链数据三部分组成。

## 3A.6 Solidity 与编译流程

流程是：

```text
Solidity/Vyper/Yul/Cairo
  -> 编译器
  -> EVM assembly/bytecode
  -> 部署到链上
```

Solidity 是静态类型、合约导向语言，支持 structs、mappings、arrays、inheritance、libraries、interfaces，并用 `require`、`assert`、`revert` 处理错误。0.8 版本开始，整数溢出默认会检查并 revert。

常用类型：`uint256`、`address`、`bytes32`、`bool`；引用类型包括 struct、array、mapping、string 和 bytes。

重要全局变量：

- `msg.sender`：当前直接调用者；
- `msg.value`：随当前调用发送的 wei；
- `block.timestamp`：当前区块时间；
- `tx.origin`：最初的 EOA，不应该用于权限认证，否则恶意合约可利用 phishing 让 `tx.origin` 仍是用户。

可见性：`external`、`public`、`internal`、`private`。状态修饰符：`view` 只能读状态，`pure` 不能读状态；通过链外 RPC 调用 view/pure 通常免费，但若被另一个链上交易调用仍然消耗 gas。

## 3A.7 EVM 结构与 ABI

EVM 是 256 位栈机，主要使用：

- Stack：操作数；
- Memory：调用期间的易失字节数组；
- Storage：永久 key-value 状态；
- Calldata：外部调用提供的只读输入。

storage 写入长期由每个节点保存，因此通常最贵。优化包括少写 storage、把只读参数放在 calldata、打包变量减少 storage slot。

ABI 函数调用的 calldata 以 selector 开头：

```text
selector = first 4 bytes of keccak256("functionName(types)")
calldata = selector || ABI-encoded arguments
```

例如 ERC20 的 `transfer(address,uint256)` 有固定 selector。合约收到 calldata 后解析 selector，调用对应函数；未知 selector 进入 fallback，空 data 且带 ETH 可进入 receive。

Solidity 的接口调用会自动完成 ABI 编码、external call 和返回值解码。事件的 indexed 参数成为可检索 topics，前端和区块浏览器依靠事件更新 UI。

## 3A.8 开发安全起点

在进入下一讲的实际攻击前，先记住：

1. 检查输入和权限；
2. 使用 `require` 处理预期失败，`assert` 检查不应被破坏的不变量；
3. 外部调用必须检查返回值；
4. 先更新状态，再进行外部调用；
5. 使用成熟库，不要随意重复实现 token、权限和数学逻辑。

---
