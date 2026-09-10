#!/usr/bin/env python3
"""Materialize explicit Phase 3 semantic reviews for all currently pending questions.

This file is a reviewed decision layer, not a similarity auto-acceptor. It only
writes `_audit/phase3_maps/05-13_semantic_review.json`; source Markdown is never
modified. `phase3_build.py` remains the authoritative validator/aggregator.
"""
from __future__ import annotations

import json
from pathlib import Path
from phase3_build import infer_intent

ROOT = Path(__file__).resolve().parent

# Decisions were reviewed against the compact semantic candidate report and the
# Phase 2 atom boundaries. Values are intentionally conservative: include only
# atoms that materially belong to the question's answer contract.
D = {
"05_Multi-Agent与Workflow/Loop控制与Harness面经补充.md": {
7:["CTX-004","CTX-001","STATE-004"],9:["REL-001","LOOP-003","TOOL-001"],10:["LOOP-003","DUR-003"],19:["CODE-001","SEC-001"],20:["TRACE-002","DUR-003","LOOP-001"],21:["CTX-004","CTX-002"],22:["STATE-001","CTX-004","SEC-001"]},
"05_Multi-Agent与Workflow/Multi-Agent与Workflow.md": {
2:["LOOP-002"],5:["MULTI-001","TOOL-008","STATE-004"],10:["MULTI-006","REL-001"],15:["HARNESS-002","LOOP-008","LOOP-010"],19:["SEC-006","SANDBOX-001","SEC-001"],23:["LOOP-002","MULTI-001","MULTI-002"]},
"05_Multi-Agent与Workflow/Skill编排与协作面经补充.md": {3:["CTX-001","SKILL-002"],14:["SKILL-001","MULTI-001","MULTI-006"]},
"06_RAG与知识库/RAG与检索.md": {24:["RAG-008","CTX-003","RAG-001"]},
"07_可靠性与安全/可靠性与安全.md": {
1:["EVAL-002","TRACE-002"],2:["HARNESS-002","EVAL-002"],3:["LOOP-008","TRACE-002","SEC-001"],4:["REL-001","REL-002","TOOL-001"],5:["REL-001","REL-002"],6:["TOOL-006","TOOL-001","TOOL-002"],10:["SEC-003","SEC-013","EVAL-003"],13:["SEC-003","SEC-006","SEC-010"],16:["SANDBOX-001","SEC-012"],18:["SANDBOX-001"],19:["SEC-005","REL-003","SEC-001"],20:["SEC-005","TOOL-006"],22:["TRACE-002"],26:["TOOL-002","TOOL-001","REL-001"],32:["TOOL-011","REL-001","TRACE-001"],35:["TOOL-002","TOOL-006","TOOL-001"],38:["TOOL-002","TOOL-001","TOOL-006"]},
"08_评测与可观测/评测、轨迹与线上故障面经补充.md": {
5:["MODEL-003","EVAL-004","EVAL-013"],6:["EVAL-004","EVAL-009"],9:["TRACE-003","DATA-002","EVAL-003"],10:["REPLAY-001","TRACE-002"],16:["TRACE-002","LOOP-010","EVAL-004"]},
"08_评测与可观测/评测与可观测性.md": {
5:["EVAL-002","EVAL-004","EVAL-015"],15:["EVAL-004","DATA-001","EVAL-013"],24:["REPLAY-001","TRACE-002"],34:["EVAL-015","EVAL-002"],35:["EVAL-001","DATA-001","EVAL-016"],37:["TRACE-002","TRACE-003","REPLAY-001"],40:["EVAL-009","EVAL-004","DATA-001"]},
"09_工程化与系统设计/生产工程与系统设计.md": {
5:["DUR-003","DUR-001","TOOL-009"],13:["CACHE-001","SEC-004"],17:["TRACE-002","STREAM-001"],18:["SEC-004","CAP-001"],20:["MODEL-002","EVAL-017","TRACE-002"],22:["ARCH-005","TOOL-005","TRACE-002","CAP-003"],23:["ARCH-007","INGEST-002","BACK-004","TOOL-005"],24:["ARCH-007","TRACE-002","CAP-003"],27:["ARCH-003","TRACE-002","CAP-003","EVAL-017"],28:["SEC-005","ARCH-005","ARCH-003"],29:["ARCH-005","ARCH-002","CAP-001","DUR-004"]},
"09_工程化与系统设计/系统设计与取舍面经补充.md": {
3:["MODEL-002","MODEL-003","EVAL-001"],6:["LOOP-002","EVAL-001"],7:["CAP-003","MODEL-002","LOOP-002"],8:["LOOP-007","EVAL-017","CAP-003"],9:["TOOL-005"],10:["MODEL-002","LOOP-007"],12:["SEC-004","CAP-001","ARCH-002"],13:["EVAL-001","EVAL-017","CAP-003"],15:["CACHE-001","INGEST-002","DUR-002"],16:["CAP-003","TOOL-005","PROJECT-001"],19:["STATE-006","DUR-003","DUR-001"],20:["ARCH-005","CAP-003","MODEL-002","LOOP-002"],21:["EVAL-008","EVAL-017","CAP-003","EVAL-001"]},
"10_模型与推理/模型与推理基础.md": {
11:["CTX-003","LLM-022"],17:["MODEL-002","EVAL-008","MODEL-003"],18:["CTX-003","CTX-004"],26:["MODEL-003","MODEL-002"],28:["DATA-003","DATA-004","EVAL-015"],29:["MODEL-002","LOOP-004","MODEL-005"],30:["MODEL-003","MODEL-002","DATA-004"]},
"10_模型与推理/高频八股与手撕面经补充.md": {
12:["LOOP-001","LOOP-004","TOOL-003"],13:["LOOP-009","LOOP-004"],14:["TOOL-003","TOOL-011"],15:["REL-001","REL-002","TOOL-011"],16:["TOOL-001","TOOL-003"],17:["TOOL-008","MODEL-001"],18:["CTX-004"],19:["RAG-006","CTX-005","RAG-007","RAG-012"],20:["EVAL-010","TEST-002"],21:["LOOP-001","LOOP-011","SEC-006","PROMPT-005"],22:["TOOL-001","TOOL-011","REL-002"],23:["TOOL-008","CAP-001","TOOL-009"]},
"11_编码与后端/编码题与后端基础.md": {
15:["BACK-001"],16:["BACK-001"],17:["REL-002"],18:["TOOL-001"],39:["TEST-002"],40:["OPS-002","TEST-002"],42:["DUR-004","TOOL-001","TOOL-009","DUR-003"],43:["TOOL-010","TOOL-001","BACK-001","SEC-006","TRACE-001","MODEL-002"]},
"12_课程深化/01_Provider与框架/Provider适配与框架选型.md": {
1:["PROV-001","PROV-008"],3:["STATE-001"],5:["PROV-006","TOOL-009"],6:["PROMPT-005"],10:["TOOL-003","SEC-001"],14:["STATE-006"],16:["STATE-006","SEC-005","DUR-003"],18:["PROV-002"],20:["OPS-002","STATE-003","TEST-002"],23:["PROV-001","TOOL-003","SEC-005"],24:["PROV-002","PROV-009","STATE-006","STATE-004"],26:["STATE-006","STATE-004","STATE-003","DUR-002"]},
"12_课程深化/02_代码Agent与ComputerUse/代码Agent与ComputerUse.md": {
11:["TOOL-007","CODE-002"],14:["LOOP-010","CODE-008","CODE-001"],17:["LOOP-008","CODE-001","CODE-008"],22:["SANDBOX-001","SANDBOX-002"],24:["SEC-005","GUI-002","GUI-001"],26:["CODE-001","CODE-008","CODE-005","CODE-006","SEC-005"]},
"12_课程深化/03_Durable与生产运维/Durable与生产运维.md": {
1:["DUR-001"],2:["DUR-001","LOOP-003","DUR-003"],3:["BACK-002","TOOL-001"],4:["TOOL-001"],6:["DUR-004","CAP-002"],7:["BACK-014","BACK-002"],8:["DUR-002","TOOL-002","STATE-006"],9:["DUR-001","STATE-001"],10:["TOOL-002","TOOL-001","BACK-002"],11:["CAP-001","SEC-004","STATE-004"],13:["CAP-002","CAP-001"],15:["OBS-003","OBS-001"],16:["OPS-002"],17:["OPS-002","STATE-003"],18:["EVAL-013","OPS-002"],19:["CAP-001","LOOP-011","CAP-002"],21:["OBS-001","OPS-001"],24:["OPS-003","OPS-004"],26:["CAP-002","LOOP-011"],27:["STATE-003","OPS-002","DUR-002"],28:["DUR-001","DUR-004","STATE-006","OPS-002"],29:["TOOL-002","REL-001","REL-003"],30:["EVAL-013","EVAL-022","REL-003"],31:["CAP-002","DUR-004","STATE-006","OBS-001"],34:["DUR-004"],35:["STATE-003","DUR-001","OPS-002"],36:["REPLAY-001","STATE-005"]},
"12_课程深化/04_知识摄取与GraphRAG/知识摄取与GraphRAG.md": {
5:["RAG-010"],6:["INGEST-001","RAG-012","INGEST-004"],7:["INGEST-002","INGEST-004","GRAPH-005"],16:["RAG-003","INGEST-011"],17:["RAG-007","EVAL-002","RAG-008"],19:["RAG-010","INGEST-005","RAG-008"],20:["RAG-006","RAG-007","RAG-008","RAG-005"],21:["RAG-007","CTX-005","RAG-006","RAG-009"],23:["METRIC-002","INGEST-009","INGEST-011","RAG-010"],31:["INGEST-002","INGEST-003","INGEST-004","INGEST-005"]},
"12_课程深化/05_身份治理与跨Agent/身份治理与跨Agent.md": {
6:["SEC-004"],9:["SEC-005","IDENT-004","IDENT-002"],10:["SEC-005"],11:["MCP-001","A2A-001","MULTI-001"],12:["A2A-001","IDENT-001","IDENT-002"],13:["MULTI-001","IDENT-004","MULTI-005"],15:["MULTI-004","A2A-001"],16:["MULTI-005","IDENT-006"],18:["REL-003","MULTI-004"]},
"12_课程深化/06_推理与模型行为/推理与模型行为.md": {
1:["MODEL-006","EVAL-001"],2:["REASON-007","LLM-014","LLM-017"],3:["CAP-003","REASON-006"],4:["REASON-006","CAP-003","REASON-005"],12:["REASON-006","MODEL-003"],15:["MODEL-003","CTX-001"],16:["PROMPT-005","SEC-001"],17:["DATA-006","REASON-007","LLM-014","REASON-006"],18:["DATA-006","DATA-004","LLM-014","REASON-007"],23:["EVAL-006","MODEL-003","SEC-001","CTX-001"]},
"12_课程深化/07_实时交互与产品/实时交互与产品.md": {
7:["TRACE-003","VOICE-004"],14:["REASON-004","UI-003"],17:["EVAL-008","EVAL-009"],18:["SKILL-001","MCP-001","TOOL-004"],19:["CTX-002"],20:["SKILL-001","SKILL-003"],21:["SKILL-001","MCP-001","SEC-006"],22:["SKILL-001","CTX-001","RAG-001"],23:["SKILL-001","EVAL-009","LOOP-002"],26:["ARCH-004","CTX-006","EVAL-009"],27:["SKILL-001","CTX-002","EVAL-006"],32:["TOOL-009","UI-003"]},
"12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md": {
1:["EVAL-004","EVAL-008"],4:["EVAL-004","EVAL-008","DATA-002"],5:["TRACE-002","REPLAY-001","EVAL-018","TOOL-003"],6:["EVAL-010","TEST-002","EVAL-019"],8:["DATA-001","EVAL-019"],9:["TEST-002","PROV-008"],13:["DATA-003","REPLAY-001","EVAL-014"],15:["PROJECT-001","MCP-002","TOOL-003"],17:["TOOL-003"],18:["TOOL-003"],19:["MCP-002"],20:["CODE-005","TEST-002","EVAL-021"],21:["PROJECT-001","PROJECT-002"],22:["PROJECT-001","PROJECT-002"],23:["EVAL-004","DATA-001"],24:["PROJECT-001","EVAL-004","EVAL-018","TOOL-003"],25:["ARCH-004","PROJECT-001","EVAL-004"]},
"13_跨主题综合题/新增题簇_Agent与AI后端.md": {
1:["ARCH-005","PROV-001","SEC-001"],2:["TOOL-002","BACK-002","PROV-006"],5:["EVAL-002"],6:["ARCH-002","PROV-002","PROV-001"],9:["PROJECT-001","ARCH-004","EVAL-009"],11:["PROJECT-002"]}
}

