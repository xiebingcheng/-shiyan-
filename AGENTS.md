# AGENTS.md — 岐黄书房

## Quick start

```bash
bundle install
bundle exec jekyll serve                  # → http://127.0.0.1:4000/ (baseurl is empty)
bundle exec jekyll build --trace          # production build (CI uses this)
```

Windows gem mirror: `bundle config mirror.https://rubygems.org https://gems.ruby-china.com`

## CI / Deploy

- Push to `main` → GitHub Actions (`.github/workflows/jekyll.yml`) → `bundle exec jekyll build --trace` → deploy `_site/` to Pages
- Custom domain `www.qihuangstudy.com` (`CNAME`); `_config.yml` has `url: "https://www.qihuangstudy.com"`, `baseurl: ""` — all URLs are root-relative
- History note: the site was once served under the `/-shiyan-/` subpath and later reverted to the domain root; keep `baseurl` empty unless the user explicitly asks

## Content workflow

### Add/Edit a post

Create/update `_posts/YYYY-MM-DD-slug.md` with front matter:

```yaml
---
lang: zh-CN              # required on EVERY post, zh-CN included
translation_key: slug    # identical across all 7 translated copies; see note below
layout: post
title: 标题
date: YYYY-MM-DD HH:MM:SS +0800
category: jieqi          # one of the 8 slugs in _data/categories.yml
tags: [tag1, tag2]
description: >           # SEO description
  摘要
excerpt: 摘要            # feed/listing excerpt
---
```

**After every post change**, regenerate category/tag pages:

```bash
python tools/generate_archives.py
```

This scans all 7 languages' `_posts/` dirs and writes `categories/<slug>.md` and `tags/<tag>.md`.

All 7 translated copies of a post share the same `translation_key` but keep their own slug/permalink. `_includes/head.html` (hreflang alternates + language switcher) and `_layouts/post.html` (sibling translation links) resolve siblings by this key — a missing/mismatched key silently breaks language switching.

### Multi-language (7 languages)

| Lang | Post dir | Prefix |
|------|----------|--------|
| zh-CN | `_posts/` | (none) |
| en | `en/_posts/` | `/en/` |
| ru | `ru/_posts/` | `/ru/` |
| fr | `fr/_posts/` | `/fr/` |
| es | `es/_posts/` | `/es/` |
| id | `id/_posts/` | `/id/` |
| ar | `ar/_posts/` | `/ar/` (RTL) |

Each language duplicates the post file tree with translated content. The permalink and `lang:` field in each post must match its directory.

### Helper scripts in `tools/`

| Script | Purpose |
|--------|---------|
| `generate_archives.py` | Regenerate category/tag pages for all 7 languages |
| `gen_pages.py` | Generate translated archive/categories/tags/search pages for non-zh-CN languages |
| `add_lang_field.py` | Retroactively add `lang:` to translated page front matter |
| `fix_yaml.py` | Sanitize i18n YAML data files |
| `fix_yaml_tags.py` | Quote tags containing YAML-special chars (`& * :` …) in all `_posts/` |
| `mark_placeholders.py` | Flag posts across the 7 trees with `placeholder: true` + hidden comment |
| `remove_placeholders.py` | Delete placeholder-marked posts (`--dry-run` available) |
| `prune_orphan_tags.py` | Delete `tags/<tag>.md` pages whose tag appears in no post (leaves category pages alone) |

## Architecture

- **Jekyll 3.10** (via `github-pages` gem) + **Ruby 3.2** (CI)
- **Plugins**: jekyll-sitemap, jekyll-feed, jekyll-seo-tag, jekyll-paginate, jekyll-include-cache
- **Theme**: Custom ancient-Chinese CSS (`assets/css/main.css`, 1879 lines), dark mode via JS + CSS variables
- **Search**: Client-side via `search.json` (Jekyll-generated index) + `assets/js/search.js`
- **i18n**: `_data/i18n.yml` (UI strings), `_data/categories.yml` + `_data/categories-i18n.yml` (canonical category slugs/names/descs), `_data/nav.yml` + `_data/nav-i18n.yml` (nav), `_data/authors.yml`
- **Analytics/CSP**: `_includes/head.html` embeds 百度统计 + 51.la and a strict `Content-Security-Policy` meta — any new external script/font/analytics domain must also be whitelisted in that CSP, or browsers silently block it (several past commits were CSP fixes)
- **No Gemfile.lock** (gitignored), no test framework, no lint/typecheck

## Config quirks

- `future: false` — posts dated after today are excluded from build
- `show_drafts: false` — drafts not rendered
- `permalink: /:year/:month/:day/:title/`
- `_config.yml` excludes `tools/`, `tests/`, `scripts/`, `build_logs/`, `.github/`, `README.md` from output
- `exclude` list strips `run.html`, `actions_jobs.json`, `build_logs*` — these are CI artifacts
- RTL support for Arabic (`ar`) via `rtl_langs` list in config

## Category slugs (8, canonical list in `_data/categories.yml`)

`jieqi` (节气养生), `shiliao` (食疗本草), `siji` (四季调养), `jingluo` (经络穴位), `qiju` (起居有常), `qingzhi` (情志养生), `jingdian` (中医经典), `lishi` (中医历史)

Only `jieqi`, `jingdian`, `lishi`, `shiliao` currently have published posts; the other four are legacy but still valid slugs.

## Troubleshooting

- Build fails? Run `bundle exec jekyll build --trace` locally to find Liquid/YAML errors
- Future-date post not appearing? Check `future: false` in `_config.yml`
- GitHub Actions fail but site is live? Old build is cached (600s edge cache); push again to trigger rebuild
