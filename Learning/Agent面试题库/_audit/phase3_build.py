#!/usr/bin/env python3
"""Build Phase 3 Question -> Atom map without modifying source Markdown.

Evidence order:
1) explicit manual shard mapping in _audit/phase3_maps/*.json
2) Phase 2 source_question_ids (hard provenance)
3) semantic ranking inside the Phase 2 scope, used only to propose candidates

For provenance-backed questions, no similarity-only atoms are appended. Questions
without provenance remain pending until an explicit manual shard mapping exists.
Similarity never decides duplicate/merge/delete; those remain Phase 4/5.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KB = ROOT.parent


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def effective_atoms():
    atoms = {a["id"]: dict(a) for a in load_json(ROOT / "atom_registry.json")}
    mig = load_json(ROOT / "atom_migrations_phase2_gate.json")
    deprecated, replacements = set(), {}
    for r in mig["rules"]:
        typ = r["type"]
        if typ == "deprecate_composite":
            deprecated.add(r["atom_id"])
            replacements[r["atom_id"]] = list(r.get("replacement_atoms", []))
        elif typ == "alias_override":
            atoms[r["atom_id"]]["aliases"] = list(r["effective_aliases"])
        elif typ == "canonical_owner_override":
            atoms[r["atom_id"]]["canonical_owner"] = r["to"]
        elif typ == "add_atom":
            atoms[r["atom"]["id"]] = dict(r["atom"])
    for aid in deprecated:
        atoms[aid]["status"] = "deprecated"
    return atoms, deprecated, replacements


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


def phase2_file_pools(valid_ids, replacements):
    log = load_json(ROOT / "atomization_log.json")
    pools = {}
    for entry in log:
        raw = set(entry.get("reused_atoms", [])) | set(entry.get("new_atoms", []))
        expanded = set()
        for aid in raw:
            expanded.update(replacements.get(aid, [aid]))
        expanded &= valid_ids
        for f in entry.get("source_files", []):
            pools.setdefault(f, set()).update(expanded)
    return pools


def answer_text(item):
    lines = (KB / item["file"]).read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[item["answer_start_line"]-1:item["answer_end_line"]]).strip()


def infer_intent(title: str):
    if any(x in title for x in ["设计一个", "如何设计", "架构如何", "模块如何拆", "怎么设计"]): return "design"
    if any(x in title for x in ["排查", "定位", "诊断", "卡死", "出错", "不稳定", "根因"]): return "debugging"
    if any(x in title for x in ["评测", "验证", "衡量", "指标", "证明"]): return "evaluation"
    if any(x in title for x in ["项目", "怎么讲", "如何回答"]): return "project_expression"
    if any(x in title for x in ["区别", "对比", "相比", "分别", "边界是什么", "与什么关系", "有什么区别"]): return "comparison"
    if any(x in title for x in ["什么时候", "何时", "取舍", "选择", "该用", "是否需要", "优缺点"]): return "tradeoff"
    if any(x in title for x in ["如何实现", "怎么实现", "伪代码", "实现一个"]): return "implementation"
    if title.startswith("什么是") or title.startswith("什么叫") or "是什么" in title: return "definition"
    if any(x in title for x in ["如何", "怎么", "为什么", "流程", "原理", "机制"]): return "mechanism"
    return "scenario"


def main():
    from sentence_transformers import SentenceTransformer

    inventory = load_json(ROOT / "question_inventory.json")
    atoms, deprecated, replacements = effective_atoms()
    active = {k:v for k,v in atoms.items() if v.get("status") == "active"}
    valid_ids = set(active)
    manual = manual_maps()
    file_pools = phase2_file_pools(valid_ids, replacements)

    for q in manual.values():
        bad = set(q["atoms"]) - valid_ids
        if bad: raise SystemExit(f"manual map unknown/deprecated atoms for {q['question_id']}: {sorted(bad)}")

    provenance = {}
    for aid, atom in active.items():
        for qid in atom.get("source_question_ids", []):
            provenance.setdefault(qid, set()).add(aid)

    atom_ids = sorted(active)
    atom_index = {a:i for i,a in enumerate(atom_ids)}
    atom_texts = [active[a]["canonical_name"] + "\n" + active[a]["definition"] + "\nalias: " + " | ".join(active[a].get("aliases", [])) for a in atom_ids]
    q_texts = [q["title"] + "\n" + answer_text(q) for q in inventory]
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    avec = model.encode(atom_texts, normalize_embeddings=True, show_progress_bar=True)
    qvec = model.encode(q_texts, normalize_embeddings=True, show_progress_bar=True)

    maps, reviews = [], []
    manual_count = evidence_count = candidate_count = 0
    for idx, item in enumerate(inventory):
        qid = item["question_id"]
        if qid in manual:
            m = dict(manual[qid]); m["mapping_source"]="manual"; m["confidence"]="reviewed"
            maps.append(m); manual_count += 1; continue

        forced = set(provenance.get(qid, set())) & valid_ids
        if forced:
            # Phase 2 provenance is a conservative, human-created evidence relation.
            # Do not contaminate it with similarity-only secondary atoms.
            pool = set(file_pools.get(item["file"], set())) | forced
            sims = [(float(qvec[idx] @ avec[atom_index[a]]), a) for a in forced]
            sims.sort(reverse=True)
            ordered = [a for _,a in sims]
            maps.append({
                "question_id":qid,"atoms":ordered,"primary_atom":ordered[0],
                "intent":infer_intent(item["title"]),"layer":item["layer"],
                "mapping_source":"source_evidence","confidence":"high"
            })
            evidence_count += 1; continue

        # No hard provenance: produce a provisional mapping only so the review is actionable.
        pool = set(file_pools.get(item["file"], set())) or set(valid_ids)
        sims = [(float(qvec[idx] @ avec[atom_index[a]]), a) for a in pool]
        sims.sort(reverse=True)
        top_score = sims[0][0]
        cutoff = max(0.40, top_score - 0.07)
        ordered = [a for s,a in sims[:8] if s >= cutoff][:5] or [sims[0][1]]
        maps.append({
            "question_id":qid,"atoms":ordered,"primary_atom":ordered[0],
            "intent":infer_intent(item["title"]),"layer":item["layer"],
            "mapping_source":"semantic_candidate_unreviewed","confidence":"needs_review"
        })
        reviews.append({
            "question_id":qid,"title":item["title"],"source_file":item["file"],
            "answer_start_line":item["answer_start_line"],"answer_end_line":item["answer_end_line"],
            "phase2_candidate_pool_size":len(pool),
            "top_candidates":[{"atom_id":a,"score":round(s,4),"name":active[a]["canonical_name"],"domain":active[a]["domain"]} for s,a in sims[:6]],
            "reason":"no_phase2_source_evidence_requires_explicit_review"
        })
        candidate_count += 1

    order={q["question_id"]:i for i,q in enumerate(inventory)}; maps.sort(key=lambda x:order[x["question_id"]])
    (ROOT/"question_atom_map.json").write_text(json.dumps({
        "phase":3,"inventory_count":len(inventory),"effective_active_atom_count":len(active),
        "effective_deprecated_atoms":sorted(deprecated),
        "mapping_counts":{"manual":manual_count,"source_evidence":evidence_count,"unreviewed_semantic_candidates":candidate_count},
        "questions":maps
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"phase3_review.json").write_text(json.dumps({"phase":3,"pending_count":len(reviews),"reviews":reviews},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    mapped={m["question_id"] for m in maps}; inv={q["question_id"] for q in inventory}; refs={a for m in maps for a in m["atoms"]}; errors=[]
    if mapped!=inv: errors.append({"question_coverage_mismatch":sorted(inv^mapped)})
    unknown=sorted(refs-valid_ids)
    if unknown: errors.append({"unknown_atom_refs":unknown})
    missing=sorted(valid_ids-refs)
    if missing: errors.append({"uncovered_active_atoms":missing})
    deprecated_refs=sorted({a for m in maps for a in m["atoms"] if a in deprecated})
    if deprecated_refs: errors.append({"deprecated_atom_refs":deprecated_refs})
    val={
        "phase":3,"structural_status":"passed" if not errors else "failed",
        "inventory_questions":len(inv),"mapped_questions":len(mapped),"question_coverage":len(mapped&inv)/len(inv) if inv else 1,
        "effective_active_atoms":len(valid_ids),"covered_active_atoms":len(valid_ids&refs),"uncovered_active_atoms":missing,
        "unknown_atom_refs":unknown,"pending_semantic_reviews":len(reviews),"errors":errors,
        "note":"Every question without Phase2 provenance requires an explicit manual shard mapping before freeze. Similarity output is provisional candidate evidence only."
    }
    (ROOT/"phase3_validation.json").write_text(json.dumps(val,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(val,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
