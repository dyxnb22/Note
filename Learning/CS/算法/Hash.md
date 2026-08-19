# Hash_done

**LeetCode 1. 两数之和（找出目标和的两个数）**
补数，`complement = target - nums[i];`
`return new int[]{map.get(target - nums[i]), i};`

**LeetCode 49. 字母异位词分组（eat、tea、ate）分组问题常用 Map<Key, List<Value>>**
`String key = new String(sortedS);`
`return new ArrayList<List<String>>(m.values());`

**LeetCode 128. 最长连续序列**
数字连续的最长序列（不要求序列元素在原数组中连续且有序）。
HashSet 快速判断某一个数的上一个数是否存在，为了找到连续序列的起点。

**LeetCode 454. 四数相加 II**
`(i, j, k, l)` 几个满足和为 0。
两两分组 + HashMap 计数。在两个 map 里寻找 `num` 和 `0-num`。

**LeetCode 290. 单词规律**
`(abb hello you you)` 两个字符串规律是否相同。
`Map<Character, String> map = new HashMap<>();`
用这个来存储两个字符串同位置的对照关系。
`String[] words = s.split(" ");`

**LeetCode 205. 同构字符串**
同上，不过是单个单词。
`Map<Character, Character> map = new HashMap<>();`

**轨迹日志修复 前缀和（前缀和 + HashMap）**
一组行动轨迹 UDLR，删除至多一段连续子串，拼接后的整段轨迹最终停在 `(x,y)`。
最短删除长度，没有就 `-1`。
`totalX - delX = targetX`。
遍历过程存储前缀和，key 为 `String key = x + "," + y;`，value 为最新索引。
