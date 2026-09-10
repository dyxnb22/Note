#!/usr/bin/env python3
"""Extract numbered questions without changing source Markdown. --check verifies artifacts."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parent
HEADING = re.compile(r'^(#{1,6})\s+(.+?)\s*$')
QUESTION = re.compile(r'^(\d+)\.\s+(.+)$')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def extract():
    inventory, files, errors = [], [], []
    for path in sorted(ROOT.rglob('*.md')):
        if AUDIT in path.parents:
            continue
        rel = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        lines = raw.decode('utf-8').splitlines()
        top = rel.split('/')[0]
        layer = ('review' if top.startswith('00_') else
                 'deepening' if top.startswith('12_') else
                 'integrated' if top.startswith('13_') else
                 'supplement' if '面经补充' in path.name else 'core')
        excluded = 'review' if layer == 'review' else 'navigation' if path.name == 'README.md' else None
        headings, fence = [], None
        for index, line in enumerate(lines):
            marker = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', line)
            if marker:
                token, suffix = marker.groups()
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence) and not suffix.strip():
                    fence = None
                continue
            if fence is None:
                match = HEADING.match(line)
                if match:
                    headings.append((index, len(match[1]), match[2]))
        if fence:
            errors.append(f'{rel}: unclosed code fence')
        numbers, section = [], ''
        for pos, (index, depth, title) in enumerate(headings):
            match = QUESTION.match(title)
            if depth <= 2:
                section = title
            if not match:
                if depth == 3 and not excluded:
                    errors.append(f'{rel}:{index+1}: unrecognized question heading')
                continue
            if depth != 3:
                errors.append(f'{rel}:{index+1}: numbered heading outside level 3')
                continue
            numbers.append(int(match[1]))
            if excluded:
                continue
            end = next((i for i, d, _ in headings[pos+1:] if d <= depth), len(lines))
            start = next((i for i in range(index+1, end) if lines[i].strip()), None)
            if start is None:
                errors.append(f'{rel}:{index+1}: empty answer')
            inventory.append(dict(
                question_id=f'Q::{rel}::{int(match[1])}', file=rel,
                number=int(match[1]), title=match[2], layer=layer, section=section,
                answer_start=lines[start] if start is not None else '',
                status='active', heading_line=index+1,
                answer_start_line=start+1 if start is not None else None,
                answer_end_line=end,
                answer_sha256=digest('\n'.join(lines[index+1:end]).encode('utf-8'))))
        if not excluded and not numbers:
            errors.append(f'{rel}: no questions detected')
        if numbers and numbers != list(range(1, len(numbers)+1)):
            errors.append(f'{rel}: non-contiguous or duplicate numbering')
        files.append(dict(file=rel, sha256=digest(raw), layer=layer,
                          exclusion_reason=excluded, numbered_question_count=len(numbers)))
    ids = [q['question_id'] for q in inventory]
    duplicates = [q for q, n in collections.Counter(ids).items() if n > 1]
    scanned = sum(f['numbered_question_count'] for f in files if not f['exclusion_reason'])
    if duplicates or scanned != len(inventory):
        errors.append('duplicate IDs or count mismatch')
    report = dict(phase=1, status='passed' if not errors else 'failed',
                  markdown_file_count=len(files),
                  question_file_count=sum(not f['exclusion_reason'] for f in files),
                  excluded_files=[f for f in files if f['exclusion_reason']],
                  scanned_numbered_questions=scanned, inventory_count=len(inventory),
                  question_coverage_percent=100 if scanned == len(inventory) and not errors else None,
                  counts_by_layer=dict(sorted(collections.Counter(q['layer'] for q in inventory).items())),
                  duplicate_question_ids=duplicates, errors=errors)
    return inventory, files, report


def serialized(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    inventory, files, report = extract()
    baseline_path = AUDIT / 'baseline.json'
    if baseline_path.exists():
        baseline = json.loads(baseline_path.read_text())
        if baseline['files'] != files:
            raise SystemExit('Source Markdown differs from immutable Phase 1 baseline.')
    elif args.check:
        raise SystemExit('Missing baseline.json')
    else:
        baseline = dict(phase=1, source_commit=subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            branch=subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
            question_count=len(inventory), files=files)
        baseline_path.write_text(serialized(baseline))
    if report['errors']:
        raise SystemExit(serialized(report))
    for name, value in [('question_inventory.json', inventory), ('inventory_validation.json', report)]:
        path = AUDIT / name
        if args.check:
            if not path.exists() or path.read_text() != serialized(value):
                raise SystemExit(f'Stale or missing artifact: {name}')
        else:
            path.write_text(serialized(value))
    print(serialized(report))


if __name__ == '__main__':
    main()
