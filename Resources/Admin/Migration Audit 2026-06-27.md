# Migration Audit 2026-06-27

这份清单记录本地知识库本轮清理结果，以及当前仍存在的迁移缺口。

注：后续目录已经进一步精简，`Knowledge` 入口和多层 Index 已被合并到 `Learning` 目录。

## 已清理

- 修正了 [Home](/Users/diaoyuxuan/Documents/Notes/Home.md) 的失效入口链接
- 修正了旧 `Knowledge` 入口里的失效“双链”引用
- 把 `CityU`、`Life`、`Java基础`、`SafeCodeAgent` 从原始 Notion 嵌入壳页改成了可读的本地说明页
- 识别出一批重复或过时的根页占位：`Tech`、`AI Agent`、`CS基础`、`Java后端`、`工具链`、`Projects`、重复的 `算法`

## 根页复核

- `Tech`：Notion 根页 5 个一级子页，本地已分别有正式入口或索引
- `Projects`：Notion 根页 3 个项目页，本地都已存在
- `工具链`：Notion 根页 3 个子页，本地都已存在
- `AI Agent`：后续已并入 `Learning/AI`
- `Life`：Notion 源页为空，本地仅保留入口即可
- `CityU`：Notion 源页仍主要由学期页和课程数据库组成，本地未拆数据库

## 明确漏页

### Algorithms

Notion `算法` 根页里，本地还缺以下独立页面：

- 滑动窗口
- 子串
- 矩阵
- 字符串
- 图论
- 二分查找
- 堆
- 贪心
- 多维动态规划
- 技巧

### Java 基础

Notion `Java基础` 下，本地还缺以下独立页面：

- Java
- Java集合

## 低风险空页

这些页本地内容很少，但与 Notion 源页一致，不属于迁移失败：

- `Life`
- `SafeCodeAgent`

## 下一步建议

优先补齐两批：

1. `Algorithms` 缺失的 10 张题型页
2. `Java基础` 下的 `Java` 与 `Java集合`
