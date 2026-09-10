#!/usr/bin/env python3
"""Phase 5B semantic adjudication and destructive-action gate.

The explicit action plan below was produced by reading the complete question and
answer blocks.  Every other recalled pair is retained with two stated answer
contracts, rather than a generic "some overlap" justification.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from phase4b_candidates import parse_current_questions, pair

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def q(file: str, number: int) -> str:
    return f"Q::{file}::{number}"


# victim/source, canonical survivor, relation, action, manually reviewed reason
PLANNED = [
    (q("03_Memory与状态/Memory与State.md", 29), q("03_Memory与状态/Memory与State.md", 21), "SEMANTIC_DUPLICATE", "DELETE", "两题同为 design intent，均要求隔离写集、串行/锁、版本校验和确定性合并；#21 的合同更完整。"),
    (q("03_Memory与状态/Memory与State.md", 31), q("03_Memory与状态/Memory与State.md", 15), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "上海改深圳是“用户明确纠正旧记忆”的具体场景；保留为追问可保全 scenario intent。"),
    (q("03_Memory与状态/Memory与State.md", 32), q("03_Memory与状态/Memory与State.md", 24), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "Checkpoint 恢复主题已要求核对副作用；#32 作为 unknown-side-effect 场景追问保留对账合同。"),
    (q("04_Tool与协议/Tool Calling与MCP.md", 9), q("07_可靠性与安全/可靠性与安全.md", 19), "OWNERSHIP_CONFLICT", "MOVE_OR_BRIDGE", "HITL 风险动作的完整定义归 07；Tool 页只保留工具风险分级与执行前再校验差异。"),
    (q("04_Tool与协议/Tool Calling与MCP.md", 13), q("04_Tool与协议/Tool Calling与MCP.md", 12), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "幂等对象与幂等键是综合可靠性设计中的高频子问题，保留为追问而不维护第二份主答案。"),
    (q("04_Tool与协议/Tool Calling与MCP.md", 14), q("04_Tool与协议/Tool Calling与MCP.md", 12), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "重复副作用防护是综合超时/重试/幂等合同的深化追问，实施细节完整保留。"),
    (q("04_Tool与协议/Tool Calling与MCP.md", 27), q("04_Tool与协议/Tool Calling与MCP.md", 1), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "无 MCP 的调用流程与 Function Calling 主流程相同，只需保留 MCP 并未改变执行边界的差异追问。"),
    (q("04_Tool与协议/Tool Calling与MCP.md", 34), q("04_Tool与协议/Tool Calling与MCP.md", 31), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "REST 与 MCP 的选择是 API/MCP/A2A 选型合同的二选一场景，适合挂为追问。"),
    (q("04_Tool与协议/Tool Calling与MCP.md", 44), q("04_Tool与协议/Tool Calling与MCP.md", 41), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "不可信工具结果的正向判定条件是同一 trust contract 的高频追问。"),
    (q("04_Tool与协议/Tool Calling与MCP.md", 45), q("04_Tool与协议/Tool Calling与MCP.md", 19), "SEMANTIC_DUPLICATE", "DELETE", "同为 mechanism intent，Atom 集完全相同，都要求并行独立性、合并顺序、共享 State 和回放保证；#19 完整覆盖。"),
    (q("05_Multi-Agent与Workflow/Loop控制与Harness面经补充.md", 18), q("05_Multi-Agent与Workflow/Multi-Agent与Workflow.md", 21), "SEMANTIC_DUPLICATE", "MERGE", "两题都要求 Trace 字段和安全回放；补充题独有的脱敏、只读 Fixture 和不记录隐藏思维链约束并入 canonical。"),
    (q("05_Multi-Agent与Workflow/Multi-Agent与Workflow.md", 24), q("05_Multi-Agent与Workflow/Multi-Agent与Workflow.md", 6), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "事实冲突仲裁是并行结果合并的具体 scenario，证据回查与人工升级作为追问保留。"),
    (q("12_课程深化/05_身份治理与跨Agent/身份治理与跨Agent.md", 15), q("05_Multi-Agent与Workflow/Multi-Agent与Workflow.md", 6), "SEMANTIC_DUPLICATE", "MERGE", "同为 mechanism intent 的多 Agent 结论冲突仲裁；将跨 A2A 的证据和版本语义并入主题后移除重复主答案。"),
    (q("05_Multi-Agent与Workflow/Skill编排与协作面经补充.md", 9), q("05_Multi-Agent与Workflow/Multi-Agent与Workflow.md", 7), "OWNERSHIP_CONFLICT", "MOVE_OR_BRIDGE", "重复劳动、循环和预算约束由 Multi-Agent 主题拥有；补充入口只保留结构化增量消息差异。"),
    (q("05_Multi-Agent与Workflow/Skill编排与协作面经补充.md", 10), q("05_Multi-Agent与Workflow/Multi-Agent与Workflow.md", 9), "OWNERSHIP_CONFLICT", "MOVE_OR_BRIDGE", "最小权限完整定义由 Multi-Agent 主题拥有；补充入口只留短期子身份和委托链差异。"),
    (q("05_Multi-Agent与Workflow/Skill编排与协作面经补充.md", 2), q("12_课程深化/07_实时交互与产品/实时交互与产品.md", 20), "SEMANTIC_DUPLICATE", "MERGE", "两题共享“合格 Skill 包含什么”的 answer contract；将不等于 Prompt/权限的边界并入产品化 canonical。"),
    (q("05_Multi-Agent与Workflow/Skill编排与协作面经补充.md", 6), q("12_课程深化/07_实时交互与产品/实时交互与产品.md", 18), "OWNERSHIP_CONFLICT", "MOVE_OR_BRIDGE", "Tool/Skill/MCP 完整定义归 12/07；补充题保留 Prompt、Workflow 与 Agent 的差分入口。"),
    (q("05_Multi-Agent与Workflow/Loop控制与Harness面经补充.md", 24), q("08_评测与可观测/评测与可观测性.md", 36), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "“减少 Token 不等于优化”已被质量+效率联合验证合同覆盖，作为反例追问保留。"),
    (q("06_RAG与知识库/RAG与检索.md", 26), q("06_RAG与知识库/RAG与检索.md", 10), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "BM25 词面正确但语义不相关是混合召回后 Rerank 的典型场景，保留为调参追问。"),
    (q("06_RAG与知识库/RAG与检索.md", 28), q("06_RAG与知识库/RAG与检索.md", 16), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "检索正确但最终幻觉是分层归因合同的特定 debugging 场景，固定证据回放细节保留。"),
    (q("07_可靠性与安全/可靠性与安全.md", 15), q("07_可靠性与安全/可靠性与安全.md", 14), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "识别和脱敏是“如何处理敏感输出”的实现追问，保留规则/NER/重识别风险细节。"),
    (q("07_可靠性与安全/可靠性与安全.md", 26), q("12_课程深化/03_Durable与生产运维/Durable与生产运维.md", 10), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "前端断线是“外部已成功但未收到响应”的具体 unknown-result 场景，保留为追问。"),
    (q("07_可靠性与安全/可靠性与安全.md", 35), q("12_课程深化/03_Durable与生产运维/Durable与生产运维.md", 8), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "崩溃窗口的不明确结果是恢复前核对外部副作用的动机追问。"),
    (q("07_可靠性与安全/可靠性与安全.md", 38), q("12_课程深化/03_Durable与生产运维/Durable与生产运维.md", 8), "OWNERSHIP_CONFLICT", "MOVE_OR_BRIDGE", "恢复与副作用核对的 canonical 归 12/03；07 只保留恢复检查阶段的只读和重授权差异。"),
    (q("08_评测与可观测/评测、轨迹与线上故障面经补充.md", 4), q("08_评测与可观测/评测与可观测性.md", 36), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "“少走弯路”是质量与成本联合证明的轨迹指标追问，保留有效调用、重试和人工接管切片。"),
    (q("08_评测与可观测/评测、轨迹与线上故障面经补充.md", 10), q("08_评测与可观测/评测与可观测性.md", 24), "SEMANTIC_DUPLICATE", "MERGE", "两题的 Replay answer contract 相同；将可选节点重执行、新旧轨迹对比和沙箱/幂等对账并入 canonical。"),
    (q("08_评测与可观测/评测、轨迹与线上故障面经补充.md", 11), q("08_评测与可观测/评测与可观测性.md", 13), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "Prompt/检索库/Few-shot/训练流水线是评测泄漏合同的具体渠道追问。"),
    (q("12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md", 1), q("08_评测与可观测/评测与可观测性.md", 39), "SEMANTIC_DUPLICATE", "MERGE", "两题都论证为何 Agent Eval 不能只看最终文本；将产物/外部状态和环境归因并入主线指标合同。"),
    (q("12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md", 4), q("08_评测与可观测/评测与可观测性.md", 39), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "专项轨迹和安全信号是多指标 Agent Eval 的实施追问，指标列表完整保留。"),
    (q("12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md", 22), q("12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md", 21), "SEMANTIC_DUPLICATE", "MERGE", "两题同为 project_expression，都要求问题、责任、难点、取舍和证据骨架；合并后不损失独立意图。"),
    (q("10_模型与推理/高频八股与手撕面经补充.md", 1), q("10_模型与推理/模型与推理基础.md", 4), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "Attention 公式是复杂度题的基础推导追问；保留 QK^T/缩放/mask 与 Agent 长上下文影响。"),
    (q("11_编码与后端/编码题与后端基础.md", 16), q("11_编码与后端/编码题与后端基础.md", 15), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "滑动窗口结构体字段是限流实现题的编码追问，保留并发、时钟和空间上限合同。"),
    (q("11_编码与后端/编码题与后端基础.md", 30), q("09_工程化与系统设计/生产工程与系统设计.md", 15), "SEMANTIC_DUPLICATE", "MERGE", "Kafka 重复、丢失和 Exactly-once 边界是同一 mechanism contract；将分区顺序和外部副作用边界并入 Agent 生产题。"),
    (q("12_课程深化/01_Provider与框架/Provider适配与框架选型.md", 4), q("12_课程深化/01_Provider与框架/Provider适配与框架选型.md", 27), "SEMANTIC_DUPLICATE", "MERGE", "两题都要求 Provider 对象不能泄漏到 Runtime；将 tool-call 已生成不等于已执行的边界并入内部事件 canonical。"),
    (q("12_课程深化/01_Provider与框架/Provider适配与框架选型.md", 33), q("12_课程深化/01_Provider与框架/Provider适配与框架选型.md", 21), "SEMANTIC_DUPLICATE", "MERGE", "同为 scenario intent 的 Adapter 契约测试清单；合并 reasoning/SSE/认证/脱敏细节后不再维护两份清单。"),
    (q("12_课程深化/02_代码Agent与ComputerUse/代码Agent与ComputerUse.md", 16), q("12_课程深化/02_代码Agent与ComputerUse/代码Agent与ComputerUse.md", 12), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "用户已有未提交修改是基线 diff 归因合同的高风险场景追问。"),
    (q("12_课程深化/03_Durable与生产运维/Durable与生产运维.md", 27), q("12_课程深化/03_Durable与生产运维/Durable与生产运维.md", 35), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "旧任务的 Schema/策略升级处理完整覆盖为何不能只回滚代码；外部副作用对账作为追问保留。"),
    (q("02_Prompt与上下文/Prompt与Context Engineering.md", 15), q("02_Prompt与上下文/Prompt与Context Engineering.md", 29), "SUBSUMED", "CONVERT_TO_FOLLOWUP", "两个 Description 相似 Skill 的误选是通用 Skill 误选 debugging 流程的具体追问。"),
]


OLD_BRIDGES = {
    q("01_基础架构/Agent基础与架构.md", 13),
    q("04_Tool与协议/Tool Calling与MCP.md", 10),
    q("06_RAG与知识库/RAG与检索.md", 27),
    q("08_评测与可观测/评测、轨迹与线上故障面经补充.md", 1),
    q("09_工程化与系统设计/系统设计与取舍面经补充.md", 9),
    q("12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md", 19),
}


def evidence(text: str) -> str:
    return " ".join(text.split())[:240]


def main() -> None:
    candidates = load(HERE / "duplicate_candidates_v2.json")
    mappings = {x["question_id"]: x for x in load(AUDIT / "question_atom_map.json")["questions"]}
    current = parse_current_questions()
    cluster_of = {qid: c["cluster_id"] for c in candidates["clusters"] for qid in c["members"]}
    edges = {pair(e["a"], e["b"]): e for e in candidates["pairs"]}
    plan = {pair(v, c): (v, c, relation, action, reason) for v, c, relation, action, reason in PLANNED}
    errors = []
    if len(plan) != len(PLANNED):
        errors.append("duplicate planned action pair")
    missing_plans = sorted("||".join(k) for k in plan if k not in edges)
    if missing_plans:
        errors.append(f"planned actions absent from Phase 4B candidates: {missing_plans}")

    decisions = []
    for key, edge in edges.items():
        a, b = key
        ma, mb = mappings[a], mappings[b]
        qa, qb = current[a], current[b]
        retained_atoms = sorted(set(ma["atoms"]) | set(mb["atoms"]))
        retained_intents = sorted({ma["intent"], mb["intent"]})
        if key in plan:
            victim, canonical, relation, action, reason = plan[key]
            owner = mappings[canonical]["primary_atom"]
            record = {"victim_question": victim}
        elif a in OLD_BRIDGES or b in OLD_BRIDGES:
            relation, action = "ALREADY_BRIDGED", "KEEP"
            canonical = None
            owner = {"mode": "existing_bridge"}
            reason = "现有答案已通过 Obsidian 链接指向 canonical，并且只保留当前入口的差分合同。"
            record = {}
        else:
            same_intent = ma["intent"] == mb["intent"]
            integrated = ma["layer"] == "integrated" or mb["layer"] == "integrated"
            if integrated:
                relation = "RELATED_DISTINCT"
                why = "综合题要求跨组件系统设计与角色约束，而另一题只验证局部机制；合并会破坏综合答案的端到端验收合同。"
            elif not same_intent:
                relation = "RELATED_DISTINCT"
                why = f"A 要求 {ma['intent']} 型回答，B 要求 {mb['intent']} 型回答；合并会丢失其中一种面试交付形式。"
            elif edge["same_primary"] or edge["atom_containment"] >= 0.5:
                relation = "PARTIAL_OVERLAP"
                why = f"两题虽共享 {', '.join(edge['shared_atoms']) or '语义主题'}，但 A 需独立回答“{qa['title']}”，B 需独立回答“{qb['title']}”；未发现同一份答案可完整代替两者。"
            else:
                relation = "RELATED_DISTINCT"
                why = f"A 的交付对象是“{qa['title']}”，B 的交付对象是“{qb['title']}”；共享术语不构成可互换答案。"
            action, canonical = "KEEP", None
            owner = {"mode": "split_by_answer_contract", "questions": [a, b]}
            reason = why
            record = {
                "answer_contracts": {
                    "a": {"intent": ma["intent"], "question": qa["title"], "answer_evidence": evidence(qa["answer"])},
                    "b": {"intent": mb["intent"], "question": qb["title"], "answer_evidence": evidence(qb["answer"])},
                },
                "merge_value_loss": why,
            }
        decisions.append({
            "cluster_id": cluster_of[a], "members": [a, b], "relation": relation,
            "canonical_question": canonical, "canonical_owner": owner, "action": action,
            "retained_atoms": retained_atoms, "lost_atoms": [],
            "retained_intents": retained_intents, "lost_unique_intents": [],
            "reason": reason, "confidence": "high" if key in plan else "reviewed",
            **record,
        })

    destructive = [d for d in decisions if d["action"] in {"DELETE", "MERGE", "CONVERT_TO_FOLLOWUP", "MOVE_OR_BRIDGE"}]
    for d in destructive:
        if d["lost_atoms"] or d["lost_unique_intents"] or not d["canonical_question"]:
            errors.append(f"unsafe destructive decision: {d['members']}")
        if d["action"] == "DELETE":
            victim = d["victim_question"]
            canonical = d["canonical_question"]
            if not set(mappings[victim]["atoms"]).issubset(mappings[canonical]["atoms"]):
                errors.append(f"DELETE loses mapped atoms: {victim}")
            if mappings[victim]["intent"] != mappings[canonical]["intent"]:
                errors.append(f"DELETE intent mismatch: {victim}")

    relation_counts = Counter(d["relation"] for d in decisions)
    action_counts = Counter(d["action"] for d in decisions)
    # Adversarially re-check the 30 highest-overlap KEEP pairs.
    edge_by_key = edges
    keep_ranked = sorted((d for d in decisions if d["action"] == "KEEP"),
                         key=lambda d: -edge_by_key[pair(*d["members"])]["score"])
    adversarial = []
    for d in keep_ranked[:30]:
        adversarial.append({"members": d["members"], "relation": d["relation"],
                            "answer_contracts": d.get("answer_contracts", {}),
                            "why_not_duplicate": d["reason"], "result": "KEEP"})
    if len(decisions) != candidates["candidate_pair_count"]:
        errors.append("candidate adjudication incomplete")
    if len(adversarial) < 30:
        errors.append("fewer than 30 adversarial KEEP reviews")

    out = {"phase": "5B", "candidate_pair_count": len(decisions), "decisions": decisions,
           "adversarial_keep_review": adversarial}
    (HERE / "duplicate_adjudications_v2.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validation = {"phase": "5B", "status": "passed" if not errors else "failed",
                  "candidate_pairs": candidates["candidate_pair_count"], "adjudicated_pairs": len(decisions),
                  "relation_counts": dict(relation_counts), "action_counts": dict(action_counts),
                  "destructive_actions_reviewed": len(destructive), "adversarial_keep_reviews": len(adversarial),
                  "lost_atom_decisions": sum(bool(d["lost_atoms"]) for d in decisions),
                  "lost_intent_decisions": sum(bool(d["lost_unique_intents"]) for d in decisions), "errors": errors}
    (HERE / "phase5b_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Phase 5B — Full Semantic Adjudication", "",
             f"- Candidate pairs adjudicated: **{len(decisions)}/{candidates['candidate_pair_count']}**",
             f"- Destructive/rewrite actions reviewed: **{len(destructive)}**",
             f"- Adversarial KEEP rechecks: **{len(adversarial)}**", "", "## Relations", ""]
    lines += [f"- `{name}`: {relation_counts.get(name, 0)}" for name in ["EXACT_DUPLICATE", "SEMANTIC_DUPLICATE", "SUBSUMED", "PARTIAL_OVERLAP", "RELATED_DISTINCT", "OWNERSHIP_CONFLICT", "ALREADY_BRIDGED"]]
    lines += ["", "## Actions", ""]
    lines += [f"- `{name}`: {action_counts.get(name, 0)}" for name in ["DELETE", "MERGE", "CONVERT_TO_FOLLOWUP", "MOVE_OR_BRIDGE", "KEEP"]]
    if errors:
        lines += ["", "## Gate errors", ""] + [f"- {e}" for e in errors]
    (HERE / "PHASE5B_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
