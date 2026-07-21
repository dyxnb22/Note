"""
第 12 课：Claude API — 生产级用法

学习目标：
1. 直接用 Anthropic SDK（不绕 LangChain）调用 Claude；
2. 掌握 Prompt Caching（提示词缓存）— 2025 年之后的生产必备；
3. 掌握 Streaming 流式输出；
4. 掌握 Tool Use（工具调用）的原生 API 格式。

为什么要学原生 SDK？
  LangChain/LangGraph 是封装层，理解原生 API 让你：
  - 能排查封装层 Bug
  - 能做性能调优（Token 成本、延迟）
  - 能读懂任何 Claude 相关的技术文档

运行（需要 ANTHROPIC_API_KEY）：
    pip install anthropic python-dotenv
    # 在 .env 里设置 ANTHROPIC_API_KEY=your_key
    python main.py

运行（无 Key，Mock 模式）：
    python main.py
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv()  # 也尝试从工作目录加载

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-6"

# ---------------------------------------------------------------------------
# 1. 基础调用
# ---------------------------------------------------------------------------


def demo_basic():
    """最简单的一次性对话。"""
    print("\n=== 1. 基础调用 ===")

    if not (HAS_ANTHROPIC and ANTHROPIC_KEY):
        print("[Mock] client.messages.create(")
        print(f"    model='{MODEL}',")
        print("    max_tokens=256,")
        print("    messages=[{'role': 'user', 'content': '用一句话解释什么是 Agent'}]")
        print(")")
        print("[Mock 回答] Agent 是一个能自主决策、调用工具、循环执行直到完成目标的 AI 系统。")
        return

    client = anthropic.Anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=256,
        messages=[{"role": "user", "content": "用一句话解释什么是 Agent"}],
    )
    print(f"回答：{message.content[0].text}")
    print(f"用量：input={message.usage.input_tokens} output={message.usage.output_tokens} tokens")


# ---------------------------------------------------------------------------
# 2. Prompt Caching（生产必备）
# ---------------------------------------------------------------------------
# 原理：把重复使用的大段文本（System Prompt、文档、工具描述）标记为 cache_control。
# Claude 会把这段内容缓存 5 分钟。
# 缓存命中时，输入 Token 费用降低 90%，延迟也大幅下降。
# 适用场景：RAG 文档注入、长 System Prompt、重复工具列表。

LONG_SYSTEM_PROMPT = """你是 DevPilot，一个专业的代码分析助手。

## 能力范围
- 代码 Bug 分析和修复建议
- 代码重构和优化建议
- 架构设计评审
- PR 描述生成

## 行为准则
1. 永远先理解用户需求，再给出建议
2. 修改建议必须是"建议级"，不直接修改用户代码
3. 给出建议时，解释原因，而不只是给结论
4. 如果信息不足，优先询问而不是猜测

## 输出格式
- 分析报告：使用 Markdown 格式
- 代码建议：使用 diff 格式
- 风险提示：使用 ⚠️ 标注

这段 System Prompt 很长，在真实生产中可能包含完整的公司代码规范文档（几千 Token）。
通过 Prompt Caching，这段内容只需要在第一次请求时处理，后续请求直接命中缓存，
节省 90% 的 Token 成本。
""" * 3  # 重复 3 次让它更长，模拟真实场景


def demo_prompt_caching():
    """展示 Prompt Caching 的用法和效果。"""
    print("\n=== 2. Prompt Caching ===")

    if not (HAS_ANTHROPIC and ANTHROPIC_KEY):
        print("[Mock] 演示 Prompt Caching 的请求结构：")
        print("""
messages.create(
    model=MODEL,
    system=[{
        "type": "text",
        "text": LONG_SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"}  # ← 关键：标记为可缓存
    }],
    messages=[...],
)

第 1 次调用：cache_creation_input_tokens = N（写入缓存，正常计费）
第 2 次调用：cache_read_input_tokens = N（读缓存，费用降低 90%）

适用场景：
  ✅ System Prompt 超过 1024 Token（Claude 最低缓存门槛）
  ✅ RAG：把检索到的文档作为缓存内容
  ✅ 工具列表很长（10+ 个工具的描述）
  ❌ 频繁变化的内容（每次都不同，无法命中缓存）
