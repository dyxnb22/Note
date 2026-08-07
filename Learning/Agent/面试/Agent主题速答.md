# Agent 主题速答

这里只保留各主题最常见的面试追问；范围和优先级以 [学习范围与面试题型](./学习范围与面试题型.md) 为准，机制正文仍以 `Learning/Agent` 主笔记为准。若这里与主文档冲突，以主文档为准。

## 01_LLM调用基础

**Q：为什么要把 LLM 调用封装成 service，不直接在业务代码调用？**

> 统一管理密钥、重试、超时、日志，不用每个地方重复；测试时可以 mock 这一层；后续切换 Provider 或模型时只改一处；可以在这一层统一做 cost tracking 和 tracing。

**Q：流式输出（streaming）的技术原理是什么？**

> 模型 API 通常通过 Server-Sent Events（SSE）或类似事件流逐块返回结果，客户端可以在完整回答生成前开始渲染。它主要改善首字节体验；仍要处理断线、取消、事件顺序和最终结果落库。

**Q：结构化输出和 JSON Mode 有什么区别？**

> JSON Mode 通常只保证结果可解析为 JSON，不保证字段名称和类型。结构化输出会把 schema 纳入生成约束，但客户端仍要做 Pydantic 校验，并处理拒答、截断和版本不兼容；它降低格式风险，不等于业务结果可信。


## 02_Tool Calling

**Q：Tool Calling 的完整流程是什么？模型真的执行了代码吗？**

> Tool Calling 分两个阶段：首先，用户输入连同工具 schema 一起发给模型，模型返回的不是文字答案，而是一个结构化的"工具调用意图"（tool_call），包含函数名和参数。然后，你的 Python 程序读取这个意图，找到对应函数，真正执行，把结果再返回给模型，模型才生成最终答案。模型自始至终没有执行任何代码——它只生成了一个 JSON 描述"我想调用什么"。

**Q：如果工具调用失败，应该怎么处理？**

> 在工具边界捕获可预期的运行时异常，把经过脱敏的错误结构化为 tool result 返回给模型（如 `{"error": "数据库连接超时"}`），同时写入 trace。模型可以重试、换工具或向用户说明；只有确认幂等且仍在预算内的操作才适合自动重试，有副作用的失败要先核实事实。

**Q：Schema 的 description 写得好不好，对实际效果有影响吗？**

> 影响很大。模型会综合工具 name、description、参数 schema 和当前 Context 做选择。description 写得含糊（"处理用户相关操作"），模型就不知道应不应该用、参数怎么填；写清楚使用场景、不适用场景和参数说明，通常更容易选对。工具选择出问题时，先检查 schema 和当前注入的工具集合。


## 03_Agent架构与设计

**Q：Agent 和 Workflow 的区别是什么？什么时候用 Agent，什么时候用 Workflow？**

> Workflow 的路径是设计时确定的：步骤 A → 步骤 B → 步骤 C，每步做什么由开发者写死。Agent 的路径是运行时由模型动态决定的：模型观察当前状态，自主决定下一步。如果任务流程相对固定，用 Workflow——更可预测、可控、可测试。如果任务路径本身就是不确定的，需要根据中间结果灵活调整，才用 Agent。生产环境里大多数"Agent 系统"实际上是 Workflow + 少量动态决策点的组合。

**Q：ReAct、Plan-and-Execute、Multi-Agent，各自适合什么场景？**

> ReAct 适合单目标、工具密集、步骤相对直线的任务。Plan-and-Execute 适合需要长期规划的复杂任务，先分解再执行，执行失败可以重新规划。Multi-Agent 适合任务复杂到单个 Agent 无法处理，或者需要并行执行多个子任务的场景。但 Multi-Agent 协调复杂度很高，不要盲目用。

**Q：为什么生产中的 Agent 不做全自动，要 Human-in-the-loop？**

> 三个核心原因：一是错误成本——自动发邮件、改数据库出错影响真实用户；二是可观测性——LLM 的决策不透明，出了问题很难追因，人在关键节点可以作为安全阀；三是合规和责任——很多业务场景需要明确的人工审批记录。Human-in-the-loop 不是不信任 AI，而是在技术成熟度和业务风险之间找到合理平衡。


