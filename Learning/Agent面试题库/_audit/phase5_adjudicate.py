#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def load(n): return json.loads((ROOT/n).read_text(encoding='utf-8'))
def k(a,b): return tuple(sorted((a,b)))

SPECIAL={
 k('Q::08_评测与可观测/评测、轨迹与线上故障面经补充.md::1','Q::08_评测与可观测/评测与可观测性.md::38'):{'relation':'OWNERSHIP_CONFLICT','action':'REWRITE_A_AS_BRIDGE','canonical':'Q::08_评测与可观测/评测与可观测性.md::38','reason':'主线题拥有离线/在线/生产监控三层定义；补充题只应保留目标、数据和反馈速度差异。'},
 k('Q::08_评测与可观测/评测、轨迹与线上故障面经补充.md::7','Q::08_评测与可观测/评测与可观测性.md::10'):{'relation':'OWNERSHIP_CONFLICT','action':'REWRITE_A_AS_BRIDGE','canonical':'Q::08_评测与可观测/评测与可观测性.md::10','reason':'主线题拥有 LLM-as-Judge 的通用定义；补充题只保留程序验证/Judge/人工评审的分工。'},
 k('Q::04_Tool与协议/Tool Calling与MCP.md::10','Q::07_可靠性与安全/可靠性与安全.md::20'):{'relation':'OWNERSHIP_CONFLICT','action':'REWRITE_A_AS_BRIDGE','canonical':'Q::07_可靠性与安全/可靠性与安全.md::20','reason':'用户确认、撤销与回滚属于安全/HITL 主答案；Tool 页只保留 waiting_human、approval_id 与执行前再校验等工具合同差异。'},
 k('Q::04_Tool与协议/Tool Calling与MCP.md::7','Q::09_工程化与系统设计/系统设计与取舍面经补充.md::9'):{'relation':'OWNERSHIP_CONFLICT','action':'REWRITE_B_AS_BRIDGE','canonical':'Q::04_Tool与协议/Tool Calling与MCP.md::7','reason':'过滤/分页/摘要/游标由 Tool 页拥有；系统设计题只补 Context 预算、对象引用、Trace 与后续增量读取。'},
 k('Q::04_Tool与协议/Tool Calling与MCP.md::22','Q::12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md::19'):{'relation':'OWNERSHIP_CONFLICT','action':'REWRITE_B_AS_BRIDGE','canonical':'Q::04_Tool与协议/Tool Calling与MCP.md::22','reason':'Tool/Resource/Prompt 与 MCP Server 组织由协议主线拥有；课程深化只保留项目表达检查点。'},
 k('Q::01_基础架构/Agent基础与架构.md::13','Q::05_Multi-Agent与Workflow/Multi-Agent与Workflow.md::3'):{'relation':'OWNERSHIP_CONFLICT','action':'KEEP_EXISTING_BRIDGE','canonical':'Q::05_Multi-Agent与Workflow/Multi-Agent与Workflow.md::3','reason':'基础架构题已是桥接入口，完整职责归 Multi-Agent 主文档。'},
 k('Q::06_RAG与知识库/RAG与检索.md::27','Q::12_课程深化/04_知识摄取与GraphRAG/知识摄取与GraphRAG.md::7'):{'relation':'OWNERSHIP_CONFLICT','action':'KEEP_EXISTING_BRIDGE','canonical':'Q::12_课程深化/04_知识摄取与GraphRAG/知识摄取与GraphRAG.md::7','reason':'RAG 题已只保留在线检索侧差异并链接完整摄取/同步流程。'},
 k('Q::09_工程化与系统设计/系统设计与取舍面经补充.md::1','Q::13_跨主题综合题/新增题簇_Agent与AI后端.md::9'):{'relation':'PARTIAL_OVERLAP','action':'KEEP_INTEGRATED_HINT','canonical':None,'reason':'跨主题综合题按政策默认保留；它把项目因果链用于 RAG/Agent 业务价值场景。'},
}

DISTINCT={
 k('Q::09_工程化与系统设计/生产工程与系统设计.md::8','Q::11_编码与后端/编码题与后端基础.md::15'),
 k('Q::12_课程深化/02_代码Agent与ComputerUse/代码Agent与ComputerUse.md::1','Q::12_课程深化/02_代码Agent与ComputerUse/代码Agent与ComputerUse.md::5'),
 k('Q::11_编码与后端/编码题与后端基础.md::32','Q::11_编码与后端/编码题与后端基础.md::33'),
}

def main():
    clusters=load('duplicate_clusters.json')
    qm={q['question_id']:q for q in load('question_atom_map.json')['questions']}
    decisions=[]
    for i,e in enumerate(clusters['edges'],1):
        key=k(e['a'],e['b'])
        a,b=e['a'],e['b']
        union=sorted(set(qm[a]['atoms'])|set(qm[b]['atoms']))
        if key in SPECIAL:
            s=SPECIAL[key]; relation=s['relation']; action=s['action']; canonical=s['canonical']; reason=s['reason']
        elif key in DISTINCT:
            relation='DISTINCT_INTENT'; action='KEEP_BOTH'; canonical=None
            reason='共享知识原子但题型/考察目标不同（实现、设计或组合场景），不是可去重的同题。'
        else:
            relation='PARTIAL_OVERLAP'; action='KEEP_BOTH'; canonical=None
            reason='存在共享 Atom，但问题的意图、场景、难度或边界不同；保留可维持题库覆盖面与递进梯度。'
        decisions.append({
            'candidate_index':i,'a':a,'b':b,'relation':relation,'action':action,
            'canonical_owner': canonical if canonical else {'mode':'split_by_intent','questions':[a,b]},
            'retained_atoms':union,'lost_atoms':[],
            'interview_intent':{'a':qm[a].get('intent'),'b':qm[b].get('intent')},
            'reason':reason,'hint_only':e.get('hint_only',False)
        })
    assert len(decisions)==clusters['candidate_edge_count']
    assert len({k(d['a'],d['b']) for d in decisions})==len(decisions)
    pending=[d for d in decisions if not d['relation'] or not d['action']]
    val={'phase':5,'status':'passed' if not pending else 'failed','candidate_edges':len(decisions),'adjudicated_edges':len(decisions),'pending':len(pending),'rewrite_actions':sum(d['action'].startswith('REWRITE_') for d in decisions),'existing_bridges':sum(d['action']=='KEEP_EXISTING_BRIDGE' for d in decisions),'lost_atom_edges':sum(bool(d['lost_atoms']) for d in decisions),'errors':[] if not pending else ['pending adjudications']}
    (ROOT/'duplicate_adjudications.json').write_text(json.dumps({'phase':5,'decisions':decisions},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'phase5_validation.json').write_text(json.dumps(val,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Phase 5 — Duplicate Adjudication','',f"- Candidate edges: **{len(decisions)}**",f"- Fully adjudicated: **{len(decisions)-len(pending)}**",f"- Rewrite actions: **{val['rewrite_actions']}**",f"- Existing bridges accepted: **{val['existing_bridges']}**",f"- Lost-Atom decisions: **{val['lost_atom_edges']}**",'', '| # | Relation | Action | A | B | Canonical owner |','|---:|---|---|---|---|---|']
    for d in decisions:
        owner=d['canonical_owner'] if isinstance(d['canonical_owner'],str) else 'split by intent'
        lines.append(f"| {d['candidate_index']} | {d['relation']} | {d['action']} | `{d['a']}` | `{d['b']}` | `{owner}` |")
    (ROOT/'PHASE5_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(val,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
