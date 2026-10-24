# 完整案例：订单查询 Agent

输入订单号后，Agent 查询状态和示例取消规则，提交结构化结论，由程序核对。数据与业务函数沿用[Python 脚本案例](../Python/案例_订单查询脚本.md)。

普通脚本按固定顺序查询。Agent 入口每轮接收一个工具提案，校验后执行，按调用 ID 回填结果，再决定是否继续。

## 启动与结果

准备 Python 3.12 或更高版本，从 Notes 根目录执行：

```bash
cd "Learning/AI/实践/order_assistant"
python3 agent.py A --trace /tmp/order-agent-trace.json
```

默认 Provider 为 scripted，不联网、不需要密钥；每轮根据已经取得的工具结果，返回预先写好的动作。运行结果包含：

```json
{
  "status": "succeeded",
  "reason": "verified",
  "model_calls": 3,
  "answer": {
    "order_id": "A",
    "status": "pending",
    "version": 1,
    "policy_id": "cancel-v1",
    "can_request_cancellation": true
  }
}
```

实际输出还包含 observations 中的订单和规则。--trace 将完整逐轮消息保存到指定文件，重复运行会覆盖该输出文件。此处目录与所有代码见[共享案例说明](../AI/实践/order_assistant/README.md)。

## 三轮怎样形成结果

| 轮次 | 模型提案 | 运行时执行及回填 | 随后掌握的事实 |
|---|---|---|---|
| 1 | call_1：lookup_order，order_id 为 A | 按固定 demo 身份查询，回填 pending 与版本 1 | 订单实际状态 |
| 2 | call_2：lookup_policy，status 为 pending | 返回 cancel-v1 与申请条件 | 适用规则 |
| 3 | call_3：submit_answer，提交订单号、状态与布尔结论 | 对照已取得的订单和规则；全部匹配后提交结果 | 答案与已查到的事实一致，任务完成 |

三次调用的额度足以完成表中路径：第三轮先处理答案，不会因额度用尽而丢掉成功结果。改成两次时，只能查到订单和规则，程序保留它们并以 budget_exhausted 结束。

提案采用 Chat Completions 的 function tool 消息结构。scripted Provider 直接构造这套消息，供观察配对过程，本身不做语言理解或模型推理。

## 一次提案与结果的实际形状

