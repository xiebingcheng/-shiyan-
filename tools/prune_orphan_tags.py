#!/usr/bin/env python3
"""
Prune orphan tag pages under tags/ and <lang>/tags/.

A tag page is kept iff its tag value appears in the front-matter `tags:`
list of at least one post under the matching language tree.

Category pages (categories/, <lang>/categories/) are NOT touched here —
they are driven by _data/categories-i18n.yml and must stay even when
a category temporarily has zero posts.

Usage:
    python tools/prune_orphan_tags.py --dry-run
    python tools/prune_orphan_tags.py
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

LANGS = [
    ("zh-CN", "_posts",         "tags"),
    ("en",    "en/_posts",      "en/tags"),
    ("ru",    "ru/_posts",      "ru/tags"),
    ("fr",    "fr/_posts",      "fr/tags"),
    ("es",    "es/_posts",      "es/tags"),
    ("id",    "id/_posts",      "id/tags"),
    ("ar",    "ar/_posts",      "ar/tags"),
]

FM_RE = re.compile(r'^---\s*\n(.*?\n)---\s*\n', re.DOTALL)
LIST_ITEM_RE = re.compile(r'^\s*-\s*(.+?)\s*$')
KV_RE = re.compile(r'^([A-Za-z_][\w-]*)\s*:\s*(.*)$')


def collect_tags(posts_dir: Path) -> set[str]:
    """Return the union of `tags:` values across all posts in posts_dir."""
    tags: set[str] = set()
    if not posts_dir.exists():
        return tags
    for p in sorted(posts_dir.glob("*.md")):
        m = FM_RE.match(p.read_text(encoding="utf-8"))
        if not m:
            continue
        fm = m.group(1)
        # locate "tags:" key, gather its list items (next non-empty indented lines)
        in_tags = False
        for line in fm.splitlines():
            if not in_tags:
                km = KV_RE.match(line)
                if km and km.group(1) == "tags":
                    in_tags = True
                    inline = km.group(2).strip()
                    if inline.startswith("[") and inline.endswith("]"):
                        for raw in inline[1:-1].split(","):
                            t = raw.strip().strip('"').strip("'")
                            if t:
                                tags.add(t)
                continue
            # in_tags = True
            stripped = line.strip()
            if not stripped:
                continue
            if not line.startswith((" ", "\t")):
                in_tags = False
                continue
            li = LIST_ITEM_RE.match(line)
            if li:
                t = li.group(1).strip().strip('"').strip("'")
                if t:
                    tags.add(t)
    return tags


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    repo_root = Path.cwd()
    total_kept = 0
    total_removed = 0
    to_remove: list[str] = []

    for lang, posts_rel, tags_rel in LANGS:
        posts_dir = repo_root / posts_rel
        tags_dir = repo_root / tags_rel
        valid = collect_tags(posts_dir)

        existing: set[str] = set()
        if tags_dir.exists():
            for p in tags_dir.glob("*.md"):
                existing.add(p.stem)  # tag value, no .md suffix

        keep = valid & existing
        orphan = existing - valid

        print(f"[{lang}] posts={len(list(posts_dir.glob('*.md'))) if posts_dir.exists() else 0}  "
              f"valid tags={len(valid)}  existing={len(existing)}  "
              f"keep={len(keep)}  orphan={len(orphan)}")

        for name in sorted(orphan):
            to_remove.append(str(tags_dir / f"{name}.md"))
            total_removed += 1
        total_kept += len(keep)

    if not to_remove:
        print("\nNothing to remove.")
        return 0

    print(f"\nWill remove {total_removed} orphan tag file(s). Keeping {total_kept}.")
    if args.dry_run:
        print("[DRY RUN] No changes made.")
        return 0

    res = subprocess.run(
        ["git", "rm", "-f", "--", *to_remove],
        cwd=repo_root,
    )
    if res.returncode != 0:
        print("[ERROR] git rm failed", file=sys.stderr)
        return res.returncode
    print(f"Removed {total_removed} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
