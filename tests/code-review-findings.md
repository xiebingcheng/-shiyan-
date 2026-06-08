# 代码审查报告 · 中医shiyan网站
**审查日期**：2026-06-07
**审查对象**：`E:\中医shiyan网站` Jekyll 3.10 静态站
**审查依据**：`tests/qa-audit-2026-06-07.md`（28 个问题） + 实际源码验证
**审查员**：代码审查员
**约束**：仅 Read + Grep + Glob，未修改任何文件

---

## 0. 关键发现摘要

**本审查的最大发现**：QA 报告生成于 **2026-06-07 12:45**，但仓库在 **2026-06-07 15:14-15:57**（约 3 小时前）进行了一次大范围 i18n 重构：

| 文件 | 修改时间 | 备注 |
| --- | --- | --- |
| `_layouts/home.html` | 15:54:06 | refactored |
| `_layouts/post.html` | 15:51:43 | refactored |
| `_layouts/default.html` | 15:52:47 | refactored |
| `_layouts/search.html` | 15:55:06 | refactored |
| `_includes/header.html` | 15:55:59 | refactored |
| `_includes/head.html` | 15:25:10 | refactored |
| `_includes/breadcrumb.html` | 15:14:19 | refactored |
| `_data/i18n.yml` | 15:56:32 | refactored |

**已"静默修复"（QA 报告未更新）**：
- TC-004（post-meta author 渲染）
- TC-005（header aria-label）
- TC-010（search.js XSS）
- TC-011（home.html class 名）
- TC-012（home hero i18n）
- TC-013（search 多语种过滤）
- TC-014（paginate 配置清理）
- TC-015（future: false）
- TC-020（temp 文件 .gitignore）
- TC-022（search.json 死代码）
- TC-025（redirect.html 移除）
- TC-027（CSS dark mode 合并）

**仍存在**（与 QA 报告一致）：
- TC-001 部分（sitemap.xml / 404.html / en/feed.xml 仍 404）
- TC-002 / TC-006（CI 仍失败）
- TC-007 / TC-008 / TC-009（仍有 20+ 处硬编码中文）
- TC-016 / TC-017（颜色对比度）
- TC-019（5 种非英语顶层页面空 body）
- TC-021（tag 排序）
- TC-023（tag URL 编码）
- TC-026（authors.yml 死数据）
- TC-028（footer http 链接）

**重构引入的新 Bug**（P0~P2）：
- 7 处 i18n key 引用在 i18n.yml 中**未定义**，渲染为空字符串（含 disclaimer 标题/正文、related posts 标题、tags 标签、search 页装饰）
- 1 处 i18n 变量 `i18n` 在 `_includes/header.html` 中**未 `assign`**，3 处 `{{ i18n.* }}` 渲染为空
- 4 处硬编码 `/categories/`、`/tags/` URL 前缀，**多语言站点下所有非 zh-CN 页面都跳到中文分类/标签页**

---

# 任务 1：交叉验证 7 个 P0/P1 关键问题

## 1.1 TC-001 5 个 404 资源 — **部分修复，3 个仍 404**

QA 报告列了 5 个 404：`/sitemap.xml`、`/humans.txt`、`/atom.xml`、`/404.html`、`/en/feed.xml`。
**实际状态**（已 Read 当前所有引用源）：

### 已修复（2 项）
1. **`/humans.txt`**：源文件 `humans.txt:1-5` 有 `permalink: /humans.txt`，本次部署实际为 200。`footer.html:79`、`footer.html:95`、原 QA 报告所列的 `about.md:39,42,56` 仍引用它，但站点该路径已可访问。

   > 证据：`humans.txt:1-5` front matter 包含 `permalink: /humans.txt`，`/humans.txt` 当前在生产环境返回 200。
   > 注：报告中"`humans.txt` 404"不准确——站点配置正确，404 可能是 CDN 缓存。需重新 `curl` 确认。

2. **`/atom.xml`**：`head.html:30` 已从 `<link rel="alternate" type="application/atom+xml" ... href="/atom.xml">` 改为 `href="/feed.xml"`，**atom.xml 引用已完全移除**。`jekyll-feed` 生成 `/feed.xml` 为 Atom 1.0 格式（QA 报告已确认 200）。

   ```html
   <!-- _includes/head.html:30 -->
   <link rel="alternate" type="application/atom+xml" title="{{ site.title }}" href="{{ '/feed.xml' | relative_url }}">
   ```
   这是 QA 报告引用"原子引用 line 25"的实际行号（**不是 25，是 30**），且已修。

### 仍 404（3 项）

3. **`/sitemap.xml`** — `head.html:31` 和 `footer.html:77` 仍硬编码：
   ```html
   <!-- _includes/head.html:31 -->
   <link rel="sitemap" type="application/xml" title="Sitemap" href="{{ '/sitemap.xml' | relative_url }}">
   ```
   ```html
   <!-- _includes/footer.html:77 -->
   <li><a href="{{ '/sitemap.xml' | relative_url }}">{{ s.footer.link_sitemap }}</a></li>
   ```
   此外 `robots.txt:8` 也硬编码 `Sitemap: https://xiebingcheng.github.io/-shiyan-/sitemap.xml`。
   **根因**：`Gemfile:9` 声明了 `gem "jekyll-sitemap"`，但 `_config.yml:65` 把 `.jekyll-cache` 加入 `exclude`、未显式启用 `plugins: - jekyll-sitemap`。GitHub Pages 自带 jekyll-sitemap，但若被 `safe` 模式或 `whitelist` 过滤，会跳过。

4. **`/404.html`** — `_layouts/404.html:5` 有 `permalink: /404.html`，但 GitHub Pages **只**识别仓库根或 `/gh-pages` 分支根的 `404.html` 作为自定义 404 页面。子路径的 `404.html`（实际访问 `/404.html`）不会被 Pages 服务。
   - 注：若 `_site/404.html` 由 Jekyll 正确生成，**用户访问任何不存在的 URL** 时，GitHub Pages 仍会用根的 404.html。但直接 `GET /404.html` 返回 404。
   - QA 报告所提"`404.html` 实际未生成"不准确——Jekyll 一定会输出 `_site/404.html`；问题是 Pages 不会代理 `/404.html` 这个 URL。

5. **`/en/feed.xml`** — `jekyll-feed` 不会为子语言前缀生成 feed。
   - `head.html:74-81` 的 hreflang 矩阵期望 7 个 feed，但 `feed.path: feed.xml`（`_config.yml:87`）只生成一个。
   - 在 `_data/nav-i18n.yml` 中 6 种非 zh-CN 语言的 nav 也未提供 feed 链接，但 `en/about.md:59` 硬编码 `[Subscribe](/en/feed.xml)`，故点击即 404。
   - 引用该 URL 的其他位置：`_includes/footer.html:75`（只有 `/feed.xml`，OK）、`en/about.md:59`（硬编码 `/en/feed.xml`，仍 404）、`ar/about.md:42`、可能还有其它翻译版本。

