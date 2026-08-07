# Computer Use 与 GUI Agent

Computer Use 让 Agent 通过截图观察界面，再提出点击、输入、滚动或快捷键动作。它适合没有稳定 API 的旧系统，但成本、脆弱性和安全风险都高；已有 API 时优先 [Tool Calling](./02_Tool%20Calling.md)。Provider 的工具名、动作 schema、模型 ID 和支持平台都随版本变化，下面的名称只作概念示例。

> **学习位置**：这是 Coding Agent 的高风险扩展。先完成 `05`、`07/08` 和 Eval，再学习 GUI；运行前核对 Provider 官方文档。

> **职责边界**：本文只补视觉观察、屏幕动作、隔离环境和 GUI 特有评测；通用工具权限、审批、沙箱和恢复仍以核心安全与可靠性文档为准。

## 1. 视觉执行循环

```text
普通 Tool：模型 → 函数(参数) → 文本事实 → 模型
GUI Agent：模型 → 屏幕动作 → 隔离环境执行 → 截图/事件 → 模型
```

关键差异是：工具结果主要是视觉状态，不是结构化 API 事实。因此每个动作都可能受布局、焦点、弹窗、登录状态和分辨率影响，不能只凭“动作已发送”判断成功。

典型能力组合可以包括 `computer`、文件编辑和 `bash`，但它们不是跨 Provider 的标准：OpenAI Responses 与 Anthropic Messages 的工具类型、事件和回填格式不同。

## 2. 原子动作

| 动作 | 输入 | 用途 |
|---|---|---|
| `screenshot` | 无 | 获取当前屏幕 |
| `left_click` / `right_click` | 坐标 | 点击控件 |
| `double_click` | 坐标 | 打开项目或文件 |
| `type` | 文本 | 在当前焦点输入 |
| `key` | 按键组合 | 提交、复制、退出等 |
| `scroll` | 方向、步数、坐标 | 浏览页面 |
| `drag` / `mouse_move` | 坐标 | 拖动或定位 |

Provider 可能返回不同名称和坐标单位；适配器负责把版本化动作转换成内部动作，并在执行前做参数、窗口和权限校验。

## 3. 最小执行合同

下面假设适配器已经把 Provider 响应归一化为 `response.text` 和 `response.actions`；真实字段不要直接从某一家 Provider 的 SDK 泄漏到执行器。

```text
for step in range(max_steps):
    response = provider.decide(task, screenshot, allowed_actions)
    record(response)

    if response.text is not None and not response.actions:
        return verify_state_or_stop(response)

    results = []
    for action in response.actions:
        policy.check(actor, action, current_state)
        result = sandbox.execute(action, timeout=action_timeout)
        results.append(result)
        if result.side_effecting:
            verify_or_request_approval(result)

    screenshot = capture_at_checkpoint(results)
    record(results, screenshot)

return stopped("max_steps")
```

实现时至少保证：

- 模型只能提出动作，沙箱/策略层决定能否执行；
- 每个动作有 `action_id`、超时、取消和结果状态；
- 必要时回填截图，但不要把每个中间画面都送入模型；
- 不可逆动作先预览或人工审批，完成后用 UI 状态或 API 事实验证；
- 最大步数、总时长、费用、网络和文件范围都有硬上限。

## 4. 何时使用

| 方案 | 定位方式 | 成本/稳定性 | 优先场景 |
|---|---|---|---|
| API / 普通工具 | 结构化资源 ID | 最低、最稳定 | 有可靠接口的业务 |
| Playwright/Selenium | DOM、selector | 较低、可精确断言 | 结构稳定的网页自动化 |
| Computer Use | 视觉与坐标 | 较高、受 UI 变化影响 | 旧系统、无 API、非结构化界面 |

选择顺序：有 API 用 API；没有 API 但 DOM 稳定用 Playwright；只有 GUI 或界面需要视觉判断时才用 Computer Use。文件和 CLI 任务直接使用受限的编辑/Shell 工具，不要截图读文件。

## 5. 隔离环境

Computer Use 不应直接操作宿主机桌面。最小环境通常是容器或独立虚拟机中的浏览器、虚拟显示（如 Xvfb）和动作驱动器：

```text
宿主机
  └─ 受限容器/VM
       ├─ DISPLAY=:1 + Xvfb
       ├─ 浏览器或目标应用
       ├─ computer adapter
       └─ workspace（只挂载必要目录）
```

启动前固定并验证：

- 只读或最小可写文件系统，禁止访问宿主机敏感目录；
- 网络默认关闭，按域名/端口放行；
- CPU、内存、进程、墙钟时间、截图大小和日志容量上限；
- 容器启动后用测试页面截图，确认显示、焦点、浏览器和清理流程正常；
- 任务结束销毁会话，避免 Cookie、下载文件和截图残留。

## 6. 成本与可靠性

```text
任务成本 = 图片/文本输入 + 模型输出 + 工具/沙箱费用
总延迟 = 模型延迟 + 截图/动作延迟 + 页面等待
```

先记录每轮图片尺寸、Token、动作数、等待时间、失败率和重试次数，再优化：

1. 能用结构化工具完成的步骤不要走 GUI；
2. 只在导航、提交、错误或关键状态处截图；
3. 选择足以识别小字和控件的分辨率，用 Eval 验证；
4. 对页面等待、重复点击和弹窗设置超时与去重；
5. 用 `max_steps`、总时长和费用预算切断卡死循环。

具体价格和模型限制进入 [版本与来源](./版本与来源.md) 核对，不在本文维护固定数字。

## 7. 安全边界

至少分开治理以下边界：

| 边界 | 最小控制 |
|---|---|
| 身份与资源 | actor、租户、目标窗口、资源范围、策略版本 |
| 文件与命令 | allowlist、`shell=False`、沙箱、超时、最小目录 |
| 网络 | 默认拒绝、域名/端口 allowlist、出站审计 |
| 高风险动作 | 购买、付款、删除、提交、发信前预览/审批 |
| 证据与审计 | 记录动作、策略决定、审批、截图摘要和最终验证 |

关键词匹配最多只能提醒用户，不能替代资源级授权。真正的策略应根据 actor、动作、资源、当前 State 和审批状态确定，见 [安全与可控性](./08_安全与可控性.md)。

## 8. 场景与 Eval

适合：旧系统自动化、跨站点表单、JavaScript 页面、探索性测试和没有 API 的开发环境。评测至少覆盖：布局变化、弹窗、登录过期、网络抖动、焦点丢失、半成功状态、重复提交、危险动作拦截、截图过大和会话清理。

若系统后来提供稳定 API，应重新评估是否回到普通工具；若需要更强的截图/DOM 双通道、动作幂等、人工审批和任务恢复，先补齐这些 Harness 能力，再增加模型自由度。

语音通道见 [语音与实时对话 Agent](./语音与实时对话Agent.md)，跨产品委托见 [跨 Agent 协议与 A2A](./跨Agent协议与A2A.md)。

## 官方来源

- [OpenAI Computer use](https://developers.openai.com/api/docs/guides/tools-computer-use)
- [Anthropic Computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)

核对日期：2026-07-30。实现前重新核对动作 schema、截图格式、模型兼容、价格和安全建议。
