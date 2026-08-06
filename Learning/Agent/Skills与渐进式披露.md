# Skills 与渐进式披露

本文回答：**Skill 是什么、和 Tool / MCP 有何不同、为什么要用渐进式披露**。懒加载实现细节见 [Context 工程](04_Context工程.md)；工具合同见 [Tool Calling](02_Tool%20Calling.md)；协议层见 [MCP 与工具协议](MCP与工具协议.md)。

## 1. 三个容易混的概念

| | Tool | Skill | MCP Server |
|---|---|---|---|
| 是什么 | 一次可调用的函数能力 | 可复用的「能力包」：说明 + 流程 + 可选工具/资源 | 按协议暴露 tools/resources/prompts 的进程或服务 |
| 粒度 | 单次动作 | 领域任务（代码审查、PDF 处理、建 MCP…） | 一组远程/本地能力的承载 |
| 主要解决 | 模型如何调用副作用 | 如何按需注入领域知识与工具，控制 context | 跨宿主复用与标准发现/调用 |
| 典型形态 | `search_files(query)` | `SKILL.md` + 脚本/工具目录 | `tools/list` + `tools/call` |

一句话：Tool 是动词；Skill 是带说明书的工具箱；MCP 是把工具箱接到不同 AI 宿主的插座。

## 2. 渐进式披露（Progressive Disclosure）

Context 有限，不能把全部技能全文塞进每轮请求。分层披露：

```text
Level 0：系统里只有「技能目录」——名称 + 一句话何时使用
Level 1：用户意图命中后，加载 Skill 摘要 / 使用步骤
Level 2：真正执行时，再加载完整 schema、示例、脚本
```

工程收益：

- 大幅减少工具定义 token（目录常驻，正文按需）；
- 降低工具选择噪声（模型先选技能域，再选具体工具）；
- 与「百级工具路由」同一思想：先缩小候选集。

Coding Agent 场景里，`SKILL.md` 常作为 Level 1/2 的载体；触发可以是：用户话术、路由分类器、或显式 `load_skill` 工具。

## 3. Skill 应包含什么

最小集合：

- **何时用 / 何时不用**（避免误触发）；
- **步骤或检查清单**（可执行的过程知识）；
- **依赖的 Tools 与权限级别**；
- **输入输出约定与失败怎么处理**；
- **示例**（few-shot，比长文规则更稳）。

不要把整本内部 Wiki 塞进 Skill；大知识仍走 RAG，Skill 只保留「怎么做这件事」。

## 4. 与 MCP 的协作

```text
Skill「订单排查」
  → 指导模型先查状态再改单
  → 实际调用经 MCP：order_query / order_refund
```

Skill 可以**不绑定** MCP（纯本地函数），也可以把 MCP 工具作为实现后端。换模型时：MCP Server 与 Skill 文档可复用；变的是 Client 侧的工具格式适配。

## 4.1 Skill 加载边界（注释版）

Skill 目录常驻、正文按需加载；加载器需要校验来源、版本和授权，不能让 Skill 文档绕过工具策略。

```python
def load_skill(name, *, catalog, reader, actor, budget):
    entry = catalog.get(name)
    if not entry or not entry.allowed_for(actor):
        raise PermissionError("skill is not available")
    if entry.token_estimate > budget:
        raise ValueError("skill exceeds context budget")

    # 正文作为能力说明注入，不等同于系统指令；工具层仍需重新授权。
    content = reader.read(entry.path, expected_version=entry.version)
    return {"name": name, "version": entry.version, "content": content}
```

Skill 更新后要重跑关联任务 Eval；目录摘要、完整正文和工具 schema 的版本必须能在 Trace 中对应起来。

## 5. 面试口述要点

- Skill = 可复用能力单元 + 渐进式披露，不是又一个 Function Calling 别名。
- 渐进式披露解决的是 **context 预算与选择难度**，不是模型变聪明。
- 与低代码「插件市场」类比可以，但生产仍要权限、版本与评测。
