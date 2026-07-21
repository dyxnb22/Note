"""
第 7 课：Agent 评估 — 怎么知道你的 Agent 是否正确工作？

本课目标：
1. 理解为什么 Agent 需要专门的评估体系（不同于普通单元测试）；
2. 理解三种评估策略：规则检查、轨迹检查、LLM-as-Judge；
3. 能写出可持续维护的 Agent 测试用例。

核心洞察：
  - 函数测试：输入 → 预期输出（确定性）
  - Agent 测试：输入 → 预期"行为范围"（非确定性）
  - Agent 测试要检查的不是"结果字符串相等"，而是"是否调用了对的工具""结论是否合理"

运行：
    python 07-eval/eval_agent.py
"""

import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable


# ---------------------------------------------------------------------------
# 1. 被测 Agent（复用第 2 课的工具 Agent）
# ---------------------------------------------------------------------------
# 评估框架不关心 Agent 用了什么框架，只关心输入/输出/轨迹。

from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


@tool
def get_weather(city: str) -> str:
    """查询城市天气。支持：北京、上海、深圳。"""
    data = {"北京": "晴，25°C", "上海": "多云，22°C", "深圳": "小雨，28°C"}
    return data.get(city, f"暂无 {city} 数据")


@tool
def calculate(expression: str) -> str:
    """计算数学表达式。"""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"计算失败: {e}"


TOOLS = [get_weather, calculate]


class AgentState(TypedDict):
    messages: Annotated[list[Any], add_messages]


def planner(state: AgentState) -> dict:
    text = state["messages"][-1].content.lower()
    tool_calls = []

    if "天气" in text:
        for city in ["北京", "上海", "深圳"]:
            if city in text:
                tool_calls.append({"name": "get_weather", "args": {"city": city}, "id": f"call_{city}"})

    if any(op in text for op in ["温差", "计算", "多少度"]):
        tool_calls.append({"name": "calculate", "args": {"expression": "25 - 22"}, "id": "call_calc"})

    if not tool_calls:
        return {"messages": [AIMessage(content="这个问题我可以直接回答，不需要调用工具。")]}

    return {"messages": [AIMessage(content="", tool_calls=tool_calls)]}


