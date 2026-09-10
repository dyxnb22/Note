#!/usr/bin/env python3
"""High-recall duplicate candidate generation for Hard Dedup v2.

Similarity signals only admit pairs for review.  They never choose a destructive
action.  The frozen Phase 1 inventory and Phase 3 atom map remain untouched.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent
KB = AUDIT.parent


def load(name: str):
    return json.loads((AUDIT / name).read_text(encoding="utf-8"))


def pair(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def kind(file: str) -> str:
    if file.startswith("13_"):
        return "integrated"
    if file.startswith("12_"):
        return "deepening"
    if "补充" in file:
        return "supplement"
    return "core"


def domain(file: str) -> str:
    if file.startswith("12_"):
        bits = file.split("/")
        return "/".join(bits[:2])
    return file.split("/", 1)[0]


CORRIDORS = [
    {"01", "05"}, {"02", "10", "12/06"}, {"03", "09", "12/03"},
    {"04", "05", "07", "12/05", "12/07"}, {"06", "12/04"},
    {"08", "12/08"}, {"11", "12/02"},
]


def owner_code(file: str) -> str:
    m = re.match(r"(\d\d)_", file)
    if not m:
        return ""
    top = m.group(1)
    if top == "12":
        m2 = re.search(r"/([0-9]{2})_", file)
        return f"12/{m2.group(1)}" if m2 else "12"
    return top


def in_corridor(a: str, b: str) -> bool:
    oa, ob = owner_code(a), owner_code(b)
    return any(oa in c and ob in c for c in CORRIDORS)


def parse_current_questions() -> dict[str, dict]:
    """Read full current question/answer blocks, independent of stale line numbers."""
    out = {}
    heading = re.compile(r"(?m)^###\s+(\d+)\.\s+([^\n]+)$")
    any_heading = re.compile(r"(?m)^(#{1,3})\s+[^\n]+$")
    for path in sorted(KB.rglob("*.md")):
        if AUDIT in path.parents or path.name == "README.md" or path.relative_to(KB).as_posix().startswith("00_"):
            continue
        rel = path.relative_to(KB).as_posix()
        text = path.read_text(encoding="utf-8")
        heads = list(any_heading.finditer(text))
        for match in heading.finditer(text):
            end = len(text)
            for nxt in heads:
                if nxt.start() > match.start() and len(nxt.group(1)) <= 3:
                    end = nxt.start()
                    break
            qid = f"Q::{rel}::{int(match.group(1))}"
            out[qid] = {
                "question_id": qid,
                "file": rel,
                "number": int(match.group(1)),
                "title": match.group(2).strip(),
                "answer": text[match.end():end].strip(),
            }
    return out


def normalize(text: str) -> str:
    text = re.sub(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), text)
    text = re.sub(r"[`*_>#|\[\](){}【】（）“”'\"]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def tokens(text: str) -> Counter:
    text = normalize(text)
    latin = re.findall(r"[a-z][a-z0-9_./+-]{1,}", text)
    han_runs = re.findall(r"[\u4e00-\u9fff]+", text)
    grams = []
    for run in han_runs:
        grams.extend(run[i:i + 2] for i in range(len(run) - 1))
    return Counter(latin + grams)


def vectors(rows: list[dict], field: str) -> list[dict[str, float]]:
    counts = [tokens(q[field]) for q in rows]
    df = Counter(t for c in counts for t in c)
    n = len(rows)
    result = []
    for counts_i in counts:
        vec = {t: (1 + math.log(c)) * (math.log((n + 1) / (df[t] + 1)) + 1) for t, c in counts_i.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1
        result.append({t: v / norm for t, v in vec.items()})
    return result


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(k, 0.0) for k, v in a.items())


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


SEEDS = {
    "state_concurrent_write": [("Q::03_Memory与状态/Memory与State.md::21", "Q::03_Memory与状态/Memory与State.md::29")],
    "memory_correction_conflict": [
        ("Q::03_Memory与状态/Memory与State.md::15", "Q::03_Memory与状态/Memory与State.md::31"),
        ("Q::03_Memory与状态/Memory与State.md::16", "Q::03_Memory与状态/Memory与State.md::31"),
    ],
    "checkpoint_unknown_effect": [("Q::03_Memory与状态/Memory与State.md::24", "Q::03_Memory与状态/Memory与State.md::32")],
    "tool_retry_idempotency": [
        ("Q::04_Tool与协议/Tool Calling与MCP.md::12", "Q::04_Tool与协议/Tool Calling与MCP.md::13"),
        ("Q::04_Tool与协议/Tool Calling与MCP.md::12", "Q::04_Tool与协议/Tool Calling与MCP.md::14"),
        ("Q::04_Tool与协议/Tool Calling与MCP.md::13", "Q::04_Tool与协议/Tool Calling与MCP.md::14"),
    ],
    "api_mcp_a2a": [("Q::04_Tool与协议/Tool Calling与MCP.md::31", "Q::04_Tool与协议/Tool Calling与MCP.md::34")],
    "tool_result_trust": [("Q::04_Tool与协议/Tool Calling与MCP.md::41", "Q::04_Tool与协议/Tool Calling与MCP.md::44")],
    "multi_agent_arbitration": [("Q::05_Multi-Agent与Workflow/Multi-Agent与Workflow.md::24", "Q::12_课程深化/05_身份治理与跨Agent/身份治理与跨Agent.md::15")],
    "trace_replay_harness": [
        ("Q::05_Multi-Agent与Workflow/Loop控制与Harness面经补充.md::18", "Q::08_评测与可观测/评测、轨迹与线上故障面经补充.md::10"),
        ("Q::08_评测与可观测/评测与可观测性.md::24", "Q::12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md::3"),
    ],
    "skill_productization": [
        ("Q::05_Multi-Agent与Workflow/Skill编排与协作面经补充.md::2", "Q::12_课程深化/07_实时交互与产品/实时交互与产品.md::20"),
        ("Q::05_Multi-Agent与Workflow/Skill编排与协作面经补充.md::6", "Q::12_课程深化/07_实时交互与产品/实时交互与产品.md::18"),
    ],
    "unknown_effect_recovery": [
        ("Q::07_可靠性与安全/可靠性与安全.md::26", "Q::12_课程深化/03_Durable与生产运维/Durable与生产运维.md::8"),
        ("Q::07_可靠性与安全/可靠性与安全.md::35", "Q::12_课程深化/03_Durable与生产运维/Durable与生产运维.md::8"),
    ],
    "eval_metrics_harness": [
        ("Q::08_评测与可观测/评测与可观测性.md::39", "Q::12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md::1"),
        ("Q::08_评测与可观测/评测与可观测性.md::39", "Q::12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md::4"),
    ],
    "production_durable_overview": [("Q::09_工程化与系统设计/生产工程与系统设计.md::5", "Q::12_课程深化/03_Durable与生产运维/Durable与生产运维.md::28")],
    # Added after the first Phase 5B full-answer pass exposed gaps that Atom
    # overlap and corpus-wide TF-IDF alone could not recover.
    "semantic_audit_expansion": [
        ("Q::05_Multi-Agent与Workflow/Loop控制与Harness面经补充.md::24", "Q::08_评测与可观测/评测与可观测性.md::36"),
        ("Q::07_可靠性与安全/可靠性与安全.md::38", "Q::12_课程深化/03_Durable与生产运维/Durable与生产运维.md::8"),
        ("Q::09_工程化与系统设计/生产工程与系统设计.md::15", "Q::11_编码与后端/编码题与后端基础.md::30"),
    ],
}


def main() -> None:
    inventory = {q["question_id"]: q for q in load("question_inventory.json")}
    mapped = {q["question_id"]: q for q in load("question_atom_map.json")["questions"]}
    current = parse_current_questions()
    errors = []
    if set(inventory) != set(mapped) or set(inventory) != set(current):
        errors.append("inventory/map/current question sets differ before candidate generation")

    rows = []
    for qid in sorted(inventory):
        q = current[qid]
        m = mapped[qid]
        rows.append({**q, "atoms": set(m["atoms"]), "primary_atom": m["primary_atom"],
                     "intent": m["intent"], "layer": m["layer"], "kind": kind(q["file"])})
    title_vecs, answer_vecs = vectors(rows, "title"), vectors(rows, "answer")
    seed_keys = {pair(a, b) for pairs in SEEDS.values() for a, b in pairs}
    valid = set(current)
    invalid_seed_qids = sorted({q for p in seed_keys for q in p if q not in valid})
    if invalid_seed_qids:
        errors.append(f"invalid seed QIDs: {invalid_seed_qids}")

    edges = []
    for i, a in enumerate(rows):
        for j in range(i + 1, len(rows)):
            b = rows[j]
            key = pair(a["question_id"], b["question_id"])
            inter = a["atoms"] & b["atoms"]
            union = a["atoms"] | b["atoms"]
            jac = len(inter) / len(union) if union else 0
            contain = len(inter) / min(len(a["atoms"]), len(b["atoms"])) if inter else 0
            same_primary = a["primary_atom"] == b["primary_atom"]
            same_domain = domain(a["file"]) == domain(b["file"])
            corridor = in_corridor(a["file"], b["file"])
            cross_layer = a["kind"] != b["kind"]
            ts = title_similarity(a["title"], b["title"])
            tv = cosine(title_vecs[i], title_vecs[j])
            av = cosine(answer_vecs[i], answer_vecs[j])
            sources = []
            if key in seed_keys:
                sources.append("known_regression_seed")
            if same_primary:
                sources.append("same_primary_atom")
            if a["atoms"] == b["atoms"]:
                sources.append("same_atom_set")
            if jac >= 0.5:
                sources.append("high_atom_jaccard")
            if len(inter) >= 2 and contain >= 0.5:
                sources.append("high_atom_containment")
            if same_domain and inter and (ts >= 0.32 or tv >= 0.28 or av >= 0.24):
                sources.append("same_domain_proximity")
            if cross_layer and inter and (same_primary or contain >= 0.5 or av >= 0.28):
                sources.append("cross_layer_overlap")
            if corridor and inter and (same_primary or contain >= 0.5 or av >= 0.26):
                sources.append("ownership_corridor")
            if ts >= 0.58 or tv >= 0.52:
                sources.append("title_semantic_similarity")
            if av >= 0.52 or (inter and av >= 0.34):
                sources.append("answer_semantic_similarity")
            if not sources:
                continue
            score = 0.26 * contain + 0.16 * jac + 0.20 * max(ts, tv) + 0.30 * av + 0.08 * same_primary
            edges.append({
                "pair_key": "||".join(key), "a": key[0], "b": key[1],
                "score": round(score, 4), "title_similarity": round(max(ts, tv), 4),
                "answer_similarity": round(av, 4), "atom_jaccard": round(jac, 4),
                "atom_containment": round(contain, 4), "shared_atoms": sorted(inter),
                "same_primary": same_primary, "same_domain": same_domain,
                "ownership_corridor": corridor, "layers": [a["kind"], b["kind"]],
                "sources": sorted(set(sources)),
            })
    edges.sort(key=lambda e: (-e["score"], e["pair_key"]))

    adjacency = defaultdict(set)
    for e in edges:
        adjacency[e["a"]].add(e["b"])
        adjacency[e["b"]].add(e["a"])
    seen, clusters = set(), []
    for qid in sorted(adjacency):
        if qid in seen:
            continue
        stack, members = [qid], []
        seen.add(qid)
        while stack:
            node = stack.pop()
            members.append(node)
            for nxt in adjacency[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        member_set = set(members)
        count = sum(e["a"] in member_set and e["b"] in member_set for e in edges)
        clusters.append({"cluster_id": f"V2C{len(clusters) + 1:03d}", "members": sorted(members), "pair_count": count})

    edge_keys = {pair(e["a"], e["b"]) for e in edges}
    seed_results = {}
    for name, pairs in SEEDS.items():
        missing = ["||".join(pair(a, b)) for a, b in pairs if pair(a, b) not in edge_keys]
        seed_results[name] = {"required_pairs": len(pairs), "recalled_pairs": len(pairs) - len(missing), "missing": missing}
    required = sum(x["required_pairs"] for x in seed_results.values())
    recalled = sum(x["recalled_pairs"] for x in seed_results.values())
    recall = recalled / required if required else 1.0
    if recall != 1.0:
        errors.append(f"known seed recall is {recalled}/{required}")
    if len(edge_keys) != len(edges):
        errors.append("duplicate pair keys")
    atom_ids = {a["id"] for a in load("atom_registry.json")}
    for rule in load("atom_migrations_phase2_gate.json")["rules"]:
        if rule["type"] == "add_atom":
            atom_ids.add(rule["atom"]["id"])
    unknown_atoms = sorted({x for e in edges for x in e["shared_atoms"] if x not in atom_ids})
    if unknown_atoms:
        errors.append(f"unknown atom refs: {unknown_atoms}")

    source_counts = Counter(s for e in edges for s in e["sources"])
    payload = {"phase": "4B", "question_count": len(rows), "candidate_pair_count": len(edges),
               "candidate_cluster_count": len(clusters), "clusters": clusters, "pairs": edges}
    (HERE / "duplicate_candidates_v2.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validation = {"phase": "4B", "status": "passed" if not errors else "failed",
                  "candidate_pair_count": len(edges), "candidate_cluster_count": len(clusters),
                  "known_seed_recall": recall, "known_seed_results": seed_results,
                  "candidate_source_breakdown": dict(sorted(source_counts.items())),
                  "duplicate_pair_keys_unique": len(edge_keys) == len(edges),
                  "all_qids_valid": not invalid_seed_qids and all(e["a"] in valid and e["b"] in valid for e in edges),
                  "all_atom_refs_valid": not unknown_atoms, "errors": errors}
    (HERE / "phase4b_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Phase 4B — High-Recall Candidate Generation", "",
             f"- Candidate pairs: **{len(edges)}**", f"- Candidate clusters: **{len(clusters)}**",
             f"- Known regression seed recall: **{recalled}/{required} ({recall:.0%})**", "",
             "Similarity and Atom overlap are recall signals only. No action is inferred in Phase 4B.", "",
             "## Candidate source breakdown", ""]
    lines += [f"- `{k}`: {v}" for k, v in sorted(source_counts.items())]
    lines += ["", "## Regression seeds", ""]
    lines += [f"- `{name}`: {x['recalled_pairs']}/{x['required_pairs']}" for name, x in seed_results.items()]
    if errors:
        lines += ["", "## Gate errors", ""] + [f"- {e}" for e in errors]
    (HERE / "PHASE4B_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
