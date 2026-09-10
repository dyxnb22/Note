#!/usr/bin/env python3
"""Build Hard Dedup v2 inventory, migration, coverage, and regression gates."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from phase4b_candidates import kind, parse_current_questions
from phase5b_adjudicate import OLD_BRIDGES, PLANNED

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent
KB = AUDIT.parent
BASELINE = "284338f99b6274e0ed16026d7c48c7188c778729"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(name: str, value) -> None:
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def effective_atoms() -> dict[str, dict]:
    atoms = {a["id"]: dict(a) for a in load(AUDIT / "atom_registry.json")}
    gate = load(AUDIT / "atom_migrations_phase2_gate.json")
    for rule in gate["rules"]:
        if rule["type"] == "deprecate_composite":
            atoms[rule["atom_id"]]["status"] = "deprecated"
        elif rule["type"] == "add_atom":
            atoms[rule["atom"]["id"]] = dict(rule["atom"])
        elif rule["type"] == "canonical_owner_override":
            atoms[rule["atom_id"]]["canonical_owner"] = rule["to"]
    return {k: v for k, v in atoms.items() if v.get("status") == "active"}


def current_inventory(current: dict[str, dict]) -> list[dict]:
    rows = []
    for qid, q in sorted(current.items(), key=lambda item: (item[1]["file"], item[1]["number"])):
        rows.append({
            "question_id": qid,
            "file": q["file"],
            "number": q["number"],
            "title": q["title"],
            "layer": kind(q["file"]),
            "status": "active",
            "answer_sha256": hashlib.sha256(q["answer"].encode()).hexdigest(),
        })
    return rows


def resolve_numeric_links() -> list[dict]:
    errors = []
    link_re = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
    for src in sorted(KB.rglob("*.md")):
        if AUDIT in src.parents:
            continue
        for match in link_re.finditer(src.read_text(encoding="utf-8")):
            raw = match.group(1)
            path_part, marker, anchor = raw.partition("#")
            if not marker or not re.match(r"\d+\.", anchor):
                continue
            if path_part:
                candidates = [src.parent / f"{path_part}.md", src.parent / path_part,
                              KB / f"{path_part}.md", KB / path_part]
            else:
                candidates = [src]
            dest = next((p.resolve() for p in candidates if p.exists()), None)
            if not dest:
                errors.append({"source": src.relative_to(KB).as_posix(), "target": raw,
                               "error": "target file missing"})
                continue
            headings = {x.strip() for x in re.findall(r"^#{1,6}\s+(.+)$", dest.read_text(encoding="utf-8"), re.M)}
            if anchor not in headings:
                errors.append({"source": src.relative_to(KB).as_posix(), "target": raw,
                               "error": "target heading missing"})
    return errors


def main() -> None:
    old_inventory = load(AUDIT / "question_inventory.json")
    old_map = {q["question_id"]: q for q in load(AUDIT / "question_atom_map.json")["questions"]}
    current = parse_current_questions()
    inventory = current_inventory(current)
    active = effective_atoms()
    title_to_current = {(q["file"], q["title"]): qid for qid, q in current.items()}
    old_by_id = {q["question_id"]: q for q in old_inventory}
    planned = {victim: (canonical, relation, action, reason)
               for victim, canonical, relation, action, reason in PLANNED}
    bridge_plan = {victim: canonical for victim, canonical, _, action, _ in PLANNED
                   if action == "MOVE_OR_BRIDGE"}

    def mapped_current(old_qid: str) -> str | None:
        old = old_by_id[old_qid]
        return title_to_current.get((old["file"], old["title"]))

    migration = []
    destination: dict[str, str] = {}
    errors = []
    for old in old_inventory:
        old_qid = old["question_id"]
        if old_qid in planned:
            canonical, _, action, _ = planned[old_qid]
            canonical_new = mapped_current(canonical)
            status = {"DELETE": "deleted", "MERGE": "merged",
                      "CONVERT_TO_FOLLOWUP": "followup", "MOVE_OR_BRIDGE": "retained"}[action]
            if action == "MOVE_OR_BRIDGE":
                new_qid = mapped_current(old_qid)
                if new_qid:
                    destination[old_qid] = new_qid
            else:
                new_qid = canonical_new
                if canonical_new:
                    destination[old_qid] = canonical_new
            migration.append({
                "old_question_id": old_qid,
                "new_question_id": new_qid,
                "status": status,
                "canonical_question": canonical_new,
            })
        else:
            new_qid = mapped_current(old_qid)
            if new_qid:
                destination[old_qid] = new_qid
            migration.append({
                "old_question_id": old_qid,
                "new_question_id": new_qid,
                "status": "retained",
                "canonical_question": new_qid,
            })
        if migration[-1]["new_question_id"] is None:
            errors.append(f"unmapped old question: {old_qid}")

    current_atoms: dict[str, set[str]] = defaultdict(set)
    current_intents: dict[str, set[str]] = defaultdict(set)
    source_questions: dict[str, list[str]] = defaultdict(list)
    for old_qid, mapping in old_map.items():
        dest = destination.get(old_qid)
        if not dest:
            errors.append(f"coverage destination missing: {old_qid}")
            continue
        current_atoms[dest].update(mapping["atoms"])
        current_intents[dest].add(mapping["intent"])
        source_questions[dest].append(old_qid)

    coverage_rows = []
    for qid in sorted(current):
        coverage_rows.append({
            "question_id": qid,
            "atoms": sorted(current_atoms[qid]),
            "primary_atom": old_map[source_questions[qid][0]]["primary_atom"] if source_questions[qid] else None,
            "intents": sorted(current_intents[qid]),
            "source_old_question_ids": sorted(source_questions[qid]),
        })

    all_refs = {atom for atoms in current_atoms.values() for atom in atoms}
    unknown_refs = sorted(all_refs - set(active))
    covered = sorted(set(active) & all_refs)
    orphan = sorted(set(active) - all_refs)
    lost_atoms = orphan.copy()

    lost_unique_intents = []
    for old_qid, mapping in old_map.items():
        dest = destination.get(old_qid)
        if not dest or mapping["intent"] not in current_intents[dest]:
            lost_unique_intents.append({"question_id": old_qid, "intent": mapping["intent"]})

    duplicate_ids = sorted(qid for qid, n in Counter(q["question_id"] for q in inventory).items() if n > 1)
    non_contiguous = []
    by_file = defaultdict(list)
    for q in inventory:
        by_file[q["file"]].append(q["number"])
    for file, numbers in by_file.items():
        if sorted(numbers) != list(range(1, len(numbers) + 1)):
            non_contiguous.append({"file": file, "numbers": sorted(numbers)})

    broken_links = resolve_numeric_links()
    invalid_followups = []
    for victim, canonical, _, action, _ in PLANNED:
        if action != "CONVERT_TO_FOLLOWUP":
            continue
        canonical_new = mapped_current(canonical)
        if not canonical_new or "**追问：" not in current[canonical_new]["answer"]:
            invalid_followups.append({"victim": victim, "canonical": canonical_new})

    ownership = []
    for atom_id, atom in sorted(active.items()):
        owners = sorted(qid for qid, refs in current_atoms.items() if atom_id in refs)
        ownership.append({
            "atom_id": atom_id,
            "canonical_owner": atom.get("canonical_owner"),
            "covering_questions": owners,
        })

    phase5 = load(HERE / "duplicate_adjudications_v2.json")
    unresolved = [d for d in phase5["decisions"]
                  if d["relation"] in {"EXACT_DUPLICATE", "SEMANTIC_DUPLICATE", "SUBSUMED"}
                  and d["action"] == "KEEP"]
    changed = subprocess.check_output(
        ["git", "-c", "core.quotepath=false", "diff", "--name-only", f"{BASELINE}...HEAD"],
        cwd=KB.parent.parent, text=True
    ).splitlines()
    prefix = "Learning/Agent面试题库/"
    modified_sources = sorted(x[len(prefix):] for x in changed
                              if x.startswith(prefix) and "/_audit/" not in x and x.endswith(".md"))
    integrated_modified = any(x.startswith("13_") for x in modified_sources)
    planned_source_files = {old_by_id[v]["file"] for v, *_ in PLANNED}
    planned_source_files.update(old_by_id[c]["file"] for _, c, *_ in PLANNED)
    out_of_scope = sorted(set(modified_sources) - planned_source_files)

    expected_counts = Counter({"deleted": 2, "merged": 9, "followup": 22, "retained": 703})
    migration_counts = Counter(x["status"] for x in migration)
    if len(old_inventory) != 736:
        errors.append(f"baseline question count changed: {len(old_inventory)}")
    if len(inventory) != 703:
        errors.append(f"unexpected v2 question count: {len(inventory)}")
    if len(active) != 319:
        errors.append(f"unexpected active atom count: {len(active)}")
    if migration_counts != expected_counts:
        errors.append(f"migration counts differ: {dict(migration_counts)}")
    if len(migration) != len(old_inventory):
        errors.append("migration is incomplete")
    if unknown_refs or orphan or lost_unique_intents or duplicate_ids or non_contiguous:
        errors.append("coverage or numbering gate failed")
    if broken_links or invalid_followups or unresolved:
        errors.append("link, follow-up, or duplicate gate failed")
    if integrated_modified or out_of_scope:
        errors.append("source diff scope gate failed")

    dump("question_inventory_v2.json", inventory)
    dump("question_atom_coverage_v2.json", {
        "questions": coverage_rows,
        "active_atom_count": len(active),
        "covered_active_atom_count": len(covered),
    })
    dump("question_id_migration.json", migration)
    dump("canonical_ownership_map_v2.json", ownership)
    validation = {
        "phase": "7B",
        "status": "passed" if not errors else "failed",
        "questions_before": len(old_inventory),
        "questions_after": len(inventory),
        "migration_counts": dict(sorted(migration_counts.items())),
        "active_atoms": len(active),
        "covered_active_atoms": len(covered),
        "lost_atoms": lost_atoms,
        "lost_unique_intents": lost_unique_intents,
        "unknown_atom_refs": unknown_refs,
        "orphan_active_atoms": orphan,
        "broken_canonical_links": broken_links,
        "unresolved_high_confidence_duplicates": unresolved,
        "invalid_followups": invalid_followups,
        "duplicate_question_ids": duplicate_ids,
        "non_contiguous_numbering": non_contiguous,
        "modified_source_files": modified_sources,
        "integrated_questions_modified": integrated_modified,
        "out_of_adjudicated_scope": out_of_scope,
        "errors": errors,
    }
    dump("phase7b_validation.json", validation)
    report = f"""# Phase 7B — Coverage Regression\n\n- Status: **{validation['status'].upper()}**\n- Questions: {len(old_inventory)} → {len(inventory)}\n- Migration: 2 deleted, 9 merged, 22 follow-up, 703 retained formal questions\n- Active Atom coverage: {len(covered)}/{len(active)}\n- Lost atoms: {len(lost_atoms)}\n- Lost unique intents: {len(lost_unique_intents)}\n- Broken canonical links: {len(broken_links)}\n- Unresolved high-confidence duplicates: {len(unresolved)}\n- Invalid follow-ups: {len(invalid_followups)}\n- Duplicate IDs: {len(duplicate_ids)}\n- Non-contiguous files: {len(non_contiguous)}\n- Source files modified: {len(modified_sources)}\n"""
    (HERE / "PHASE7B_REPORT.md").write_text(report, encoding="utf-8")
    if errors:
        raise SystemExit("Phase 7B failed: " + "; ".join(errors))


if __name__ == "__main__":
    main()
