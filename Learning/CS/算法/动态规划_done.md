# 动态规划

**LeetCode 70. 爬楼梯。**
爬 `1` 或 `2` 个台阶，有多少种不同的方法可以爬到楼顶。构造一个dp 数组， `dp[i] = dp[i - 1] + dp[i - 2]`

**LeetCode 118. 杨辉三角**
每个数是它左上方和右上方的数的和。
`row.add(c.get(i - 1).get(j - 1) + c.get(i - 1).get(j));`

**LeetCode 198. 打家劫舍**
两间相邻的房屋在同一晚上被小偷闯入，系统会自动报警。
`dp[i] = Math.max(dp[i - 1], dp[i - 2] + nums[i-1])`

**LeetCode 213. 打家劫舍 II。围成一圈。**
第 0 间和最后一间不能同时偷。

1. 不偷最后一间 `dp1`
2. 不偷第一间 `dp2`
然后比较。

**LeetCode 337. 打家劫舍 III。**
二叉树结构的布局

- `res[0]`（偷当前节点）：如果决定偷当前节点，那么它的左右孩子节点都不能偷。
- `res[1]`（不偷当前节点）：如果决定不偷当前节点，那么它的左右孩子节点偷或不偷都可以，取其中的最大值。
`res[0] = root.val + left[1] + right[1];`
`res[1] = Math.max(left[0], left[1])+ Math.max(right[0], right[1]);`

**LeetCode 279. 完全平方数**
和为 `n` 的完全平方数的最少数量。完全背包问题。
从前往后遍历：`dp[j] = Math.min(dp[j], dp[j - i*i] + 1);`

**LeetCode 322. 零钱兑换。完全背包**
`coins` 表示不同面额的硬币，凑成总金额最少的硬币个数。
从前往后遍历：`dp[j] = Math.min(dp[j], dp[j - coin] + 1)`

**LeetCode 518. 零钱兑换 II（组合方案数量）**
双重循环：`dp[i] += dp[i - coin];`

**LeetCode 139. 单词拆分。**
字符串 `s` 和字符串列表 `wordDict` 作为字典（可重复使用），能否拼接。
双重循环。`set.contains(s.substring(j, i)) && isValid[j]`

**LeetCode 300. 最长递增子序列**
最长严格递增子序列的长度，不要求原先位置连续。
双重循环：
`if(nums[i] > nums[j]) { dp[i] = Math.max(dp[i], dp[j] + 1);} `

**LeetCode 674. 最长连续递增序列**
单重循环，只需要检查前一个数。
`dp[i] = dp[i-1] + 1;`

**LeetCode 152. 乘积最大子数组**
连续，有负数。
用两个数组跟踪，要么弃置前面结果，要么都乘一遍。
`maxF[i] = Math.max(maxF[i - 1] * nums[i], Math.max(nums[i], minF[i - 1] * nums[i]))`
`minF[i] = Math.min(minF[i - 1] * nums[i], Math.min(nums[i], maxF[i - 1] * nums[i]));`

**LeetCode 416. 分割等和子集**
一个数组是否能分割成等和子集，0-1 背包问题，从后往前。
`dp[j] = Math.max(dp[j], dp[j - nums[i]] + nums[i])`

**LeetCode 32. 最长有效括号**(一个只包含 '(' 和 ')' 的字符串，找出最长有效（格式正确且连续）括号子串的长度)
`dp[i]` 表示“必须以 `i` 位置结尾”的最长有效括号长度。')' 位一直为0，只有遇到')'才需要处理。pre = i - dp[i - 1] - 1 从这个位置开始寻找有效的'('   [当前 `')'` 前面，跳过一整段已经有效的括号之后，可能和当前 `')'` 匹配的 `'('` 的位置]
`dp[i] = dp[i - 1] + 2 + (pre > 0 ? dp[pre - 1] : 0);` 中间已有的有效长度 + 新配上的一对括号 + 左边能接上的有效长度

**LeetCode 343. 整数拆分** 正整数 n ，将其拆分为 k 个 正整数 的和（ k >= 2 ），使这些整数的乘积最大化
`dp[i]` 表示 数字 `i` 至少拆成两个正整数后，乘积的最大值
`dp[i] = Math.max(dp[i], Math.max(dp[i - j] * j, j*(i-j)));` 相当于固定好j，不必对j进行拆分，因为1*dp[i-1]肯定覆盖了

**LeetCode 1049. 最后一块石头的重量 II** 把所有石头分成两堆，让两堆重量尽可能接近，最后剩下的重量就是两堆差值。
`int[] dp = new int[target + 1];` 容量不超过 `j` 的背包，最多可以装多少重量的石头
从后往前遍历 `dp[j] = Math.max(dp[j], dp[j - stones[i]] + stones[i]);`

**LeetCode 494. 目标和** 添加 '+' 或 '-' ，然后串联起所有整数，求运算结果等于 target 的不同 表达式 的数目

1.   P - N = target （最终结果等于目标值） P 正数 N 负数
2.   P + N = sum （所有数字之和）

`addSum = (sum + target) / 2`，然后问题转成 01 背包：凑满 `addSum` 有多少种方法，`dp[j] += dp[j - nums[i]]`，并且必须倒序遍历