""")
        return

    client = anthropic.Anthropic()

    def make_request(turn: int, question: str):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=128,
            system=[{
                "type": "text",
                "text": LONG_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},  # 标记为可缓存
            }],
            messages=[{"role": "user", "content": question}],
        )
        usage = resp.usage
        cache_write = getattr(usage, "cache_creation_input_tokens", 0)
        cache_read = getattr(usage, "cache_read_input_tokens", 0)
        print(f"  第 {turn} 次 | 写缓存={cache_write} 读缓存={cache_read} 输出={usage.output_tokens} tokens")
        print(f"         回答: {resp.content[0].text[:80]}")

    make_request(1, "介绍一下你的能力")
    make_request(2, "如何分析一个 Bug？")  # 同一个 System Prompt，命中缓存


# ---------------------------------------------------------------------------
# 3. Streaming 流式输出
# ---------------------------------------------------------------------------


def demo_streaming():
    """展示如何流式接收 Claude 的回答，适合需要实时展示进度的场景。"""
    print("\n=== 3. Streaming 流式输出 ===")

    if not (HAS_ANTHROPIC and ANTHROPIC_KEY):
        print("[Mock] 用 stream=True 或 with client.messages.stream(...) 启用流式输出")
        print("[Mock 流式回答] 什么是...")
        import time
        for char in "流式输出让用户实时看到 Agent 的思考过程，而不用等待完整回答。":
            print(char, end="", flush=True)
            time.sleep(0.03)
        print()
        return

    client = anthropic.Anthropic()
    print("回答（流式）：", end="", flush=True)
    with client.messages.stream(
        model=MODEL,
        max_tokens=128,
        messages=[{"role": "user", "content": "用一句话解释流式输出的好处"}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
    print()


# ---------------------------------------------------------------------------
# 4. Tool Use（原生 API 格式）
# ---------------------------------------------------------------------------
# LangChain @tool 会自动生成这个格式。
# 理解原生格式，能帮你调试和自定义工具调用行为。

TOOLS_DEFINITION = [
    {
        "name": "get_weather",
        "description": "查询城市天气。",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称，例如北京、上海"}
            },
            "required": ["city"],
        },
    },
    {
        "name": "calculate",
        "description": "计算数学表达式，例如 '2 + 3 * 4'。",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式字符串"}
            },
            "required": ["expression"],
        },
    },
]

WEATHER_DATA = {"北京": "晴，25°C", "上海": "多云，22°C"}


def _execute_tool(name: str, inputs: dict) -> str:
    if name == "get_weather":
        return WEATHER_DATA.get(inputs["city"], "无数据")
    if name == "calculate":
        try:
            return str(eval(inputs["expression"], {"__builtins__": {}}, {}))
        except Exception as e:
            return f"计算失败: {e}"
    return "未知工具"


def demo_tool_use():
    """展示 Claude 原生 Tool Use 的完整循环。"""
    print("\n=== 4. Tool Use（原生 API）===")

    if not (HAS_ANTHROPIC and ANTHROPIC_KEY):
        print("[Mock] Tool Use 原生请求结构：")
        print("""
# 第 1 次请求：把工具定义传给 Claude
response = client.messages.create(
    model=MODEL,
    tools=TOOLS_DEFINITION,          # ← 工具列表（JSON Schema 格式）
    messages=[{"role": "user", "content": "北京天气？"}]
)

# response.stop_reason == "tool_use" 时，Claude 想调用工具
# response.content 里有 tool_use block：
{
    "type": "tool_use",
    "id": "toolu_01...",
    "name": "get_weather",
    "input": {"city": "北京"}
}

# 执行工具后，把结果回传（第 2 次请求）
messages.append({
    "role": "assistant",
    "content": response.content
})
messages.append({
    "role": "user",
    "content": [{"type": "tool_result", "tool_use_id": "toolu_01...", "content": "晴，25°C"}]
})

# Claude 综合工具结果，生成最终回答
""")
        return

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": "北京和上海今天天气怎么样？温差是多少？"}]

    # ReAct 循环
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=512,
            tools=TOOLS_DEFINITION,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            text = next((b.text for b in response.content if hasattr(b, "text")), "")
            print(f"最终回答：{text}")
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = _execute_tool(block.name, block.input)
                    print(f"  工具调用: {block.name}({block.input}) → {result}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break


# ---------------------------------------------------------------------------
# 5. 多轮对话（带历史）
# ---------------------------------------------------------------------------


def demo_multi_turn():
    """展示如何维护对话历史，实现真正的多轮上下文。"""
    print("\n=== 5. 多轮对话 ===")

    conversation = []
    turns = [
        "你好，我在学 AI Agent",
        "LangGraph 和 LangChain 有什么区别？",
        "我应该先学哪个？",
    ]

    if not (HAS_ANTHROPIC and ANTHROPIC_KEY):
        print("[Mock] 多轮对话只需要在 messages 里累积历史：")
        for i, turn in enumerate(turns, 1):
            print(f"  第 {i} 轮：{turn}")
        print("""
messages = []  # 历史消息列表

for user_input in turns:
    messages.append({"role": "user", "content": user_input})
    response = client.messages.create(model=MODEL, messages=messages, ...)
    messages.append({"role": "assistant", "content": response.content[0].text})
    # 下一轮时 Claude 能看到完整历史
""")
        return

    client = anthropic.Anthropic()
    for turn in turns:
        conversation.append({"role": "user", "content": turn})
        resp = client.messages.create(model=MODEL, max_tokens=128, messages=conversation)
        answer = resp.content[0].text
        conversation.append({"role": "assistant", "content": answer})
        print(f"  用户: {turn}")
        print(f"  Claude: {answer[:150]}")
        print()


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== 第 12 课：Claude API 生产级用法 ===")

    if not HAS_ANTHROPIC:
        print("[注意] anthropic 包未安装：pip install anthropic")
    if not ANTHROPIC_KEY:
        print("[注意] 未找到 ANTHROPIC_API_KEY，以 Mock 模式运行")
        print("       在 .env 里设置：ANTHROPIC_API_KEY=your_key")
    print()

    demo_basic()
    demo_prompt_caching()
    demo_streaming()
    demo_tool_use()
    demo_multi_turn()

    print("""
=== 本课要点回顾 ===

1. 基础调用    messages.create() → content[0].text
2. 缓存        cache_control={'type':'ephemeral'} → System Prompt 成本降 90%
3. 流式        with client.messages.stream() as s → 实时展示进度
4. 工具调用    tools=[...] → stop_reason=='tool_use' → 执行 → tool_result → 循环
5. 多轮对话    累积 messages 列表，Claude 自动理解上下文

成本优化顺序（重要性降序）：
  1. Prompt Caching（System Prompt / RAG 文档）
  2. 选合适的模型（Haiku 适合简单路由，Sonnet 适合主力推理）
  3. max_tokens 控制（避免 LLM 过度输出）
  4. 消息历史裁剪（超长对话压缩旧消息）
""")
