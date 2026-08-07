# 12. Claude API Agent

## 这一步在路线中的位置

建议先完成 01–05，再把本项目当作 Provider 对照实验：核心不是换一个 SDK，而是观察同一个 Agent 机制如何映射到另一套原生请求、响应、Streaming 和 Tool Use 形状。

配套理论：[LLM 调用基础](../../../../01_LLM调用基础.md)。

## 运行前准备

先安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Mock 模式（推荐先运行）

```bash
python main.py
```

没有 `ANTHROPIC_API_KEY` 时不会发起网络请求，而是打印五个主题的请求结构和循环关系。先用 Mock 模式确认 `messages`、`tool_use`、`tool_result` 和缓存标记分别处在哪里。

### 真实调用（可选）

```bash
cp .env.example .env
# 编辑 .env，填写真实密钥和当前可用的模型 ID
python main.py
```

`ANTHROPIC_MODEL` 不在代码里硬编码：模型 ID 会变化，应以当前 Provider 控制台/文档为准。不要提交 `.env` 或把密钥写进笔记。

## 读代码时抓住五个映射

1. `client.messages.create`：一次 Provider 调用；
2. `response.content`：Provider 返回的 typed content blocks；
3. `stop_reason == "tool_use"`：模型提出 Tool Use，不等于工具已经执行；
4. 执行本地函数后回传 `tool_result`：这是下一轮输入；
5. `cache_control`：一种 Provider 特有的缓存提示，不是 Agent 必须具备的记忆。

本项目里的计算工具使用受限 AST，而不是 `eval`；这是因为模型生成的参数必须经过解析、校验和权限边界，不能直接当 Python 代码执行。

## Prompt Caching 的正确预期

缓存适合重复出现、稳定且足够长的前缀，例如 System Prompt、文档或工具描述；变化频繁的内容不一定命中。命中率、门槛、缓存时长、价格和可缓存字段以当前 Provider 文档与实际用量账本为准，所以它是优化手段，不是“生产必备”的前置条件。

## 验收

- 能把 Provider 的 typed blocks 与内部 `ToolCall`/`ToolResult` 概念对应起来；
- 能画出 `tool_use → 本地执行 → tool_result → 下一次请求`；
- 能说明 Streaming 只改变传输/展示时机，不自动改变任务成功条件；
- 能在 Mock 模式下读懂缓存请求结构，并说出至少一个不应缓存的动态内容。
