# 普通数组

**LeetCode 53. 最大子数组和。**
找出一个具有最大和的连续子数组。当目前记录的和小于 0，直接弃之，变为当前的 `nums[i]`。

**LeetCode 56. 合并区间。**
返回一个不重叠的区间数组。用 `curStart, curEnd` 跟踪。有重叠，更新终点；没重叠，存入，开启新区间。循环结束后一定会剩下一组待处理的，直接存进去。
`Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));`
`res.add(new int[]{curStart, curEnd});`
`res.toArray(new int[res.size()][])`

**LeetCode 189. 轮转数组。**
将数组中的元素向右轮转 `k` 个位置（`k % n`）。
1. 整体翻转
2. 翻转前 `k` 个
3. 翻转后 `n-k` 个

**LeetCode 238. 除了自身以外数组的乘积。**
“除自身以外的乘积”拆分为两个部分：左侧所有数的乘积（Prefix Product）和右侧所有数的乘积（Suffix Product）。
先算 `suf`，从后往前，数组记录。`pre` 为 `nums[0]` 到 `nums[i-1]` 的乘积，int 跟踪，直接乘到 `suf[i]` 中。

**LeetCode 41. 缺失的第一个正数**
既然我们要找的是 `[1, n]` 之间的正整数，那我们就把数组当成一个哈希表，尝试让数字 `i` 坐在下标 `i - 1` 的位置上。
从头开始遍历，`nums[i]` 在 `[1,n]` 之间，`nums[i] != nums[nums[i] - 1]`。然后找第一个学号与座位编号不匹配的学生 `nums[i] != i + 1`。

**LeetCode 383. 赎金信。**
`ransomNote` 能不能由 `magazine` 里面的字符构成（每个字符只使用一次）。
`cnt[c - 'a']` 记录字符出现数。

**LeetCode 724. 寻找数组的中心下标**
其左侧所有元素相加的和等于右侧所有元素相加的和。
前缀和，`sumNum[i] == sumNum[nums.length] - sumNum[i + 1]`。

**LeetCode 88. 合并两个有序数组。**
用两个指针记录两个数组，第三个数组来存放数值。

**LeetCode 26. 删除有序数组中的重复项**
只保留“和后一个元素不一样”的元素，最后一个元素默认添加。

**LeetCode 80. 删除有序数组中的重复项 II**
重复的不超过 2。用一个 `count` 来记录重复数量，不重复就清零，重复就累加。

**LeetCode 228. 汇总区间**
连续区间汇总起来，记录首尾。
`while (i + 1 < nums.length && nums[i + 1] == nums[i] + 1) { i++; }`
