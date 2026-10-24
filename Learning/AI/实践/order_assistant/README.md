# 订单咨询：从 Python 脚本到 Agent

同一份订单数据有两个入口：query_orders.py 按固定路径完成查询；agent.py 接收模型工具提案，执行后回填观察，再判断是否结束。完整讲解分别在[Python 案例](../../../Python/案例_订单查询脚本.md)和[Agent 案例](../../../Agent/案例_订单查询Agent.md)。

## 环境与目录

Python 3.12 或更高版本；全部代码只依赖标准库。已在 Python 3.12.13 与 3.14.6 上验证本地运行。

```text
order_assistant/
├── data/orders.json    # A、B、X 三条教学订单
├── orders.py           # 数据、可见范围和规则
├── query_orders.py     # 固定查询入口
├── providers.py        # 脚本化模型与可选接口
└── agent.py            # 提案、校验、执行、回填与停止
```

从 Notes 根目录进入案例目录：

```bash
cd "Learning/AI/实践/order_assistant"
python3 --version
```

本地数据文件中的 pending 订单满足示例取消申请条件，shipped 与 cancelled 不满足。入口固定使用 demo 模拟已登录身份；这套数据与规则用于讲解，不连接真实订单系统。

## 普通脚本入口

```bash
python3 query_orders.py A
```

输出订单 A、状态 pending、版本 1、规则 cancel-v1，以及 can_request_cancellation 为 true。查询 B 时输出 shipped 和 false，程序同样正常结束。完整输出与代码流向见[Python 讲解](../../../Python/案例_订单查询脚本.md)。

## Agent 入口

```bash
python3 agent.py A --trace /tmp/order-agent-trace.json
```

默认选择 scripted Provider。它不读取密钥、不访问网络，根据已有观察依次提出 lookup_order、lookup_policy、submit_answer。预期最终 status 为 succeeded，reason 为 verified，model_calls 为 3。输出也保留已取得的 observations。

轨迹文件记录每轮 request_messages、proposal 和 tool_result。指定的 --trace 文件会被覆盖；不传该选项时只输出最终结果。轨迹不包含认证请求头，仍会包含本次订单输入与查询结果。

## 已展示的失败结果

以下均为完整运行路径，具体控制逻辑见[Agent 讲解](../../../Agent/案例_订单查询Agent.md#失败分支的运行表现)。

| 命令 | 实际结果 | 退出码 |
|---|---|---:|
| python3 query_orders.py A | pending，申请条件为 true | 0 |
| python3 query_orders.py B | shipped，申请条件为 false | 0 |
| python3 query_orders.py X | not_found，不输出 private 订单事实 | 2 |
| python3 agent.py A | 三轮后 succeeded／verified | 0 |
| python3 agent.py B | 三轮后成功，申请条件为 false | 0 |
| python3 agent.py X | 第一轮停止，reason 为 not_found | 2 |
| python3 agent.py A --max-rounds 2 | budget_exhausted；保留订单与规则，无最终答案 | 2 |

本地 Provider 样本还覆盖了错误参数回填、错误答案拒绝、重复调用 ID、截断与不支持的内容字段处理。

## 可选模型接口

仅显式指定 compatible 模式时访问网络。本例接入非流式 Chat Completions function tools 子集；服务与模型必须支持该子集，不能只凭“兼容”名称推断能力。完整端点由 LLM_CHAT_URL 指定，与原 llm_learning 示例使用的 LLM_BASE_URL 不同。

将下面的示例值替换为所用服务的实际配置：

```bash
export LLM_CHAT_URL="https://your-service.example/v1/chat/completions"
export LLM_MODEL="服务支持的模型标识"
export LLM_API_KEY="你的密钥"
python3 agent.py A --provider compatible --max-rounds 6 --trace /tmp/order-agent-live.json
```

适配器发送 model、messages、tools、tool_choice="required"、stream=false；取得完整 function 调用后才交给执行器。遇到流式、并行工具、推理内容块或其他不支持的协议字段，会明确报告限制。网络等待设置 15 秒超时，它不是整个任务的总期限。

真实模型可能选择错误工具、提出不合法参数或直接拒绝，因此结果需要以实际运行记录为准。脚本化路径不衡量模型效果。真实模型调用尚未验证；接口结构按 [OpenAI 官方文档](https://developers.openai.com/api/docs/guides/function-calling?tool-use=chat-completions)核对，并以本地响应样本验证解析。

## 与已有实践的关系

[原 Agent 入门示例](../llm_learning/01_agent_basics/学习文档.md)展示计算、时间与本地记事，用文本 JSON 约定动作。本案例补充原生工具调用消息、可信查询范围、逐轮轨迹和提交结果校验，沿用两组理论笔记中的订单场景。

进一步阅读：[Python 语言核心](../../../Python/01_语言核心.md)、[Agent 路线](../../../Agent/00_02_阅读路线.md)。业务写入、异步取消、持久化恢复、MCP、RAG 与生产部署分别在对应专题中展开。
