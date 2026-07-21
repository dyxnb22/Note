# 代码 Agent 基础设施

这篇笔记回答一个具体问题：**为什么 Coding Agent 不只是“给模型几个文件工具”**。

一个能修改真实代码库的 Agent，至少需要理解代码、选择上下文、产生可审查的变更、运行验证，并能从失败反馈中继续执行。

```text
Repository
  → 发现文件和符号
  → 选择上下文
  → 读取相关实现
  → 生成 patch
  → 应用变更
  → 运行测试 / lint / typecheck
  → 读取失败反馈
  → 修复或请求人工介入
```

## 1. 代码 Agent 的最小工具集

不要一开始暴露几十个工具。一个可学习、可评测的最小集合是：

| 工具 | 作用 | 关键约束 |
|---|---|---|
| `list_dir` / `glob` | 发现文件 | 限制 workspace 范围 |
| `search` | 按文本搜索 | 限制结果数量和单条长度 |
| `read_file` | 读取实现 | 支持行号范围和大小上限 |
| `edit_file` / `apply_patch` | 修改代码 | 变更必须可审查、可回滚 |
| `run_tests` | 验证行为 | 命令白名单、超时、输出截断 |
| `git_diff` | 观察变更 | 不把未授权文件混入提交 |

`bash` 很强，但边界不清。学习阶段可以保留它；生产系统应优先提供更窄、更容易审计的原子工具。

## 2. Repository Navigation

代码 Agent 的第一步通常不是“生成代码”，而是定位正确的实现位置。

推荐由宽到窄：

```text
目录结构
  → 文件名 / glob
  → 文本搜索（ripgrep）
  → 符号搜索（函数、类、接口）
  → AST / Tree-sitter
  → LSP（定义、引用、类型、诊断）
```

### 文本搜索和符号搜索的区别

文本搜索适合快速发现字符串、配置和错误信息；符号搜索适合追踪调用关系、定义和引用。不要用 embedding 检索替代所有代码导航：代码中的精确名称、路径和类型关系通常更重要。

### 代码库地图

可以为大型仓库维护轻量级地图：

```json
{
  "root": "src/",
  "modules": [
    {"path": "src/auth", "purpose": "身份与权限", "entrypoints": ["router.py"]}
  ],
  "commands": {
    "test": "pytest",
    "lint": "ruff check .",
    "typecheck": "mypy src"
  }
}
```

地图不是事实来源。它需要通过实际文件、测试和命令验证，过期时应允许 Agent 重新扫描。

## 3. Context 选择

代码 Agent 的 context 不是“尽可能多读文件”，而是“让当前决策拥有足够证据”。

```text
当前任务
  + 目标文件
  + 直接调用者 / 被调用者
  + 类型和接口定义
  + 相关测试
  + 构建和运行命令
  + 最近的错误反馈
```

建议保留每段代码的来源：文件路径、起止行号、提交版本或读取时间。最终回答和 patch 都应该能够回指这些证据。

## 4. Edit、Patch 与 Write

### 直接覆盖文件

适合新建文件或完全重写的小文件；风险是容易覆盖并发修改，且 diff 不够清晰。

### 精确替换

要求旧片段唯一匹配：

```python
def replace_unique(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"expected one match, got {count}")
    return text.replace(old, new)
```

### Unified Diff / Patch

适合审查、回滚和多人协作。应用前必须检查：

- 文件路径在 workspace 内；
- patch 上下文仍然匹配；
- 目标文件没有未经授权的并发变更；
- 应用后 `git diff` 只包含预期文件。

模型提出 patch 不等于 patch 已经被批准。应用 patch 仍然是一个需要策略检查的动作。

## 5. 验证闭环

写操作完成后，至少按以下顺序验证：

```text
语法 / import
  → 定向单元测试
  → lint / format
  → typecheck
  → 相关集成测试
  → 必要时运行完整测试
```

不要让 Agent 只看最后一行错误。工具结果应包含：命令、退出码、stdout/stderr 摘要、耗时、被截断信息和工作目录。

```python
def validation_result(command: str, completed) -> dict:
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
        "truncated": len(completed.stdout) > 4000 or len(completed.stderr) > 4000,
    }
```

## 6. Git 与 Worktree

Git 对 Coding Agent 不只是版本控制，也是观察状态和恢复错误的工具。

```text
任务开始 → 记录 base commit
变更前   → 检查 dirty files 和用户修改
变更后   → git diff / git status
验证失败 → 保留失败现场，必要时回滚 patch
并行任务 → 每个任务使用独立 worktree
```

Agent 不能擅自覆盖用户已有修改。至少要区分：

- 任务开始前已有的 diff；
- 当前任务产生的 diff；
- 其他 Agent 或外部进程产生的 diff。

## 7. 代码 Agent 常见失败

| 失败 | 根因 | 改进 |
|---|---|---|
| 找错文件 | 只依赖语义搜索 | 结合路径、符号、调用者和测试 |
| 读了太多代码 | 没有 context 预算 | 先定位，再按依赖扩展 |
| patch 应用错位置 | 匹配不唯一或文件已变化 | 唯一匹配、版本检查、失败即停 |
| 改完但没验证 | 把“生成完成”当作“任务完成” | 写后验证和证据回传 |
| 修复循环失控 | 每次都重复同一动作 | 记录失败 fingerprint，检测 stuck loop |
| 破坏用户修改 | 没有基线 diff | 任务开始前快照，变更分层记录 |

## 8. 练习与验收

在一个小型 Python 仓库上实现：

1. `search → read_file → apply_patch → run_tests → git_diff` 五工具循环；
2. patch 只允许修改 workspace 内文件；
3. 运行命令有超时和输出上限；
4. Agent 能读取测试失败并尝试一次定向修复；
5. 任务开始前已有的 diff 不被覆盖；
6. 用 10 个固定 bug case 记录成功率、修改文件数、测试轮数和成本。

推荐参考：

- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/)
- [Language Server Protocol](https://microsoft.github.io/language-server-protocol/)
- [Git 文档](https://git-scm.com/docs)