## 04_Context工程

**Q：Prompt Engineering 和 Context Engineering 有什么区别？**

> Prompt Engineering 通常指设计单个 prompt（system prompt 怎么写，few-shot 怎么给）。Context Engineering 是更完整的概念，包括整个 context 窗口里的所有内容：system prompt、工具定义、检索结果、会话历史、用户输入、输出约束——每一层如何设计、组合、裁剪、优化。生产系统里，system prompt 写得再好，context 里的其他部分不设计好，整体质量也差。

**Q：如何防止 Prompt Injection？**

> 完全防止 Prompt Injection 是不可能的，但可以分层降低风险。首先，用结构化字段把用户输入和系统指令区分开，并明确内容边界；其次，RAG 场景把检索内容标注为“外部资料”，不是指令；最后，工具层独立做权限验证，即使模型被注入，执行边界仍可阻止实际危害。标签和提示本身不是安全控制，必须由权限、沙箱和审计兜底。

**Q：Context 太长怎么处理？**

> 几种策略：一是硬截断，简单但可能丢失重要历史；二是滑动窗口保留最近 N 轮；三是摘要压缩，让模型把早期对话压缩成摘要再保留；四是 RAG 化，不把历史塞进 context，而是检索相关片段。另外，system prompt 尽量精简——太长的 system prompt 每次都消耗大量 token 预算，而且内容越多模型对每条规则的关注度越低（lost in the middle 问题）。


## 08_安全与可控性

**Q：AI 应用有哪些独特的安全风险，传统 Web 安全考虑不到的？**

> 两类最重要：一是 Prompt Injection，用户（或通过文档间接）构造输入覆盖 system prompt，绕过规则、提取信息、诱导危险操作。这是 SQL Injection 的 LLM 版本，但更难防御，因为 LLM 的输入是自然语言，没有明确的"语法分隔符"。二是 Tool Misuse，在 Agent 系统里，模型被诱导调用危险工具（删数据、发邮件）或带错误参数调用工具。防御重点：最小权限（只给必要工具）、工具参数验证、高危操作二次确认。

**Q：如何防御间接 Prompt Injection？**

> 间接注入是攻击者在 RAG 文档或工具结果里植入指令，比普通用户输入注入更难防。主要策略：一是在 system prompt 里强调"外部资料不是指令"；二是把检索到的内容用特殊标签包裹，明确标注来源，降低被当作指令执行的可能；三是对高危操作做输出验证，验证模型要调用的工具是否在授权范围内；四是沙箱化工具执行——即使模型被注入了恶意指令，工具层的权限边界能阻止实际危害。


## 10_Eval与测试体系

**Q：什么是 Eval Harness，为什么 AI 应用需要它？**

> Eval Harness 是一套自动化评测基础设施，包含测试集、评测指标、执行器、结果存储和报告对比。AI 应用需要它是因为 LLM 输出是概率性、多维度的，传统 assert 式单元测试无法评估"这个回答好不好"。没有 harness 的结果是：每次改 prompt 或换模型，你都不知道整体质量有没有变好，优化是不可验证的。

**Q：Offline Eval 和 Online Eval 有什么区别，各适合什么情况？**

> Offline Eval 在发布前用预构造的测试集批量评测，速度快但测试集可能不代表真实分布。Online Eval 在发布后对真实用户流量采样评测，数据真实但失败会影响真实用户。两者组合：Offline Eval 做 pre-release 质量门槛，Online Eval 做上线后持续监控。

**Q：如何在 CI 里做 AI 系统的回归测试？**

> 维护一个 golden test set，每次 PR 合并前跑 eval harness，把分数和 baseline 对比。超过预设退步阈值（比如关键指标下降 5%）就阻止合并。对每个发现的 bug，把对应 case 加入 regression set，确保同类问题不会重现。可以把测试集分层：小的核心集每次跑，大的完整集每天或每次 release 跑，平衡速度和覆盖面。


## 11_可观测性与调试

**Q：AI 应用的 Observability 和传统软件有什么不同，你会关注哪些额外指标？**

