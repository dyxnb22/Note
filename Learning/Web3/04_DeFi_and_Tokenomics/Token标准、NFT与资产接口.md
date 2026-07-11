# Token 标准、NFT 与资产接口

Token 标准定义资产合约与钱包、DEX、市场之间的共同接口。ERC-20 表示可互换余额；ERC-721 表示唯一 token；ERC-1155 支持同一合约中的可互换和非同质资产。标准解决互操作，不保证资产价值或合约安全。

实现重点包括 `transfer/approve/transferFrom` 的授权语义、事件、metadata、supply 与权限。无限授权方便但扩大被盗风险；转账税、黑名单、可升级逻辑等非标准行为会破坏上层假设。

NFT 的所有权与内容存储不同：链上通常只存 token 与 URI，图片/元数据可能依赖中心化服务或 IPFS。分析资产时要同时看合约权利、元数据可用性与发行方控制权。

`#web3 #erc20 #nft #token-standard`