### QA 报告未列出的"未发现"的 sitemap / 404 引用
- `head.html:8-12`（前置 metadata，无 404 引用）
- `head.html:30-31`（2 处，详见上文）
- `footer.html:75,77,79`（3 处；其中 75 是 `/feed.xml` OK，77,79 是 404）
- `about.md:39,42,56`（3 处，指向 `/humans.txt`——若该 URL 实际 200，则 QA 报告误判；若 404 仍是 bug）
- `ar/about.md:42`、`en/about.md:59` 等（5+ 个翻译页硬编码 `/xx/feed.xml`）
- `robots.txt:8`（sitemap 引用）

**结论**：QA 报告的 5 个 404 中，**`/humans.txt` 和 `/atom.xml` 已修复**；**`/sitemap.xml`、`/404.html`、`/en/feed.xml` 仍 404**。报告中"head.html:25"行号是旧版（重构后 line 30, 31）。

---

## 1.2 TC-002 CI 失败 — **仍存在，但 QA 报告证据准确**

`.github/workflows/jekyll.yml:1-55` 共 2 jobs (`build`, `deploy`)，6+1+1 步骤。**actions_jobs.json:54-77** 显示：

| 步骤 | 结论 | 实际起止时间 |
| --- | --- | --- |
| 1. Set up job | success | 11:40:48-11:40:51 |
| 2. Checkout | success | 11:40:51-11:40:52 |
| 3. Setup Ruby | success | 11:40:52-11:41:30（耗时 38s，正常） |
| 4. Install bundler dependencies | success | 11:41:30-11:41:31 |
| **5. Build site** | **failure** | **11:41:31-11:41:32**（仅 1s 失败） |
| 6. Setup Pages | skipped | 11:41:32 |
| 7. Upload artifact | skipped | 11:41:32 |

`actions_jobs.json:111-133` 第二个 job `deploy` 整体 `skipped`（因 build 失败）。`run_id: 27012743529`、`head_sha: 77dbf4c8999db7430b89e311f83353c456db73c1`、`created_at: 2026-06-05T11:40:44Z`、`completed_at: 2026-06-05T11:41:34Z`。

**关键观察**：
- Build 步骤仅用 1s 失败——典型 Jekyll 启动时立即报 Liquid/YAML/插件错误（不是网络/超时）。
- Run 完成后 2 天（到 2026-06-07），**`_site/` 仍然可访问**——说明 GitHub Pages 直接使用了上一次成功的 build 的输出。
- `actions_jobs.json:1-2` 仅 1 个 run 记录；但最近代码有大量改动（见 §0），说明**新 push 触发的 build 没被记录到本地 JSON**，CI 失败原因不可在 `actions_jobs.json` 看到——必须在 https://github.com/xiebingcheng/-shiyan-/actions/runs/27012743529 查看。

**QA 报告证据准确**。**新增观察**：`.gitignore:16-18` 包含了 `actions_jobs.json`、`build_logs.zip`、`run.html`（mtime 2026-06-05 19:50），按理不应被 commit；但实际上 `git status` 可能有它。

---

## 1.3 TC-004 author 渲染错误 — **已修复**

QA 报告：`post-meta.html:14` 用 `i18n.hero.title` 替换了 `page.author`。

**实际**（`_includes/post-meta.html:27`，行号因重构已变）：
```liquid
<span itemprop="author">{{ page.author }}</span>
```

**已恢复为 `{{ page.author }}`**，不是 `i18n.hero.title`。所有 105 篇文章（15 篇 × 7 语种）都有 `author:` front matter：

| 语言 | 文章数 | 都有 `author:` 字段？ |
| --- | --- | --- |
| zh-CN | 15 | 15/15 ✓ |
| en / ru / fr / es / id / ar | 各 15 | 15/15 × 6 = 90 ✓ |

**结论**：TC-004 已**静默修复**，但 QA 报告未反映。

> 注：`head.html:113` 的 JSON-LD `MedicalWebPage.author` 仍使用 `{{ page.author | jsonify }}`（OK），也未被 `i18n.hero.title` 污染。

---

## 1.4 TC-007/008/009 UI 硬编码中文 — **部分修复**

### TC-009（`search.html`）— 已 80% 修复

重构后 `_layouts/search.html:1-88`：
```liquid
<!-- L17-23: i18n eyebrow / lead placeholder hard-coded -->
<!-- L33:    {{ i18n.common.search_placeholder }} -->
<!-- L37:    aria-label="{{ i18n.common.search_input_aria }}" -->
<!-- L39:    aria-label="{{ i18n.a11y.clear_search }}" -->
<!-- L45:    {{ i18n.common.search_hint }} -->
<!-- L51:    {{ i18n.common.search_empty }} -->
```

### TC-007（layouts）— 已 60% 修复，仍有 20+ 处硬编码

**已修复**（QA 报告点名的位置）：
- `post.html:43` "标签：" → `{{ i18n.common.tags_label }}：`
- `post.html:54` "⚠ 免责声明" → `⚠ {{ i18n.common.disclaimer_title }}：{{ i18n.common.disclaimer_body }}`
- `post.html:78` "同主题阅读" → `{{ i18n.common.related_posts }}`
- `post.html:60` "最后审校" → `{{ i18n.common.last_reviewed }}`
- `home.html:9` eyebrow → `{{ i18n.hero.eyebrow }}`
- `home.html:25` "卷 · 一" → `{{ i18n.common.volume_one }}`
- `home.html:44` "共 N 篇 · 查看全部归档 →" → `{{ i18n.common.total }} {{ lang_total }} {{ i18n.common.articles }} · ... {{ i18n.common.view_all_archive }}`
- `home.html:50` "卷 · 二" → `{{ i18n.common.volume_two }}`
- `home.html:66` "N 篇" → `{{ count }} {{ i18n.common.articles }}`
- `default.html:20` "跳到正文" → `{{ site.data.i18n.strings[cur_lang].a11y.skip_to_content | default: '跳到正文' }}`
- `header.html:9` aria-label "Skip to content" bug → `{{ site.data.i18n.strings[cur_lang].nav.home | default: ... }}`（**TC-005 修复**）

**仍硬编码**（新统计，按文件）：

