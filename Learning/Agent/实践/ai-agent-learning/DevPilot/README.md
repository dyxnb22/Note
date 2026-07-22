# DevPilot：代码分析与修改建议助手 MVP

DevPilot 是这套课程的最终综合练习。当前版本刻意做成 MVP：**先跑通 Agent 工程闭环，再逐步接入真实 LLM 和自动改代码能力**。

## 当前能力

```text
START
  -> Router       判断任务类型：bug_fix / feature / code_review
  -> Analyzer     扫描语言、搜索关键词、定位候选文件
  -> Fixer        生成建议级 diff
  -> Approval     人工审批
  -> Reviewer     审查建议的风险
  -> PR Creator   生成 PR 标题和描述草稿
  -> END
```

## 为什么不直接自动改代码

学习阶段最重要的是先掌握：

- State 如何设计；
- 每个 Agent 节点如何分工；
- 工具如何接入；
- 人工审批如何放进流程；
- 如何避免 Agent 直接误改文件。

所以当前 Fixer 只生成“建议级 diff”，不会直接写文件。后续可以把它升级为真实 patch 生成、应用、测试和回滚。

## 运行

```bash
# 在 DevPilot/ 目录下执行
cp .env.example .env       # 如果需要接入真实模型
python src/main.py
```

示例输入：

```text
修复 login 函数的空值问题
新增一个配置读取功能
审查当前项目的工具函数
```

## CLI 命令

```text
/lang java,python,go   手动指定分析语言
/lang auto             重新自动检测语言
/lang                  查看当前语言配置
/scan                  扫描仓库源码文件分布
/thread <id>           切换对话线程
/help                  查看帮助
/quit                  退出
```

## 后续升级路线

1. 把 Router 替换成真实 LLM 分类。
2. 把 Analyzer 改成 ReAct：LLM -> ToolNode -> LLM 循环。
3. 让 Fixer 生成真实 unified diff，并用 `git apply --check` 验证。
4. 审批通过后自动应用 patch。
5. 运行测试并把结果写回 State。
6. 接入 GitHub，创建真实 Pull Request。

## 面试话术

> DevPilot 是一个基于 LangGraph 的代码分析 Agent MVP。我把流程拆成 Router、Analyzer、Fixer、Approval、Reviewer 和 PR Creator 六个节点，每个节点只负责一个明确职责。当前版本不会直接修改代码，而是先搜索仓库、定位候选文件、生成建议级 diff，再通过 human-in-the-loop 审批后进入审查和 PR 草稿生成。这个设计重点展示了 Agent 的状态流转、工具使用、人工介入和工程可控性。
