# Computer Use 与 GUI Agent

这篇文档解决一个问题：**如何让 AI Agent 操作图形界面（浏览器、桌面应用），而不仅仅是调用 API**。

Computer Use 是一种视觉执行模式：模型读取屏幕截图，再提出点击、输入、滚动或快捷键等操作。Provider 的工具名称、版本字段、模型 ID 和支持的平台都会变化；本笔记中的 `computer_*`、`text_editor_*`、`bash_*` 以及模型名都是版本化示例，运行前必须核对对应 Provider 的官方文档。

---

## 1. 核心概念

### 普通 Tool Use vs Computer Use

```
普通 Tool Use：
  模型 → 调用函数(参数) → 返回文本结果 → 模型

Computer Use：
  模型 → 决定操作(点击/输入/截图) → 执行操作 → 截图 → 模型
                    ↑_______________________________________↓
                           视觉感知循环（Visual Loop）
```

**关键差别**：Computer Use 的"工具结果"是截图（图片），不是文本。模型通过"看"屏幕来感知当前状态，而不是读取 API 返回值。

### 三个内置工具

```python
tools = [
    {
        "type": "computer_20250124",   # 最新版本号可查 Anthropic 文档
        "name": "computer",
        "display_width_px": 1024,
        "display_height_px": 768,
        "display_number": 1,           # X display number，Linux 环境
    },
    {
        "type": "text_editor_20250124",
        "name": "str_replace_editor",  # 文件编辑工具（比截图更高效的文件操作）
    },
    {
        "type": "bash_20250124",
        "name": "bash",                # 执行 shell 命令
    },
]
```

---

## 2. Computer 工具的原子操作

`computer` 工具支持以下 action：

| action | 参数 | 说明 |
|--------|------|------|
| `screenshot` | 无 | 截取当前屏幕，返回 base64 图片 |
| `left_click` | `coordinate: [x, y]` | 左键单击 |
| `right_click` | `coordinate: [x, y]` | 右键单击 |
| `double_click` | `coordinate: [x, y]` | 双击 |
| `type` | `text: str` | 在当前焦点位置输入文字 |
| `key` | `text: str` | 按键（如 `"ctrl+c"`, `"Return"`, `"Escape"`）|
| `scroll` | `coordinate`, `direction`, `amount` | 滚动 |
| `mouse_move` | `coordinate: [x, y]` | 移动鼠标（不点击）|
| `left_click_drag` | `start_coordinate`, `coordinate` | 拖拽 |
| `cursor_position` | 无 | 返回当前鼠标位置 |

---

## 3. 完整执行循环

```python
import anthropic
import base64
import subprocess

client = anthropic.Anthropic()

def take_screenshot() -> str:
    """截取屏幕，返回 base64 编码的 PNG"""
    # Linux with Xvfb
    result = subprocess.run(
        ["import", "-window", "root", "-display", ":1", "/tmp/screen.png"],
        capture_output=True,
    )
    with open("/tmp/screen.png", "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

def execute_computer_action(action: str, **params) -> str | None:
    """执行 computer action，有些 action 需要返回截图"""
    if action == "screenshot":
        return take_screenshot()

    elif action == "left_click":
        x, y = params["coordinate"]
        subprocess.run(["xdotool", "mousemove", str(x), str(y), "click", "1"])
        return None

    elif action == "type":
        subprocess.run(["xdotool", "type", "--", params["text"]])
        return None

    elif action == "key":
        subprocess.run(["xdotool", "key", "--", params["text"]])
        return None

    # ... 其他 action 类似

def computer_use_loop(task: str):
    messages = [{"role": "user", "content": task}]

    tools = [
        {
            "type": "computer_20250124",
            "name": "computer",
            "display_width_px": 1024,
            "display_height_px": 768,
        }
    ]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=tools,
            messages=messages,
        )

        # 追加 assistant 回复
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # 任务完成，返回最终文本
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "任务完成"

        if response.stop_reason != "tool_use":
            break

        # 执行所有工具调用
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            if block.name == "computer":
                action = block.input["action"]
                params = {k: v for k, v in block.input.items() if k != "action"}
                result = execute_computer_action(action, **params)

                if result is not None:  # screenshot 返回图片
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": result,
                                },
                            }
                        ],
                    })
                else:  # 非截图操作，返回成功确认
                    # 操作完成后立即截图，让模型看到结果
                    screenshot = take_screenshot()
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": [
                            {"type": "text", "text": f"action '{action}' executed"},
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": screenshot,
                                },
                            },
                        ],
                    })

        messages.append({"role": "user", "content": tool_results})
```

---

## 4. 沙箱环境搭建

Computer Use **必须**在隔离环境里运行，不能直接操作宿主机桌面。

