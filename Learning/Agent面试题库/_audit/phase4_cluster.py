#!/usr/bin/env python3
from __future__ import annotations
import json, re
from difflib import SequenceMatcher
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parent

def load(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8'))

def norm_title(s):
    s = s.lower()
    s = re.sub(r'[`*_#\[\]()（）【】<>“”"\'，。！？、：；/\\|+-]', ' ', s)
    s = re.sub(r'\b(如何|为什么|什么是|怎么|怎样|请|一个|一种|哪些|分别|应该|可以|是否|有什么|是什么)\b', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def title_sim(a,b):
    return SequenceMatcher(None, norm_title(a), norm_title(b)).ratio()

def kind(file):
    if file.startswith('13_'): return 'integrated'
    if file.startswith('12_'): return 'deepening'
    if '补充' in file: return 'supplement'
    return 'core'

def topdir(file): return file.split('/',1)[0]

def main():
    inv = {q['question_id']: q for q in load('question_inventory.json')}
    mp = load('question_atom_map.json')['questions']
    qs=[]
    for m in mp:
        q=inv[m['question_id']]
        qs.append({
            'question_id':m['question_id'],'file':q['file'],'title':q['title'],
            'layer':q.get('layer',m.get('layer','core')),'kind':kind(q['file']),
            'atoms':set(m['atoms']),'primary_atom':m['primary_atom']
        })

    edges=[]
    for i,a in enumerate(qs):
        for b in qs[i+1:]:
            inter=a['atoms'] & b['atoms']
            if not inter: continue
            uni=a['atoms'] | b['atoms']
            jac=len(inter)/len(uni)
            contain=len(inter)/min(len(a['atoms']),len(b['atoms']))
            ts=title_sim(a['title'],b['title'])
            same_primary=a['primary_atom']==b['primary_atom']
            same_domain=topdir(a['file'])==topdir(b['file'])
            integrated='integrated' in (a['kind'],b['kind'])
            deep_bridge=('deepening' in (a['kind'],b['kind'])) and not (a['kind']==b['kind']=='deepening')

            # Conservative candidate gate: Atom overlap is mandatory; weak one-atom
            # overlaps need substantially similar wording. Integrated questions are
            # hint-only even when admitted.
            admitted=False
            reasons=[]
            if a['atoms']==b['atoms'] and ts>=0.42:
                admitted=True; reasons.append('same_atom_set')
            if same_primary and contain>=0.67 and ts>=0.46:
                admitted=True; reasons.append('same_primary_containment')
            if len(inter)>=2 and contain>=0.75 and ts>=0.40:
                admitted=True; reasons.append('multi_atom_containment')
            if len(a['atoms'])==len(b['atoms'])==1 and same_primary and ts>=0.58:
                admitted=True; reasons.append('single_atom_title_match')
            if same_domain and same_primary and ts>=0.62:
                admitted=True; reasons.append('same_domain_primary_title')
            if deep_bridge and same_primary and contain>=0.5 and ts>=0.50:
                admitted=True; reasons.append('core_deepening_bridge')
            if integrated and ts>=0.50 and contain>=0.5:
                admitted=True; reasons.append('integrated_hint')
            if not admitted: continue

            score=round(0.45*contain+0.25*jac+0.30*ts,4)
            edges.append({
                'a':a['question_id'],'b':b['question_id'],'score':score,
                'title_similarity':round(ts,4),'jaccard':round(jac,4),
                'containment':round(contain,4),'shared_atoms':sorted(inter),
                'same_primary':same_primary,'same_domain':same_domain,
                'kinds':[a['kind'],b['kind']], 'hint_only':integrated,
                'reasons':reasons
            })
    edges.sort(key=lambda x:(-x['score'],x['a'],x['b']))

    # Connected components are review clusters, not automatic merge groups.
    adj=defaultdict(set)
    for e in edges:
        adj[e['a']].add(e['b']); adj[e['b']].add(e['a'])
    seen=set(); comps=[]
    for qid in sorted(adj):
        if qid in seen: continue
        stack=[qid]; seen.add(qid); nodes=[]
        while stack:
            x=stack.pop(); nodes.append(x)
            for y in adj[x]:
                if y not in seen: seen.add(y); stack.append(y)
        sub=[e for e in edges if e['a'] in nodes and e['b'] in nodes]
        comps.append({'cluster_id':f'C{len(comps)+1:03d}','questions':sorted(nodes),'edge_count':len(sub),'max_score':max(e['score'] for e in sub),'hint_only':all(e['hint_only'] for e in sub)})

    out={'phase':4,'question_count':len(qs),'candidate_edge_count':len(edges),'cluster_count':len(comps),'clusters':comps,'edges':edges}
    (ROOT/'duplicate_clusters.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    val={'phase':4,'status':'passed','question_count':len(qs),'candidate_edge_count':len(edges),'cluster_count':len(comps),'duplicate_edge_keys_unique':len({tuple(sorted((e['a'],e['b']))) for e in edges})==len(edges),'errors':[]}
    (ROOT/'phase4_validation.json').write_text(json.dumps(val,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    byid={q['question_id']:q for q in qs}
    lines=['# Phase 4 — Duplicate Candidate Clustering','',f'- Questions: **{len(qs)}**',f'- Candidate edges: **{len(edges)}**',f'- Review clusters: **{len(comps)}**','', '> Phase 4 只生成候选，不做删除/合并裁决。`13_跨主题综合题` 仅作为重复提示，默认不删。','', '## Candidate edges','', '| # | Score | A | B | Shared atoms | Hint only |','|---:|---:|---|---|---|---|']
    for n,e in enumerate(edges,1):
        qa,qb=byid[e['a']],byid[e['b']]
        def esc(s): return s.replace('|','\\|').replace('\n',' ')
        lines.append(f"| {n} | {e['score']:.3f} | `{e['a']}` — {esc(qa['title'])} | `{e['b']}` — {esc(qb['title'])} | {', '.join(e['shared_atoms'])} | {'yes' if e['hint_only'] else 'no'} |")
    (ROOT/'PHASE4_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(val,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
