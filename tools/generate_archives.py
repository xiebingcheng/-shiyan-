#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_archives.py
扫描 _posts/*.md 自动生成：
  - categories/<slug>.md
  - tags/<tag>.md
  - categories/index.md 分类总览
  - tags/index.md 标签总览
  - archive.md 时间归档

每次添加/修改文章后跑一次：
  python tools/generate_archives.py
"""
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "_posts"
CATS = ROOT / "categories"
TAGS = ROOT / "tags"

CATEGORIES_DATA = ROOT / "_data" / "categories.yml"


def parse_front_matter(text):
    """解析 Jekyll front matter（YAML 子集，足以覆盖本项目用到的语法）"""
    m = re.match(r'^---\s*\n(.*?\n)---\s*\n(.*)$', text, re.DOTALL)
    if not m:
        return None, text
    fm, body = m.group(1), m.group(2)
    meta = {}
    current_list_key = None
    for line in fm.splitlines():
        if not line.strip():
            continue
        if line.startswith('  - ') and current_list_key:
            meta.setdefault(current_list_key, []).append(line[4:].strip().strip('"').strip("'"))
            continue
        if ':' in line:
            k, _, v = line.partition(':')
            k = k.strip()
            v = v.strip()
            if not v:
                current_list_key = k
                meta[k] = []
            else:
                current_list_key = None
                if v == 'true':
                    meta[k] = True
                elif v == 'false':
                    meta[k] = False
                elif v.startswith('[') and v.endswith(']'):
                    # inline list: [a, b, c]
                    items = v[1:-1].split(',')
                    meta[k] = [x.strip().strip('"').strip("'") for x in items if x.strip()]
                else:
                    meta[k] = v.strip('"').strip("'")
    return meta, body


def load_category_meta():
    """从 _data/categories.yml 解析分类元数据（仅取 slug 与 name 字段）"""
    if not CATEGORIES_DATA.exists():
        return {}
    meta = {}
    cur = None
    for line in CATEGORIES_DATA.read_text(encoding='utf-8').splitlines():
        s = line.rstrip()
        if s.startswith('- slug:'):
            cur = {'slug': s.split(':', 1)[1].strip()}
            meta[cur['slug']] = cur
        elif cur and s.strip().startswith('name:'):
            cur['name'] = s.split(':', 1)[1].strip()
        elif cur and s.strip().startswith('desc:'):
            cur['desc'] = s.split(':', 1)[1].strip()
        elif cur and s.strip().startswith('color:'):
            cur['color'] = s.split(':', 1)[1].strip().strip('"')
    return meta


def scan_posts():
    """扫描 _posts，返回 [(meta, filepath)] 列表，按日期降序"""
    items = []
    for p in sorted(POSTS.glob("*.md")):
        text = p.read_text(encoding='utf-8')
        meta, _ = parse_front_matter(text)
        if not meta or not meta.get('title'):
            continue
        # 从文件名取日期
        m = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)\.md', p.name)
        if m:
            try:
                dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                meta['_date'] = dt
                meta['_slug'] = m.group(4)
            except ValueError:
                pass
        meta['_filename'] = p.name
        items.append(meta)
    items.sort(key=lambda x: x.get('_date') or datetime.min, reverse=True)
    return items


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    print(f"  [OK] {path.relative_to(ROOT)}")


def render_category(slug, posts, cat_meta):
    name = cat_meta.get(slug, {}).get('name', slug)
    desc = cat_meta.get(slug, {}).get('desc', '')
    post_items = "\n".join(
        f'        <li class="post-list__item post-list__item--rich">\n'
        f'          <time class="post-list__date" datetime="{p.get("_date").strftime("%Y-%m-%d")}">{p.get("_date").strftime("%Y-%m-%d")}</time>\n'
        f'          <a class="post-list__link" href="/{(p.get("_date").strftime("%Y/%m/%d") + "/" + p["_slug"] + "/")}">{p["title"]}</a>\n'
        + (f'          <p class="post-list__excerpt">{p.get("excerpt","").strip()[:120]}</p>\n' if p.get("excerpt") else "")
        + f'        </li>'
        for p in posts
    )
    body = f"""---
layout: category
title: 分类：{name}
permalink: /categories/{slug}/
category: {slug}
category_name: {name}
category_desc: "{desc}"
---
"""
    write_file(CATS / f"{slug}.md", body)


def render_tag(tag, posts):
    # TC-023: 对非 ASCII tag 做 percent-encoding，保证跨 Jekyll 版本的 URL 稳定性。
    # 已存在的 tags/<chinese>.md 文件不再重命名（避免破坏既有 permalink），
    # 这里只为未来新加的 tag 生成 URL-encoded 文件名 / permalink。
    safe_tag = tag if all(ord(c) < 128 for c in tag) else quote(tag, safe='')
    post_items = "\n".join(
        f'        <li class="post-list__item post-list__item--rich">\n'
        f'          <time class="post-list__date" datetime="{p.get("_date").strftime("%Y-%m-%d")}">{p.get("_date").strftime("%Y-%m-%d")}</time>\n'
        f'          <a class="post-list__link" href="/{(p.get("_date").strftime("%Y/%m/%d") + "/" + p["_slug"] + "/")}">{p["title"]}</a>\n'
        + (f'          <p class="post-list__excerpt">{p.get("excerpt","").strip()[:120]}</p>\n' if p.get("excerpt") else "")
        + f'        </li>'
        for p in posts
    )
    body = f"""---
layout: tag
title: 标签：#{tag}
permalink: /tags/{safe_tag}/
tag: {tag}
---
"""
    write_file(TAGS / f"{safe_tag}.md", body)


def main():
    if not POSTS.exists():
        print("✘ _posts 目录不存在", file=sys.stderr)
        sys.exit(1)

    cat_meta = load_category_meta()
    posts = scan_posts()
    print(f"扫描到 {len(posts)} 篇文章")

    by_cat = defaultdict(list)
    by_tag = defaultdict(list)
    for p in posts:
        if p.get('category'):
            by_cat[p['category']].append(p)
        for t in p.get('tags', []) or []:
            by_tag[t].append(p)

    # 分类页
    CATS.mkdir(exist_ok=True)
    for slug, ps in by_cat.items():
        render_category(slug, ps, cat_meta)
        print(f"  [CAT] {slug}: {len(ps)} 篇")

    # 标签页
    TAGS.mkdir(exist_ok=True)
    for tag, ps in by_tag.items():
        render_tag(tag, ps)
        print(f"  [TAG] {tag}: {len(ps)} 篇")

    print(f"\n[OK] 完成：{len(by_cat)} 个分类，{len(by_tag)} 个标签")


if __name__ == '__main__':
    main()
