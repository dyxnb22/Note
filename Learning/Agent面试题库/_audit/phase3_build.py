#!/usr/bin/env python3
"""Build Phase 3 Question -> Atom map without modifying source Markdown.

Evidence order:
1) explicit manual shard mapping in _audit/phase3_maps/*.json
2) Phase 2 source_question_ids (definition provenance; hard evidence)
3) multilingual sentence embedding similarity (candidate generation only)

Similarity never decides duplicate/merge/delete. Low-confidence auto mappings are
written to phase3_review.json and must be adjudicated before Phase 3 is frozen.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KB = ROOT.parent


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def effective_atoms():
    atoms = {a["id"]: dict(a) for a in load_json(ROOT / "atom_registry.json")}
    mig = load_json(ROOT / "atom_migrations_phase2_gate.json")
    deprecated = set()
    for r in mig["rules"]:
        typ = r["type"]
        if typ == "deprecate_composite":
            deprecated.add(r["atom_id"])
        elif typ == "alias_override":
            atoms[r["atom_id"]]["aliases"] = list(r["effective_aliases"])
        elif typ == "canonical_owner_override":
            atoms[r["atom_id"]]["canonical_owner"] = r["to"]
        elif typ == "add_atom":
            atoms[r["atom"]["id"]] = dict(r["atom"])
    for aid in deprecated:
        atoms[aid]["status"] = "deprecated"
    return atoms, deprecated


def manual_maps():
    out = {}
    d = ROOT / "phase3_maps"
    if not d.exists():
        return out
    for p in sorted(d.glob("*.json")):
        obj = load_json(p)
        for q in obj.get("questions", []):
            qid = q["question_id"]
            if qid in out:
                raise SystemExit(f"duplicate manual map: {qid}")
            out[qid] = q
    return out


def answer_text(item):
    path = KB / item["file"]
    lines = path.read_text(encoding="utf-8").splitlines()
    start = item["answer_start_line"] - 1
    end = item["answer_end_line"]
    return "\n".join(lines[start:end]).strip()


def infer_intent(title: str):
    t = title.lower()
    if any(x in title for x in ["设计一个", "如何设计", "架构如何", "模块如何拆", "怎么设计"]):
        return "design"
    if any(x in title for x in ["排查", "定位", "诊断", "失败", "卡死", "出错", "不稳定", "为什么会"]):
        return "debugging"
    if any(x in title for x in ["评测", "验证", "衡量", "指标", "证明"]):
        return "evaluation"
    if any(x in title for x in ["项目", "怎么讲", "如何回答"]):
        return "project_expression"
    if any(x in title for x in ["区别", "对比", "相比", "分别", "边界是什么", "与什么关系", "有什么区别"]):
        return "comparison"
    if any(x in title for x in ["什么时候", "何时", "取舍", "选择", "该用", "是否需要", "优缺点"]):
        return "tradeoff"
    if any(x in title for x in ["如何实现", "怎么实现", "代码", "伪代码", "SQL", "实现一个"]):
        return "implementation"
    if title.startswith("什么是") or title.startswith("什么叫") or "是什么" in title:
        return "definition"
    if any(x in title for x in ["如何", "怎么", "为什么", "流程", "原理", "机制"]):
        return "mechanism"
    return "scenario"


def norm(v):
    n = math.sqrt(sum(x*x for x in v)) or 1.0
    return [x/n for x in v]


def main():
    from sentence_transformers import SentenceTransformer

    inventory = load_json(ROOT / "question_inventory.json")
    atoms, deprecated = effective_atoms()
    active = {k:v for k,v in atoms.items() if v.get("status") == "active"}
    manual = manual_maps()

    valid_ids = set(active)
    for q in manual.values():
        bad = set(q["atoms"]) - valid_ids
        if bad:
            raise SystemExit(f"manual map unknown/deprecated atoms for {q['question_id']}: {sorted(bad)}")

    provenance = {}
    for aid, atom in active.items():
        for qid in atom.get("source_question_ids", []):
            provenance.setdefault(qid, set()).add(aid)

    atom_ids = sorted(active)
    atom_texts = [
        active[a]["canonical_name"] + "\n" + active[a]["definition"] + "\nalias: " + " | ".join(active[a].get("aliases", []))
        for a in atom_ids
    ]
    q_texts = [q["title"] + "\n" + answer_text(q) for q in inventory]

    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    avec = model.encode(atom_texts, normalize_embeddings=True, show_progress_bar=True)
    qvec = model.encode(q_texts, normalize_embeddings=True, show_progress_bar=True)

    maps = []
    reviews = []
    auto_count = evidence_count = manual_count = 0

    for idx, item in enumerate(inventory):
        qid = item["question_id"]
        if qid in manual:
            m = dict(manual[qid])
            m["mapping_source"] = "manual"
            m["confidence"] = "reviewed"
            maps.append(m)
            manual_count += 1
            continue

        sims = [(float(qvec[idx] @ avec[j]), atom_ids[j]) for j in range(len(atom_ids))]
        sims.sort(reverse=True)
        forced = set(provenance.get(qid, set()))
        selected = set(forced)

        top_score = sims[0][0]
        cutoff = max(0.42, top_score - 0.10)
        for score, aid in sims[:12]:
            if score >= cutoff and len(selected) < 6:
                selected.add(aid)

        # Keep hard evidence, but avoid similarity-only atom explosion.
        ranked = [(s,a) for s,a in sims if a in selected]
        ranked.sort(reverse=True)
        ordered = [a for _,a in ranked]
        if not ordered:
            ordered = [sims[0][1]]

        # Primary prefers strongest provenance atom if any, otherwise strongest semantic candidate.
        if forced:
            primary = max(((s,a) for s,a in sims if a in forced), default=(0.0, ordered[0]))[1]
            evidence_count += 1
        else:
            primary = ordered[0]
            auto_count += 1

        row = {
            "question_id": qid,
            "atoms": ordered,
            "primary_atom": primary,
            "intent": infer_intent(item["title"]),
            "layer": item["layer"],
            "mapping_source": "source_evidence+semantic" if forced else "semantic_candidate",
            "confidence": "high" if forced else ("medium" if top_score >= 0.55 else "needs_review")
        }
        maps.append(row)

        # A question with no Phase2 source evidence is reviewed when similarity is weak
        # or the two best candidate scores are nearly tied across different domains.
        if not forced:
            gap = sims[0][0] - sims[1][0]
            d0 = active[sims[0][1]]["domain"]
            d1 = active[sims[1][1]]["domain"]
            if top_score < 0.55 or (gap < 0.025 and d0 != d1):
                reviews.append({
                    "question_id": qid,
                    "title": item["title"],
                    "top_candidates": [
                        {"atom_id": a, "score": round(s, 4), "name": active[a]["canonical_name"], "domain": active[a]["domain"]}
                        for s,a in sims[:6]
                    ],
                    "reason": "low_similarity" if top_score < 0.55 else "cross_domain_near_tie"
                })

    maps.sort(key=lambda x: next(i for i,q in enumerate(inventory) if q["question_id"] == x["question_id"]))
    map_obj = {
        "phase": 3,
        "inventory_count": len(inventory),
        "effective_active_atom_count": len(active),
        "effective_deprecated_atoms": sorted(deprecated),
        "mapping_counts": {"manual": manual_count, "source_evidence_or_semantic": evidence_count, "semantic_only": auto_count},
        "questions": maps
    }
    (ROOT / "question_atom_map.json").write_text(json.dumps(map_obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "phase3_review.json").write_text(json.dumps({"phase":3,"pending_count":len(reviews),"reviews":reviews}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    mapped = {m["question_id"] for m in maps}
    inv = {q["question_id"] for q in inventory}
    atom_refs = {a for m in maps for a in m["atoms"]}
    errors = []
    if mapped != inv:
        errors.append({"question_coverage_mismatch": sorted(inv ^ mapped)})
    unknown = sorted(atom_refs - valid_ids)
    if unknown:
        errors.append({"unknown_atom_refs": unknown})
    missing_atoms = sorted(valid_ids - atom_refs)
    if missing_atoms:
        errors.append({"uncovered_active_atoms": missing_atoms})
    if any("PROMPT-006" in m["atoms"] for m in maps):
        errors.append({"deprecated_atom_referenced": "PROMPT-006"})

    val = {
        "phase":3,
        "structural_status":"passed" if not errors else "failed",
        "inventory_questions":len(inv),
        "mapped_questions":len(mapped),
        "question_coverage": len(mapped & inv) / len(inv) if inv else 1,
        "effective_active_atoms":len(valid_ids),
        "covered_active_atoms":len(valid_ids & atom_refs),
        "uncovered_active_atoms":missing_atoms,
        "unknown_atom_refs":unknown,
        "pending_semantic_reviews":len(reviews),
        "errors":errors,
        "note":"Semantic similarity is candidate generation only; duplicate adjudication remains Phase 4/5. Phase 3 is freeze-ready only when pending_semantic_reviews=0 or every pending item has an explicit manual override."
    }
    (ROOT / "phase3_validation.json").write_text(json.dumps(val, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    print(json.dumps(val, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
