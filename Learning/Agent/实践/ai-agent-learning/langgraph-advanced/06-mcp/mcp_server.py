"""
第 6 课（上）：MCP Server — 用标准协议暴露工具

本课目标：
1. 理解 MCP（Model Context Protocol）是什么，为什么 2025 年之后成为标准；
2. 理解 MCP Server 如何用 @mcp.tool() 把 Python 函数暴露成协议工具；
3. 理解 MCP 和原生 Function Call 的核心区别。

背景：
  MCP 是 Anthropic 在 2024 年发布的开放工具协议。
  到 2025 年底，Claude、Cursor、VS Code Copilot、Gemini、OpenAI 等主流系统全面支持。
  核心思路：把工具从 Agent 代码里拆出来 → 变成独立服务 → 任意 AI 系统都能复用。

运行方式 A（有 fastmcp）：
    pip install "fastmcp>=2.0"
    python 06-mcp/mcp_server.py

运行方式 B（无依赖，默认）：
    python 06-mcp/mcp_server.py
    # 以 Mock 模式运行，演示工具实现和 MCP vs Function Call 的区别
"""

try:
    from fastmcp import FastMCP
    HAS_FASTMCP = True
except ImportError:
    HAS_FASTMCP = False


# ---------------------------------------------------------------------------
# 工具实现（与 MCP 无关，是纯业务逻辑）
# ---------------------------------------------------------------------------
# 关键洞察：工具的"实现"和工具的"注册方式"是完全分离的。
# 用原生 Function Call 时，把函数传给 LangChain @tool；
# 用 MCP 时，把函数传给 @mcp.tool()。
# 实现逻辑完全一样，只是注册到不同的协议层。

WEATHER_DATA = {
    "北京": "晴，25°C，湿度 40%",
    "上海": "多云，22°C，湿度 65%",
    "深圳": "小雨，28°C，湿度 80%",
    "杭州": "阴，20°C，湿度 70%",
    "成都": "晴，18°C，湿度 55%",
}


def _get_weather_impl(city: str) -> str:
    return WEATHER_DATA.get(city, f"暂无 {city} 的天气数据，支持：{'、'.join(WEATHER_DATA)}")


def _calculate_impl(expression: str) -> str:
    try:
        # 学习项目用 eval；生产环境换 ast.literal_eval 或 sympy
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算失败: {e}"


def _search_docs_impl(query: str) -> str:
    """模拟文档检索，后续 07 课会换成真实 RAG。"""
    knowledge = {
        "mcp": (
            "MCP (Model Context Protocol) 是 Anthropic 2024 年发布的开放工具协议。"
            "Server 用 @mcp.tool() 暴露工具，Client（任意 AI 系统）通过 JSON-RPC 调用。"
            "和原生 Function Call 的最大区别：工具跨 Agent/平台复用。"
        ),
        "langgraph": (
            "LangGraph 是基于有向图的 Agent 编排框架。"
            "核心概念：StateGraph、Node（函数）、Edge（连线）、Checkpointer（状态持久化）。"
            "2025 年之后支持原生 MCP 工具接入。"
        ),
        "rag": (
            "RAG (Retrieval-Augmented Generation) 流程："
            "文档 → 切分 → Embedding → 向量库 → 检索 top-K → 注入 LLM 上下文 → 生成回答。"
            "2026 年主流做法：混合检索（向量 + BM25）+ Re-ranking。"
        ),
        "a2a": (
            "A2A (Agent-to-Agent) 是 Google 2025 年提出的多 Agent 通信协议。"
            "和 MCP 的关系：MCP 解决 Agent↔工具，A2A 解决 Agent↔Agent。"
        ),
    }
    query_lower = query.lower()
    for key, answer in knowledge.items():
        if key in query_lower:
            return answer
    return f"未找到 '{query}' 的文档。可用关键词：{', '.join(knowledge)}"


# ---------------------------------------------------------------------------
# MCP Server 注册（需要 fastmcp）
# ---------------------------------------------------------------------------
# @mcp.tool() 的 docstring 很重要：AI 模型靠它判断何时调用这个工具。
# 参数类型注解也会被转成 JSON Schema 传给 AI 模型。

if HAS_FASTMCP:
    mcp = FastMCP("DevPilot MCP Server", version="1.0.0")

    @mcp.tool()
    def get_weather(city: str) -> str:
        """查询城市实时天气。支持：北京、上海、深圳、杭州、成都。"""
        return _get_weather_impl(city)

    @mcp.tool()
    def calculate(expression: str) -> str:
        """计算数学表达式，例如 '(100 + 200) * 0.15'。返回计算结果字符串。"""
        return _calculate_impl(expression)

    @mcp.tool()
    def search_docs(query: str) -> str:
        """搜索 AI Agent 技术文档。支持关键词：mcp、langgraph、rag、a2a。"""
        return _search_docs_impl(query)


# ---------------------------------------------------------------------------
# Mock 演示（无依赖，直接可运行）
# ---------------------------------------------------------------------------


def _print_comparison():
    print("""
╔══════════════════════════════════════════════════════════════╗
║         MCP Server vs 原生 Function Call 对比               ║
╠══════════════════════════════════════════════════════════════╣
║  维度            原生 Function Call    MCP Server            ║
║  ─────────────   ──────────────────    ──────────────────    ║
║  工具定义位置    在 Agent 代码里        独立进程/服务         ║
║  复用性          只有本 Agent 能用      任意 AI 系统能连      ║
║  支持系统        绑定特定 SDK           Claude/Cursor/GPT/…   ║
║  协议            各厂商私有             开放 JSON-RPC         ║
║  适用场景        简单内部工具           需要跨系统共享的工具  ║
╚══════════════════════════════════════════════════════════════╝

结论：
  - 内部工具、只给自己的 Agent 用 → 原生 Function Call（更简单）
  - 需要在 Cursor/VS Code/多个 Agent 之间共享 → MCP Server
""")


def demo_mock():
    print("=== 第 6 课：MCP Server（Mock 模式）===")
    print("[注意] fastmcp 未安装，以 Mock 模式演示工具实现")
    print("       安装真实 MCP：pip install 'fastmcp>=2.0'")
    print()

    cases = [
        ("get_weather", {"city": "上海"}, _get_weather_impl("上海")),
        ("calculate", {"expression": "(100 + 200) * 0.15"}, _calculate_impl("(100 + 200) * 0.15")),
        ("search_docs", {"query": "什么是 mcp"}, _search_docs_impl("什么是 mcp")),
    ]

    for tool_name, args, result in cases:
        print(f"工具: {tool_name}")
        for k, v in args.items():
            print(f"  {k} = '{v}'")
        print(f"  → {result[:120]}")
        print()

    _print_comparison()


if __name__ == "__main__":
    if HAS_FASTMCP:
        print("启动 MCP Server（stdio 模式）...")
        print("在另一个终端运行：python 06-mcp/mcp_client.py")
        mcp.run()
    else:
        demo_mock()
