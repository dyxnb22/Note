# Lecture 3B：Ethereum 安全、ERC20 与 DeFi 入口

来源：课程课件 `lecture3b-ethereum-security-handout.pdf`（原 PDF 未随笔记入库，当前只保留整理稿。）

## 3B.1 为什么智能合约格外危险

智能合约代码部署后不容易修改，且常常直接保管大量资产；代码公开、攻击者可以反复分析；交易不可逆；一个合约还可能被其他协议组合调用。因此普通软件中的“发现 bug 后上线 hotfix”在链上可能不可行。

## 3B.2 The DAO 与重入攻击

典型错误代码的逻辑是：

```solidity
function withdrawBalance() public {
    uint amount = userBalances[msg.sender];
    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok);
    userBalances[msg.sender] = 0;
}
```

问题在于外部 call 发生在状态更新前。若 `msg.sender` 是攻击合约，接收 ETH 时会执行 fallback；fallback 又调用 `withdrawBalance()`。EVM 虽然是单线程的，但外部调用会让 Bank 暂停，攻击合约在 Bank 尚未把余额改为 0 时嵌套进入下一次提款：这不是并行 race，而是**顺序嵌套调用**。

### 3B.2.1 CEI 模式

安全顺序是 **Checks-Effects-Interactions**：

1. Checks：验证余额、权限和参数；
2. Effects：先把余额等状态更新好；
3. Interactions：最后才调用外部合约或发送 ETH。

重入时再次看到的余额已经是 0，因此无法重复提款。如果最后的外部调用失败，应恢复状态或直接 revert。WETH 的 withdraw 逻辑就是这一模式的典型应用。

## 3B.3 ERC 与 ERC20

EIP 是协议层改进提案，ERC 更偏向应用层合约接口标准。ERC20 是可互换 token 标准；每个 token 都是独立的合约，有自己的 `balances` mapping，钱包只是把多个合约中的余额聚合展示。

核心函数：

- `totalSupply()`：总供应；
- `balanceOf(address)`：账户余额；
- `transfer(to, amount)`：调用者直接转 token；
- `approve(spender, amount)`：授权 spender 最多花多少；
- `allowance(owner, spender)`：查询授权额度；
- `transferFrom(from, to, amount)`：spender 在 allowance 内代 owner 转账。

`approve` 只设置权限，不立即移动 token。典型 DEX 流程：

```text
Alice -> approve(DEX, 100)
DEX   -> transferFrom(Alice, Bob, 60)
剩余 allowance = 40
```

这使 DEX、借贷协议和订阅合约可以代表用户使用 token，也带来 allowance 过大、恶意 spender 和授权管理风险。

实际发行 ERC20 时，讲义建议使用 OpenZeppelin 等经过广泛使用的库，而不是从零手写余额、授权和铸币逻辑。发行者还必须明确 `mint`、`burn`、暂停和管理员权限，否则“标准接口”并不代表 token 的经济规则可信。

## 3B.4 DAO、组合性和 Flash Loan

DAO 是由 token 持有者通过智能合约治理的组织：token 可以代表投票权，提案通过后按规则动用资金。它把“谁有权决定”从公司章程转成了合约状态和投票规则，但仍然有投票权集中、治理攻击、委托和升级权限风险。ERC20 的标准接口让任意合约都能与 token 交互，形成“money legos”：

```text
USDC -> Aave 借贷 -> aUSDC
     -> 作为抵押品 -> 借 DAI
     -> Uniswap 换成 ETH
```

Flash loan 允许在同一笔交易中无抵押借出大量资金，但必须在交易结束前归还，否则整个交易回滚。它可以用于套利、清算和抵押品交换，也可被用于短暂操纵 AMM 价格，再攻击依赖该价格的协议。关键是：原子性保证“借到但不还”的状态不会留下，但不保证被组合的逻辑正确。

## 3B.5 稳定币与 MakerDAO

加密资产价格波动大，稳定币试图把 token 价值锚定 1 美元。主要类型：

1. **法币储备型**：USDC、USDT，发行方持有现金或国债；稳定性较强，但发行方可以冻结 token、银行或托管机构可能出问题。
2. **加密抵押型**：DAI，用户锁定超过借款价值的 ETH 等资产，由智能合约管理；更去中心化，但面临抵押品暴跌和清算风险。
3. **算法型**：依靠铸造/销毁和激励维持锚定，没有充足外部储备；UST 的崩溃说明信心和流动性恶化时可能出现死亡螺旋。

DAI 可以理解成“加密当铺”：用户锁入约 130 美元或更高的 ETH，借出最多约 100 DAI；若抵押率跌破阈值，预言机提供价格，任何清算者都可以出售抵押品并收取罚金，从而使系统债务得到覆盖。用户偿还 DAI 和费用后取回抵押品。

稳定币体现了去中心化取舍：USDC 的效率和稳定性更高但有发行方；DAI 的审查阻力更强但需要超额抵押、预言机和清算机制。

## 3B.6 本讲总结

- CEI 让状态先于外部交互更新，防止最经典的重入攻击；
- ERC20 通过统一接口让 token 能够被钱包和协议互操作；
- `approve/allowance/transferFrom` 是“合约代用户花 token”的机制；
- ERC20、借贷、DEX、稳定币和 flash loan 通过组合性形成 DeFi；
- 每多一层组合，就多一层代码、预言机、清算和治理风险。

---