**LeetCode 474. 一和零** 每个字符串就是一个物品，消耗 zeroNum 个 0 和 oneNum 个 1，价值是 1。
背包有两个容量：最多 m 个 0，最多 n 个 1。问最多能装多少个字符
`int[][] dp = new int[m + 1][n + 1];`  最多使用 i 个 0 和 j 个 1，最多可以选多少个字符串
`dp[i][j] = Math.max(dp[i][j], dp[i - zeroNum][j - oneNum] + 1);` 字符串里0和1的数量

**LeetCode 123. 买卖股票的最佳时机 III **最多完成两笔交易
- **`dp[i][0]`**：未进行过任何操作（初始状态，代码中由于默认为 0 且后续不更新，常被忽略）。
- **`dp[i][1]`**：**第一次持有**股票的状态（可能是今天买的，也可能是之前买的没卖）。
- **`dp[i][2]`**：**第一次卖出**股票后的状态（保持卖出状态，或者今天刚卖出）。
- **`dp[i][3]`**：**第二次持有**股票的状态。
- **`dp[i][4]`**：**第二次卖出**股票后的状态。

```java
    dp[i][1] = Math.max(dp[i - 1][1], -prices[i]);
    dp[i][2] = Math.max(dp[i - 1][2], dp[i - 1][1] + prices[i]);
    dp[i][3] = Math.max(dp[i - 1][3], dp[i - 1][2] - prices[i]);
    dp[i][4] = Math.max(dp[i - 1][4], dp[i - 1][3] + prices[i]);
```

**LeetCode 188. 买卖股票的最佳时机 IV** 最多可以完成 k 笔交易
`int[] dp = new int[2*k + 1];`

```java
        if (j % 2 == 1) {
            dp[j] = Math.max(dp[j], dp[j - 1] - prices[i]);
        } else {
            dp[j] = Math.max(dp[j], dp[j - 1] + prices[i]);
        }
```

**LeetCode 309. 买卖股票的最佳时机含冷冻期** 卖出股票后，你无法在第二天买入股票 (即冷冻期为 1 天)。

dp[0]：持有股票
dp[1]：不持有股票，且不是今天刚卖出，也不是冷冻期，可以理解为“空闲状态”
dp[2]：今天刚卖出股票
dp[3]：冷冻期

```java
    int tmp1 = dp[0];
    int tmp2 = dp[2];
    dp[0] = Math.max(dp[0], Math.max(dp[1] - prices[i], dp[3] - prices[i]));
    dp[1] = Math.max(dp[1], dp[3]);
    dp[2] = tmp1 + prices[i];
    dp[3] = tmp2;
```

**LeetCode 714. 买卖股票的最佳时机含手续费**

```java
    int tmp1 = dp[0];
    dp[0] = Math.max(dp[0], dp[1] - prices[i]);
    dp[1] = Math.max(dp[1], tmp1 + prices[i] - fee);
```

**LeetCode 718. 最长重复子数组** 两个整数数组，返回最长公共连续子数组长度
`dp[i][j] = dp[i - 1][j - 1] + 1; ` 以 nums1[i - 1] 结尾、以 nums2[j - 1] 结尾的最长公共连续子数组长度
相等就从左上角加一，不相等就断掉为 0

**LeetCode 1143. 最长公共子序列** 不要求连续

        if (ch1[i - 1] == ch2[j - 1]) {
            dp[i][j] = dp[i - 1][j - 1] + 1;
        } else {
            dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
        }

**LeetCode 1035. 不相交的线** 连接端点 nums1[i] == nums2[j] 本质：最长公共子序列 LCS 同LeetCode 1143

**LeetCode 392. 判断子序列**。判断 s 是否为 t 的子序列（相对位置不变，不要求连续）

```java
        if (s.charAt(i - 1) == t.charAt(j - 1)) {
            dp[i][j] = dp[i - 1][j - 1] + 1; // s - i  t - j
        } else {
            dp[i][j] = dp[i][j - 1]; // 当前 t 的字符不要了，继续看 t 前 j - 1 个字符能匹配多少
        }
```

这里不需要考虑 `dp[i-1][j]`，因为我们的目标是看 s 是否为 t 的子序列，顺序和存在性只取决于 t 的消耗

**LeetCode 115. 不同的子序列** 给你两个字符串 s 和 t ，统计并返回在 s 的 **子序列** 中 t 出现的个数
 `dp[i][j]`： 在 s 的前 j 个字符中，t 的前 i 个字符出现的次数。
`dp[0][j] = 1;` 初始化: t 为空字符串时，在 s 的任意前 j 个字符中，都有 1 种出现方式

```java
for (int i = 1; i <= tLen; i++) {
    for (int j = 1; j <= sLen; j++) {
        if (t.charAt(i - 1) == s.charAt(j - 1)) {
            // 匹配时：使用 s[j-1] 的方案数 + 不使用 s[j-1] 的方案数
            dp[i][j] = dp[i - 1][j - 1] + dp[i][j - 1];
        } else {
            // 不匹配时：只能承接之前的方案数
            dp[i][j] = dp[i][j - 1];
        }
    }
}
```



**LeetCode 42. 接雨水** 给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子，下雨之后能接多少雨水。  **前缀最大值 + 后缀最大值** 每个位置能接多少水，取决于它左边最高柱子和右边最高柱子中较矮的那个。`max_left[i] = Math.max(max_left[i - 1], height[i - 1]);max_right[i] = Math.max(max_right[i + 1], height[i + 1]);` 然后取它们的最小值作为当前位置高度
