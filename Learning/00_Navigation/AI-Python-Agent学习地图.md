# Python → AI → Agent 学习地图

这张地图解决三个目录之间最容易混淆的问题：先学什么、哪些内容只看一份、实践代码应该去哪里。

## 一句话边界

```text
Python：可复用的语言、工程和服务基础
   ↓
AI：模型、训练、表示和 LLM 原理
   ↓
Agent：模型调用、工具、状态、编排、治理和交付
```

实践代码不单独形成第四套理论，而是回链到上面三层：

- `Learning/Python/`：Python 语言、标准库、工程化、HTTP 和服务化。
- `Learning/AI/`：深度学习、Transformer、LLM 原理和 AI 工具认知。
- `Learning/Agent/`：LLM 调用、Tool Calling、Agent Loop、RAG、Workflow、MCP、安全、评测和生产化。
- `Learning/Python/实践/`：只放 Python 基础或通用工程练习。
- `Learning/AI/实践/`：深度学习和 LLM 课程实验。
- `Learning/Agent/实践/`：Agent 应用与 Agent Harness 代码实验。

## 推荐主线

### 0. Python 基础与工程化

适合 Python 不熟或希望补工程基础时：

1. [Python 学习路径](../Python/Python.md)
2. [Python 核心语法](../Python/Python核心语法.md)
3. [Python 工程化](../Python/Python工程化.md)
4. [HTTP 与 API 调用](../Python/HTTP与API调用.md)
5. 按需阅读 [FastAPI](../Python/FastAPI.md)、[代码组织与设计模式](../Python/Python代码组织与设计模式.md)、[错误与 Debug](../Python/错误与Debug.md)

### 1. Python 到 Agent 的桥接

[Python Agent 工程化补充](../Python/Python%20Agent工程化补充.md)是唯一的 Python/Agent 桥接主文档，集中练习：

- Pydantic、TypedDict、Protocol 和外部数据边界；
- asyncio、并发上限、取消、超时和重试；
- 幂等、配置、日志、装饰器和上下文管理器；
- 如何为模型输出、工具参数和运行时状态建立可测试的合同。

已有 Python 基础时，不需要重复通读所有语法，直接从这篇桥接文档进入 Agent 主线即可。

### 2. AI 模型与 LLM 原理

根据目标选择一条，不需要把所有摘要重复读两遍：

| 目标 | 入口 | 作用 |
|---|---|---|
| 系统学习神经网络和训练 | [动手学深度学习路线](../AI/DeepLearning/README.md) | D2L 顺序：自动微分、线性模型、MLP、CNN、RNN、Transformer、NLP |
| 快速建立 LLM 心智模型 | [LLM 基础](../AI/LLM基础.md) | Token、Embedding、Transformer、生成、对齐、RAG 和 Context |
| 连接深度学习与 LLM 工程 | [深度学习基础桥接笔记](../AI/DeepLearning.md) | 只补够用的数学、训练循环、Transformer、LoRA 和 HuggingFace |

`AI/DeepLearning/` 是系统课程；`AI/DeepLearning.md` 是桥接速览；`AI/LLM基础.md` 是应用工程需要的 LLM 原理。三者职责不同，不再互相复制正文。

## Agent 文档职责

下面是 `Learning/Agent/` 的唯一主题地图。看起来相近的文档保留，是因为它们分别承担设计、实现、评测或交付职责：

| 层次 | 主文档 | 负责的问题 |
|---|---|---|
| 核心运行时 | [LLM 调用基础](../Agent/LLM调用基础.md)、[Tool Calling](../Agent/Tool%20Calling.md)、[Agent 架构与设计](../Agent/Agent架构与设计.md) | 模型调用、工具合同、Agent Loop、状态和终止 |
| Harness 工程 | [Context 工程](../Agent/Context工程.md)、[代码 Agent 基础设施](../Agent/代码%20Agent%20基础设施.md)、[Durable Execution](../Agent/Durable%20Execution与分布式可靠性.md) | 上下文、代码库操作、验证、Checkpoint、恢复和隔离 |
| 知识与编排 | [RAG](../Agent/RAG.md)、[知识系统](../Agent/知识系统.md)、[Memory 与状态管理](../Agent/Memory与状态管理.md)、[Workflow 与编排](../Agent/Workflow与编排.md)、[LangGraph](../Agent/LangGraph.md)、[MCP 与工具协议](../Agent/MCP与工具协议.md)、[多 Agent 协作](../Agent/多Agent协作的边界与模式.md) | 检索、知识治理、持久记忆、固定流程、框架实现、外部工具协议和协作边界 |
| 产品与协同 | [Agent 产品与人机协同](../Agent/Agent产品与人机协同.md) | 是否适合 AI、自主性、澄清、审批、接管和产品指标 |
| 质量与治理 | [Agent 安全与威胁建模](../Agent/Agent安全与威胁建模.md)、[安全与可控性](../Agent/安全与可控性.md)、[Agent 身份与数据治理](../Agent/Agent身份与数据治理.md) | 威胁分析、防御实现、身份、租户和数据生命周期 |
| 评测与运维 | [Agent Eval 实验方法](../Agent/Agent%20Eval实验方法.md)、[Eval 与测试体系](../Agent/Eval与测试体系.md)、[可观测性与调试](../Agent/可观测性与调试.md)、[Agent 运维与事故响应](../Agent/Agent运维与事故响应.md) | Task/Trajectory、Harness、CI、Trace、发布、告警和事故 |
| 生产交付 | [成本与性能工程](../Agent/成本与性能工程.md)、[部署与生产化](../Agent/部署与生产化.md) | 预算、延迟、限流、部署、灰度和回滚 |
| 扩展与表达 | [推理模型与 Extended Thinking](../Agent/推理模型与Extended%20Thinking.md)、[模型行为与工具调用训练](../Agent/模型行为与工具调用训练.md)、[Computer Use 与 GUI Agent](../Agent/Computer%20Use与GUI%20Agent.md)、[项目表达与面试](../Agent/项目表达与面试.md) | 研究分支、GUI Agent、模型行为实验和项目输出 |

