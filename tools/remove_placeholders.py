#!/usr/bin/env python3
"""
Remove posts that carry BOTH the `placeholder: true` field in front matter
AND the `<!-- 此文章为占位文章 -->` comment after it. Idempotent.

Usage:
    python tools/remove_placeholders.py --dry-run   # show what would be removed
    python tools/remove_placeholders.py             # actually `git rm` them
"""
import argparse
import os
import subprocess
import sys

LANGS = [
    "_posts",
    "en/_posts",
    "ru/_posts",
    "fr/_posts",
    "es/_posts",
    "id/_posts",
    "ar/_posts",
]

FIELD = "placeholder: true"
COMMENT = "<!-- 此文章为占位文章 -->"
WINDOW = 2000  # chars from start of file (covers longest observed front matter)


def find_targets(repo_root: str) -> list[str]:
    targets: list[str] = []
    for rel_dir in LANGS:
        abs_dir = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(abs_dir):
            print(f"[WARN] missing dir: {rel_dir}", file=sys.stderr)
            continue
        for fname in sorted(os.listdir(abs_dir)):
            if not fname.endswith(".md"):
                continue
            p = os.path.join(abs_dir, fname)
            with open(p, "r", encoding="utf-8", newline="") as f:
                head = f.read(WINDOW)
            if FIELD in head and COMMENT in head:
                targets.append(p)
    return targets


def group_by_lang(paths: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in paths:
        parts = p.replace("\\", "/").split("/")
        # rel paths look like "_posts/foo.md" or "en/_posts/foo.md"
        if len(parts) >= 3 and parts[-2] == "_posts":
            lang = parts[-3] or "_posts"
        else:
            lang = parts[-2] if len(parts) >= 2 else "?"
        out.setdefault(lang, []).append(os.path.basename(p))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would be removed and exit")
    args = ap.parse_args()

    repo_root = os.getcwd()
    targets = find_targets(repo_root)

    if not targets:
        print("No files carry both markers. Nothing to do.")
        return 0

    by_lang = group_by_lang(targets)
    print(f"Files to remove: {len(targets)}")
    for lang, files in sorted(by_lang.items()):
        print(f"  {lang}: {len(files)}")
    print()

    print("Sample (first 12):")
    for p in targets[:12]:
        print(f"  {p}")
    if len(targets) > 12:
        print(f"  ... and {len(targets) - 12} more")
    print()

    if args.dry_run:
        print("[DRY RUN] Nothing deleted.")
        return 0

    # Use git rm -f to delete and stage in one step
    rel = [os.path.relpath(p, repo_root).replace("\\", "/") for p in targets]
    res = subprocess.run(
        ["git", "rm", "-f", "--", *rel],
        cwd=repo_root,
    )
    if res.returncode != 0:
        print("[ERROR] git rm failed", file=sys.stderr)
        return res.returncode

    print(f"Removed {len(targets)} files (staged in git).")
    print()
    print("Next step: regenerate category/tag pages:")
    print("  python tools/generate_archives.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