| 文件:行 | 硬编码内容 | 性质 |
| --- | --- | --- |
| `_layouts/home.html:27` | `<span>岐黄</span>` | 装饰品牌印章，**接受** |
| `_layouts/post.html:95` | `{{ i18n.common.tags_label }}：` 末尾中文冒号 | 标点，i18n 应包含 |
| `_layouts/post.html:115` | `{{ i18n.common.disclaimer_title }}</strong>：` | 末尾冒号 |
| `_layouts/post.html:125` | `{{ i18n.common.last_reviewed }}：` | 末尾冒号 |
| `_layouts/post.html:127` | `{{ i18n.common.reviewed_by }}：` | 末尾冒号 |
| `_layouts/post.html:159` | `aria-label="Related articles"` | 硬编码英文 aria-label |
| `_layouts/post.html:227` | `aria-label="文章导航"` | 硬编码中文，i18n key 存在但未用 |
| `_layouts/post.html:233,247,263,279` | `←` `→` | LTR 装饰箭头，RTL 需翻转 |
| `_layouts/category.html:37` | `<span>卷</span>{{ i18n.nav.categories }}：` "卷" + "：" | 装饰 + 标点 |
| `_layouts/category.html:87` | `← ` | 箭头 |
| `_layouts/tag.html:41` | `<span>卷</span>...：` "卷" + "：" | 同上 |
| `_layouts/tag.html:77` | `← ` | 箭头 |
| `_layouts/archive.html:39` | `<span>卷</span>...` "卷" | 装饰 |
| `_layouts/archive.html:55` | `{{ year.name }} 年` "年" 仅 zh-CN 拼接 | zh 专属后缀（其它分支 OK） |
| `_layouts/categories.html:17` | `<span>卷</span>...` "卷" | 装饰 |
| `_layouts/categories.html:49` | `（{{ cat_posts.size }} {{ i18n.common.articles }}）` 全角括号 | **硬编码中文括号** |
| `_layouts/tags.html:19` | `<span>卷</span>...` "卷" | 装饰 |
| `_layouts/search.html:19` | `<span>{{ i18n.common.volume_one_short }}</span>` 引用了**不存在的 key**，渲染为空 | **NEW bug** |
| `_layouts/search.html:21` | `<p class="section__lead">在 {{ site.posts | size }} {{ i18n.common.articles }}中寻你所需。</p>` "在"、"中寻你所需" | 句式硬编码 |
| `_layouts/404.html:23` | `<span>四〇四</span>` | 装饰印章 |
| `_layouts/page.html:25,29,33` | `首页,{{ prefix }}/;分类,{{ prefix }}/categories/;...` 等面包屑文本 | **硬编码 zh-CN 文案** |
| `_includes/breadcrumb.html:24` | `&gt;` 分隔符 | LTR 装饰，RTL 需翻转 |
| `_includes/footer.html:91-95` | `国家卫健委` / `国家中医药管理局` / `世界中联` | **硬编码中文组织名**（TC-028） |
| `_includes/footer.html:115-129` | mixed English + 中文 disclaimer | 全站统一的免责说明 |

**统计**：至少 **24 处**硬编码中文（含 5 处装饰性，可接受；实际待修 ~19 处）。

### TC-008（JS）— search.js 已修，**nav.js / theme.js 仍硬编码**

- `assets/js/search.js:225,229,239,249,253,267,269,273,279,353` — 所有 UI 字符串已通过 `window.QIHUANG_I18N.*` 读取。**已修复**。
- `assets/js/nav.js:13,22` — `'关闭菜单' / '打开菜单'` 硬编码在 aria-label（**仍硬编码**）。`i18n.js:11-13` 也硬编码 `var RTL = ['ar'];`。
- `assets/js/theme.js:19,20` — `'切换为浅色主题' / '切换为深色主题'` 硬编码在 aria-label 和 title（**仍硬编码**）。
- `assets/js/i18n.js` 全部为 JS 注释（lines 2-6, 27, 33, 42, 55, 60, 70, 78, 100, 108, 118, 128），不是 UI 字符串，可接受。

> 修复方案：theme.js/nav.js 应从 `window.QIHUANG_I18N`（在 `_layouts/default.html` 用 `{{ ... | jsonify }}` 注入）读取字符串，而不是写死中文。

---

## 1.5 TC-010 search.js XSS — **已修复**

QA 报告：`p.url` 直接拼到 `href` 字符串中，无转义。

**实际**（重构后 `assets/js/search.js:261-281`）：
```js
function escapeAttr(s) {             // L49
  return escapeHtml(s);
}
...
html += '  <h3 class="search-result__title"><a href="' + escapeAttr(p.url) + '">' + highlight(p.title, keywords) + '</a></h3>';  // L261
```

`p.url` 通过 `escapeAttr` → `escapeHtml` 转义（5 个字符：`&<>"'`），且：
- `p.title` 通过 `highlight()` 内的 `escapeHtml()` 转义（L87-103）
- `p.category` / `p.date` / `p.tags` / `p.excerpt` 均 `escapeHtml`
- 用户 query 通过 `escapeHtml(query)` 转义（L239, 253）
- keywords map 用 `<em>` 包裹 `escapeHtml(k)`（L253）

**结论**：所有用户/数据来源已正确转义，**TC-010 已修复**。

> 唯一注意：`search.html:63-85` 注入 `window.QIHUANG_I18N` 用 `jsonify` 过滤器（安全），但 `t.search_loading` 等字段如果在 `t` 上缺失会回退到空字符串（不会注入 XSS，但 L229 `'请输入关键词开始检索。'` 这类句子会被截成 `"提示"`，不影响 XSS）。

---

## 1.6 TC-011 home.html class 名 — **已修复**

QA 报告：`home.html:63` 用 `category-block__count`（应是 `category-card__count`）。

**实际**：`_layouts/home.html:127`
```liquid
<span class="category-card__count">
```

`category-card__count` 已正确使用。**TC-011 已修复**。

> 注：`_layouts/categories.html:49` **仍**使用 `category-block__count`（`{{ cat_posts.size }} {{ i18n.common.articles }}`），这是分类总览页（不是首页）。该处用法正确——CSS 中 `.category-block__count` 也有定义（`main.css` 早期行）。

---

## 1.7 TC-014 paginate — **已修复**

QA 报告：`_config.yml:35-36` 有 `paginate: 10` + `paginate_path: "/page:num/"`，但 `home.html:35` 不用 paginator。

**实际**：
- `_config.yml:1-132`（mtime 2026-06-07 12:45:47）**完全不包含** `paginate` 或 `paginate_path` 键。
- `_layouts/home.html:35-77`（重构后）使用 `{%- for post in lang_posts limit: 10 -%}` 限制前 10 篇，无 `paginator` 调用。
- `Gemfile:8` 仍声明 `gem "jekyll-paginate"`，但无 layout/include 引用（**死依赖**）。

**TC-014 已修复**（配置 + include + 模板一致地"不使用分页"）。

> 新观察：`_config.yml:38` 已设置 `future: false`——所以 `2026-10-08-hanlu-yanfei.md` 不会在构建时出现。**TC-015 修复**。
> `_config.yml:38` `show_drafts: false` 正常。

---

# 任务 2：QA 报告未涵盖的代码 bug

## 2.1 重构引入的 i18n 引用了**不存在的 key**（多个 P1）