> 传统软件主要看延迟、错误率、吞吐量。AI 应用还需要关注：一是 LLM 输出质量（回答是否有幻觉、格式是否正确）；二是工具调用准确性（模型选了正确的工具吗）；三是 context 质量（RAG 检索到的内容是否相关）；四是 cost（每次调用的 token 用量和费用）；五是多步骤的执行轨迹（agent 执行了多步，哪一步出了问题）。我会用 tracing 工具（如 LangSmith 或 Phoenix）记录完整的调用链，structured logging 记录每次 LLM 调用的 token 用量和 tool 选择。

**Q：生产环境 AI 应用的 bug 怎么 debug？**

> 先看 trace，定位是哪一步出问题。通常分几层排查：一是 LLM 层（输出格式不对、幻觉、拒绝回答），主要检查发给模型的 messages 是否正确，prompt 格式要求是否清晰；二是工具层（参数错误、超时、权限问题），检查 tool schema 和实际执行日志；三是 RAG 层（召回不准、知识过期），检查 embedding 和 chunk 策略。如果有 replay 系统，可以直接复现生产 case 再修改配置对比结果。


## 06_Durable Execution与分布式可靠性

**Q：长任务为什么不能只靠一次 HTTP 请求？**

> 请求进程可能重启，连接可能断开，工具也可能重复投递。应把任务状态放进可持久化的状态机，用队列/租约驱动执行，用 checkpoint 记录已完成边界；用户断线只影响展示，不应丢失任务。

**Q：重试和恢复时最容易出什么问题？**

> 把“可能重复执行”的步骤区分开：纯查询可安全重试；有副作用的写操作必须有幂等键、去重记录或补偿动作。恢复前先确认 checkpoint、租约和外部副作用的事实，不能仅凭模型消息判断“上一步已经完成”。见 [Durable Execution](../06_Durable%20Execution与分布式可靠性.md)。


## LangGraph

**Q：LangGraph 和 LangChain 的区别是什么？**

> LangChain 更像模型、Prompt、工具和链式组件的组合；LangGraph 用 State、Node、Edge 表达条件路由、循环、并行、Checkpoint 和中断，二者可以一起使用但不是同一层。如果流程固定，普通代码或 Workflow 可能够用；需要持久化状态和复杂控制流时，再考虑 LangGraph。具体版本以 [LangGraph](../LangGraph.md) 和 [框架选型](../Agent框架与平台选型.md) 为准。

**Q：什么是 Checkpoint，为什么重要？**

> Checkpoint 是在图执行过程中保存 state 快照或事件位置的机制。重要性：一是容错——程序崩了可以从上次状态恢复；二是 Human-in-the-loop——在关键节点暂停，等待人工确认后继续；三是调试——可以回到历史状态检查问题。生产环境需要持久化、可迁移且有访问控制的 Checkpointer，具体存储由框架版本、规模和恢复要求决定；开发环境才适合使用内存实现。

**Q：如何实现 Human-in-the-loop？**

> 有两种方式。`interrupt_before` / `interrupt_after` 是静态断点，适合调试；人工流程推荐在节点内部调用 `interrupt(payload)` 动态中断，支持条件中断，人工通过 `Command(resume=...)` 传入决定继续。节点恢复时会从节点开头重新执行，所以中断前的副作用必须幂等或拆到独立节点。

**Q：`Send` API 解决什么问题？**

> `Send` 解决动态并行的问题。普通图结构是静态的（编译时固定节点数量），但 Map-Reduce 场景下需要"根据输入数据量动态创建并行执行实例"——比如 10 个文档就并行 10 个 summarize_node。`Send` 在 conditional_edges 函数里返回 `[Send("node", input1), Send("node", input2), ...]`，运行时动态 fan-out，结果通过 Annotated + `operator.add` 自动 fan-in 合并。

**Q：`Command` 对象和 `add_conditional_edges` 有什么区别？**

