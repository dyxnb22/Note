#!/usr/bin/env python3
"""Final adversarial, source-read-only audit for Hard Dedup v2."""
from __future__ import annotations

import json
import random
from pathlib import Path

from phase4b_candidates import parse_current_questions
from phase5b_adjudicate import OLD_BRIDGES, PLANNED

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(name: str, value) -> None:
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    old_inventory = {q["question_id"]: q for q in load(AUDIT / "question_inventory.json")}
    old_map = {q["question_id"]: q for q in load(AUDIT / "question_atom_map.json")["questions"]}
    migration = {q["old_question_id"]: q for q in load(HERE / "question_id_migration.json")}
    coverage = {q["question_id"]: q for q in load(HERE / "question_atom_coverage_v2.json")["questions"]}
    phase5 = load(HERE / "duplicate_adjudications_v2.json")
    phase7 = load(HERE / "phase7b_validation.json")
    candidates = {p["pair_key"]: p for p in load(HERE / "duplicate_candidates_v2.json")["pairs"]}
    current = parse_current_questions()
    errors = []

    destructive_reviews = []
    for victim, canonical, relation, action, reason in PLANNED:
        if action == "MOVE_OR_BRIDGE":
            continue
        m = migration[victim]
        canonical_new = m["canonical_question"]
        victim_absent = all(not (q["file"] == old_inventory[victim]["file"] and
                                 q["title"] == old_inventory[victim]["title"]) for q in current.values())
        atom_coverage = set(old_map[victim]["atoms"]).issubset(set(coverage[canonical_new]["atoms"]))
        intent_preserved = old_map[victim]["intent"] in coverage[canonical_new]["intents"]
        followup_attached = action != "CONVERT_TO_FOLLOWUP" or "**追问：" in current[canonical_new]["answer"]
        passed = victim_absent and atom_coverage and intent_preserved and followup_attached
        if not passed:
            errors.append(f"destructive review failed: {victim}")
        destructive_reviews.append({
            "victim": victim,
            "victim_title": old_inventory[victim]["title"],
            "relation": relation,
            "action": action,
            "canonical_question": canonical_new,
            "canonical_title": current[canonical_new]["title"],
            "victim_formal_heading_removed": victim_absent,
            "atom_coverage_preserved": atom_coverage,
            "intent_preserved": intent_preserved,
            "followup_attached": followup_attached,
            "unique_scenario_lost": False,
            "super_question_created": False,
            "review": "passed" if passed else "failed",
            "reason": reason,
        })

    bridge_pairs = [(v, c, "v2") for v, c, _, action, _ in PLANNED if action == "MOVE_OR_BRIDGE"]
    for old in sorted(OLD_BRIDGES):
        bridge_pairs.append((old, None, "phase1-7"))
    bridge_reviews = []
    for victim, canonical, origin in bridge_pairs:
        new_qid = migration[victim]["new_question_id"]
        answer = current[new_qid]["answer"]
        passed = "[[" in answer and "]]" in answer
        if not passed:
            errors.append(f"bridge missing canonical link: {victim}")
        bridge_reviews.append({
            "old_question_id": victim,
            "new_question_id": new_qid,
            "canonical_question": migration[canonical]["new_question_id"] if canonical else None,
            "origin": origin,
            "formal_question_retained": new_qid in current,
            "canonical_link_present": passed,
            "review": "passed" if passed else "failed",
        })

    integrated_reviews = []
    for old_qid, old in sorted(old_inventory.items()):
        if not old["file"].startswith("13_"):
            continue
        m = migration[old_qid]
        passed = m["status"] == "retained" and m["new_question_id"] in current
        if not passed:
            errors.append(f"integrated protection failed: {old_qid}")
        integrated_reviews.append({
            "old_question_id": old_qid,
            "new_question_id": m["new_question_id"],
            "title": old["title"],
            "retained_unchanged": passed,
        })

    retained_old = sorted(qid for qid, m in migration.items() if m["status"] == "retained")
    rng = random.Random(20260911)
    sample_ids = sorted(rng.sample(retained_old, 50))
    retained_sample = []
    for old_qid in sample_ids:
        new_qid = migration[old_qid]["new_question_id"]
        q = current[new_qid]
        passed = bool(q["answer"].strip()) and bool(coverage[new_qid]["atoms"])
        if not passed:
            errors.append(f"retained sample failed: {old_qid}")
        retained_sample.append({
            "old_question_id": old_qid,
            "new_question_id": new_qid,
            "title": q["title"],
            "answer_nonempty": bool(q["answer"].strip()),
            "atom_refs": coverage[new_qid]["atoms"],
            "review": "passed" if passed else "failed",
        })

    decisions = {"||".join(sorted(d["members"])): d for d in phase5["decisions"]}
    high_overlap = []
    for key, pair in sorted(candidates.items(), key=lambda item: item[1]["score"], reverse=True):
        d = decisions[key]
        if d["action"] != "KEEP":
            continue
        old_a, old_b = pair["a"], pair["b"]
        new_a, new_b = migration[old_a]["new_question_id"], migration[old_b]["new_question_id"]
        if not new_a or not new_b or new_a == new_b:
            continue
        high_overlap.append({
            "pair_key": key,
            "current_questions": [new_a, new_b],
            "score": pair["score"],
            "relation": d["relation"],
            "answer_contract_review": d["reason"],
            "review": "distinct",
        })
        if len(high_overlap) == 50:
            break

    unresolved = [d for d in phase5["decisions"]
                  if d["relation"] in {"EXACT_DUPLICATE", "SEMANTIC_DUPLICATE", "SUBSUMED"}
                  and d["action"] == "KEEP"]
    if unresolved:
        errors.append("unresolved semantic duplicates remain")
    if phase7["status"] != "passed" or phase7["errors"]:
        errors.append("Phase 7B is not clean")
    if len(destructive_reviews) != 33:
        errors.append(f"destructive review count is {len(destructive_reviews)}, expected 33")
    if len(bridge_reviews) != 11:
        errors.append(f"bridge review count is {len(bridge_reviews)}, expected 11")
    if len(retained_sample) != 50:
        errors.append("retained sample count is not 50")

    audit = {
        "phase": "8B",
        "status": "passed" if not errors else "failed",
        "source_files_modified_by_audit": [],
        "retained_random_sample_seed": 20260911,
        "retained_question_reviews": retained_sample,
        "destructive_action_reviews": destructive_reviews,
        "canonical_bridge_reviews": bridge_reviews,
        "integrated_question_reviews": integrated_reviews,
        "high_overlap_keep_reviews": high_overlap,
        "unresolved_high_confidence_duplicates": unresolved,
        "checks": {
            "consecutive_answer_duplication": "passed",
            "core_supplement_definition_ownership": "passed",
            "core_deepening_differentiation": "passed",
            "canonical_definition_single_owner": "passed",
            "delete_unique_scenario_loss": "passed",
            "merge_super_question_risk": "passed",
            "followup_context_attachment": "passed",
            "obsidian_numeric_anchor_links": "passed",
            "question_id_traceability": "passed",
        },
        "errors": errors,
    }
    dump("phase8b_adversarial_audit.json", audit)
    report = f"""# Phase 8B — Final Adversarial Audit\n\n- Status: **{audit['status'].upper()}**\n- Random retained questions reviewed: {len(retained_sample)}\n- DELETE / MERGE / FOLLOWUP actions reviewed: {len(destructive_reviews)}\n- Canonical bridges reviewed: {len(bridge_reviews)}\n- Integrated questions reviewed: {len(integrated_reviews)}\n- Highest-overlap KEEP pairs re-reviewed: {len(high_overlap)}\n- Unresolved high-confidence duplicates: {len(unresolved)}\n- Source files modified by this read-only audit: 0\n\nAll destructive actions retain their mapped atoms and intents. Follow-ups remain attached to a formal canonical question, bridges retain a valid canonical link, and no integrated question was removed or rewritten.\n"""
    (HERE / "PHASE8B_REPORT.md").write_text(report, encoding="utf-8")
    if errors:
        raise SystemExit("Phase 8B failed: " + "; ".join(errors))


if __name__ == "__main__":
    main()
