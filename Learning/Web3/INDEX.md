# Web3 学习索引

这条主线同时回答两类问题：链上系统怎样运行，以及它为什么会产生不同于传统后端和金融系统的信任、治理与风险结构。

## 学习路径

```text
概念与信任边界
  → 状态、共识和扩容
  → 钱包、交易与 RPC
  → 智能合约工程
  → DeFi 机制与安全
  → 治理、研究和项目验证
```

## 核心文档

| 阶段 | 主文档 |
|---|---|
| 系统边界 | [Web3 到底是什么](00_Foundations/Web3%20到底是什么：它和互联网、金融、数据库各是什么关系.md)、[身份、资产、状态和权限](00_Foundations/链上世界里的身份、资产、状态和权限.md) |
| 学习方法 | [为什么从工程和机制两条线学习](00_Foundations/为什么要从工程和机制两条线同时学%20Web3.md) |
| 链的运行 | [为什么区块链是状态机](01_Blockchain_and_Consensus/为什么区块链是状态机而不只是数据库.md) |
| 用户与交易 | [钱包、私钥、签名和地址](02_Wallets_Transactions_and_RPC/钱包、私钥、签名和地址.md)、[交易、Gas、Nonce 和确认](02_Wallets_Transactions_and_RPC/交易、Gas、Nonce%20和链上确认.md) |
| 合约工程 | [Solidity 合约解决什么问题](03_Smart_Contracts_and_Development/Solidity%20合约到底在解决什么问题.md)、[权限与多签](03_Smart_Contracts_and_Development/权限控制、所有权和多签的基本逻辑.md) |
| DeFi | [AMM](04_DeFi_and_Tokenomics/AMM%20为什么能在没有订单簿时完成交易.md)、[超额抵押](04_DeFi_and_Tokenomics/借贷协议为什么离不开超额抵押.md)、[稳定币](04_DeFi_and_Tokenomics/稳定币的几种基本路线.md) |
| 研究工作流 | [如何研究一个协议](07_Research_and_Build_Workflow/如何研究一个协议.md) |

## 机制速查

- [Web3 概念速查](00_Foundations/Web3概念速查.md)
- [区块链网络机制速查](01_Blockchain_and_Consensus/区块链网络机制速查.md)
- [钱包与交易工程速查](02_Wallets_Transactions_and_RPC/钱包与交易工程速查.md)
- [智能合约工程速查](03_Smart_Contracts_and_Development/智能合约工程速查.md)
- [DeFi 机制与风险速查](04_DeFi_and_Tokenomics/DeFi机制与风险速查.md)
- [Web3 安全速查](05_Security_and_Risks/Web3安全速查.md)
- [治理与合规速查](06_Governance_and_Crypto_Society/治理与合规速查.md)
- [Web3 研究与构建速查](07_Research_and_Build_Workflow/Web3研究与构建速查.md)

## 验证原则

1. 先写清资产、主体、权限和信任来源。
2. 沿交易生命周期检查签名、广播、排序、执行、确认和失败。
3. 对协议同时分析平静期和极端市场状态。
4. 合约测试覆盖示例、模糊测试和业务不变量；审计不能替代权限治理。
5. 标准、网络参数、合约地址和监管结论使用前重新核验。

主要参考入口：[Ethereum 开发文档](https://ethereum.org/developers/docs/)、[Solidity 文档](https://docs.soliditylang.org/)、[EIPs](https://eips.ethereum.org/)、[OpenZeppelin 文档](https://docs.openzeppelin.com/)。核对日期：2026-07-22。

`#web3 #blockchain #smart-contract #index`