### Docker + Xvfb 方案（推荐）

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    xvfb \           # 虚拟显示
    x11vnc \         # VNC 服务（可选，用于调试时查看屏幕）
    xdotool \        # 模拟鼠标键盘
    imagemagick \    # 截图工具（import 命令）
    python3 python3-pip \
    chromium-browser \
    && rm -rf /var/lib/apt/lists/*

# 启动虚拟显示
ENV DISPLAY=:1
RUN echo '#!/bin/bash\nXvfb :1 -screen 0 1024x768x24 &\nsleep 1\nexec "$@"' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

```bash
# 构建并运行
docker build -t computer-use-sandbox .
docker run -it --rm \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    computer-use-sandbox \
    python3 agent.py "打开浏览器，访问 github.com，截图"
```

### 验证环境

```bash
# 在容器里验证虚拟显示正常工作
export DISPLAY=:1
Xvfb :1 -screen 0 1024x768x24 &
sleep 1

# 截图测试
import -window root -display :1 /tmp/test.png
echo "截图大小: $(wc -c < /tmp/test.png) bytes"
```

---

## 5. 成本注意事项

Computer Use 比普通 tool use **贵得多**：

```
普通工具调用结果：几百 token（文本）
Computer Use 截图：1024x768 PNG ≈ 1000-2000 token（图片按 token 计费）

典型任务（10次截图 + 20次操作）：
  截图 token ≈ 15,000 input tokens
  模型推理  ≈ 5,000 output tokens
  总计      ≈ $0.05-0.15 per task（claude-sonnet-4-6 定价）
```

**成本优化策略：**

```python
# 1. 操作后不是每次都截图，只在关键节点截图
# 错误：每个 click 后都截图
# 正确：执行一系列操作后，统一截图确认状态

# 2. 降低截图分辨率（够用即可）
"display_width_px": 1024,   # 不要用 1920，信息密度够了
"display_height_px": 768,

# 3. 优先用 bash/str_replace_editor 工具
# 如果任务可以用 CLI 完成，不要用 computer 截图
# bash("cat /etc/hosts") 远比截图看文件内容便宜

# 4. 设置 max_steps 上限
MAX_STEPS = 50
step = 0
while step < MAX_STEPS:
    step += 1
    ...
```

---

## 6. 与 Playwright/Selenium 的对比

| 维度 | Claude Computer Use | Playwright / Selenium |
|------|--------------------|-----------------------|
| **如何定位元素** | 视觉（看坐标）| CSS selector / XPath |
| **处理动态页面** | 截图感知，不关心 DOM | 需要等待特定元素 |
| **可测试性** | 难以精确断言 | 精确 assert |
| **脆弱性** | UI 布局变化时影响坐标 | selector 失效 |
| **无障碍站点** | 可以操作任何可见元素 | 需要有 DOM 结构 |
| **成本** | 高（LLM 每步都调用）| 低（纯本地执行）|
| **适合场景** | 复杂非结构化任务、旧系统 | 确定性自动化测试 |

**选择原则**：
- 有 API 就用 API（最便宜）
- API 没有但网站结构规整 → Playwright
- 网站复杂/旧系统/任务需要判断 → Computer Use
- 纯文件/CLI 操作 → bash 工具（不需要 computer）

---

## 7. 安全边界

Computer Use 是高风险操作，必须加安全约束：

```python
# 1. 隔离环境（不能访问宿主机文件系统）
# 2. 网络隔离（限制容器能访问的域名）
# 3. 禁止执行危险命令
BANNED_COMMANDS = [
    "rm -rf", "sudo", "chmod 777", "curl | sh",
    "wget | sh", "> /dev/sda",
]

def safe_bash(command: str) -> str:
    for banned in BANNED_COMMANDS:
        if banned in command:
            return f"Error: banned command pattern '{banned}'"
    return subprocess.run(command, shell=True, capture_output=True, text=True).stdout

# 4. 人工确认高风险操作
HIGH_RISK_ACTIONS = ["购买", "付款", "删除", "提交", "发送邮件"]

def needs_human_approval(action_description: str) -> bool:
    return any(keyword in action_description for keyword in HIGH_RISK_ACTIONS)

# 5. 会话时长限制
MAX_LOOP_SECONDS = 300  # 5 分钟超时
```

---

## 8. 典型应用场景

```
✓ 旧系统自动化（没有 API，只有 GUI）
✓ 需要跨多个网站/应用完成的任务
✓ 表单填写（复杂 web 表单）
✓ 数据抓取（JavaScript 渲染的页面，Playwright 处理困难的）
✓ 软件测试（探索性测试，不只是回归）
✓ 开发工作流自动化（打开 IDE、运行命令、查看结果）
```

---

## 9. 面试高频

**Q：Computer Use 和普通 tool call 的本质区别是什么？**

> 普通 tool call 是模型调用函数，结果是文本。Computer Use 是模型看截图（图片）来感知当前界面状态，然后决定下一个操作（点击/输入），操作执行后再截图，形成视觉感知循环。模型靠"看"而不是靠"读 API 返回值"来理解环境。

**Q：Computer Use 的主要工程挑战是什么？**

> 三个主要挑战：一是成本，截图 token 很贵，任务复杂时累积成本快；二是可靠性，UI 布局变化会导致坐标偏移（比 selector 更脆弱）；三是安全，模型可以执行任意鼠标键盘操作，必须在隔离环境里运行，且高风险操作需要人工确认。工程上一般结合 bash 工具使用，能用 CLI 完成的不用截图，只有真正需要视觉判断的环节才调用 computer 工具。

**Q：什么情况下用 Computer Use 而不是 Playwright？**

> Playwright 适合有确定性 DOM 结构的网站，可以精确 assert，成本低，速度快。Computer Use 适合：旧系统（无 DOM 可操作）、高度动态的 JS 页面（Playwright 难以等待）、需要视觉判断的任务（判断按钮是否灰色/可点击）、以及跨多个不同类型应用的复合任务。如果有 API 永远优先用 API，Computer Use 是没有更好选项时的最后手段。
