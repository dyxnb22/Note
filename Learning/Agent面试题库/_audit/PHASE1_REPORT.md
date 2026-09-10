# Phase 1 — Question Inventory

本次范围仅为正式编号题的事实抽取，没有执行 Atomization、候选生成、重复裁决或正文修改。

基线 commit：`a5f564d8e51b7a47018d8cd9f6244db55044bf61`。
工作分支：`agent-kb-dedup-v1`。建分支前 `git pull --ff-only` 返回 Already up to date。

扫描 29 个现有 Markdown 文件，其中 25 个题目文件、2 个 review 文件、2 个 README 导航文件。
正式题实际为 **736** 道，比需求示例中的 728 道多 8 道；数量以当前仓库扫描为准，未为匹配示例而排除任何正式题。

| layer | 正式题数 |
| --- | ---: |
| core | 385 |
| supplement | 101 |
| deepening | 239 |
| integrated | 11 |
| 合计 | 736 |

## 资产与字段

- `question_inventory.json`：正式题数组。路径相对于题库根目录，ID 使用 `Q::<原始相对路径>::<原始编号>`。
- `baseline.json`：原始 commit、分支、题数、每个源文件的 SHA-256 及排除原因。
- `inventory_validation.json`：统计、排除清单和校验错误。
- `inventory.py`：仅使用 Python 标准库的提取和校验程序。

`section` 为题目前最近的一级或二级标题原文；`answer_start` 为题目标题后首个非空行原文，允许表格、列表等形式，不强制要求“答：”。行号均为 1-based，`answer_end_line` 包含该行，答案范围在下一个同级或更高级标题前结束。`answer_sha256` 对标题后至该边界的正文按 LF 连接后计算；文件哈希则针对原始字节。

按顶层 `00` / `12` / `13` 识别 review / deepening / integrated，其余文件名含“面经补充”标为 supplement，其他正式题标为 core。README 单列为 navigation 排除；review 不进入正式题清单。解析忽略围栏代码块，识别当前题库统一使用的 `### 数字. 标题`。异常三级标题、其他层级编号标题、空答案和不连续编号会使校验失败，避免静默漏题。

## 验证结果

- 正式编号题覆盖：736 / 736（100%）。
- 重复 Question ID：0。
- 编号异常、空答案和无法识别的题目标题：0。
- review 与导航文件均已明确排除。
- 独立原始行正则扫描与清单的文件、标题行号集合完全一致。
- 全部 29 个现有 Markdown 文件与基线 Git commit 的字节哈希一致。
- `inventory.py --check` 复跑通过。

在仓库根目录复核：

```bash
python3 'Learning/Agent面试题库/_audit/inventory.py' --check
```

不加 `--check` 可重新生成清单与校验报告；已有基线不可被静默覆盖，源文件发生变化时程序会报错。后续阶段需要单独处理基线迁移，本次没有创建空的 Atom Registry、Atom Map 或 Cluster 文件来冒充已完成分析。知识覆盖与重复关系尚未评估，不能据本阶段推断去重完成。
