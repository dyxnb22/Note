# Web3 高级工程与协议安全

本篇从 EVM 执行进入合约工程、Oracle/Indexer、L2、跨链、MEV、账户抽象和升级治理。目标不是追逐链和协议名称，而是识别资产、状态、信任、排序和恢复边界。

## 1. EVM 状态

Ethereum 将执行环境表示为状态机。账户包含 Nonce、余额、代码和存储根；合约 Bytecode 在 EVM 中执行。

理解四类数据：

- Stack：指令操作数，空间小、生命周期为调用。
- Memory：调用期间的临时字节数组。
- Storage：合约持久状态，写入成本高。
- Calldata：外部调用的只读输入。

具体 Opcode 和 Gas 成本可能随升级变化，使用前查当前网络规则。

## 2. 调用语义

- `call`：调用目标代码，目标使用自己的 Storage。
- `delegatecall`：执行目标代码，但使用调用方 Storage、地址和上下文。
- `staticcall`：只读调用语义。

低级调用返回成功标志和数据，必须检查。外部调用会把控制权交给不可信代码，因此状态更新顺序和重入保护非常重要。

## 3. ABI 与事件

ABI 定义函数选择器、参数编码、返回值和事件。事件写入日志，适合链下索引和通知，不是合约内可直接读取的状态。

升级或更换实现时，ABI 兼容只是一个维度，还要检查 Storage Layout、权限和事件语义。

## 4. Gas 与资源

Gas 限制单次执行资源并为网络定价。优化顺序：

1. 先保证正确和安全。
2. 减少不必要 Storage 写入。
3. 选择合适数据布局和批处理。
4. 用测试和 Gas Report 验证。

微小 Gas 节省不能换取不可读的权限和算术逻辑。

## 5. Solidity 工程结构

```text
contracts/ → scripts/ → tests/
→ deployment records → verification
→ monitoring → upgrade/governance
```

固定编译器和依赖版本；生成 ABI、Bytecode 和部署参数；不同网络配置和私钥分离。

## 6. Foundry/Hardhat 测试

测试层次：

- 单元测试：函数与权限。
- 集成测试：多合约和 Token。
- Fork Test：在固定区块模拟链上依赖。
- Fuzz Test：生成输入寻找边界。
- Invariant Test：随机调用序列后验证系统不变量。

Fork 测试依赖具体历史状态，不代表未来协议行为。

## 7. 部署

部署前：

- 固定 Commit、Compiler、Optimizer。
- 验证构造参数和初始权限。
- 模拟部署和 Gas。
- 多签/Timelock 执行高风险动作。
- 验证源码与 Bytecode。
- 保存地址、交易和配置。

部署后检查 Owner、Role、Pause、Upgrade Admin、Oracle 和关键限额。

## 8. 安全不变量

典型不变量：

- 总资产守恒。
- 用户债务不被无授权减少。
- 提款不超过权益。
- 抵押率低于阈值必须受限。
- 只有授权主体能升级或暂停。
- 同一签名/Nonce 不可重放。

安全测试围绕不变量和攻击者能力，而不是只跑正常示例。

## 9. 重入

外部调用期间，攻击者可以回调原合约。防御：

- Checks-Effects-Interactions。
- 重入锁。
- Pull Payment。
- 限制可调用目标。
- 把跨合约流程写成明确状态机。

防护一个函数不一定阻止跨函数或跨合约重入。

## 10. 价格与 Oracle

链上协议需要链外或其他市场价格时引入 Oracle 信任。

检查：

- 价格来源和聚合。
- 更新频率与过期。
- 小数位和单位。
- 异常值和熔断。
- 单市场流动性。
- 治理与密钥。

直接使用低流动性 AMM 即时价格容易被闪电贷操纵；TWAP 也有窗口和市场变化边界。

## 11. 闪电贷与组合攻击

闪电贷提供单交易内的大额临时资本，本身不是漏洞，但会放大价格操纵、治理投票、清算和会计错误。

测试要模拟多个协议组合和单交易原子路径，不只验证单合约。

## 12. 签名与重放

签名消息包含：

- Domain/Chain ID。
- 合约地址。
- 动作与参数。
- Nonce。
- Deadline。

签名恢复出的地址仍要通过权限和业务校验。跨链、跨合约和升级后重放必须显式防止。

## 13. Indexer

Indexer 从区块、交易、日志和 Trace 构建可查询视图：