def should_use_tools(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


from langgraph.prebuilt import ToolNode


def responder(state: AgentState) -> dict:
    messages = state["messages"]
    tool_results = [m for m in messages if isinstance(m, ToolMessage)]
    if not tool_results:
        return {"messages": [AIMessage(content="没有工具结果。")]}

    # 从 AIMessage 的 tool_calls 中提取调用参数，让输出包含完整上下文
    tool_call_map: dict[str, dict] = {}
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_call_map[tc["id"]] = tc

    lines = ["工具结果："]
    for r in tool_results:
        tc = tool_call_map.get(getattr(r, "tool_call_id", ""), {})
        args_str = ", ".join(f"{k}={v}" for k, v in tc.get("args", {}).items())
        lines.append(f"  {r.name}({args_str}): {r.content}")

    return {"messages": [AIMessage(content="\n".join(lines))]}


def build_agent():
    g = StateGraph(AgentState)
    g.add_node("planner", planner)
    g.add_node("tools", ToolNode(TOOLS))
    g.add_node("responder", responder)
    g.add_edge(START, "planner")
    g.add_conditional_edges("planner", should_use_tools)
    g.add_edge("tools", "responder")
    g.add_edge("responder", END)
    return g.compile()


# ---------------------------------------------------------------------------
# 2. 评估框架
# ---------------------------------------------------------------------------


@dataclass
class TestCase:
    name: str
    input: str
    checkers: list[Callable[[dict], tuple[bool, str]]]  # 每个 checker 返回 (passed, reason)
    description: str = ""


@dataclass
class EvalResult:
    case_name: str
    passed: bool
    failures: list[str] = field(default_factory=list)
    latency_ms: float = 0.0
    tool_calls_made: list[str] = field(default_factory=list)


def _extract_tool_calls(messages: list) -> list[str]:
    """从 messages 中提取所有工具调用名称（用于轨迹检查）。"""
    calls = []
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            calls.extend(tc["name"] for tc in msg.tool_calls)
    return calls


def _extract_final_text(messages: list) -> str:
    """提取最后一条 AIMessage 的文本内容。"""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            content = getattr(msg, "content", "")
            if content:
                return content
    return ""


# ---------------------------------------------------------------------------
# 3. 检查器库（Checker Functions）
# ---------------------------------------------------------------------------
# 每个 Checker 接收 run_result（包含 messages、tool_calls 等），
# 返回 (passed: bool, reason: str)。


def must_call_tool(*tool_names: str):
    """工具调用检查：确保 Agent 调用了指定工具（轨迹检查）。"""
    def checker(result: dict) -> tuple[bool, str]:
        called = result["tool_calls"]
        missing = [t for t in tool_names if t not in called]
        if missing:
            return False, f"未调用工具: {missing}，实际调用: {called}"
        return True, f"已调用: {list(tool_names)}"
    checker.__name__ = f"must_call_tool({','.join(tool_names)})"
    return checker


def must_not_call_tool(*tool_names: str):
    """工具调用检查：确保 Agent 没有调用不必要的工具。"""
    def checker(result: dict) -> tuple[bool, str]:
        called = result["tool_calls"]
        unexpected = [t for t in tool_names if t in called]
        if unexpected:
            return False, f"不应调用工具: {unexpected}"
        return True, f"未调用禁止工具"
    checker.__name__ = f"must_not_call_tool({','.join(tool_names)})"
    return checker


def output_contains(*keywords: str):
    """输出检查：最终回答包含关键词。"""
    def checker(result: dict) -> tuple[bool, str]:
        text = result["final_text"].lower()
        missing = [kw for kw in keywords if kw.lower() not in text]
        if missing:
            return False, f"输出缺少关键词: {missing}\n  实际输出: {result['final_text'][:200]}"
        return True, f"包含所有关键词: {list(keywords)}"
    checker.__name__ = f"output_contains({','.join(keywords)})"
    return checker


def output_matches_pattern(pattern: str):
    """输出检查：最终回答匹配正则表达式。"""
    def checker(result: dict) -> tuple[bool, str]:
        if re.search(pattern, result["final_text"]):
            return True, f"匹配模式: {pattern}"
        return False, f"不匹配模式: {pattern}\n  实际输出: {result['final_text'][:200]}"
    checker.__name__ = f"output_matches_pattern({pattern})"
    return checker


def latency_under(ms: int):
    """性能检查：响应时间低于阈值。"""
    def checker(result: dict) -> tuple[bool, str]:
        actual = result["latency_ms"]
        if actual <= ms:
            return True, f"延迟 {actual:.0f}ms ≤ {ms}ms"
        return False, f"延迟 {actual:.0f}ms 超过 {ms}ms"
    checker.__name__ = f"latency_under({ms}ms)"
    return checker


# ---------------------------------------------------------------------------
# 4. 评估执行器
# ---------------------------------------------------------------------------


class AgentEvaluator:
    def __init__(self, agent):
        self.agent = agent
        self.results: list[EvalResult] = []

    def run_case(self, case: TestCase) -> EvalResult:
        start = time.time()
        try:
            output = self.agent.invoke({"messages": [HumanMessage(content=case.input)]})
        except Exception as e:
            result = EvalResult(
                case_name=case.name,
                passed=False,
                failures=[f"Agent 抛出异常: {e}"],
            )
            self.results.append(result)
            return result

        latency_ms = (time.time() - start) * 1000
        tool_calls = _extract_tool_calls(output["messages"])
        final_text = _extract_final_text(output["messages"])

        run_result = {
            "messages": output["messages"],
            "tool_calls": tool_calls,
            "final_text": final_text,
            "latency_ms": latency_ms,
        }

        failures = []
        for checker in case.checkers:
            passed, reason = checker(run_result)
            if not passed:
                failures.append(f"  [{checker.__name__}] FAIL: {reason}")

        result = EvalResult(
            case_name=case.name,
            passed=len(failures) == 0,
            failures=failures,
            latency_ms=latency_ms,
            tool_calls_made=tool_calls,
        )
        self.results.append(result)
        return result

    def run_all(self, cases: list[TestCase]) -> None:
        print(f"\n{'='*60}")
        print(f"  运行 {len(cases)} 个测试用例")
        print(f"{'='*60}")

        for case in cases:
            result = self.run_case(case)
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"\n{status}  {case.name}  ({result.latency_ms:.0f}ms)")
            if case.description:
                print(f"  描述: {case.description}")
            print(f"  工具调用: {result.tool_calls_made or '无'}")
            if result.failures:
                for f in result.failures:
                    print(f)

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        print(f"\n{'='*60}")
        print(f"  结果: {passed}/{total} 通过")
        print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# 5. 测试用例定义
# ---------------------------------------------------------------------------


TEST_CASES = [
    TestCase(
        name="天气查询_北京",
        input="北京今天天气怎么样？",
        description="Agent 应调用 get_weather，回答包含温度",
        checkers=[
            must_call_tool("get_weather"),
            must_not_call_tool("calculate"),
            output_contains("北京", "25"),
            latency_under(3000),
        ],
    ),
    TestCase(
        name="多城市天气+温差",
        input="北京和上海的天气如何？温差是多少？",
        description="Agent 应调用 get_weather 两次 + calculate 一次",
        checkers=[
            must_call_tool("get_weather", "calculate"),
            output_contains("北京", "上海"),
        ],
    ),
    TestCase(
        name="不需要工具的问题",
        input="你能做什么？",
        description="不相关问题不应触发工具调用",
        checkers=[
            must_not_call_tool("get_weather", "calculate"),
        ],
    ),
    TestCase(
        name="单纯计算",
        input="计算 100 * 0.15",
        description="纯计算问题只应调用 calculate，不应查天气",
        checkers=[
            must_call_tool("calculate"),
            must_not_call_tool("get_weather"),
        ],
    ),
]


# ---------------------------------------------------------------------------
# 6. 运行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== 第 7 课：Agent 评估 ===")
    print("""
核心概念：
  - 规则检查（Rule-based）：工具调用轨迹、关键词、延迟 → 确定性，速度快
  - 轨迹检查（Trajectory）：检查 Agent 的每一步，而不只是最终输出
  - LLM-as-Judge：用另一个 LLM 评判输出质量 → 适合开放式问题
                   （本课 Mock 版暂不实现，需要 LLM Key）
""")

    agent = build_agent()
    evaluator = AgentEvaluator(agent)
    evaluator.run_all(TEST_CASES)

    print("""
下一步练习：
  1. 增加一个 search_docs 工具，写新的测试用例
  2. 故意让 Agent 行为出错（比如删掉一个工具），观察哪些测试用例失败
  3. 接入真实 LLM 后，把 must_call_tool 换成 LLM-as-Judge（问 LLM：这个回答合理吗？）
""")
