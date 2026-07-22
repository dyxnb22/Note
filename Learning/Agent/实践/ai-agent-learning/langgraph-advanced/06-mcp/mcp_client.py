"""
第 6 课（下）：MCP Client — LangGraph 连接 MCP Server

本课目标：
1. 理解 LangGraph Agent 如何通过 MCP 协议调用外部工具；
2. 理解 MultiServerMCPClient 的职责（工具发现 + 调用代理）；
3. 理解"把 MCP 工具当 LangChain Tool 用"的适配层原理。

运行方式 A（完整 MCP 模式，需要安装依赖 + API Key）：
    pip install "fastmcp>=2.0" "langchain-mcp-adapters>=0.1" "langchain-anthropic>=0.3"
    # 另一个终端启动 Server：python 06-mcp/mcp_server.py
    python 06-mcp/mcp_client.py

运行方式 B（Mock 模式，默认，无需任何依赖或 Key）：
    python 06-mcp/mcp_client.py
"""

import asyncio
import os
import sys

# 确保能找到 mcp_server 里的工具实现（Mock 模式复用）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    HAS_MCP_ADAPTERS = True
except ImportError:
    HAS_MCP_ADAPTERS = False

try:
    from langchain_anthropic import ChatAnthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    from langchain_openai import ChatOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# ---------------------------------------------------------------------------
# 工具调用 Mock（复用 mcp_server 里的实现）
# ---------------------------------------------------------------------------

from mcp_server import _get_weather_impl, _calculate_impl, _search_docs_impl

MOCK_TOOLS = {
    "get_weather": _get_weather_impl,
    "calculate": _calculate_impl,
    "search_docs": _search_docs_impl,
}


# ---------------------------------------------------------------------------
# 真实 MCP Client（需要 langchain-mcp-adapters + LLM）
# ---------------------------------------------------------------------------


async def run_with_real_mcp(server_script: str, user_query: str):
    """使用真实 MCP 协议连接 Server，再用 LangGraph ReAct Agent 处理请求。"""
    from langgraph.prebuilt import create_react_agent

    llm = _get_llm()
    if not llm:
        print("[跳过] 未找到 LLM API Key，退出到 Mock 模式")
        return False

    async with MultiServerMCPClient(
        {
            "devpilot": {
                "command": "python",
                "args": [server_script],
                "transport": "stdio",
            }
        }
    ) as client:
        tools = client.get_tools()
        print(f"[MCP] 发现 {len(tools)} 个工具: {[t.name for t in tools]}")

        agent = create_react_agent(llm, tools)
        result = await agent.ainvoke({"messages": [{"role": "user", "content": user_query}]})

        print("\n[Agent 回答]")
        for msg in result["messages"]:
            content = getattr(msg, "content", "")
            if content and getattr(msg, "type", "") == "ai":
                print(content)
        return True


def _get_llm():
    """优先 Anthropic → OpenAI → DeepSeek，全部没有则返回 None。"""
    from dotenv import load_dotenv
    load_dotenv()

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")

    if anthropic_key and HAS_ANTHROPIC:
        return ChatAnthropic(model="claude-sonnet-4-6", max_tokens=1024)
    if openai_key and HAS_OPENAI:
        return ChatOpenAI(model=os.environ["OPENAI_MODEL"], max_tokens=1024)
    if deepseek_key and HAS_OPENAI:
        return ChatOpenAI(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            api_key=deepseek_key,
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            max_tokens=1024,
        )
    return None


# ---------------------------------------------------------------------------
# Mock Agent Loop（无依赖，展示 MCP Client 的调用流程）
# ---------------------------------------------------------------------------


def mock_agent_loop(user_query: str):
    """
    模拟 MCP Client 的工作流程：
      1. 从 Server 获取可用工具列表（这里直接读 MOCK_TOOLS）
      2. 根据请求决定调用哪些工具（这里用关键词规则模拟 LLM 决策）
      3. 调用工具，把结果传给 LLM（这里直接打印）
      4. LLM 综合结果生成最终回答
    """
    print(f"\n[用户] {user_query}")
    print(f"[MCP Client] 已发现工具：{list(MOCK_TOOLS.keys())}")

    # 模拟 LLM 工具调用决策
    calls = []
    query_lower = user_query.lower()

    if "天气" in query_lower:
        for city in ["北京", "上海", "深圳", "杭州", "成都"]:
            if city in user_query:
                calls.append(("get_weather", {"city": city}))

    if any(op in query_lower for op in ["计算", "+", "-", "*", "/", "温差", "多少度"]):
        calls.append(("calculate", {"expression": "25 - 22"}))

    if any(kw in query_lower for kw in ["mcp", "langgraph", "rag", "a2a", "什么是", "介绍"]):
        for kw in ["mcp", "langgraph", "rag", "a2a"]:
            if kw in query_lower:
                calls.append(("search_docs", {"query": kw}))
                break

    if not calls:
        calls.append(("search_docs", {"query": user_query[:20]}))

    # 执行工具调用
    results = []
    for tool_name, args in calls:
        fn = MOCK_TOOLS[tool_name]
        result = fn(**args)
        print(f"[工具调用] {tool_name}({args}) → {result[:80]}")
        results.append(f"{tool_name}: {result}")

    # 模拟 LLM 综合结果
    print("\n[Agent 回答（Mock）]")
    print("根据工具调用结果：")
    for r in results:
        print(f"  - {r[:100]}")


def _print_mcp_architecture():
    print("""
╔═══════════════════════════════════════════════════════╗
║              MCP Client 架构                          ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  用户请求                                             ║
║     ↓                                                 ║
║  LangGraph Agent                                      ║
║     ↓ (发现工具)                                      ║
║  MultiServerMCPClient  ←→  MCP Server 1 (天气)        ║
║                        ←→  MCP Server 2 (数据库)      ║
║                        ←→  MCP Server 3 (GitHub)     ║
║     ↓ (工具调用结果)                                  ║
║  LLM 综合生成最终回答                                 ║
║                                                       ║
║  关键点：一个 Client 可以同时连多个 Server            ║
╚═══════════════════════════════════════════════════════╝
""")


def main():
    print("=== 第 6 课（下）：MCP Client ===")

    _print_mcp_architecture()

    test_queries = [
        "北京和上海今天天气如何？温差是多少？",
        "介绍一下 MCP 协议",
        "什么是 RAG？",
    ]

    if HAS_MCP_ADAPTERS and _get_llm():
        print("[模式] 检测到 MCP 依赖 + LLM Key，尝试真实 MCP 模式")
        server_path = os.path.join(os.path.dirname(__file__), "mcp_server.py")
        for query in test_queries[:1]:
            asyncio.run(run_with_real_mcp(server_path, query))
    else:
        if not HAS_MCP_ADAPTERS:
            print("[模式] Mock（未安装 langchain-mcp-adapters）")
        else:
            print("[模式] Mock（未配置 LLM API Key）")
        print("安装完整依赖：pip install 'fastmcp>=2.0' 'langchain-mcp-adapters>=0.1' 'langchain-anthropic>=0.3'")
        print()

        for query in test_queries:
            mock_agent_loop(query)
            print()


if __name__ == "__main__":
    main()