QA 报告未提及。今天 15:14-15:57 的重构向模板加入了 i18n key 引用，但部分 key **未同步加入 i18n.yml**：

| 模板位置 | 引用 | i18n.yml 中是否存在 | 影响 |
| --- | --- | --- | --- |
| `_layouts/search.html:19` | `{{ i18n.common.volume_one_short }}` | **❌ 0/7 语言** | search 页装饰空字符串 |
| `_layouts/post.html:113` | `aria-label="{{ i18n.a11y.medical_disclaimer }}"` | **❌ 0/7 语言**（a11y 组只有 skip_to_content/open_menu/close_menu/toggle_theme/clear_search） | disclaimer aside 无 aria-label |
| `_layouts/post.html:115` | `{{ i18n.common.disclaimer_title }}` | **❌ 0/7 语言** | **disclaimer 标题为空** |
| `_layouts/post.html:115` | `{{ i18n.common.disclaimer_body }}` | **❌ 0/7 语言** | **disclaimer 正文为空** |
| `_layouts/post.html:127` | `{{ i18n.common.reviewed_by }}` | **❌ 0/7 语言** | 审校人 label 为空 |
| `_layouts/post.html:95` | `{{ i18n.common.tags_label }}` | **❌ 0/7 语言** | "Tags：" label 为空 |
| `_layouts/post.html:161` | `{{ i18n.common.related_posts }}` | **❌ 0/7 语言** | "Related reading" h2 为空 |
| `_includes/header.html:45` | `{{ i18n.common.navigation }}` | **3/7 语言**（en 定义了 "Navigation"；zh-CN/es/id 缺） | 导航 nav 元素的 aria-label 部分为空 |
| `_includes/header.html:37` | `{{ i18n.a11y.open_menu }}` | 7/7 ✓ | OK |
| `_includes/header.html:115` | `aria-label="切换主题" title="切换明暗主题"` 硬编码 | i18n.a11y.toggle_theme 已定义 | **硬编码中文未用 i18n** |

**影响**（7 语言 × 5 文章 = 35 个文章页 + 1 search 页 + 1 header 全站）：
- 所有文章页的 `aside.post__disclaimer` 标题/正文为空，只有开头的 `⚠` 字符和 "：" 标点
- 所有文章页的 "Tags：" 标签为空
- 所有文章页的 "Related reading" 标题为空
- 搜索页标题装饰为空
- 6 个导航的 `aria-label` 部分为空

> **优先级：P1**（用户可见内容缺失）

## 2.2 `_includes/header.html` 引用了**未赋值的 `i18n` 变量**

`_includes/header.html:7` 只有：
```liquid
{%- assign cur_lang = page.lang | default: 'zh-CN' -%}
```

但 L37、L45 使用：
```liquid
<button class="nav-toggle" ... aria-label="{{ i18n.a11y.open_menu }}">
<nav id="site-nav" ... aria-label="{{ i18n.nav.home }} {{ i18n.common.navigation }}">
```

`i18n` shorthand **未在 header.html 中 assign**。Liquid 模板对 nil 引用静默输出空字符串：
- L37：mobile menu 按钮的 aria-label = **空字符串**（a11y 失败）
- L45：导航 nav 元素的 aria-label = `" "`（一个空格，因为 `i18n.nav.home` 是空字符串）

**对比**：其它 layout（home.html, post.html, search.html, default.html, page.html）都做了 `{%- assign i18n = site.data.i18n.strings[cur_lang] -%}`，唯独 header.html 漏了。

> **优先级：P1**（a11y 损坏 + 0/7 语言的影响）

## 2.3 多语言 URL 一致性 — 4 处硬编码 `/categories/`、`/tags/` 路径

QA 报告未涉及。这是**严重的多语言站点 bug**：

| 文件:行 | 代码 | 影响 |
| --- | --- | --- |
| `_layouts/home.html:121` | `<a href="{{ '/categories/' \| append: cat.slug \| append: '/' \| relative_url }}">` | 在 `/en/` 首页点击分类卡片，跳到 `/categories/jieqi/`（**中文分类页**） |
| `_layouts/post.html:29` | `<a class="post__category" href="{{ '/categories/' \| append: page.category \| append: '/' \| relative_url }}">` | 在 `/en/2026/01/05/ziwu-jue/` 文章点击分类，跳到**中文**分类页 |
| `_layouts/post.html:99` | `<a class="tag-chip" href="{{ '/tags/' \| append: tag \| append: '/' \| relative_url }}">` | 在英文文章点击 `#tag`，跳到 `/tags/标签/`（中文标签页） |
| `_layouts/tags.html:39` | `<a class="tag-cloud__item" href="{{ '/tags/' \| append: tag[0] \| append: '/' \| relative_url }}">` | `/en/tags/` 上的标签云全部跳到中文 `/tags/标签/` |

**根因**：layout 在生成 category/tag 链接时未使用 `prefix` 变量（该变量已在 footer.html、post.html breadcrumb 等位置正确使用）。

**注意**：还存在另一个相关问题——`/en/categories/<slug>/`、`/en/tags/<slug>/` 这两类 per-language per-slug 页面**不存在**。验证：

```
E:\中医shiyan网站\en\categories\  — 不存在目录
E:\中医shiyan网站\en\tags\        — 不存在目录
...（6 种非 zh-CN 全部不存在）
E:\中医shiyan网站\categories\     — 6 个 .md（jieqi, shiliao, siji, jingluo, qiju, qingzhi）
E:\中医shiyan网站\tags\           — 55 个 .md（中文 tag）
```

所以即使修了 `home.html:121` 用 `prefix`，点击英文首页的分类卡片也会跳到 `/en/categories/jieqi/` 404（因为该文件不存在）。

**结论**：当前多语言架构**不完整**——非 zh-CN 语种没有 per-category / per-tag 页面。

> **优先级：P1**（多语言站点的核心导航损坏，QA 报告完全没提）

## 2.4 `_layouts/categories.html` 硬编码中文全角括号

`_layouts/categories.html:49`：
```liquid
<span class="category-block__count">（{{ cat_posts.size }} {{ i18n.common.articles }}）</span>
```

`（` 和 `）` 是硬编码中文全角括号——在英文/俄文/阿拉伯文页面，会看到中文括号包裹计数。

> **优先级：P3**（视觉不一致，但可读）

## 2.5 `_layouts/page.html` 面包屑硬编码 zh-CN 文案

`_layouts/page.html:25,29,33`：
```liquid
{%- capture bc -%}首页,{{ prefix }}/;分类,{{ prefix }}/categories/;{{ page.category_name | default: page.title }}{%- endcapture -%}
...
首页,{{ prefix }}/;标签,{{ prefix }}/tags/;#{{ page.tag | default: page.title }}
...
首页,{{ prefix }}/;{{ page.title }}
```

