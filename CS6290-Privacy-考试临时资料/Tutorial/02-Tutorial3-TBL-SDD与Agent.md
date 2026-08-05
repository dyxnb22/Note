# 第二部分：Tutorial 3 —— TBL、SDD 与可靠 AI agent

Tutorial 3 的主题虽然不是传统区块链算法，但它教的是**如何把复杂系统任务做得可靠、可审查、可验证**。

## 13. Team-Based Learning（TBL）

### 13.1 核心观点

可靠 agent 依靠约 80% 的人类引导、审查和验证，而不是继续堆更多 prompt。人类的角色不是被动写 prompt，而是**可靠性工程师**：设计任务边界、验收标准、工具、测试、可观测性、回滚和审查点。

TBL 的三个动作：

- **Guide**：给出目标、边界和成功定义；
- **Verify**：检查结果是否真的满足规则；
- **Critique**：主动寻找反例、遗漏和偏差。

### 13.2 四阶段协议

可以把一次可靠任务固定为：

1. **Spec**：写清楚目标、非目标、约束和验收标准；
2. **Plan**：拆成可执行、可独立验证的步骤；
3. **Execute**：逐步实施并记录证据；
4. **Review**：由人或另一个 agent 审查，并检查测试、diff、日志和最终产物。

反偏差规则：如果大家一开始就完全同意，必须暂停并主动问“最可能错在哪里？”因为过快的一致可能只是共享同一个假设或确认偏误。

### 13.3 为什么 peer critique 胜过 solo prompting

单个 agent 容易出现：

- 确认偏误：只寻找支持原方案的证据；
- 盲点：没有独立角色发现遗漏；
- 漂移：任务越做越偏离最初目标；
- “看起来正确”：输出语法正确，但没有满足真实需求。

同伴审查要求对方证明结论、指出边界条件，并把“我认为正确”换成“这是可复核证据”。

---

## 14. Spec-Driven Development（SDD）

### 14.1 为什么 AI 时代更需要规格

LLM 擅长生成看起来合理的代码，但较弱于：

- 发现没有写出来的需求；
- 维持多步骤目标的一致性；
- 识别真正的边界条件；
- 自己证明实现符合需求。

因此 SDD 是：

~~~text
需求 + 约束 + 验证
~~~

它在错误还便宜的时候加入检查点。

### 14.2 “vibe coding” 为什么会失败

典型链条是：

~~~text
模糊 prompt → agent 猜测 → 代码看起来合理 → 静默偏离真实需求
~~~

症状包括巨大的 diff、反复试错、把所有资料塞进上下文、没有明确验收条件、没有独立审查。SDD 用“契约 + 检查”替代猜测。

### 14.3 一页规格就是一个契约

最小规格只要回答三个问题：

1. **Goal**：要解决什么问题？
2. **Constraints**：必须遵守什么边界？包括安全、性能、兼容性、数据格式。
3. **Acceptance**：怎样通过可观察结果判断完成？

推荐的一页模板：

~~~text
Feature:
Goal:
Non-goals:
User flows:
Acceptance criteria:
Constraints:
Verification plan:
~~~

验收条件要可测试。不要写“很快”“安全”“用户体验好”；要写成：

- 在 1000 req/min 下 p95 延迟小于 200 ms；
- 错误登录不能暴露账户是否存在；
- 每个用户每小时最多 5 次密码重置；
- 重试使用指数退避，最多 3 次。

### 14.4 SDD 什么时候用、什么时候跳过

适合使用 SDD：

- 至少 3 个步骤；
- 存在边界条件；
- 多人协作；
- 涉及安全、数据、金钱或声誉；
- 错误修复成本高。

可以跳过完整 SDD：

- 单文件的小修改；
- 一次性的抛弃式脚本；
- 没有人会审查、文档本身比任务更重的情况。

原则是“最小而活的工件”：规格少于 1–2 页，任务清单大约 10–30 个 checkbox，文档更新属于完成任务的一部分。

---

## 15. GitHub Spec Kit 工作流

Spec Kit 把 SDD 固化为仓库内的可审查工件：

~~~text
specify → plan → tasks → implement
~~~

常见命令序列：

~~~text
/speckit.constitution
/speckit.specify
/speckit.plan
/speckit.tasks
/speckit.implement
~~~

### 15.1 Constitution

Constitution 是项目规则，应该只有 5–10 条、可执行、可检查，例如：必须有测试、错误必须记录、禁止把大 JSON 塞进聊天、要支持回滚、敏感数据不能写日志。

