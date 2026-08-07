# Web3

这条主线同时学习链上系统如何运行，以及它不同于传统后端和金融系统的信任、治理与风险结构。

## 学习顺序

```text
概念与信任边界 → 状态/共识/扩容 → 钱包/交易/RPC
→ 智能合约 → DeFi → 安全/治理 → 研究与高级工程
```

| 阶段 | 主文档 |
|---|---|
| 系统边界 | [Web3 到底是什么](00_Foundations/Web3%20到底是什么：它和互联网、金融、数据库各是什么关系.md)、[身份/资产/状态/权限](00_Foundations/链上世界里的身份、资产、状态和权限.md) |
| 链的运行 | [区块链是状态机](01_Blockchain_and_Consensus/为什么区块链是状态机而不只是数据库.md) |
| 用户与交易 | [钱包、私钥、签名和地址](02_Wallets_Transactions_and_RPC/钱包、私钥、签名和地址.md)、[交易与确认](02_Wallets_Transactions_and_RPC/交易、Gas、Nonce%20和链上确认.md) |
| 合约工程 | [Solidity 合约](03_Smart_Contracts_and_Development/Solidity%20合约到底在解决什么问题.md)、[权限与多签](03_Smart_Contracts_and_Development/权限控制、所有权和多签的基本逻辑.md) |
| DeFi | [AMM](04_DeFi_and_Tokenomics/AMM%20为什么能在没有订单簿时完成交易.md)、[借贷](04_DeFi_and_Tokenomics/借贷协议为什么离不开超额抵押.md)、[稳定币](04_DeFi_and_Tokenomics/稳定币的几种基本路线.md) |
| 高级与研究 | [协议研究](07_Research_and_Build_Workflow/如何研究一个协议.md)、[高级工程与安全](08_Advanced_Engineering/Web3高级工程与协议安全.md) |

## 验证原则

先写清资产、主体、权限和信任来源；沿交易生命周期检查签名、广播、排序、执行、确认和失败；对协议同时分析平静期与极端状态；测试覆盖示例、模糊测试和业务不变量；标准、网络参数、合约地址和监管结论使用前重新核验。

目录内的“速查”页只做复习和问题定位，不替代主文档。主要入口：[Ethereum](https://ethereum.org/developers/docs/)、[Solidity](https://docs.soliditylang.org/)、[EIPs](https://eips.ethereum.org/)、[OpenZeppelin](https://docs.openzeppelin.com/)。核对日期：2026-07-30。

`#web3 #blockchain #smart-contract #index`
