#!/usr/bin/env python3
"""Vault audit: broken wiki-links, broken relative md links, orphan notes, size stats."""
import os
import re
import sys
import urllib.parse
from collections import defaultdict

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".obsidian", ".claudian", ".git", ".trash", "node_modules"}

md_files = []
for root, dirs, files in os.walk(VAULT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in files:
        if f.endswith(".md"):
            md_files.append(os.path.join(root, f))

# Map basename (without .md) -> list of paths, for wiki-link resolution
name_map = defaultdict(list)
relpath_set = set()
for p in md_files:
    rel = os.path.relpath(p, VAULT)
    relpath_set.add(rel)
    name_map[os.path.splitext(os.path.basename(p))[0]].append(rel)

wiki_re = re.compile(r"(?<!\!)\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
embed_re = re.compile(r"\!\[\[([^\]\|#]+)")
mdlink_re = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)")

def strip_code(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    return text

broken_wiki = []
broken_rel = []
inbound = defaultdict(int)

for p in md_files:
    rel = os.path.relpath(p, VAULT)
    with open(p, encoding="utf-8", errors="replace") as fh:
        text = strip_code(fh.read())
    for m in wiki_re.finditer(text):
        target = m.group(1).strip()
        if not target:
            continue
        # resolve: by basename or by path
        base = os.path.splitext(os.path.basename(target))[0]
        if base in name_map:
            for t in name_map[base]:
                inbound[t] += 1
        else:
            # try as path relative to vault
            cand = target if target.endswith(".md") else target + ".md"
            if cand in relpath_set:
                inbound[cand] += 1
            else:
                broken_wiki.append((rel, target))
    for m in mdlink_re.finditer(text):
        href = m.group(1)
        if href.startswith(("http://", "https://", "mailto:", "#", "obsidian://")):
            continue
        if href.startswith("/"):
            continue  # absolute local paths: report separately? skip
        href = urllib.parse.unquote(href.split("#")[0])
        if not href:
            continue
        target_abs = os.path.normpath(os.path.join(os.path.dirname(p), href))
        if not os.path.exists(target_abs):
            broken_rel.append((rel, m.group(1)))
        elif target_abs.endswith(".md"):
            inbound[os.path.relpath(target_abs, VAULT)] += 1

print(f"TOTAL_MD {len(md_files)}")
print(f"\n== BROKEN WIKI LINKS ({len(broken_wiki)}) ==")
for src, t in broken_wiki:
    print(f"{src}\t[[{t}]]")
print(f"\n== BROKEN RELATIVE LINKS ({len(broken_rel)}) ==")
for src, t in broken_rel:
    print(f"{src}\t({t})")

orphans = [r for r in sorted(relpath_set) if inbound[r] == 0
           and not os.path.basename(r).startswith(("README", "INDEX"))]
print(f"\n== ORPHAN NOTES (no inbound links, {len(orphans)}) ==")
for r in orphans:
    print(r)

sizes = sorted(((os.path.getsize(os.path.join(VAULT, r)), r) for r in relpath_set), reverse=True)
print("\n== LARGEST 15 ==")
for s, r in sizes[:15]:
    print(f"{s//1024:6d}K  {r}")
print("\n== SMALLEST 25 (possible stubs) ==")
for s, r in sizes[-25:]:
    print(f"{s:6d}B  {r}")