### 15.2 Specify

Specify 写“做什么”和“为什么”，不急着决定具体技术架构。它应该包含用户行为、非目标和 Given/When/Then 验收条件，避免写成长篇设计论文。

### 15.3 Plan

Plan 只记录关键架构选择、数据契约、风险和验证策略；它是供审查的工程计划，不是小说。

### 15.4 Tasks

一个好任务应该小、可执行、可独立验证并产出证据，例如“新增接口并补充失败场景测试”。坏任务是“实现整个支付系统”。如果任务无法在一个清晰的 diff 和一组测试里检查，就应该继续拆分。

### 15.5 Implement

实施阶段每一步都应该留下：

- 代码 diff；
- 测试命令和结果；
- 生成的文件或截图；
- 当前进度；
- 失败原因与下一步。

没有证据，就没有可信度。

### 15.6 常见陷阱

- 文档太多：用 artifact budget 限制数量；
- 文档过时：文档更新纳入 done；
- 计划无人审查：把计划审查设为实现前的 gate；
- 计划和另一份计划互相漂移：只保留一个 canonical plan。

---

## 16. Context Engineering：上下文也需要内存管理

把上下文窗口看成有限而易失的 RAM，把磁盘文件看成容量大、可持久化的磁盘：

- RAM/上下文：快，但小，压缩或换轮次后可能丢失；
- 磁盘：慢一点，但能保存任务状态、研究结果、错误和决定。

不要把所有文档都粘贴进上下文。采用 progressive disclosure：

1. 先读很小的近期摘要；
2. 找到与当前步骤有关的文件；
3. 只加载相关段落；
4. 行动后验证并把结果写回磁盘。

### 16.1 Planning-with-Files 三文件状态机

多步骤任务可以只保留三个工作文件：

- task_plan.md：路线、任务清单和当前步骤；
- findings.md：研究结果、决定和重要假设；
- progress.md：已做事项、命令证据、失败和下一步。

四条防漂移规则：

1. 先建计划再执行；
2. 两次查找之后就把发现写入 findings.md；
3. 所有错误写入 progress.md；
4. 同一策略连续失败两次后必须换策略，而不是重复尝试。

progress.md 不应只写“完成了”，而应写：做了什么、运行了什么命令、得到什么输出、为什么失败、接下来改变什么。

---

## 17. Agent 架构、Actor–Critic 和断言

### 17.1 God Model fallacy

一个巨大模型不自动解决任务分解、独立验证、长程状态和可靠集成问题。更实用的架构是：

- **Supervisor**：规划、分派、整合；
- **Minions/tools**：执行范围窄、输出精确的子任务；
- **Critic**：独立审查和找反例。

### 17.2 Actor–Critic loop

可靠 agent 是循环而不是一次性生成：

~~~text
Actor 提议/执行 → Critic 检查 → 更新计划和日志 → 必要时用新策略重试
~~~

没有 critic，就没有工程纪律；只有提示词而没有可执行验证，输出仍然只是猜测。

### 17.3 Guardrails 与 Assertions

- **Guardrails**：限制格式、风格、策略和权限；
- **Assertions**：在运行时检查真实状态，例如测试、schema、性能阈值、错误码和不变量。

Guardrail 只能约束“应该怎么输出”，assertion 才能验证“现实中是否真的正确”。自主程度越高，越需要 runtime assertions、日志、监控和 rollback，而不是只写一个更好的 prompt。

### 17.4 Superpowers 和统一工作流

Tutorial 中的 Superpowers 代表一种 skills-driven workflow：把 brainstorming、写计划、执行计划、TDD、系统调试和 code review 变成默认习惯，而不是临时提醒。典型过程是：

~~~text
brainstorm → 压缩成 spec → plan → tasks → TDD implement → review/evidence
~~~

它和 Spec Kit 可以结合：Superpowers 负责互动式思考和计划，Spec Kit 负责将结果固定为仓库内工件；两者必须共享一个 canonical plan。课堂实验可按“范围/验收 → 小任务 → 测试/断言 → 调试 → 完成审查/证据”执行。

### 17.5 Tutorial 3 的总原则

~~~text
SDD = 契约 + 可验证标准
Context engineering = 磁盘持久状态 + 渐进加载
TBL = 同伴批评 + 反偏差 + 验证文化
可靠 agent = Plan → Act → Critique → Evidence
~~~

---

