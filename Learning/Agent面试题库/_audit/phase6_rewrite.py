#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
KB=ROOT.parent

REWRITES={
 'Q::08_评测与可观测/评测、轨迹与线上故障面经补充.md::1': '答：完整的“离线评测 / 在线评测 / 生产监控”职责边界见 [[评测与可观测性#38. 离线评测、在线评测和生产监控分别回答什么问题？|主线第 38 题]]。本题只补充两个面试维度：离线使用冻结任务与环境，反馈快、可重复；在线面对真实分布、权限、并发和用户行为，反馈更慢但更接近业务价值。线上 Badcase 需经抽样、标注和归因后再进入稳定回归集。',
 'Q::08_评测与可观测/评测、轨迹与线上故障面经补充.md::7': '答：LLM-as-Judge 的基础优缺点、Rubric、多评委与人工校准见 [[评测与可观测性#10. LLM-as-a-Judge 的优点、问题和改进方法是什么？|主线第 10 题]]。本题只补充验证器分工：格式、数值、代码测试、权限和真实工具状态优先程序验证；开放式质量再交给 Judge；高风险或评审分歧进入人工复核。',
 'Q::04_Tool与协议/Tool Calling与MCP.md::10': '答：用户侧预览、确认、撤销和回滚的完整安全规则见 [[../07_可靠性与安全/可靠性与安全#20. 如何让用户预览、确认、撤销和回滚 Agent 动作？|可靠性与安全第 20 题]]。Tool 层只保留执行合同差异：动作先生成结构化预览并持久化 `waiting_human`，批准后绑定 `approval_id`，执行前再次校验权限和资源版本；可逆动作保存反向操作或快照，不可逆动作进入补偿或人工对账。',
 'Q::09_工程化与系统设计/系统设计与取舍面经补充.md::9': '答：工具侧的过滤、字段选择、分页/游标、带引用摘要与继续读取机制见 [[../04_Tool与协议/Tool Calling与MCP#7. 工具返回过大时如何截断、分页或摘要？|Tool Calling 第 7 题]]。系统设计层额外关注 Context/Token 预算、对象存储引用和 Trace：大结果不要全量塞进模型，摘要必须可回源，后续追问按游标或引用增量读取，且权限与版本校验不能因摘要缓存而省略。',
 'Q::12_课程深化/08_评测实验与项目表达/评测实验与项目表达.md::19': '答：MCP 中 Tool、Resource、Prompt 的完整定义与 Server 组织方式见 [[../../../04_Tool与协议/Tool Calling与MCP#22. MCP Server 如何设计？工具、资源和 Prompt 如何组织？|Tool Calling 与 MCP 第 22 题]]。本题作为项目表达检查点只强调边界：Tool 是可执行动作，Resource 是读取型数据，Prompt 是可复用模板；MCP Server 暴露能力，但不拥有宿主的授权、审批、停止与结果验收。',
}

def parse_qid(qid):
    body=qid[3:]
    file,num=body.rsplit('::',1)
    return file,int(num)

def replace_answer(text,num,new_answer):
    # Preserve heading/title and replace only the answer block up to the next
    # level-3-or-higher section boundary. Targeted answers are paragraph blocks.
    pat=re.compile(rf'(?ms)(^### {num}\. [^\n]+\n\n)(答：.*?)(?=\n\n(?:### |## |---|\*\*追问))')
    m=pat.search(text)
    if not m:
        # Last question before EOF/next non-heading block fallback.
        pat=re.compile(rf'(?ms)(^### {num}\. [^\n]+\n\n)(答：.*?)(?=\n\n## |\Z)')
        m=pat.search(text)
    if not m: raise SystemExit(f'cannot locate answer for question {num}')
    return text[:m.start(2)] + new_answer + text[m.end(2):]

def main():
    adj=json.loads((ROOT/'duplicate_adjudications.json').read_text(encoding='utf-8'))['decisions']
    expected=set()
    for d in adj:
        if d['action']=='REWRITE_A_AS_BRIDGE': expected.add(d['a'])
        elif d['action']=='REWRITE_B_AS_BRIDGE': expected.add(d['b'])
    if expected!=set(REWRITES):
        raise SystemExit(f'rewrite decision mismatch: expected={sorted(expected)} configured={sorted(REWRITES)}')

    changed=[]; before_counts={}; after_counts={}
    byfile={}
    for qid,new_answer in REWRITES.items():
        file,num=parse_qid(qid); byfile.setdefault(file,[]).append((num,qid,new_answer))
    for file,items in byfile.items():
        p=KB/file
        text=p.read_text(encoding='utf-8')
        before_counts[file]=len(re.findall(r'(?m)^### \d+\. ',text))
        new=text
        for num,qid,answer in sorted(items,reverse=True):
            new=replace_answer(new,num,answer)
            changed.append(qid)
        after_counts[file]=len(re.findall(r'(?m)^### \d+\. ',new))
        if before_counts[file]!=after_counts[file]: raise SystemExit(f'question heading count changed: {file}')
        p.write_text(new,encoding='utf-8')

    val={'phase':6,'status':'passed','rewrite_questions':len(changed),'modified_source_files':sorted(byfile),'question_heading_counts_preserved':before_counts==after_counts,'deleted_questions':0,'changed_question_ids':sorted(changed),'errors':[]}
    (ROOT/'phase6_validation.json').write_text(json.dumps(val,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Phase 6 — Adjudicated Rewrite','',f"- Rewritten bridge entries: **{len(changed)}**",f"- Modified source files: **{len(byfile)}**",'- Deleted questions: **0**','- Question headings renumbered: **0**','', '仅改写 Phase 5 明确裁决为 bridge 的答案；canonical question 保持完整答案。','', '## Rewritten entries','']
    lines += [f'- `{q}`' for q in sorted(changed)]
    (ROOT/'PHASE6_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(val,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
