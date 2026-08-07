# 11. MCP Server

## 这一步在路线中的位置

先完成 00–10。MCP 是把工具、资源和提示词暴露给外部宿主的一种协议边界，不是理解 Agent Loop 的前置条件；本项目用于把已经学过的 Tool 合同放到跨进程场景里观察。

配套理论：[MCP 与工具协议](../../../../MCP与工具协议.md)。

## 先分清三个原语

| 原语 | 谁主动发起 | 作用 | 本项目示例 |
|---|---|---|---|
| Tool | 模型/宿主请求调用 | 执行一个可调用操作；可以有副作用，也可以只读 | `add_note`、`search_notes` |
| Resource | 模型/宿主读取 | 提供只读数据 | `notes://stats`、`notes://all` |
| Prompt | 用户/宿主选择 | 提供可复用的提示词模板 | `summarize_notes` |

不要把 MCP Server 当成“会自己思考的 Agent”：它主要负责声明能力、接收协议请求、执行函数并返回结果。是否让模型调用、何时停止、是否需要人工批准，仍由宿主侧的 Agent Loop 决定。

## 运行

### 先运行 Mock 模式（推荐）

不安装 `fastmcp` 也能观察业务函数和三种原语：

```bash
python main.py
```

Mock 输出不会启动协议监听，只是把同一批函数按 Tool/Resource 的语义调用一遍。

### 再运行真实 stdio Server（可选）

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

此时程序会等待 MCP 宿主通过 **stdio** 发送协议消息；终端看起来没有普通输出并不代表卡死。要看到实际的发现、调用和返回，还需要一个支持 MCP 的宿主/客户端连接它。

## 建议阅读顺序

1. 先看 `_add_note_impl`、`_search_notes_impl`：它们与 MCP 无关，是业务函数；
2. 再看 `@mcp.tool`、`@mcp.resource`、`@mcp.prompt`：这是协议注册层；
3. 最后看 `demo_without_mcp`：把协议原语和真实函数对应起来。

## 验收

- 能说明 Tool、Resource、Prompt 的边界；
- 能指出 `add_note` 会改变状态，而 `search_notes`、`notes://stats` 只读；
- 能解释“Server 提供能力”与“Agent 决定是否调用”不是一回事；
- 能分别运行 Mock 模式和真实 Server，并写下两者的输出/等待行为差异。
