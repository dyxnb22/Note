#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
obj = json.loads((ROOT / 'phase3_review.json').read_text(encoding='utf-8'))
lines = ['# Phase 3 Compact Review', '', f'Pending: {obj.get("pending_count", 0)}', '', '| Question | Title | Top candidates |', '|---|---|---|']
for r in obj.get('reviews', []):
    cands = '; '.join(f"{c['atom_id']}={c['name']}({c['score']:.3f})" for c in r.get('top_candidates', [])[:4])
    title = r.get('title','').replace('|','\\|').replace('\n',' ')
    lines.append(f"| `{r['question_id']}` | {title} | {cands} |")
(ROOT / 'PHASE3_COMPACT_REVIEW.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f"wrote {len(obj.get('reviews', []))} pending rows")
