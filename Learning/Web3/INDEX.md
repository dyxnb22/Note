# Web3 索引

这个索引页不只是目录，而是把 `Web3` 整理成一条可长期复习的主线地图。现在这 38 篇已经按学习价值、先修关系和复习优先级重新排成三层梯度。

## 关于本专题

这条线的目标，不是追逐某个币种或短期热点，而是理解链上系统是怎么工作的，协议为什么这样设计，风险为什么会反复出现，以及一个 Web3 产品从钱包、合约到数据服务是如何拼起来的。

你现有的 [web3](</Users/diaoyuxuan/web3/README.md>) 参考目录更偏工程实操路线；这里则把它升级成知识库结构，方便长期沉淀、交叉阅读和反复复习。

## 梯度说明

- `第一梯队（12 篇）`：母问题，最值得反复复习，优先建立整个 Web3 的共用语言和主干框架。
- `第二梯队（13 篇）`：关键扩展层，负责把主干补厚，把核心系统里的关键约束和高频风险讲透。
- `第三梯队（13 篇）`：补全层，负责把生态理解、治理、工程落地和研究视角接起来。

## 推荐学习路径

**第一阶段：先把底层语言立起来**
`Web3 到底是什么` → `为什么要从工程和机制两条线同时学 Web3` → `链上世界里的身份、资产、状态和权限`

**第二阶段：补链上系统和交互主干**
`为什么区块链是状态机而不只是数据库` → `钱包、私钥、签名和地址` → `交易、Gas、Nonce 和链上确认` → `Solidity 合约到底在解决什么问题`

**第三阶段：进入协议与资产主干**
`AMM 为什么能在没有订单簿时完成交易` → `借贷协议为什么离不开超额抵押` → `稳定币的几种基本路线`

**第四阶段：建立研究视角**
`如何研究一个协议`，再回头串联安全、治理、索引和数据分析专题。

## 第一梯队

这些笔记是整条 Web3 主线的母篇，适合最先读、最先反复复习：

- [链上世界里的身份、资产、状态和权限](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/00_Foundations/链上世界里的身份、资产、状态和权限.md)
- [为什么要从工程和机制两条线同时学 Web3](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/00_Foundations/为什么要从工程和机制两条线同时学%20Web3.md)
- [Web3 到底是什么：它和互联网、金融、数据库各是什么关系](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/00_Foundations/Web3%20到底是什么：它和互联网、金融、数据库各是什么关系.md)
- [为什么区块链是状态机而不只是数据库](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/01_Blockchain_and_Consensus/为什么区块链是状态机而不只是数据库.md)
- [交易、Gas、Nonce 和链上确认](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/02_Wallets_Transactions_and_RPC/交易、Gas、Nonce%20和链上确认.md)
- [钱包、私钥、签名和地址](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/02_Wallets_Transactions_and_RPC/钱包、私钥、签名和地址.md)
- [权限控制、所有权和多签的基本逻辑](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/03_Smart_Contracts_and_Development/权限控制、所有权和多签的基本逻辑.md)
- [Solidity 合约到底在解决什么问题](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/03_Smart_Contracts_and_Development/Solidity%20合约到底在解决什么问题.md)
- [借贷协议为什么离不开超额抵押](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/04_DeFi_and_Tokenomics/借贷协议为什么离不开超额抵押.md)
- [稳定币的几种基本路线](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/04_DeFi_and_Tokenomics/稳定币的几种基本路线.md)
- [AMM 为什么能在没有订单簿时完成交易](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/04_DeFi_and_Tokenomics/AMM%20为什么能在没有订单簿时完成交易.md)
- [如何研究一个协议](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/07_Research_and_Build_Workflow/如何研究一个协议.md)

## 第二梯队

这些笔记负责把主干补厚，尤其是把关键约束、关键风险和关键实现边界讲清楚：

- [公链、协议、dApp、钱包、交易所分别是什么](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/00_Foundations/公链、协议、dApp、钱包、交易所分别是什么.md)
- [学习 Web3 时最容易混淆的几层问题](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/00_Foundations/学习%20Web3%20时最容易混淆的几层问题.md)
- [共识机制在解决什么问题：PoW、PoS 和最终性](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/01_Blockchain_and_Consensus/共识机制在解决什么问题：PoW、PoS%20和最终性.md)
- [为什么会有 Layer2：扩容、成本和安全继承](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/01_Blockchain_and_Consensus/为什么会有%20Layer2：扩容、成本和安全继承.md)
- [账户模型、状态转换和链上执行](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/01_Blockchain_and_Consensus/账户模型、状态转换和链上执行.md)
- [签名登录为什么需要 nonce、domain 和 deadline](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/02_Wallets_Transactions_and_RPC/签名登录为什么需要%20nonce、domain%20和%20deadline.md)
- [RPC、节点和链上读取：应用到底在和谁通信](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/02_Wallets_Transactions_and_RPC/RPC、节点和链上读取：应用到底在和谁通信.md)
- [合约升级为什么危险：Proxy、治理和状态一致性](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/03_Smart_Contracts_and_Development/合约升级为什么危险：Proxy、治理和状态一致性.md)
- [事件为什么是链上和后端之间的桥梁](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/03_Smart_Contracts_and_Development/事件为什么是链上和后端之间的桥梁.md)
- [滑点、深度和无常损失到底在讲什么](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/04_DeFi_and_Tokenomics/滑点、深度和无常损失到底在讲什么.md)
- [清算机制为什么是 DeFi 的压力测试点](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/04_DeFi_and_Tokenomics/清算机制为什么是%20DeFi%20的压力测试点.md)
- [重入攻击为什么反复出现](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/05_Security_and_Risks/重入攻击为什么反复出现.md)
- [Oracle 为什么是 DeFi 的高风险入口](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/05_Security_and_Risks/Oracle%20为什么是%20DeFi%20的高风险入口.md)