下面摘自第一轮，工具参数是 JSON 字符串：

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [{
    "id": "call_1",
    "type": "function",
    "function": {
      "name": "lookup_order",
      "arguments": "{\"order_id\": \"A\"}"
    }
  }]
}
```

程序执行后将结果关联到相同调用 ID：

```json
{
  "role": "tool",
  "tool_call_id": "call_1",
  "content": "{\"status\": \"ok\", \"data\": {\"order_id\": \"A\", \"status\": \"pending\", \"version\": 1}}"
}
```

第一轮历史只有 system 和 user。查完订单，第二轮追加 assistant 提案和 tool 结果；查完规则，第三轮再追加对应消息。模型由此看到原目标和各条结果的来历，只发最近一个结果就会丢失这些关联。

本例没有 MCP 层，call_1 是模型工具调用 ID。若进一步接入 MCP，还需要把它与协议请求 ID 映射，参见[Tool Calling 与 MCP](04_Tool与协议/Tool%20Calling与MCP.md)。

## 代码中的职责

| 位置 | 处理内容 | 对应笔记 |
|---|---|---|
| [orders.py](../AI/实践/order_assistant/orders.py) | 数据读取、租户范围、规则与咨询结果 | [Python 脚本讲解](../Python/案例_订单查询脚本.md) |
| [providers.py](../AI/实践/order_assistant/providers.py) | 脚本化决策或非流式兼容接口 | [Provider 适配](10_模型与推理/02_Provider适配与框架选型.md) |
| [agent.py](../AI/实践/order_assistant/agent.py)的 TOOLS、parse_call、validate_arguments | 工具描述、调用 ID、注册名与参数校验 | [工具契约](04_Tool与协议/Tool%20Calling与MCP.md) |
| execute | 使用可信 demo 身份调用工具，保存订单与规则，核对答案 | [Memory 与 State](03_Memory与状态/Memory与State.md) |
| run | 请求、执行、回填、记录与停止 | [运行时状态流转](01_基础架构/运行时机制与状态流转.md) |
| main | 运行参数、Provider 选择、结果和轨迹文件 | [Python 工程基础](../Python/04_工程基础.md) |

Provider 只收到模型消息和工具说明，看不到整个数据文件或 State 字典。order 和 policy 由执行器在查询成功后写入，模型自报的租户、版本或成功标记不能覆盖它们。

## 参数、事实与完成分别检查

parse_call 检查提案是否完整、是否只有一个 function 调用，以及调用 ID 是否已经使用。

validate_arguments 检查工具是否注册、参数是否为 JSON 对象，以及字段集合、字符串、枚举与布尔类型是否符合要求。这里实现了本例所需的 Schema 子集；复杂输入可采用[Python 参数校验](../Python/06_Agent开发.md#在运行时校验工具参数)中的 Pydantic。

execute 继续检查动作是否符合当前任务：订单号要与查询目标一致，规则要适用于查到的订单状态，提交的答案要同时有订单和规则作为依据。JSON 格式正确，也可能因为这些条件不满足而被拒绝。

submit_answer 提交结构化咨询结论，verified 表示提交的字段与本次查询到的订单和规则一致。这个验证只检查结构化字段，不检查自然语言答案，也不执行取消订单。

## 失败分支的运行表现

| 情形 | 程序怎样处理 |
|---|---|
| X 不在 demo 可见范围，或编号不存在 | 第一轮回填 not_found，任务停止；不输出其他租户的订单事实 |
| 与目标不符的订单号、额外 tenant 参数、错误状态值、布尔字段类型错误或无效 JSON 参数 | 回填 invalid_arguments，模型可在剩余轮数内修正 |
| 缺少调用 ID、重复 ID、多工具并行提案或参数不是 JSON 字符串 | 停止为 provider_error，不猜测如何执行 |
| 两轮已用完，只有订单和规则 | failed／budget_exhausted，保留 observations，不误报成功 |
| 最后一轮提交匹配事实的答案 | succeeded／verified |
| 模型服务 HTTP 错误、网络错误、截断、拒绝或不支持的内容块 | 适配器或运行时报告 provider_error，保留本次已取得的观察 |

表中的分类和字段名由本案例定义。取消订单、通知、审批和写操作重试不在实现范围内。

## 接入真实模型时发生什么变化

只有显式选择 --provider compatible 才会访问模型服务。接口配置与完整命令见[运行说明](../AI/实践/order_assistant/README.md#可选模型接口)。兼容接口须支持非流式文本、function tools、required 工具选择，并按调用 ID 接收结果。

本例每轮只允许一个工具调用，不支持流式拼接、推理内容块和签名连续性等额外协议；收到这些返回会报错。真实模型的提案顺序和所需轮数可能不同，三轮固定路径不能代表真实模型的成功率。

Provider 在此采用同步 def；[Python 运行时章节](../Python/06_Agent开发.md)中的 async Protocol 是异步接口示意，不能把同步对象直接当作该异步接口使用。采用异步客户端时，需要一起处理 await、超时和取消。

该消息结构参照 [OpenAI 官方 Function Calling 文档](https://developers.openai.com/api/docs/guides/function-calling?tool-use=chat-completions)。离线执行和适配器的本地响应样本已验证，真实模型调用尚未验证。

## 接下来读哪些机制

需要让进程结束后继续任务时，再读[Durable 与生产运维](09_工程化与系统设计/02_Durable与生产运维.md)；需要文档证据时，读[RAG 与检索](06_RAG与知识库/RAG与检索.md)。固定规则查询并未实现分块、Embedding、重排或完整 RAG。

[端到端设计](11_端到端设计与交付/端到端Agent系统设计.md)继续讨论业务写入、审批与结果核对；[阅读路线](00_02_阅读路线.md)列出了按目标进入这些主题的顺序。