两组重点边界：

- [Agent 安全与威胁建模](../Agent/Agent安全与威胁建模.md)先回答“谁能影响系统、资产是什么、攻击面在哪里”；[安全与可控性](../Agent/安全与可控性.md)再回答“用什么策略、沙箱、脱敏和恢复机制防御”。
- [Agent Eval 实验方法](../Agent/Agent%20Eval实验方法.md)评估完整任务轨迹、环境副作用和发布门槛；[Eval 与测试体系](../Agent/Eval与测试体系.md)建设通用 Harness、测试集、指标、Mock 和 CI。

### 3. Agent 核心主线

完成 Python 桥接后，按下面顺序阅读：

```text
LLM 调用基础
  → Tool Calling
  → Agent 架构与设计
  → Context 工程
  → 安全与可控性 / Agent 安全与威胁建模
  → Eval 与测试体系 / Agent Eval 实验方法
  → 部署与生产化
```

对应入口：[Agent 工程知识库](../Agent/README.md) 和 [Agent 学习路线图](../Agent/学习路线图.md)。

## 实践项目如何选择

| 实践项目 | 所在目录 | 定位 | 是否需要全部完成 |
|---|---|---|---|
| Python 基础练习 | [Python/实践/Python基础练习](../Python/实践/Python基础练习/README.md) | 变量、类型、输出和条件判断 Notebook | Python 不熟时选做 |
| DeepPath Lab | [AI/实践/DeepPathLab](../AI/实践/DeepPathLab/README.md) | 自动微分、线性模型、MLP、CNN 的项目制从零实现 | 想补模型训练基础时完成 |
| llm_learning | [AI/实践/llm_learning](../AI/实践/llm_learning/README.md) | 从深度学习、Transformer 到 Agent、RAG、评测、微调和研究的宽路线 | 作为 LLM 工程扩展，不与 Agent 主线重复通读 |
| ai-agent-learning | [Agent/实践/ai-agent-learning](../Agent/实践/ai-agent-learning/README.md) | SDK/API → Tool Calling → Agent Loop → LangGraph → RAG/MCP 的入门主线 | Agent 应用开发优先完成 01–09 |
| learn-claude-code | [Agent/实践/learn-claude-code](../Agent/实践/learn-claude-code/README.md) | Agent Harness 的 Context、权限、任务、恢复、团队和 MCP 机制 | 已会基础 Agent 后选修 |

选择原则：同一知识点优先完成一条实践路线，再用另一条路线做对照；不要因为目录里有多份代码就把它们当成多门必修课。

## 本轮整理清单

- [x] 保留 `Python`、`AI`、`Agent` 三个主题边界，不把语言基础、模型原理和运行时设计混在一起。
- [x] 建立本地图，统一说明主线、分支和实践项目的选择关系。
- [x] 将 Python 下名称含糊的单 Notebook 目录和文件改为 `Python基础练习/基础语法与条件判断.ipynb`。
- [x] 明确 `DeepLearning/`、`DeepLearning.md`、`LLM基础.md` 的不同职责，避免把摘要当成第二套课程。
- [x] 将 `AI工具与编程助手.md` 定位为 AI 工具使用速查；Agent 运行时和治理仍以 `Learning/Agent/` 为主。
- [x] 明确两组容易重叠的 Agent 文档：威胁建模 vs 防御实现，Agent Eval 实验方法 vs 通用 Eval Harness。
- [x] 明确三套 Agent/LLM 实践的分工：应用入门、Harness 深入、LLM 工程宽路线。
- [x] 保留实践项目内部重复的 `.gitignore`、`.env.example` 和依赖文件；它们是各自项目的隔离配置，不属于知识重复。
- [x] 为三个主题 README 和 Learning 总索引补充本地图入口。
- [x] 清理当前 Notes 内的 `.DS_Store`；未来由系统重建的文件由 `.gitignore` 忽略。

## 后续维护规则

1. 新增理论时先判断是否已有主文档；已有主题只补原文，不新建同义标题。
2. 新增实践时只保留代码、运行说明、实验结果和项目 README；理论解释回链主题文档。
3. 一篇文档如果同时承担“速查”和“完整教程”，优先拆成入口页 + 唯一主文档，不复制正文。
4. 删除内容前先做全文链接检查；可回退的历史代码优先移入废纸篓，不直接永久删除。
5. 价格、模型名、协议版本和产品命令属于易变信息，保留来源和核对日期，不把它们当成稳定理论。