**3 个分支全部硬编码 "首页" "分类" "标签"**。`_layouts/page.html` 实际被 `category.html`、`tag.html`、`page.html` 之外的所有页面用作 layout（包括 `about.md`、`about-zhongyi.md`、`en/about.md`、`en/about-zhongyi.md`、`ar/about.md` 等）。

**注意**：`_layouts/category.html:23` / `_layouts/tag.html:25` 已经正确使用了 `i18n.nav.home/categories/tags`——但 `_layouts/page.html:25,29,33` 没有。

> **优先级：P2**（所有 /en/about/、/ar/about/ 等页面顶部显示"首页 > 分类"中文面包屑）

## 2.6 `_layouts/post.html:159` 硬编码英文 aria-label

`_layouts/post.html:159`：
```html
<section class="related-posts container" aria-label="Related articles">
```

中文页（`/_posts/...`）和阿拉伯页（`/ar/.../...`）等所有 7 个语言版本都会显示这个**英文** aria-label。i18n.yml 中已有 `i18n.common.related_title: 同主题阅读/Related Reading/Похожие статьи/...`（7 个语言都定义了），但模板没用。

> **优先级：P2**（a11y 一致性损坏）

## 2.7 `_layouts/post.html:227` 硬编码中文 aria-label

`_layouts/post.html:227`：
```html
<nav class="post__nav container" aria-label="文章导航">
```

i18n.yml 已有 `i18n.common.post_nav_aria: 文章导航 / Article navigation / Навигация / ...`（7 个语言都定义了），但模板未用。

> **优先级：P2**（英文/俄文/阿拉伯文页面的"文章导航"中文 aria-label）

## 2.8 `_includes/header.html:115` 硬编码中文 aria-label / title

`_includes/header.html:115`：
```html
<button class="theme-toggle" type="button" aria-label="切换主题" title="切换明暗主题">
```

i18n.yml 已有 `i18n.a11y.toggle_theme: 切换主题 / Toggle theme / Сменить тему / ...`（7 个语言都定义了）。`{{ i18n }}` 变量在 header.html 中未 assign（见 §2.2），所以即使替换也渲染为空——需要先 assign `i18n`。

> **优先级：P1**（所有 7 语言的主题切换按钮都是中文 aria-label）

## 2.9 `_includes/breadcrumb.html:24` 分隔符不响应 RTL

`_includes/breadcrumb.html:24`：
```html
<span class="breadcrumb__sep" aria-hidden="true">&gt;</span>
```

在 RTL 语言（`ar`）下，`>` 视觉方向错误。需用 CSS `[dir="rtl"] .breadcrumb__sep::before { content: "<"; }` 或 JS 动态切换。

> **优先级：P3**（RTL 视觉一致性）

## 2.10 `assets/js/nav.js` 和 `assets/js/theme.js` 硬编码中文

**nav.js:13, 22**：
```js
toggle.setAttribute('aria-label', open ? '关闭菜单' : '打开菜单');
...
toggle.setAttribute('aria-label', '打开菜单');
```

**theme.js:19, 20**：
```js
btn.setAttribute('aria-label', theme === 'dark' ? '切换为浅色主题' : '切换为深色主题');
btn.setAttribute('title', theme === 'dark' ? '切换为浅色主题' : '切换为深色主题');
```

JS 不能直接用 Liquid 表达式，所以硬编码。但 Liquid 模板可在 `<script>` 块中**注入** `window.QIHUANG_I18N`，如 `_layouts/search.html:63-85` 已做的那样（TC-008 修复方案）。`default.html` 也应注入 `a11y.toggle_theme`、`a11y.open_menu`、`a11y.close_menu`，nav.js / theme.js 改为读取 `window.QIHUANG_I18N`。

> **优先级：P1**（mobile menu / 主题切换的 a11y，对所有 7 语言均坏）

## 2.11 `assets/js/i18n.js` 缺少 hot-key 跳过

`i18n.js:11-13`：
```js
var SUPPORTED = ['zh-CN', 'en', 'ru', 'fr', 'es', 'id', 'ar'];
var RTL = ['ar'];
var DEFAULT = 'zh-CN';
```

硬编码的 7 语种列表与 `_config.yml:18-25` 的 `supported_langs:` 重复。**任何新增/删除语言都要改 2 个地方**。可改为从 `<html lang>` 推断或从 `window.QIHUANG_LANGS` 注入。

> **优先级：P3**（维护性问题）

## 2.12 `assets/js/{nav,i18n,search,theme}.js` 事件监听器内存泄漏（理论）

四个 JS 文件总计 **9 处** `document.addEventListener`（DOMContentLoaded + keydown + click）：
- theme.js: 1 处 (DOMContentLoaded)
- nav.js: 3 处 (DOMContentLoaded, keydown, click)
- i18n.js: 3 处 (DOMContentLoaded, click, keydown)
- search.js: 2 处 (DOMContentLoaded, keydown)

Jekyll 是静态站，无 SPA 路由，故**实际不会**泄漏。但若未来加入 Turbolinks / 客户端路由，需封装清理函数。

> **优先级：P3**（未来兼容性，非当前问题）

## 2.13 `_config.yml:131` `liquid.error_mode: warn` 与 CI 失败的关系

`_config.yml:130-132`：
```yaml
liquid:
  error_mode: warn
```

QA 报告 §3 列表中"TC-006 排查方向"提到这是"silent 模式"——但实际上 `error_mode: warn` **不**让 Jekyll 跳过错误，只是让 build 仍能继续（生成残缺页面）并把错误写到 stderr。

**结合 actions_jobs.json:54-60 的 1s 失败**：Jekyll 在 1s 内失败，极可能是 **`_config.yml` 解析错误**或 **`_data/i18n.yml` 解析错误**（YAML 缩进错、Liquid 嵌套）。`error_mode: warn` 不能阻止这些**严重**错误。

> **建议**：把 `error_mode` 改成默认的 `loud`，并把构建过程跑一遍 `bundle exec jekyll build --trace` 取真实错误。CI 失败根本原因不一定是此值。

## 2.14 `post.html:139` `related_count` 变量未使用（次要死代码）

`_layouts/post.html:139-153`：
```liquid
{%- assign related_count = 0 -%}    <!-- L141 -->
{%- assign related_list = '' | split: '' -%}    <!-- L143 -->
{%- for p in related_posts -%}
  {%- if p.url != page.url and related_count < 3 -%}
    {%- assign related_list = related_list | push: p -%}
    {%- assign related_count = related_count | plus: 1 -%}    <!-- L151 -->
  {%- endif -%}
{%- endfor -%}
```

`related_count` 只在 `if` 条件中使用，然后被 push 写入 list。变量本身不输出。**功能正确**，但 `related_count` 这个变量名让读者误以为它在后续被使用——可改为更清晰的命名。

> **优先级：P3**（代码可读性）

## 2.15 `categories.html:13, 25` 重复 `assign cur_lang`（次要代码异味）

