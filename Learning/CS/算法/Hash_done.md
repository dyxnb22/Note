**LeetCode 1. 两数之和（找出目标和的两个数）**
补数，`complement = target - nums[i];` `return new int[]{map.get(target - nums[i]), i};`

**LeetCode 454. 四数相加 II**
统计满足 `(i, j, k, l)` 对应数字之和为 `0` 的四元组数量。两两分组 + HashMap 计数，在两个 map 里寻找 `num` 和 `0 - num`。

**LeetCode 49. 字母异位词分组（eat、tea、ate）**
分组问题常用 `Map<Key, List<Value>>`：遍历每个单词，将字符排序后作为 `key`，把原单词加入 `map[key]` 对应的列表。遍历结束后，取出 map 中所有列表作为结果。
`String key = new String(sortedS);` `return new ArrayList<List<String>>(m.values());`

**LeetCode 290. 单词规律**
`(abb, hello you you)`：判断模式字符串和单词序列是否对应。 存储两个字符串同位置的对应关系；还要检查反向映射，保证一一对应。`String[] words = s.split(" ");`
`Map<Character, String> p2w = new HashMap<>();Map<String, Character> w2p = new HashMap<>();`

**LeetCode 205. 同构字符串**
同上，不过映射的是字符到字符。`Map<Character, Character> map = new HashMap<>();` 还要检查反向映射，保证一一对应。

**LeetCode 202. 快乐数（不断求各位数字平方和，最终是否为 1）**
用 HashSet 记录出现过的中间和；若出现重复，就进入循环，不是快乐数。`n = sum(int(digit) ** 2 for digit in str(n))`

**LeetCode 36. 有效的数独（判断 9×9 数独是否合法）**
用 HashSet 分别记录行、列、宫格中出现过的数字，例如 `rows = [set() for _ in range(9)]`。宫格索引 `k = (i//3)*3 + j//3`。遍历每个格子，若当前数字已存在于对应的行、列或宫格集合中（如 `num in rows[i]`），则返回 `false`；否则标记为已访问。

**LeetCode 128. 最长连续序列**
数字连续的最长序列（不要求序列元素在原数组中连续且有序）。HashSet 快速判断某一个数的上一个数是否存在，从而找到连续序列的起点。

**轨迹日志修复：前缀和 + HashMap**
一组行动轨迹 `UDLR`，删除至多一段连续子串并拼接，使整段轨迹最终停在 `(x, y)`。求最短删除长度；无解返回 `-1`。`totalX - delX = targetX`。遍历过程存储前缀和，key 为 `String key = x + "," + y;`，value 为最新索引。