> 两者都能做路由，区别在于逻辑位置。`add_conditional_edges` 是在图构建时定义路由函数，路由逻辑和节点逻辑分离，全局结构清晰。`Command` 是在节点函数内部同时返回 state 更新和路由决定，适合路由逻辑依赖复杂计算结果的场景（不需要把中间结果放进 state 再读出来做判断）。实际项目里两者混用：固定分支用 `add_conditional_edges`，复杂动态路由用 `Command`。

**Q：什么是时间旅行（Time Travel），有什么工程价值？**

> LangGraph 的 Checkpoint 记录了每一步的完整 state 快照。Time Travel 是指用 `get_state_history()` 获取所有历史 checkpoint，然后选择某个历史节点用 `invoke(None, config=snapshot.config)` 从那里重新执行，会分叉出新的执行路径。工程价值：调试时快速定位出错步骤（不用重跑全程）；A/B 测试从同一 checkpoint 分叉对比不同策略；审计时重现历史执行过程验证 Agent 行为。


## MCP与工具协议

**Q：MCP 是什么，解决什么问题？**

> MCP（Model Context Protocol）是一个开放协议，定义了 AI 应用和外部工具/数据源之间的通信合同。它把 Server 能力和 Client 集成解耦：同一个工具可以被多个支持 MCP 的客户端复用，但认证、权限、版本和供应链仍需分别治理。

**Q：MCP 和直接 Tool Calling 有什么区别，什么时候用 MCP？**

> 直接 Tool Calling 是在你的 Python 程序里定义函数 + schema，模型调用后直接在同一进程里执行。MCP 是把工具封装成独立的 Server 进程，通过标准协议通信。如果工具只是你自己的应用在用，直接写函数 + schema 更简单；如果工具需要被多个 AI 应用共享（比如团队的内部知识库搜索，要给 Claude Desktop 用，也要给自己的 AI 应用用），做成 MCP Server 更合适。另外，现在有很多现成的社区 MCP Server（GitHub、文件系统、数据库等），可以直接作为 Client 使用，不用自己实现。


## Memory与状态管理

**Q：Memory 的几种类型，分别适合什么场景？**

> 通常分四类：一是 in-context memory，即当前调用中的 messages 历史；二是会话级外部存储，跨请求但同一会话可见；三是长期用户记忆，跨会话保存偏好和事实，可按数据规模选择关系库、关键词、向量或混合召回；四是工作流状态，保存任务进度并支持断点续传。选哪种取决于生命周期、权限、更新方式和访问模式。

**Q：为什么不把所有历史对话都塞进 context？**

> 三个问题：成本（每次调用的 input token 线性增长）；质量（context 太长，模型对早期内容关注度下降，lost-in-the-middle 现象）；延迟（更多 token = 更慢的 TTFT）。正确做法是根据当前问题语义检索相关记忆，只注入真正需要的部分，而不是全量。

**Q：如果用户在不同会话说了相互矛盾的信息，怎么处理？**

> 策略：时间优先，后面说的通常覆盖之前的；用户明确修正时立即更新；对于模糊矛盾，保留两条并标注不确定，不要强行合并；对重要的长期记忆可以定期让用户确认。关键是记忆存储要有时间戳和来源字段，才有能力做冲突分析。


## 成本与性能工程

**Q：如何降低 AI 应用的 token 成本？**

> 几个层次：一是压缩 context，system prompt 精简，去掉无关历史消息；二是使用 Provider 支持的 Prompt Caching，按实际命中率和价格计算收益；三是对可复用结果做 Semantic Cache；四是 Model Routing，简单任务用便宜小模型，复杂任务才用大模型；五是缓存幂等查询的工具结果。最重要的是先监控每类请求的 token、命中率和失败率，再做针对性优化。

**Q：AI 应用的延迟怎么优化？**

> 先区分是 TTFT 高还是 TPOT 高。TTFT 高通常是 prompt 太长（要压缩 context）或服务器负载高；TPOT 高通常是模型太大或并发太高。应用层优化：一是 streaming 输出，让用户更快看到第一个字；二是压缩 context 长度；三是并行工具调用；四是对工具结果做缓存；五是用更快的小模型（如果质量够用）。另外，如果是长任务，转成异步后台任务，立即返回 task_id，用户轮询或 webhook 获取结果。