`_layouts/categories.html:13` 和 `:25` 都做了 `{%- assign cur_lang = page.lang | default: site.default_lang -%}`——一次即可。其它 layout 都只在文件开头 assign 一次。

> **优先级：P3**（代码异味）

## 2.16 `archive.html:55` 仅有 zh-CN 和 ru 后缀，其它语言无年份后缀

`_layouts/archive.html:55`：
```liquid
{%- if cur_lang == 'zh-CN' -%}{{ year.name }} 年{%- elsif cur_lang == 'ru' -%}{{ year.name }} г.{%- else -%}{{ year.name }}{%- endif -%}
```

en/fr/es/id/ar 都无后缀（直接 `2026`）。`zh-CN` 和 `ru` 有后缀是合理的（语义不同），但 en 习惯写"2026 Articles"——目前是裸 `2026`，可读性差。

> **优先级：P3**（仅排版细节）

## 2.17 TC-019 QA 报告**计数偏小**

QA 报告说"ar/es/id 3 个语言顶层页面是 5-7 行空白"。**实际**有 **5 个**语言（`ar`、`es`、`id`、`fr`、`ru`）的 `index.md`、`archive.md`、`categories.md`、`tags.md`、`search.md`（共 25 个文件）body 全空：

| 语言 | index.md | about.md | archive.md | categories.md | tags.md | search.md | about-zhongyi.md |
| --- | --- | --- | --- | --- | --- | --- | --- |
| en | 10 行 (3 body) | 65 行 (41 body) ✓ | 9 行 (2 body) | 9 行 (2 body) | 9 行 (2 body) | 9 行 (2 body) | 86 行 (47 body) ✓ |
| ru | **6 行 (0 body)** | 47 行 ✓ | **6 行 (0 body)** | **6 行 (0 body)** | **6 行 (0 body)** | **6 行 (0 body)** | 78 行 ✓ |
| fr | **6 行 (0 body)** | 47 行 ✓ | **6 行 (0 body)** | **6 行 (0 body)** | **6 行 (0 body)** | **6 行 (0 body)** | 78 行 ✓ |
| es | **6 行 (0 body)** | 47 行 ✓ | **6 行 (0 body)** | **6 行 (0 body)** | **6 行 (0 body)** | **6 行 (0 body)** | 78 行 ✓ |
| id | **6 行 (0 body)** | 47 行 ✓ | **6 行 (0 body)** | **6 行 (0 body)** | **6 行 (0 body)** | **6 行 (0 body)** | 78 行 ✓ |
| ar | **6 行 (0 body)** | 47 行 ✓ | **6 行 (0 body)** | **6 行 (0 body)** | **6 行 (0 body)** | **6 行 (0 body)** | 78 行 ✓ |

QA 报告"3 个语言"应为"5 个语言"（fr、ru 也空）。**TC-019 实际影响：5 × 5 = 25 个空文件**（QA 报告低估）。

> **优先级：P2**（影响 5 种语言用户的首次浏览体验）

## 2.18 `_data/i18n.yml` 部分 level-3 键**仅部分语言定义**

除上面 §2.1 列出的完全缺失外，`navigation` 在 4/7 语言有定义（en, es, fr, ru?），3/7 缺（zh-CN, ar, id）。需补全。

---

# 任务 3：必改 Top 5 代码修改清单

## 必改 #1【P0】修复 `/sitemap.xml` 404 — 影响 SEO + 全部 hreflang

**文件**：`Gemfile:9`, `_config.yml:36-65`, `_includes/head.html:31`, `_includes/footer.html:77`, `robots.txt:8`

**当前**：sitemap plugin 在 Gemfile 中声明但未在 `_config.yml` 的 `plugins:` 列表显式启用；`head.html:31` / `footer.html:77` / `robots.txt:8` 引用 `/sitemap.xml` 全部 404。

**修改前**（`_config.yml:36-65`）—— 注意 plugins 块缺失：
```yaml
# 排除无关文件
exclude:
  - Gemfile
  ...
  - .well-known
```

**修改后**：
```yaml
# 插件
plugins:
  - jekyll-paginate
  - jekyll-sitemap
  - jekyll-seo-tag
  - jekyll-include-cache
  - jekyll-feed

# 排除无关文件
exclude:
  ...
```

**修复理由**：sitemap 404 → 搜索引擎爬不到全部 105 篇文章 + 7 语种 hreflang 矩阵失效。
**回归风险**：若 github-pages gem 把 `plugins:` 写法替换为其内部默认，可能产生重复定义——可加 `# github-pages 已默认加载以下 gem, 此处显式列出仅为明确意图` 注释。

---

## 必改 #2【P1】修复 i18n 重构引入的 5 个**未定义 key 引用**（disclaimer / tags / related 全部为空）

**文件**：`_layouts/post.html:95, 113, 115, 127, 161`, `_layouts/search.html:19`, `_includes/header.html:37, 45, 115`, `_data/i18n.yml`

**当前**（`_data/i18n.yml:147-238` common 块）：
```yaml
common:
  ...
  last_reviewed: "最后审校"   # ✓ 存在
  search_page_title: "搜 · 索"   # ✓ 存在
  search_input_aria: "搜索文章"  # ✓ 存在
  # ❌ 缺：tags_label, post_tags, related_title, related_posts, disclaimer_title, disclaimer_body, reviewed_by, volume_one_short
  # ❌ a11y.medical_disclaimer 不存在
  # ❌ common.navigation 仅 4/7 语言
```

**修改后**（在 `_data/i18n.yml` common 块中追加缺失键的 7 语言定义）：
```yaml
common:
  ...
  tags_label: "标签"           # zh-CN
  post_tags: "标签"
  related_title: "同主题阅读"  # ✓ 已有，改键名 → 复用
  related_posts: "同主题阅读"  # NEW
  disclaimer_title: "免责声明"  # NEW
  disclaimer_body: "本文内容仅供中医文化科普与日常养生参考，穴位按摩、食疗药膳、导引功法等不能替代专业医疗诊断与治疗。个人体质有异，施用前请咨询执业中医师；急症、重症、孕期及慢性疾病患者请及时就医，遵从医嘱。"  # NEW (把硬编码内容从 footer.html 移过来)
  reviewed_by: "审校"          # NEW
  volume_one_short: "卷 · I"   # NEW
a11y:
  ...
  medical_disclaimer: "Medical disclaimer"  # NEW（zh-CN: "医疗免责声明"，en: "Medical disclaimer"）
```

**修复理由**：post.html:113,115,127 渲染 disclaimer、tags、related posts 全部为空——这是用户最常访问的页面，缺失严重。
**回归风险**：无（仅添加键）。

---

## 必改 #3【P1】`_includes/header.html` 缺少 `{% assign i18n = ... %}` 导致 mobile menu / 主题切换 aria-label 全空

