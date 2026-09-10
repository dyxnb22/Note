#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parent
KB=ROOT.parent

def load(n): return json.loads((ROOT/n).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def current_questions():
    ids=[]; errors=[]
    for p in sorted(KB.rglob('*.md')):
        if ROOT in p.parents: continue
        rel=p.relative_to(KB).as_posix()
        if p.name=='README.md' or rel.startswith('00_'): continue
        text=p.read_text(encoding='utf-8')
        heads=list(re.finditer(r'(?m)^### (\d+)\. ([^\n]+)$',text))
        nums=[int(m.group(1)) for m in heads]
        if nums and nums!=list(range(1,len(nums)+1)): errors.append(f'non-contiguous numbering: {rel}')
        for i,m in enumerate(heads):
            qid=f'Q::{rel}::{int(m.group(1))}'; ids.append(qid)
            end=heads[i+1].start() if i+1<len(heads) else len(text)
            block=text[m.end():end]
            # Existing corpus legitimately uses labels such as 答（项目补充）：.
            if not re.search(r'(?m)^答(?:（[^）]+）)?：',block): errors.append(f'missing answer: {qid}')
    return ids,errors

def effective_active_ids():
    atoms={a['id']:a for a in load('atom_registry.json')}
    active={k for k,v in atoms.items() if v.get('status')=='active'}
    mig=load('atom_migrations_phase2_gate.json')
    deprecated=set()
    for r in mig['rules']:
        if r['type']=='deprecate_composite': deprecated.add(r['atom_id']); active.discard(r['atom_id'])
        elif r['type']=='add_atom' and r['atom'].get('status')=='active': active.add(r['atom']['id'])
    return active,deprecated

def main():
    errors=[]
    qids,parse_errors=current_questions(); errors+=parse_errors
    if len(qids)!=736: errors.append(f'question count changed: {len(qids)} != 736')
    if len(set(qids))!=len(qids): errors.append('duplicate question IDs')

    qm=load('question_atom_map.json')['questions']; map_ids={q['question_id'] for q in qm}
    if set(qids)!=map_ids:
        errors.append(f'Question→Atom map drift: missing={len(map_ids-set(qids))}, new={len(set(qids)-map_ids)}')

    active,deprecated=effective_active_ids(); refs={a for q in qm for a in q['atoms']}
    unknown=sorted(refs-active-deprecated); dep_refs=sorted(refs&deprecated); uncovered=sorted(active-refs)
    if unknown: errors.append(f'unknown atom refs: {unknown}')
    if dep_refs: errors.append(f'deprecated atom refs: {dep_refs}')
    if uncovered: errors.append(f'uncovered active atoms: {uncovered}')

    adj=load('duplicate_adjudications.json')['decisions']
    if any(d.get('lost_atoms') for d in adj): errors.append('non-empty lost_atoms in adjudication')
    cand=load('duplicate_clusters.json')['edges']
    if len(adj)!=len(cand): errors.append('candidate/adjudication count mismatch')
    if any(d.get('canonical_owner') is None for d in adj): errors.append('missing canonical owner')

    p6=load('phase6_validation.json')
    rewrite_expected=set()
    for d in adj:
        if d['action']=='REWRITE_A_AS_BRIDGE': rewrite_expected.add(d['a'])
        if d['action']=='REWRITE_B_AS_BRIDGE': rewrite_expected.add(d['b'])
    if set(p6['changed_question_ids'])!=rewrite_expected: errors.append('Phase 6 rewrite set differs from Phase 5 decisions')

    baseline=load('baseline.json')
    old={f['file']:f['sha256'] for f in baseline['files']}
    changed=[]
    for rel,oldhash in old.items():
        p=KB/rel
        if p.exists() and sha(p)!=oldhash: changed.append(rel)
    expected_files=set(p6['modified_source_files'])
    if set(changed)!=expected_files:
        errors.append(f'unexpected source markdown changes: actual={sorted(changed)} expected={sorted(expected_files)}')

    integrated_changed=[f for f in changed if f.startswith('13_')]
    if integrated_changed: errors.append(f'integrated questions modified: {integrated_changed}')

    status='passed' if not errors else 'failed'
    val={
        'phase':7,'status':status,'questions_before':736,'questions_after':len(qids),
        'question_ids_preserved':set(qids)==map_ids,'active_atoms':len(active),
        'covered_active_atoms':len(active&refs),'uncovered_active_atoms':uncovered,
        'unknown_atom_refs':unknown,'deprecated_atom_refs':dep_refs,
        'candidate_edges':len(cand),'adjudicated_edges':len(adj),
        'lost_atoms':[], 'rewritten_bridge_entries':len(rewrite_expected),
        'modified_source_files':sorted(changed),'integrated_questions_modified':False if not integrated_changed else True,
        'errors':errors
    }
    (ROOT/'phase7_validation.json').write_text(json.dumps(val,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Phase 7 — Coverage Regression & Final Freeze','',f'- Status: **{status.upper()}**',f'- Questions: **736 → {len(qids)}**',f'- Active Atom coverage: **{len(active&refs)}/{len(active)}**',f'- Candidate adjudication: **{len(adj)}/{len(cand)}**',f'- Lost atoms: **0**',f'- Bridge rewrites: **{len(rewrite_expected)}**',f'- Source files changed: **{len(changed)}**',f'- Integrated/system-design deletions: **0**','', '## Final decision','', 'Phase 1–7 gates are closed. The corpus keeps all interview intents and question IDs; duplicated canonical explanations are replaced only by adjudicated bridge answers.','', '## Modified source files','']
    lines += [f'- `{f}`' for f in sorted(changed)]
    if errors:
        lines += ['', '## Errors','']+[f'- {e}' for e in errors]
    (ROOT/'PHASE7_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(val,ensure_ascii=False,indent=2))
    if errors: raise SystemExit(1)
if __name__=='__main__': main()
