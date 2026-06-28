# AI 应用工程知识库

这个目录是从 Python 工程基础到 AI 应用全链路工程的完整知识库。

目标：**既适合学习，也适合面试复习，也适合做完项目后回看**。

---

## 目录结构

### Python 工程基础

| 文档 | 内容 |
|------|------|
| `Python/Python核心语法.md` | 语言基础、标准库、async |
| `Python/Python工程化.md` | 虚拟环境、依赖管理、配置、日志、测试 |
| `Python/Python代码组织与设计模式.md` | Service/Client/Repository/Pipeline 模式 |
| `Python/HTTP与API调用.md` | requests/httpx、重试、客户端封装 |
| `Python/FastAPI.md` | 路由、请求响应模型、依赖注入、服务化 |
| `Python/错误与Debug.md` | 排错流程、常见错误、最小复现 |

### AI 应用工程核心

| 文档 | 内容 |
|------|------|
| `Agent/LLM调用基础.md` | SDK、messages、streaming、结构化输出 |
| `Agent/Agent架构与设计.md` | Agent Loop、范式、状态、Human-in-the-loop |
| `Agent/Tool Calling.md` | Schema 设计、执行循环、错误处理、权限 |
| `Agent/Context工程.md` | Context 构造、System Prompt、窗口管理、注入防御 |
| `Agent/RAG与知识系统.md` | Ingestion、检索增强、Agentic RAG、评估 |
| `Agent/Memory与状态管理.md` | 四类记忆、存储策略、召回、用户画像 |
| `Agent/Workflow与LangGraph.md` | 图编排、状态机、checkpoint、中断恢复 |
| `Agent/MCP与工具协议.md` | MCP 原理、集成模式、自建协议考量 |
| `Agent/Eval与测试体系.md` | Harness、测试集、Offline/Online Eval、回归 |
| `Agent/可观测性与调试.md` | Tracing、Logging、Replay、失败分类 |
| `Agent/安全与可控性.md` | Prompt Injection、工具沙箱、权限边界 |
| `Agent/成本与性能工程.md` | Token 成本、延迟、缓存、Model Routing |
| `Agent/部署与生产化.md` | 部署模式、版本管理、灰度、生产 Checklist |
| `Agent/项目表达与面试.md` | 项目讲法、面试高频、回答框架 |

---

## 学习路径建议

### 路径 A：从零开始

```
Python核心语法 → Python工程化 → HTTP与API调用
→ LLM调用基础 → Tool Calling → Agent架构与设计
→ Context工程 → RAG与知识系统 → Memory与状态管理
→ Workflow与LangGraph → MCP与工具协议
→ Eval与测试体系 → 可观测性与调试 → 安全与可控性
→ 成本与性能工程 → 部署与生产化 → 项目表达与面试
```

### 路径 B：已有 Python 基础，直接进 AI 工程

```
LLM调用基础 → Agent架构与设计 → Tool Calling → Context工程
→ RAG与知识系统 → Memory与状态管理 → Eval与测试体系
→ 其他按需
```

### 路径 C：面试前快速复习

```
Agent架构与设计（面试高频部分）
→ Tool Calling（面试高频部分）
→ RAG与知识系统（面试高频部分）
→ Eval与测试体系（面试高频部分）
→ 项目表达与面试
```

---

## 与 Learning/AI 的边界

- **模型工作原理、LLM 理论、fine-tuning 基础** → 看 `Learning/AI/`
- **如何用模型、如何构建系统、如何上生产** → 看这个目录