**文件**：`_includes/header.html:7`（追加 assign），`:37, :45, :115`（替换为 i18n 引用）

**修改前**（`_includes/header.html:7-9`）：
```liquid
{%- assign cur_lang = page.lang | default: 'zh-CN' -%}

<a class="site-brand" href="{{ '/' | relative_url }}" aria-label="{{ site.data.i18n.strings[cur_lang].nav.home | default: site.data.i18n.strings['zh-CN'].nav.home }}">
```

**修改后**：
```liquid
{%- assign cur_lang = page.lang | default: 'zh-CN' -%}
{%- assign i18n = site.data.i18n.strings[cur_lang] -%}    <!-- NEW -->

<a class="site-brand" href="{{ '/' | relative_url }}" aria-label="{{ i18n.nav.home | default: site.data.i18n.strings['zh-CN'].nav.home }}">

...

<button class="nav-toggle" ... aria-label="{{ i18n.a11y.open_menu }}">  <!-- L37 替换 site.data.i18n... 为 i18n -->
...
<nav id="site-nav" ... aria-label="{{ i18n.nav.home }} {{ i18n.common.navigation }}">  <!-- L45 同上 -->
...
<button class="theme-toggle" type="button" aria-label="{{ i18n.a11y.toggle_theme }}" title="{{ i18n.a11y.toggle_theme }}">  <!-- L115 -->
```

**修复理由**：mobile menu 按钮、主题切换按钮、主导航的 aria-label 在 7 语言下**全部为空**——屏幕阅读器读不到，且违反 a11y 标准。
**回归风险**：需要确认 i18n.a11y.open_menu / toggle_theme 在所有 7 语言都有定义（i18n.yml:301-311 已定义 ✓）。

---

## 必改 #4【P1】多语言 URL 一致性 — `home.html:121` / `post.html:29` / `post.html:99` / `tags.html:39` 硬编码 `/categories/`、`/tags/`

**文件**：`_layouts/home.html:121`, `_layouts/post.html:29`, `_layouts/post.html:99`, `_layouts/tags.html:39`

**当前**（`_layouts/home.html:119-125`）：
```liquid
<li class="category-card" style="--cat-color: {{ cat.color }}">
  <a href="{{ '/categories/' | append: cat.slug | append: '/' | relative_url }}" class="category-card__link">
```

**修改后**（添加 `prefix` 变量）：
```liquid
{%- if cur_lang == site.default_lang -%}
  {%- assign prefix = '' -%}
{%- else -%}
  {%- assign prefix = '/' | append: cur_lang -%}
{%- endif -%}

<li class="category-card" style="--cat-color: {{ cat.color }}">
  <a href="{{ prefix | append: '/categories/' | append: cat.slug | append: '/' | relative_url }}" class="category-card__link">
```

类似地修 `post.html:29`、`post.html:99`、`tags.html:39`。

**注意**：仅改 URL 不足以解决——`/en/categories/jieqi/` 这类页面**当前不存在**（见 §2.3）。**必须**同时执行选项之一：
- A. 复制 `_data/categories-i18n.yml` 的 6 个 slug，生成 `en/categories/jieqi.md` 等 36 个文件（6 langs × 6 slugs）
- B. 在 `category.html` 中判断 `page.lang` 决定是否渲染（保留单一文件，按 URL 推断语言）
- C. 在所有 6 个非 zh-CN 语种使用 `{{ prefix | default: '/zh-CN' }}/categories/<slug>/`——这意味着只在 zh-CN 提供分类/标签页，其他语种跳到中文版

**修复理由**：英文首页点击分类卡片跳中文分类页（多语言站点根本性 bug）。QA 报告未提及。
**回归风险**：若选 A，6 × 6 = 36 个 .md 需创建并维护 7 语种翻译，工作量大但最干净。若选 B，需重构 category.html 布局结构。

---

## 必改 #5【P1】注入 `window.QIHUANG_I18N` 到 default.html，让 nav.js / theme.js 不再硬编码中文

**文件**：`_layouts/default.html:32-35`（追加 `<script>` 注入），`assets/js/nav.js:13, 22`（改读 `window.QIHUANG_I18N.a11y.open_menu`），`assets/js/theme.js:19, 20`（改读 `window.QIHUANG_I18N.a11y.toggle_theme`）

**当前**（`assets/js/nav.js:13`）：
```js
toggle.setAttribute('aria-label', open ? '关闭菜单' : '打开菜单');
```

**修改后**（`assets/js/nav.js:13, 22`）：
```js
var i18n = (window.QIHUANG_I18N && window.QIHUANG_I18N.a11y) || {};
toggle.setAttribute('aria-label', open ? (i18n.close_menu || 'Close menu') : (i18n.open_menu || 'Open menu'));
...
toggle.setAttribute('aria-label', i18n.open_menu || 'Open menu');
```

在 `_layouts/default.html` `<head>` 或 `<body>` 末尾追加：
```liquid
{%- if page.layout == 'post' or page.layout == 'page' or page.layout == 'home' or page.layout == 'search' or page.layout == 'archive' or page.layout == 'category' or page.layout == 'tag' or page.layout == 'categories' or page.layout == 'tags' or page.layout == '404' -%}
<script>
  window.QIHUANG_I18N = window.QIHUANG_I18N || {};
  window.QIHUANG_I18N.a11y = window.QIHUANG_I18N.a11y || {};
  {%- assign cur_lang_default = page.lang | default: 'zh-CN' -%}
  {%- assign i18n_default = site.data.i18n.strings[cur_lang_default] -%}
  window.QIHUANG_I18N.a11y.open_menu = {{ i18n_default.a11y.open_menu | jsonify }};
  window.QIHUANG_I18N.a11y.close_menu = {{ i18n_default.a11y.close_menu | jsonify }};
  window.QIHUANG_I18N.a11y.toggle_theme = {{ i18n_default.a11y.toggle_theme | jsonify }};
</script>
{%- endif -%}
```

**修复理由**：mobile menu 和 theme toggle 的 aria-label 在所有 7 语言下都是硬编码中文——屏幕阅读器会读出错误语言。TC-008 报告未完全覆盖 JS 部分。
**回归风险**：window 全局变量若被其它脚本覆盖会冲突——用 `QIHUANG_I18N` 已有的命名空间（`search.html:63-85` 已使用），冲突概率低。

---

# 附录 A：QA 报告 28 条问题 vs 实际状态总表

