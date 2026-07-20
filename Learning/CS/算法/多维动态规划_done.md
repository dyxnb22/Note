**LeetCode 62. 不同路径** 一个机器人每次只能向下或者向右移动一步。机器人试图达到网格的右下角。问总共有多少条不同的路径
`dp[i][j] = dp[i - 1][j] + dp[i][j - 1];`
**LeetCode 64. 最小路径和** 路径上的数字总和为最小
`grid[i][j] = Math.min(grid[i - 1][j], grid[i][j - 1]) + grid[i][j]`
**LeetCode 5. 最长回文子串** 给你一个字符串 `s`，找到 `s` 中最长的 回文 子串。
`dp[i][j]`表示 `s[i..j]`是否是回文串。先枚举子串长度。`if (j - i > 3) dp[i][j] = dp[i + 1][j - 1]`

**LeetCode 1143**. 最长公共子序列**  不要求连续`dp[i][j] = dp[i - 1][j - 1] + 1;dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);`

**LeetCode 72. 编辑距离**给你两个单词 `word1` 和 `word2`， *请返回将 **`word1`** 转换成 **`word2`** 所使用的最少操作数*  （插入、删除、替换）
`dp[i][j]` 表示将 `word1` 的前 `i` 个字符转换为 `word2` 的前 `j` 个字符，所需要的最少操作次数

`        if (word1.charAt(i - 1) == word2.charAt(j - 1)) {
            dp[i][j] = dp[i - 1][j - 1];
        } else {
            dp[i][j] = Math.min(Math.min(dp[i - 1][j - 1], dp[i][j - 1]), dp[i - 1][j]) + 1;
        }// 替换、插入、删除` 
