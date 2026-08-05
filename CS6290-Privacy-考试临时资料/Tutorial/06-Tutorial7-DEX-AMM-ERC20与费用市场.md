# 第六部分：Tutorial 7 —— DEX、AMM、ERC-20 与费用市场

## 27. DEX 和 Uniswap 的 AMM

DEX 不依赖中心化订单簿撮合，而是让：

1. LP 向智能合约存入一对资产；
2. 交易者直接和池子交换；
3. 合约按公式自动计算价格和输出数量；
4. LP 按份额退出并取回两种资产。

Uniswap v2 风格 AMM 使用恒定乘积：

~~~text
x · y = k,
~~~

其中 x,y 是池中两种 token 的数量，k 在忽略手续费和交易过程变化时保持不变。池子的边际价格大致由 y/x 决定；交易会改变比例，套利者会把池价和外部市场价拉回一致。

## 28. LP 的收益与损失

- **交易费**：每笔 swap 的一部分分给 LP，通常用 APR 表示；APR 是简单年化，不自动包含复利。
- **流动性挖矿**：协议额外发放治理/原生 token，若奖励再投资，常用 APY 表示，包含复利。
- **Impermanent Loss（IL）**：两种资产的相对价格变化时，AMM 自动再平衡，LP 的组合价值可能低于自己直接持有原始资产的价值。价格偏离越大，IL 通常越大。

“无常”只表示若价格回到初始比例，损失可能消失；如果此时退出，损失就实际实现了。

## 29. ERC-20

ERC-20 是 Ethereum 上的**同质化 token** 标准，单位之间可互换。核心函数包括：

~~~text
totalSupply()
balanceOf(account)
transfer(to, amount)
transferFrom(from, to, amount)
approve(spender, amount)
allowance(owner, spender)
~~~

题目只要求三个，但理解六个更完整：approve 设置授权额度，transferFrom 使用这个额度代表用户转账。

## 30. Uniswap 数值题

初始池子：

~~~text
6 ETH + 9600 DAI
k = 6 × 9600 = 57600.
~~~

价格升到 3600 DAI/ETH 后，稳定池满足：

~~~text
y = 3600x
x·y = 57600
3600x² = 57600
x = 4,
y = 14400.
~~~

因此 LP 取回 4 ETH + 14,400 DAI，按新价格估值：

~~~text
4×3600 + 14400 = 28800 DAI.
~~~

如果自己一直持有 6 ETH + 9600 DAI：

~~~text
6×3600 + 9600 = 31200 DAI.
~~~

相对直接持有的无常损失为：

~~~text
31200 - 28800 = 2400 USD.
~~~

这 2400 的经济受益者主要是**套利者**：他们在池价仍低于外部 ETH 价格时，用 DAI 从池中买走 ETH，直到池子达到新的价格比例。套利者获得差价，池子则留下更多 DAI、更少 ETH。

## 31. EIP-1559 priority fee

如果 tx1 的 priority fee 是 y，tx2 是 2y，并且二者都满足 max fee 约束，tx2 **更可能**被区块生产者优先打包，但不保证一定在 tx1 前执行。

原因包括：

- 更高 tip 只是经济激励，不是协议强制排序；
- tx1 可能更早抵达生产者的 mempool；
- 生产者要最大化总收益，可能优先考虑 MEV，而非单纯 tip；
- nonce、交易依赖、gas limit、私有 relay 和构块策略也会影响排序。

---