def main():
    inventory = json.loads((ROOT / "question_inventory.json").read_text(encoding="utf-8"))
    by_id = {q["question_id"]: q for q in inventory}
    rows = []
    for src, numbers in D.items():
        for number, atoms in numbers.items():
            qid = f"Q::{src}::{number}"
            if qid not in by_id:
                raise SystemExit(f"decision references missing inventory question: {qid}")
            q = by_id[qid]
            rows.append({
                "question_id": qid,
                "atoms": atoms,
                "primary_atom": atoms[0],
                "intent": infer_intent(q["title"]),
                "layer": q["layer"],
            })
    # Verify this review layer exactly targets all currently pending questions not
    # already covered by the pre-existing 01-04 manual shards.
    review = json.loads((ROOT / "phase3_review.json").read_text(encoding="utf-8"))
    pending = {r["question_id"] for r in review["reviews"]}
    existing = set()
    for p in (ROOT / "phase3_maps").glob("*.json"):
        obj = json.loads(p.read_text(encoding="utf-8"))
        existing.update(x["question_id"] for x in obj.get("questions", []))
    expected = pending - existing
    actual = {r["question_id"] for r in rows}
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise SystemExit(f"review decision coverage mismatch: missing={missing} extra={extra}")
    out = {
        "phase": 3,
        "review_kind": "explicit_semantic_review",
        "reviewed_pending_questions": len(rows),
        "questions": sorted(rows, key=lambda x: next(i for i,q in enumerate(inventory) if q["question_id"] == x["question_id"]))
    }
    target = ROOT / "phase3_maps" / "05-13_semantic_review.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} reviewed mappings to {target.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
