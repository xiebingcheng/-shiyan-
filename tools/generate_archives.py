#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_archives.py
扫描 7 个语种的 _posts/，自动生成：

  zh-CN（默认）:
    - categories/<slug>.md
    - tags/<tag>.md
  en/ru/fr/es/id/ar:
    - <lang>/categories/<slug>.md
    - <lang>/tags/<tag>.md

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

# 7 语种 + 每个语种对应的 _posts 目录
LANGS = [
    ('zh-CN', ROOT / '_posts',         ''),       # 默认语种，目录在前缀
    ('en',     ROOT / 'en' / '_posts', 'en'),
    ('ru',     ROOT / 'ru' / '_posts', 'ru'),
    ('fr',     ROOT / 'fr' / '_posts', 'fr'),
    ('es',     ROOT / 'es' / '_posts', 'es'),
    ('id',     ROOT / 'id' / '_posts', 'id'),
    ('ar',     ROOT / 'ar' / '_posts', 'ar'),
]

CATEGORIES_DATA = ROOT / "_data" / "categories.yml"
CATEGORIES_I18N = ROOT / "_data" / "categories-i18n.yml"


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
                    items = v[1:-1].split(',')
                    meta[k] = [x.strip().strip('"').strip("'") for x in items if x.strip()]
                else:
                    meta[k] = v.strip('"').strip("'")
    return meta, body


def load_category_meta():
    """从 _data/categories.yml 解析分类元数据（中文 fallback）"""
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


def load_category_i18n():
    """从 _data/categories-i18n.yml 解析 7 语种分类名称/描述。返回 {slug: {lang: {name, desc}}}。"""
    if not CATEGORIES_I18N.exists():
        return {}
    out = {}
    cur_slug = None
    cur_lang = None
    for raw in CATEGORIES_I18N.read_text(encoding='utf-8').splitlines():
        s = raw.rstrip()
        stripped = s.strip()
        if stripped.startswith('- slug:'):
            cur_slug = stripped.split(':', 1)[1].strip()
            out[cur_slug] = {}
        elif cur_slug and stripped.endswith(':') and not stripped.startswith('-'):
            # e.g. "  zh-CN:"
            cur_lang = stripped[:-1].strip()
            out[cur_slug][cur_lang] = {}
        elif cur_slug and cur_lang and stripped.startswith('name:'):
            out[cur_slug][cur_lang]['name'] = stripped.split(':', 1)[1].strip()
        elif cur_slug and cur_lang and stripped.startswith('desc:'):
            out[cur_slug][cur_lang]['desc'] = stripped.split(':', 1)[1].strip()
    return out


def scan_posts(posts_dir):
    """扫描指定 _posts 目录，返回 [(meta, filepath)] 列表，按日期降序。"""
    items = []
    if not posts_dir.exists():
        return items
    for p in sorted(posts_dir.glob("*.md")):
        text = p.read_text(encoding='utf-8')
        meta, _ = parse_front_matter(text)
        if not meta or not meta.get('title'):
            continue
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


def render_category(slug, posts, lang, prefix, cat_meta_zh, cat_i18n):
    """生成单语种分类页 front matter。"""
    # 名称/描述优先级：当前语种 > 中文 fallback
    cat_block = cat_i18n.get(slug, {})
    cur = cat_block.get(lang, {})
    name = cur.get('name') or cat_block.get('zh-CN', {}).get('name') or cat_meta_zh.get(slug, {}).get('name', slug)
    desc = cur.get('desc') or cat_block.get('zh-CN', {}).get('desc') or cat_meta_zh.get(slug, {}).get('desc', '')

    permalink = f"/{prefix}/categories/{slug}/" if prefix else f"/categories/{slug}/"
    out_dir = ROOT / prefix / 'categories' if prefix else ROOT / 'categories'
    out_path = out_dir / f"{slug}.md"

    # 用 YAML 安全字符串：双引号转义内部双引号；若值已带引号则不重复包裹
    def yq(s):
        s = str(s)
        if s.startswith('"') and s.endswith('"') and len(s) >= 2:
            return s
        return '"' + s.replace('"', '\\"') + '"'
    body = f"""---
layout: category
title: {yq(name)}
permalink: {permalink}
category: {slug}
category_name: {yq(name)}
category_desc: {yq(desc)}
lang: {lang}
---
"""
    write_file(out_path, body)


def render_tag(tag, posts, lang, prefix):
    """生成单语种标签页 front matter。文件名与 permalink 保留原 UTF-8（与既有 zh-CN 文件一致）。"""
    permalink = f"/{prefix}/tags/{tag}/" if prefix else f"/tags/{tag}/"
    out_dir = ROOT / prefix / 'tags' if prefix else ROOT / 'tags'
    out_path = out_dir / f"{tag}.md"

    body = f"""---
layout: tag
title: "#{tag}"
permalink: {permalink}
tag: {tag}
lang: {lang}
---
"""
    write_file(out_path, body)


def main():
    cat_meta_zh = load_category_meta()
    cat_i18n = load_category_i18n()

    total_cats = 0
    total_tags = 0

    for lang, posts_dir, prefix in LANGS:
        if not posts_dir.exists():
            print(f"⚠ [{lang}] {posts_dir.relative_to(ROOT)} 不存在，跳过")
            continue

        posts = scan_posts(posts_dir)
        print(f"\n[{lang}] 扫描到 {len(posts)} 篇文章 ({posts_dir.relative_to(ROOT)})")

        by_cat = defaultdict(list)
        by_tag = defaultdict(list)
        for p in posts:
            if p.get('category'):
                by_cat[p['category']].append(p)
            for t in p.get('tags', []) or []:
                by_tag[t].append(p)

        for slug, ps in by_cat.items():
            render_category(slug, ps, lang, prefix, cat_meta_zh, cat_i18n)
            total_cats += 1
            print(f"  [CAT] {slug}: {len(ps)} 篇")

        for tag, ps in by_tag.items():
            render_tag(tag, ps, lang, prefix)
            total_tags += 1
            print(f"  [TAG] {tag}: {len(ps)} 篇")

    print(f"\n[OK] 完成：{total_cats} 个分类页 × {len(LANGS)} 语种候选，{total_tags} 个标签页 × {len(LANGS)} 语种候选")


if __name__ == '__main__':
    main()
