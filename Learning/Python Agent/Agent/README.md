# AI Agent 工程知识库

> **新来？先读 [`学习路线图.md`](学习路线图.md)** — 包含五个学习阶段、两个项目的对照关系、每日节奏和实战项目建议。

---

# AI 应用工程

这个子目录是 AI 应用工程的核心知识库，覆盖从 LLM 调用到生产部署的完整链路。

## 推荐阅读顺序

```
1. LLM调用基础             ← 起点，一切的基础（含多模态/Vision/PDF）
2. Agent架构与设计         ← 理解 Agent 是什么
3. Tool Calling            ← Agent 的执行层
4. Context工程             ← 工程质量的关键
5. RAG与知识系统           ← 最常见的 AI 应用场景
6. Memory与状态管理        ← 生产系统的核心难题
7. Workflow与LangGraph     ← 复杂流程的编排
8. MCP与工具协议           ← 工具集成的标准化
9. 推理模型与ExtendedThinking ← 2025+ 重要新范式
10. Computer Use与GUI Agent   ← Anthropic 差异化能力
11. Eval与测试体系         ← 让优化可验证
12. 可观测性与调试         ← 生产环境看不见问题等于没有
13. 安全与可控性           ← 生产前必须过关
14. 成本与性能工程         ← 跑得起才算可用（含 Batch API）
15. 部署与生产化           ← 上线前的最后一关
16. 项目表达与面试         ← 把工程价值表达出来
```

## 知识地图

```
          LLM调用基础
               ↓
         Agent架构与设计
         ↙     ↓     ↘
   Tool       Context    RAG
  Calling      工程    知识系统
     ↘          ↓       ↙
      Memory与状态管理
               ↓
     Workflow与LangGraph
               ↓
       ┌───────┴──────────┐
   MCP协议         Eval测试体系
       └───────┬──────────┘
               ↓
  可观测性 · 安全 · 成本 · 部署
               ↓
         项目表达与面试
```

## 按场景选文档

**面试准备（2 周）**
→ 必读：`Agent架构与设计` → `Tool Calling` → `Context工程` → `RAG与知识系统` → `项目表达与面试`
→ 补充：`Eval与测试体系`（LLM 测试话题越来越常见）、`Memory与状态管理`
→ 可跳过：`MCP与工具协议`（面试不常考，用到时再读）

**做 RAG 项目**
→ 核心：`LLM调用基础` → `Context工程` → `RAG与知识系统`
→ 生产化：`Eval与测试体系` → `可观测性与调试` → `部署与生产化`

**做 Agent 项目**
→ 核心：`LLM调用基础` → `Agent架构与设计` → `Tool Calling` → `Memory与状态管理`
→ 复杂流程：`Workflow与LangGraph`
→ 生产化：`安全与可控性` → `成本与性能工程` → `部署与生产化`

**补工程短板（已有项目经验）**
→ 直接看你不熟的那篇，文档互相独立，不必顺序读

## 必读 vs 按需

| 文档 | 分类 | 理由 |
|------|------|------|
| `LLM调用基础` | **必读** | 所有文档的前置 |
| `Agent架构与设计` | **必读** | 理解 Agent 是什么 |
| `Tool Calling` | **必读** | Agent 的执行核心 |
| `Context工程` | **必读** | 工程质量的关键，面试高频 |
| `RAG与知识系统` | **必读** | 最常见 AI 应用场景 |
| `Memory与状态管理` | 按需 | 做多轮对话或长任务时 |
| `Workflow与LangGraph` | 按需 | 需要复杂流程编排时 |
| `MCP与工具协议` | 按需 | 需要多工具集成标准化时 |
| `推理模型与ExtendedThinking` | **必读** | 2025+ 主流范式，面试热点 |
| `Computer Use与GUI Agent` | 按需 | Anthropic 特有能力，旧系统自动化 |
| `Eval与测试体系` | 按需 | 需要可验证的质量改进时 |
| `可观测性与调试` | 按需 | 上生产前 |
| `安全与可控性` | 按需 | 上生产前 |
| `成本与性能工程` | 按需 | 有成本压力时 |
| `部署与生产化` | 按需 | 上线前 |
| `项目表达与面试` | 按需 | 面试前 |

## 常见混淆边界

| 混淆点 | 澄清 |
|--------|------|
| Prompt Engineering vs Context Engineering | 这里用"Context 工程"——因为生产系统里 prompt 只是 context 的一部分，完整的 context 包含工具定义、检索结果、记忆、历史等 |
| LangGraph vs 自己写 while 循环 | `Workflow与LangGraph.md` 有详细对比；短期项目 while 循环够用，需要 checkpoint/human-in-the-loop/可视化时才需要 LangGraph |
| RAG vs Fine-tuning | `RAG与知识系统.md` 有选择指南；RAG 解决"没有知识"，Fine-tuning 解决"行为/风格/格式不对" |
| Memory vs Context | Memory 是跨请求的持久存储；Context 是当次请求的窗口内容。见 `Memory与状态管理.md` |