```text
RPC → 区块游标 → 解码事件
→ 幂等落库 → 确认/回滚 → API
```

需要处理链重组、缺块、重复、Provider 限流、ABI 版本和全量重放。链下索引不是链上事实源。

## 14. RPC

RPC 节点可能延迟、限流、返回不同高度或缺少历史数据。客户端记录 Block Number/Hash，关键读取使用多个来源或自建验证。

批量请求、订阅和日志范围应限流，避免一次大查询拖垮 Provider。

## 15. L2 与 Rollup

Rollup 在链下执行交易，把结果和必要数据/证明提交到 L1：

- Optimistic Rollup：默认接受，争议期通过 Fraud Proof 挑战。
- ZK Rollup：提交 Validity Proof 验证状态转换。

评估不只看费用和 TPS，还要看 Sequencer、证明、数据可用性、强制退出、升级权限和桥。

## 16. 数据可用性

状态转换可验证还不够，用户必须获得重建状态所需数据。数据放在 L1、Blob、外部委员会或其他 DA 层，会产生不同安全假设。

“有证明”不等于“用户始终可取回数据”。

## 17. 跨链桥

桥需要证明另一系统发生了什么。主要模型：

- 原生/官方桥。
- Light Client/验证证明。
- 多签或验证者集合。
- Liquidity Network。

检查资产锁定/铸造、消息重放、最终性、验证者、升级、暂停和限额。桥把多个系统的风险组合起来，通常是高价值攻击面。

## 18. MEV

区块构建者可以通过包含、排除和排序交易提取价值。常见表现：

- DEX 套利。
- 清算。
- Sandwich。
- NFT/稀缺资源抢跑。

用户保护包括 Slippage、Deadline、Commit-Reveal、Batch Auction、私有提交和协议级设计。私有通道会引入新的中继和审查信任。

## 19. Account Abstraction

智能账户允许自定义认证、批量、代付 Gas、限额和恢复。工程上检查：

- EntryPoint/执行入口。
- UserOperation 或授权对象。
- Bundler/Paymaster。
- Nonce 与重放。
- 验证 Gas 和 DoS。
- Session Key、Guardian 和恢复。

体验改善不自动等于更安全；恢复人与代付者成为新的信任主体。

## 20. 代理升级

Proxy 使用 `delegatecall` 把逻辑与地址/Storage 分离。常见风险：

- Storage Collision/Layout 变化。
- 初始化函数被重复调用。
- Upgrade Admin 权限。
- 新实现破坏不变量。
- Selector 冲突。
- 用户不知道语义已改变。

升级流程应有多签、Timelock、模拟、Storage 检查、Canary/限额、事件和回滚方案。

## 21. 治理攻击

治理权来自 Token、委托、多签或委员会。分析：

- 提案门槛。
- 投票期与快照。
- 借贷/闪电贷影响。
- Timelock。
- 紧急暂停。
- Admin 可绕过什么。
- 社会层恢复。

“去中心化”要拆成提案、投票、执行、升级和资产控制的具体权力。

## 22. 协议安全实验

1. 实现可重入 Vault 并修复。
2. 操纵低流动性价格源。
3. 复现签名重放。
4. Fork 测试清算和极端价格。
5. 升级 Proxy 并检查 Storage。
6. 模拟 Indexer 链重组。
7. 画 L2/Bridge 退出和信任图。

## 验收清单

- 能解释 EVM 数据区和调用语义。
- 合约有单元、Fuzz、Invariant 和 Fork 测试。
- Oracle、Indexer、L2、Bridge 均写出信任边界。
- MEV、账户抽象和升级纳入安全模型。
- 高权限动作由多签、Timelock、审计和监控约束。

## 来源与核验

- [Ethereum EVM](https://ethereum.org/developers/docs/evm/)
- [Ethereum Scaling](https://ethereum.org/developers/docs/scaling/)
- [Ethereum Data Availability](https://ethereum.org/developers/docs/data-availability)
- [Ethereum MEV](https://ethereum.org/developers/docs/mev/)
- [Ethereum Account Abstraction](https://ethereum.org/roadmap/account-abstraction)
- [Solidity Security Considerations](https://docs.soliditylang.org/en/latest/security-considerations.html)
- [OpenZeppelin Upgrades](https://docs.openzeppelin.com/upgrades)

网络升级、EIP 状态、工具和监管均会变化；使用前按目标链和版本重新核验。核对日期：2026-07-27。

`#web3 #evm #solidity #rollup #security`
