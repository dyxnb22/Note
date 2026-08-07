# 00 最小 Agent Loop 练习

这是一个可选的无 API、无 SDK 预热练习。它用一个固定的 Mock Provider 把一次调用、一次工具执行和下一轮循环串起来：

```text
内部 CallRequest
  → Provider 原始响应
  → Adapter 归一化为 ModelResult
  → Agent 决定执行 read_file
  → ToolResult 回填
  → 下一轮得到最终文本
```

## 目标

完成后应该能解释：

- Provider 合同和内部模型合同有什么区别；
- Adapter 为什么是翻译层；
- ToolCall 为什么不是工具执行结果；
- Agent Loop 为什么需要第二轮；
- State、Trace 和 ModelResult 分别放在哪里。

## 运行

本练习只需要 Python 标准库：

```bash
python main.py
```

不需要 API Key，也不会访问网络或修改文件。

## 观察输出

重点观察每一步：

1. 用户任务进入 `CallRequest`；
2. Mock Provider 返回一个原始 `tool_call`；
3. Adapter 转为内部 `ModelResult`；
4. 执行器读取内存中的文件；
5. `ToolResult` 带着同一个 `call_id` 回填；
6. 第二轮返回最终文本，Loop 停止。

## 练习

1. 把 `read_file` 改成不存在的路径，增加 `file_not_found` 错误；
2. 把工具结果中的文件内容截断，观察为什么需要结果大小限制；
3. 把 `MAX_STEPS` 改成 1，说明为什么任务会以 `budget_exhausted` 停止；
4. 为 `ModelResult` 增加 `usage` 和 `request_id`，但不要把它们放入模型输入；
5. 写一张表，标出哪些数据进入 Context，哪些只进入 Trace。

这个练习是概念模拟，不是生产 Provider，也不替代后面的真实 SDK 练习。