## 第三梯队

这些笔记负责把生态、工程落地、治理和研究工作流接起来，适合在主干建立后系统补全：

- [跨链为什么危险：资产桥、消息桥与信任假设](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/01_Blockchain_and_Consensus/跨链为什么危险：资产桥、消息桥与信任假设.md)
- [Mempool、打包、失败交易和用户体验](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/02_Wallets_Transactions_and_RPC/Mempool、打包、失败交易和用户体验.md)
- [为什么 Foundry 测试不只是单元测试](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/03_Smart_Contracts_and_Development/为什么%20Foundry%20测试不只是单元测试.md)
- [状态变量、函数、事件、modifier 分别扮演什么角色](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/03_Smart_Contracts_and_Development/状态变量、函数、事件、modifier%20分别扮演什么角色.md)
- [Token 设计、治理代币和激励错配](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/04_DeFi_and_Tokenomics/Token%20设计、治理代币和激励错配.md)
- [审计、模糊测试和不变量测试分别解决什么问题](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/05_Security_and_Risks/审计、模糊测试和不变量测试分别解决什么问题.md)
- [私钥、授权和前端钓鱼风险](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/05_Security_and_Risks/私钥、授权和前端钓鱼风险.md)
- [监管、合规和去中心化叙事的张力](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/06_Governance_and_Crypto_Society/监管、合规和去中心化叙事的张力.md)
- [链上治理为什么常常落到少数人手里](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/06_Governance_and_Crypto_Society/链上治理为什么常常落到少数人手里.md)
- [DAO 在解决什么问题，又解决得怎么样](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/06_Governance_and_Crypto_Society/DAO%20在解决什么问题，又解决得怎么样.md)
- [从最小 demo 到可展示 Web3 项目](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/07_Research_and_Build_Workflow/从最小%20demo%20到可展示%20Web3%20项目.md)
- [链上数据分析到底在看什么](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/07_Research_and_Build_Workflow/链上数据分析到底在看什么.md)
- [事件索引服务为什么是 Web3 后端的关键能力](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/07_Research_and_Build_Workflow/事件索引服务为什么是%20Web3%20后端的关键能力.md)

## 通用判断框架

学习任何 Web3 主题时，都可以按下面顺序压缩成自己的复习答案：

1. 它解决的是哪一层问题：用户体验、协议规则、工程基础设施还是治理？
2. 状态如何变化：谁能触发，系统依据什么规则执行，结果如何确认？
3. 信任和权限落在哪里：谁掌握关键权力，哪些假设一旦失效会放大风险？
4. 如何落地和验证：看哪些指标、测试哪些边界、如何处理失败和异常？

不要只记名词或项目案例，要能把“机制 → 约束 → 风险 → 工程取舍”讲成一条链。

## 怎么用

- `第一次进入`：先按第一梯队读，建立共同语言。
- `已经过完一轮`：按第二梯队补关键机制和风险。
- `准备做项目或做研究`：第三梯队要和第一、第二梯队交叉读，而不是最后孤立读。

## 完整目录

- 根说明：[README.md](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/README.md)
- 共同语言：[00_Foundations](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/00_Foundations/README.md)
- 链与共识：[01_Blockchain_and_Consensus](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/01_Blockchain_and_Consensus/README.md)
- 钱包与交易：[02_Wallets_Transactions_and_RPC](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/02_Wallets_Transactions_and_RPC/README.md)
- 合约与开发：[03_Smart_Contracts_and_Development](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/03_Smart_Contracts_and_Development/README.md)
- DeFi 与 Tokenomics：[04_DeFi_and_Tokenomics](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/04_DeFi_and_Tokenomics/README.md)
- 安全与风险：[05_Security_and_Risks](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/05_Security_and_Risks/README.md)
- 治理与加密社会：[06_Governance_and_Crypto_Society](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/06_Governance_and_Crypto_Society/README.md)
- 研究与构建流程：[07_Research_and_Build_Workflow](/Users/diaoyuxuan/Documents/Notes/Learning/Web3/07_Research_and_Build_Workflow/README.md)

---

`#web3 #index #learning-map`
