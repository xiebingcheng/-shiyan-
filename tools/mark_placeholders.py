#!/usr/bin/env python3
"""
Mark all posts across the 7 language trees as placeholders.
Adds:
  1) `placeholder: true` inside the front matter (machine-readable flag)
  2) `<!-- 此文章为占位文章 -->` right after the closing `---` of front matter
     (human-readable marker, hidden in rendered output)

Idempotent: skips files that already contain the marker.
"""
import os
import sys

LANGS = [
    ("_posts", "zh-CN"),
    ("en/_posts", "en"),
    ("ru/_posts", "ru"),
    ("fr/_posts", "fr"),
    ("es/_posts", "es"),
    ("id/_posts", "id"),
    ("ar/_posts", "ar"),
]

MARKER_FIELD = "placeholder: true"
MARKER_COMMENT = "<!-- 此文章为占位文章 -->"


def process_file(path: str) -> str:
    """Return one of: 'marked', 'skipped', 'error:<reason>'."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        content = f.read()

    # Idempotency check (window covers the longest observed front matter)
    if MARKER_FIELD in content[:2000] and MARKER_COMMENT in content[:2000]:
        return "skipped"

    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        return "error:missing opening ---"

    close_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            close_idx = i
            break
    if close_idx is None:
        return "error:missing closing ---"

    # 1) Insert `placeholder: true` inside front matter, just before the closing ---
    fm_text = "\n".join(lines[1:close_idx])
    if "placeholder:" not in fm_text:
        lines.insert(close_idx, MARKER_FIELD)
        close_idx += 1

    # 2) Insert HTML comment right after the front matter closing ---
    # Find the first non-empty line after the closing ---
    body_start = close_idx + 1
    first_nonempty = body_start
    while first_nonempty < len(lines) and lines[first_nonempty].strip() == "":
        first_nonempty += 1
    # Look ahead a few lines for an existing marker to avoid duplicates
    lookahead = "\n".join(lines[first_nonempty:first_nonempty + 5])
    if "此文章为占位文章" not in lookahead:
        lines.insert(first_nonempty, MARKER_COMMENT)

    new_content = "\n".join(lines)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new_content)
    return "marked"


def main() -> int:
    base = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(base)

    counts = {"marked": 0, "skipped": 0, "error": 0}
    errors = []

    for rel_dir, lang in LANGS:
        abs_dir = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(abs_dir):
            print(f"[WARN] missing dir: {rel_dir}", file=sys.stderr)
            continue

        files = sorted(f for f in os.listdir(abs_dir) if f.endswith(".md"))
        for fname in files:
            fpath = os.path.join(abs_dir, fname)
            result = process_file(fpath)
            if result == "marked":
                counts["marked"] += 1
            elif result == "skipped":
                counts["skipped"] += 1
            else:
                counts["error"] += 1
                errors.append(f"  {rel_dir}/{fname}: {result}")

    print(f"\n=== Placeholder marker run ===")
    print(f"  lang trees   : {len(LANGS)}")
    print(f"  newly marked : {counts['marked']}")
    print(f"  skipped      : {counts['skipped']}")
    print(f"  errors       : {counts['error']}")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
