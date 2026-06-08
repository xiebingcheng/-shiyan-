# AGENTS.md — 岐黄书房

## Quick start

```bash
bundle install
bundle exec jekyll serve                  # → http://127.0.0.1:4000/-shiyan-/
bundle exec jekyll build --trace          # production build (CI uses this)
```

Windows gem mirror: `bundle config mirror.https://rubygems.org https://gems.ruby-china.com`

## CI / Deploy

- Push to `main` → GitHub Actions (`.github/workflows/jekyll.yml`) → `bundle exec jekyll build --trace` → deploy `_site/` to Pages
- `baseurl: "/-shiyan-"` in `_config.yml` — local URLs are `/shiyan-/...`
- Deployed at `https://xiebingcheng.github.io/-shiyan-/`

## Content workflow

### Add/Edit a post

Create/update `_posts/YYYY-MM-DD-slug.md` with front matter:

```yaml
---
layout: post
title: 标题
date: YYYY-MM-DD HH:MM:SS +0800
category: jieqi        # one of: jieqi, shiliao, siji, jingluo, qiju, qingzhi
tags: [tag1, tag2]
excerpt: 摘要
lang: zh-CN             # required for non-zh-CN posts
---
```

**After every post change**, regenerate category/tag pages:

```bash
python tools/generate_archives.py
```

This scans all 7 languages' `_posts/` dirs and writes `categories/<slug>.md` and `tags/<tag>.md`.

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

## Architecture

- **Jekyll 3.10** (via `github-pages` gem) + **Ruby 3.2** (CI)
- **Plugins**: jekyll-sitemap, jekyll-feed, jekyll-seo-tag, jekyll-paginate, jekyll-include-cache
- **Theme**: Custom ancient-Chinese CSS (`assets/css/main.css`, 1879 lines), dark mode via JS + CSS variables
- **Search**: Client-side via `search.json` (Jekyll-generated index) + `assets/js/search.js`
- **i18n**: `_data/i18n.yml` (UI strings), `_data/categories-i18n.yml` (category names), `_data/nav-i18n.yml` (nav)
- **No Gemfile.lock** (gitignored), no test framework, no lint/typecheck

## Config quirks

- `future: false` — posts dated after today are excluded from build
- `show_drafts: false` — drafts not rendered
- `permalink: /:year/:month/:day/:title/`
- `_config.yml` excludes `tools/`, `tests/`, `build_logs/`, `.github/` from output
- `exclude` list strips `run.html`, `actions_jobs.json`, `build_logs*` — these are CI artifacts
- RTL support for Arabic (`ar`) via `rtl_langs` list in config

## Category slugs (6)

`jieqi` (节气养生), `shiliao` (食疗本草), `siji` (四季调养), `jingluo` (经络穴位), `qiju` (起居有常), `qingzhi` (情志养生)

## Troubleshooting

- Build fails? Run `bundle exec jekyll build --trace` locally to find Liquid/YAML errors
- Future-date post not appearing? Check `future: false` in `_config.yml`
- GitHub Actions fail but site is live? Old build is cached (600s edge cache); push again to trigger rebuild