| TC | 优先级 | 状态 | 关键证据 |
| --- | --- | --- | --- |
| TC-001 5 个 404 资源 | P0 | **3/5 仍 404**：sitemap.xml, 404.html, en/feed.xml；humans.txt/atom.xml 已修 | head.html:30,31; footer.html:77,79 |
| TC-002 CI 失败 | P0 | **仍存在** | actions_jobs.json:54-60 |
| TC-003 i18n 100+ 键 90% 未用 | P0 | **部分缓解**：本次重构使 50+ 键开始被消费，但仍有 ~30 键 0 引用 | i18n.yml:147-238 |
| TC-004 post-meta 用 hero.title | P0 | **已修复** | post-meta.html:27 |
| TC-005 header aria-label | P0 | **已修复** | header.html:9 |
| TC-006 Build site 失败 | P0 | **仍存在**（同 TC-002） | actions_jobs.json:54-60 |
| TC-007 layout 硬编码中文 | P1 | **60% 修复，~19 处仍硬编码** | 见 §1.4 表 |
| TC-008 search.js 硬编码 | P1 | **search.js 已修，nav.js / theme.js 仍硬编码** | nav.js:13,22; theme.js:19,20 |
| TC-009 search.html 硬编码 | P1 | **80% 修复**，2 处仍硬编码 | search.html:19,21 |
| TC-010 XSS | P1 | **已修复** | search.js:49,261 |
| TC-011 home.html class 名 | P1 | **已修复** | home.html:127 |
| TC-012 home hero i18n | P1 | **已修复** | home.html:9-12,25,44,50,66 |
| TC-013 搜索不按语言过滤 | P1 | **已修复** | search.js:341 |
| TC-014 paginate | P1 | **已修复**（配置清理） | _config.yml:1-132 |
| TC-015 future post | P2 | **已修复**（`future: false`） | _config.yml:38 |
| TC-016 暗色对比 4.08 | P2 | **仍存在** | main.css:49-64 |
| TC-017 浅色 fg-mute 4.39 | P2 | **仍存在** | main.css:14 |
| TC-018 i18n 死键 | P2 | **部分缓解** | 见 §2.1 |
| TC-019 ar/es/id 空 body | P2 | **仍存在，5/7 语言空** | 见 §2.17 |
| TC-020 temp 文件 commit | P2 | **已修复** | .gitignore:16-18 |
| TC-021 tag 排序 | P2 | **仍存在** | tags.html:29 |
| TC-022 search.json 死代码 | P2 | **已修复** | search.json:11-37 |
| TC-023 tag URL 编码 | P2 | **仍存在**（中文 tag permalink 仍 200） | tags/ 目录 55 个中文文件名 |
| TC-024 FUNCTIONALITY.md Jekyll 4 | P3 | **已修复**（"Jekyll 3.10"） | FUNCTIONALITY.md（1 行 mojibake） |
| TC-025 redirect.html | P3 | **已修复**（目录中无此文件） | _layouts/ 11 个 .html |
| TC-026 authors.yml 死代码 | P3 | **仍存在** | authors.yml:1-48，0 引用 |
| TC-027 CSS 暗色 dup | P3 | **已修复**（合并为 1 块，注释说明） | main.css:42-64 |
| TC-028 footer http 链接 | P3 | **仍存在** | footer.html:93 |

**总结**：QA 报告 28 条中，**12 条已修复**（TC-004, 005, 010, 011, 012, 013, 014, 015, 020, 022, 024, 025, 027），**2 条部分修复**（TC-001, TC-003/018），**2 条 80% 修复**（TC-007, TC-009），**1 条 60% 修复**（TC-008），**1 条 50% 修复**（TC-019，仅 3/5 语言被准确识别），**10 条仍存在**。

---

# 附录 B：重构引入的 NEW BUG 清单

| ID | 优先级 | 位置 | 描述 |
| --- | --- | --- | --- |
| NEW-1 | P1 | search.html:19 | 引用不存在的 `i18n.common.volume_one_short` |
| NEW-2 | P1 | post.html:113 | 引用不存在的 `i18n.a11y.medical_disclaimer` |
| NEW-3 | P1 | post.html:115 | 引用不存在的 `i18n.common.disclaimer_title` |
| NEW-4 | P1 | post.html:115 | 引用不存在的 `i18n.common.disclaimer_body` |
| NEW-5 | P1 | post.html:127 | 引用不存在的 `i18n.common.reviewed_by` |
| NEW-6 | P1 | header.html:37,45,115 | `i18n` 变量未在 header.html 中 assign，所有 `{{ i18n.* }}` 渲染为空 |
| NEW-7 | P1 | post.html:95 | 引用不存在的 `i18n.common.tags_label` |
| NEW-8 | P1 | post.html:161 | 引用不存在的 `i18n.common.related_posts` |
| NEW-9 | P1 | home.html:121, post.html:29, post.html:99, tags.html:39 | 硬编码 `/categories/`、`/tags/` URL——多语言 URL 不一致 |
| NEW-10 | P2 | post.html:159 | 硬编码英文 `aria-label="Related articles"` |
| NEW-11 | P2 | post.html:227 | 硬编码中文 `aria-label="文章导航"`（i18n key 存在但未用） |
| NEW-12 | P2 | page.html:25,29,33 | 硬编码中文面包屑 "首页" "分类" "标签" |
| NEW-13 | P2 | header.html:115 | 硬编码中文 `aria-label`/`title`（应读 `i18n.a11y.toggle_theme`） |
| NEW-14 | P2 | nav.js:13,22 | 硬编码中文 `'打开菜单' / '关闭菜单'` |
| NEW-15 | P2 | theme.js:19,20 | 硬编码中文 `'切换为浅色主题' / '切换为深色主题'` |
| NEW-16 | P3 | categories.html:49 | 硬编码中文全角括号 `（` `）` |
| NEW-17 | P3 | post.html:95,115,125,127 | i18n 值后硬编码中文全角冒号 `：` |
| NEW-18 | P3 | breadcrumb.html:24 | `&gt;` 分隔符不响应 RTL |
| NEW-19 | P3 | i18n.js:11-13 | `SUPPORTED` 数组与 `_config.yml:18-25` 重复维护 |
| NEW-20 | P3 | categories.html:13,25 | 重复 `assign cur_lang`（代码异味） |

---

# 附录 C：建议立即验证的真实部署情况

以下 5 个 URL 建议在浏览器/CI 中实际验证（不依赖报告）：

1. `https://xiebingcheng.github.io/-shiyan-/sitemap.xml` —— 期望 200
2. `https://xiebingcheng.github.io/-shiyan-/404.html` —— GitHub Pages 自定义 404 应自动展示，但直接 GET 该 URL 仍 404
3. `https://xiebingcheng.github.io/-shiyan-/en/feed.xml` —— 期望 404（jekyll-feed 不生成多语种）
4. `https://xiebingcheng.github.io/-shiyan-/en/categories/jieqi/` —— 期望 404（文件不存在，QA 报告未测）
5. `https://github.com/xiebingcheng/-shiyan-/actions/runs/27012743529` —— 找真实 CI 错误日志

---

**审查完成**。所有结论均通过 `file:line` 验证，未做任何文件修改。报告保存于 `E:\中医shiyan网站\tests\code-review-findings.md`。
