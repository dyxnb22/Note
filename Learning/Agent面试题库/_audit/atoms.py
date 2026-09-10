#!/usr/bin/env python3
"""Phase 2 registry authoring and structural validation (no source Markdown writes)."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REGISTRY = HERE / 'atom_registry.json'
LOG = HERE / 'atomization_log.json'
INVENTORY = json.loads((HERE / 'question_inventory.json').read_text())


def read(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def normalize(value):
    return re.sub(r'[^\w]', '', unicodedata.normalize('NFKC', value).casefold())


def scope_files(scope):
    parts = scope.split('/')
    return sorted({q['file'] for q in INVENTORY if all(
        actual.startswith(expected + '_') for actual, expected in zip(q['file'].split('/'), parts))
        and (len(parts) > 1 or not scope == '12')})


def validate(atoms):
    errors, labels = [], {}
    known = {q['question_id'] for q in INVENTORY}
    ids = [a['id'] for a in atoms]
    if len(ids) != len(set(ids)):
        errors.append('Duplicate IDs')
    owners = {f'{n:02}' for n in range(1, 14)} | {f'12/{n:02}' for n in range(1, 9)}
    for a in atoms:
        missing = False
        for field in ['id', 'canonical_name', 'definition', 'domain', 'aliases', 'status', 'canonical_owner', 'source_question_ids']:
            if field not in a:
                errors.append(f'{a.get("id")}: missing {field}')
                missing = True
        if missing:
            continue
        for field in ['id', 'canonical_name', 'definition', 'domain', 'status', 'canonical_owner']:
            if not isinstance(a[field], str) or not a[field].strip():
                errors.append(f'{a.get("id")}: invalid {field}')
        if not isinstance(a['aliases'], list) or not all(isinstance(s, str) and s.strip() for s in a['aliases']):
            errors.append(f'{a["id"]}: invalid aliases')
            continue
        if not re.fullmatch(r'[A-Z][A-Z0-9]*-\d{3}', a['id']):
            errors.append(f'Invalid ID: {a["id"]}')
        if a['status'] not in ['active', 'needs_review']:
            errors.append(f'Invalid status: {a["id"]}')
        if not a['source_question_ids'] or set(a['source_question_ids']) - known:
            errors.append(f'Invalid source references: {a["id"]}')
        if len(a['source_question_ids']) != len(set(a['source_question_ids'])):
            errors.append(f'Duplicate source references: {a["id"]}')
        if a['domain'] != a['id'].split('-')[0].lower():
            errors.append(f'Domain/ID mismatch: {a["id"]}')
        owner = a['canonical_owner']
        if owner.startswith('external:'):
            target = ROOT.parent / owner.split(':', 1)[1]
            if not target.exists() and not target.with_suffix('.md').exists():
                errors.append(f'Missing external owner: {a["id"]}: {owner}')
        elif owner not in owners or not scope_files(owner):
            errors.append(f'Unknown canonical owner: {a["id"]}: {owner}')
        candidates = a.get('candidate_existing_atoms', [])
        if set(candidates) - set(ids) or a['id'] in candidates:
            errors.append(f'Invalid candidate atom references: {a["id"]}')
        if a['status'] == 'needs_review' and not a.get('review_reason'):
            errors.append(f'Missing review reason: {a["id"]}')
        for name in [a['canonical_name'], *a['aliases']]:
            key = normalize(name)
            if key in labels and labels[key] != a['id']:
                errors.append(f'Name/alias collision: {name}: {labels[key]} / {a["id"]}')
            labels[key] = a['id']
    definitions = Counter(a['definition'] for a in atoms)
    errors.extend(f'Duplicate definition: {d}' for d, n in definitions.items() if n > 1)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['read', 'add', 'check'])
    parser.add_argument('scope', nargs='?')
    parser.add_argument('--reuse', default='')
    parser.add_argument('--note', default='')
    args = parser.parse_args()
    baseline = read(HERE / 'baseline.json', {})
    sources = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in ROOT.rglob('*.md') if HERE not in p.parents}
    if sources != {f['file']: f['sha256'] for f in baseline.get('files', [])}:
        raise SystemExit('Source Markdown differs from Phase 1 baseline; stop atom authoring.')
    atoms = read(REGISTRY, [])
    log = read(LOG, [])
    if args.command == 'read':
        print('FULL EXISTING REGISTRY (id | name | aliases | definition | owner)')
        for a in atoms:
            print(' | '.join([a['id'], a['canonical_name'], ', '.join(a['aliases']), a['definition'], a['canonical_owner']]))
        files = scope_files(args.scope)
        if not files:
            raise SystemExit('No matching source files')
        for i, f in enumerate(files, 1):
            print(f'\nSOURCE {i}: {f}\n{(ROOT / f).read_text()}')
        write(HERE / '.registry_read.json', dict(scope=args.scope, registry_sha256=fingerprint(atoms)))
    elif args.command == 'add':
        receipt = read(HERE / '.registry_read.json', {})
        if receipt != dict(scope=args.scope, registry_sha256=fingerprint(atoms)):
            raise SystemExit('Read full current registry and scope first')
        if any(b['scope'] == args.scope for b in log):
            raise SystemExit('Scope already processed')
        files = scope_files(args.scope)
        new = []
        for line in sys.stdin.read().splitlines():
            if not line.strip():
                continue
            atom_id, name, definition, aliases, owner, refs = line.split('|')
            sources = []
            for ref in refs.split(';'):
                file_index, numbers = ref.split(':')
                sources.extend(f'Q::{files[int(file_index)-1]}::{int(n)}' for n in numbers.split(','))
            new.append(dict(id=atom_id, canonical_name=name, definition=definition,
                            domain=atom_id.split('-')[0].lower(), aliases=aliases.split(';') if aliases else [],
                            status='active', canonical_owner=owner, source_question_ids=sources))
        reuse = args.reuse.split(',') if args.reuse else []
        if set(reuse) - {a['id'] for a in atoms}:
            raise SystemExit('Unknown reused atom IDs')
        errors = validate(atoms + new)
        if errors:
            raise SystemExit('\n'.join(errors))
        log.append(dict(scope=args.scope, existing_registry_sha256=fingerprint(atoms),
                        existing_atom_count=len(atoms), source_files=files,
                        source_question_ids=[q['question_id'] for q in INVENTORY if q['file'] in files],
                        reused_atoms=reuse, new_atoms=[a['id'] for a in new],
                        review_note=args.note))
        write(REGISTRY, atoms + new)
        write(LOG, log)
        (HERE / '.registry_read.json').unlink()
        print(f'{args.scope}: added {len(new)}, reused {len(reuse)}, registry total {len(atoms)+len(new)}')
    else:
        errors = validate(atoms)
        by_id = {a['id']: a for a in atoms}
        created = []
        for batch in log:
            if batch['source_files'] != scope_files(batch['scope']):
                errors.append(f'Scope source mismatch: {batch["scope"]}')
            expected_questions = [q['question_id'] for q in INVENTORY if q['file'] in batch['source_files']]
            if batch['source_question_ids'] != expected_questions:
                errors.append(f'Scope question mismatch: {batch["scope"]}')
            if batch['existing_atom_count'] != len(created) or batch['existing_registry_sha256'] != fingerprint(created):
                errors.append(f'Registry history mismatch: {batch["scope"]}')
            if set(batch['reused_atoms']) - {a['id'] for a in created}:
                errors.append(f'Unknown or not-yet-created reused atoms: {batch["scope"]}')
            for atom_id in batch['new_atoms']:
                if atom_id not in by_id:
                    errors.append(f'Unknown created atom: {atom_id}')
                    continue
                original = dict(by_id[atom_id])
                # Phase 2 final review may flag status, but does not rewrite definitions.
                original['status'] = 'active'
                original.pop('candidate_existing_atoms', None)
                original.pop('review_reason', None)
                created.append(original)
        if [a['id'] for a in created] != [a['id'] for a in atoms]:
            errors.append('Creation log does not match registry order/IDs')
        reviewed = [q for batch in log for q in batch['source_question_ids']]
        missing = sorted({q['question_id'] for q in INVENTORY} - set(reviewed))
        counts = Counter(reviewed)
        errors.extend(f'Duplicate scope review: {q}' for q,n in counts.items() if n > 1)
        report = dict(phase=2, structural_status='passed' if not errors else 'failed',
                      scope_complete=not missing, atom_count=len(atoms),
                      counts_by_domain=dict(sorted(Counter(a['domain'] for a in atoms).items())),
                      source_questions_read=len(set(reviewed)), inventory_count=len(INVENTORY),
                      atoms_with_valid_source_evidence=sum(bool(a['source_question_ids']) for a in atoms),
                      distinct_source_evidence_questions=len({q for a in atoms for q in a['source_question_ids']}),
                      pending_atom_reviews=[a['id'] for a in atoms if a['status'] == 'needs_review'],
                      missing_source_questions=missing, errors=errors,
                      limitations=['Source reading coverage is not Question-to-Atom mapping coverage.',
                                   'Semantic atom uniqueness requires review; exact name/alias checks alone cannot prove it.',
                                   'Knowledge coverage and orphan atoms are evaluated in Phase 3 and regression phases.'])
        write(HERE / 'atom_validation.json', report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if errors:
            raise SystemExit(1)


if __name__ == '__main__':
    main()
