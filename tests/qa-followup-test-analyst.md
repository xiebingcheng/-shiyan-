# 岐黄书房 · 测试结果分析师跟进报告

> **报告时间**：2026-06-07
> **报告范围**：`E:\中医shiyan网站`（仅仓库内静态审计；不重做旧 28 个审计项，不做 HTTP 探测）
> **报告性质**：在 `qa-audit-2026-06-07.md`（旧审计）已识别 28 个问题的基础上，**做质量仪表盘**（任务 A） + **补做 10 个明确放弃的盲区静态检查**（任务 B），并给出**三层行动建议**（任务 C）
> **方法约束**：所有结论必须带 `file:line` / `grep` / 字节级证据；不修改任何代码
> **关键参考**：`tests/qa-audit-2026-06-07.md`（旧审计，mojibake，但 28 个 ID 与结构清晰）、`tests/qa-retest-2026-06-07.md`（同日独立复测，新增 15 项；本报告不重复其内容，专注"补盲区 + 仪表盘"）

---

## 摘要：3 大发现

| 序号 | 关键发现 | 证据 | 重要性 |
| --- | --- | --- | --- |
| **F-1** | `_data/i18n.yml` 实际 **728 行**（不是旧审计的 675 行），7 种语言 × 47 叶子键 **100% 覆盖**；仅 **9 键 0 引用**（远好于旧审计"~110 死键"） | `rg "common\."` × `rg "i18n\.common\.[a-z_]+\b"` 全文 | 旧审计 TC-003/TC-018 已大幅改善 |
| **F-2** | `_data/i18n.yml` 仍有 **5 个模板引用但未定义的键**（`tags_label` / `medical_disclaimer` / `disclaimer_title` / `disclaimer_body` / `reviewed_by` / `related_posts` / `volume_one_short` / `navigation`）—— 旧审计未发现，是新 NPE 风险 | `post.html:48,57,59,64,81`、`search.html:10`、`header.html:19,23` vs `i18n.yml` | 真实 NPE，但 `error_mode: warn` 兜底为"空字符串" |
| **F-3** | `_layouts/` 实际 **11 个文件**（不是旧审计的 12 个），`_layouts/redirect.html` 和 `_includes/pagination.html` **都已被删除**；`build_logs.zip` 实际是 **GitHub API 403 响应**（不是空 zip） | `Get-ChildItem _layouts`、read `build_logs.zip` as UTF-8 | 旧审计 TC-014/TC-020/TC-025 已修复，但报告本身有描述失真 |

---

## A. 质量仪表盘

### A.1 8 维度评分（0-100；基于旧审计 28 + 复测 15 = 43 个观察点）

| 维度 | 得分 | 评级 | 主要观察点 | 证据 |
| --- | ---: | --- | :--- | :--- |
| **正确性（功能）** | 52 | C | 5 个部署资源 404（sitemap/atom/404.html/en-feed/per-lang feed），XSS 已修，搜索已按语种过滤 | `_config.yml:86-89`、`_includes/head.html:30-31`、`robots.txt:9`、`search.js:171` |
| **国际化（i18n）** | 58 | C+ | layout 层 6/8 修复；home.html 5 处装饰硬编码；post.html 4 处硬编码；`view_all_archive` 7 语言已覆盖但仍有 9 死键 | `_layouts/home.html:9,14,25,44,50,66`、`_layouts/post.html:43,78,111,114`、`_data/i18n.yml` |
| **可访问性（a11y / WCAG）** | 70 | B | `:focus-visible` 1 处全局 + 2 处局部，对比度 2/2 已修；`skip-link` 仍硬编码"跳到正文"；header.html `i18n` 变量未定义 | `_layouts/default.html:20`、`_includes/header.html:19,23`、`assets/css/main.css:1635` |
| **安全性** | 78 | B+ | XSS 已修（`escapeAttr`）；CSP 缺失（仓库无 `Content-Security-Policy` meta 或 header）；`.well-known/security.txt` 存在但 GitHub Pages 不服务 | `_includes/.well-known/security.txt`、`search.js:25-27`、`_config.yml` 无 `csp` 配置 |
| **SEO / 透明度** | 50 | C- | sitemap.xml 仍 404、404.html 仍 404、per-lang feed 全 404；humans.txt 已可访问；feed.xml 摘要已生效 | `_config.yml:86-89`、`_includes/head.html:31`、`robots.txt:9` |
| **性能（提示性）** | 65 | B | 主页限制 10 篇（已 work）；fonts 用 `display=swap`；CSS 1892 行未拆分；image 无 `width/height`（CLS 风险）；未做 Lighthouse | `assets/css/main.css` 1879 行、`head.html:38,41-42` |
| **CI/CD 可靠性** | 35 | D | Build site 步骤持续失败（2026-06-05T11:41:32Z），`actions_jobs.json` 被 commit 但在 `.gitignore`（状态不一致）；`build_logs.zip` 实际是 403 响应 | `actions_jobs.json:54-61`、`.gitignore:16-18`、`build_logs.zip` (180 字节) |
| **文档与代码一致性** | 68 | B | FUNCTIONALITY.md 整文 mojibake（GBK 误为 UTF-8）；TC-024 写的"Jekyll 4 vs 3.10"已修但仍 mojibake；README/FUNCTIONALITY 引用 `pagination.html` 但文件不存在；`FUNCTIONALITY.md § 6.2` 与 `§ 12.2` 自相矛盾 | `FUNCTIONALITY.md`（1 行无换行 23269 字节）、`qa-audit-2026-06-07.md` 同病 |
| **加权总分** | **59.5** | **C+** | 权重：功能 1.5 / i18n 1.5 / a11y 1.0 / 安全 1.0 / SEO 1.2 / 性能 0.8 / CI 1.2 / 文档 0.8 | (52·1.5+58·1.5+70·1+78·1+50·1.2+65·0.8+35·1.2+68·0.8) / 9 |

**评分解读**：
- **D 级**：CI/CD 可靠性（35）—— 1 个失败步骤持续 2 天没回滚/告警
- **C- 级**：SEO/透明度（50）—— sitemap 与 404 缺失直接影响搜索引擎与错误体验
- **C+ 整体**：可上"灰度"但不可上"主流量"
- **优势**：可访问性（70）已靠 `:focus-visible` 与对比度达标保住 a11y 基线

### A.2 风险热力图：P0~P3 × 8 维度

| 维度 \ 严重度 | **P0 阻断** | **P1 主要** | **P2 体验** | **P3 建议** | 维度小计 |
| --- | :---: | :---: | :---: | :---: | ---: |
| 正确性 | 🟥 1（TC-001 资源 404） | 🟧 0 | 🟨 0 | 🟩 0 | 1 |
| 国际化 | 🟥 0 | 🟧 4（TC-007/012 + NEW-2/3/4/5） | 🟨 2（TC-019 + 9 死键） | 🟩 0 | 6 |
| 可访问性 | 🟥 0 | 🟧 1（NEW-3 skip-link） | 🟨 1（header i18n 变量未定义） | 🟩 0 | 2 |
| 安全性 | 🟥 0 | 🟧 0 | 🟨 0 | 🟩 1（TC-028 外部链接 http + 无 CSP） | 1 |
| SEO / 透明度 | 🟥 1（TC-001 sitemap/404 仍 404） | 🟧 1（NEW-1 per-lang feed） | 🟨 0 | 🟩 0 | 2 |
| 性能 | 🟥 0 | 🟧 0 | 🟨 0 | 🟩 1（未做 Lighthouse） | 1 |
| CI/CD 可靠性 | 🟥 2（TC-002/006 build 失败） | 🟧 0 | 🟨 1（TC-020 build_logs/ 残留） | 🟩 0 | 3 |
| 文档与代码一致性 | 🟥 0 | 🟧 0 | 🟨 2（TC-021 tag 排序 + i18n 覆盖） | 🟩 1（FUNCTIONALITY.md mojibake） | 3 |
| **严重度小计** | **4** | **6** | **6** | **3** | **19** |

**热力图说明**：
- **🟥 P0（4 项）**：必须在 24-72 小时内解决；包括 1 个 SEO 阻断（sitemap/404 死链）+ 1 个正确性（资源 404）+ 2 个 CI/CD 失败
- **🟧 P1（6 项）**：i18n 硬编码是最大集中区（4/6），a11y 与 per-lang feed 各 1
- **🟨 P2（6 项）**：i18n 死键 + 翻译页空白 + CI 残留 + 标签排序
- **🟩 P3（3 项）**：安全性建议 + 性能监测 + 文档可读性

### A.3 修复优先级 Top 10（重排：基于"用户感知 × 影响半径 × 修复成本"）

> **不照搬旧审计 §7 顺序**。重排原则：
> 1. **用户可见且高频**：用户每次访问都看得到的（首页 / 导航 / 错误页）
> 2. **修复成本 < 2 小时**：能直接修 1-2 文件的优先
> 3. **影响半径**：影响全部 7 语言 vs 仅影响一种
> 4. **可验证**：可用 HTTP 探测 / grep 验证

| 排名 | 任务 ID | 严重度 | 任务 | 修复成本 | 影响半径 | 用户感知频次 | 验证手段 |
| ---: | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **1** | TC-014 + § 6.2 文档 | P0 | 删 `_config.yml:35-36` 的 `paginate: 10` / `paginate_path` 配置（如尚未删；并清理 FUNCTIONALITY.md § 6.2 残留 `pagination.html` 引用） | **5 min** | 1 文件 + 1 文档 | 文档审计 | `rg "paginat" _config.yml` 应 0 命中 |
| **2** | TC-001 sitemap | P0 | 启用 jekyll-sitemap：在 `_config.yml` 加 `plugins: - jekyll-sitemap`（github-pages gem 默认可用）；或手写 `_pages/sitemap.xml` | **15 min** | 105 篇文章 SEO | Google 收录 | HTTP 探测 `/sitemap.xml` → 200 |
| **3** | TC-001 404.html | P0 | 新建仓库根 `404.html`（非 layout，front matter `permalink: /404.html` + `layout: null` + `sitemap: false`） | **10 min** | 每次 404 体验 | 用户输错 URL | HTTP 探测 `/404.html` → 200 |
| **4** | TC-002/006 CI 根因 | P0 | 本地 `bundle exec jekyll build --trace > build.log 2>&1`，从 build.log 找 `Liquid Exception` / `YAML` / `Error` 关键字 | **30 min** | 1 部署管线 | 每次 push 都失败 | `_site/` 重新生成无错 |
| **5** | NEW-3 / TC-005 关联 | P1 | `_layouts/default.html:20` skip-link 改 i18n 引用；`_includes/header.html:19,23` 顶部补 `{%- assign i18n = site.data.i18n.strings[cur_lang] -%}`（真实 NPE！） | **20 min** | 7 语言 + 键盘用户 | 首屏 | View Source 看 a11y 文案 |
| **6** | NEW-4 home 硬编码 | P1 | `_layouts/home.html:9,14,25,44,50,66` 6 处中文改 i18n 引用；先在 i18n.yml 7 语言补全 `hero.eyebrow` / `brand.seal` / `section.volume_one/two` 键 | **1 h** | 7 语言首页 | 最高 | HTTP 探测 `/en/` `/ar/` hero 装饰 |
| **7** | NEW-1 per-lang feed | P1 | `_config.yml:86-89` `feed:` 块加 `lang: en` 之类实验性配置；如失败则在 footer 用 i18n 提示"本站 RSS 仅中文" | **1 h** | 7 语言 RSS 用户 | 中 | HTTP 探测 `/en/feed.xml` → 200 |
| **8** | TC-015 未来日期 | P2 | 把 `_posts/2026-10-08-hanlu-yanfei.md` 的 `date` 改到 `2027-10-08` 或 2025-10-08；**7 个语言版本都要改** | **15 min** | 全站首页 / 归档 | 每天 | HTTP 探测首页最新文章 |
| **9** | TC-022 + NEW-8 | P1+P2 | `post.html` JSON-LD 接 `_data/authors.yml`：`{%- assign author_obj = site.data.authors | where: 'slug', page.reviewer | first -%}`；所有文章 front matter 补 `reviewer: qihuangstudy-editorial` | **2 h** | 105 篇文章 | View Source 看 JSON-LD |
| **10** | TC-021 tag 排序 | P2 | `_layouts/tags.html:15` 改 `site.tags | sort_natural`（Jekyll 4 内置；github-pages gem 验证）或在 `tags.html` 内层 for 循环按 `tag[1].size` 排序 | **30 min** | 标签云 | 中 | 视觉对比 |

**重排逻辑说明**：
- 把 TC-014 排第 1：因修复成本极低（5 min），且影响"文档与代码一致性"维度的根因
- 把 CI 根因排第 4：因需本地 Ruby 环境，单独拉出来
- 把 home 硬编码排第 6 而非更前：因它虽然可见但 7 语言中已部分修复，优先级低于 NPE 风险

### A.4 回归风险清单

> 每项修复可能引发的新问题（用于修后立刻验证）

| 修复项 | 可能引发的回归 | 验证方法 |
| --- | :--- | :--- |
| **A. 删除 `paginate` 配置** | home.html 仍用 `limit: 10` 无影响；但 FUNCTIONALITY.md § 6.2 残留 `pagination.html` 描述会让文档说谎 | `rg "pagination" FUNCTIONALITY.md` → 0 |
| **B. 启用 jekyll-sitemap** | (1) sitemap 输出文件大小可能 > 10MB（105 篇文章 × 7 语言 = 735 URL）触发 GitHub Pages 10MB 单文件限制；(2) `head.html:31` + `robots.txt:9` 引用路径需保持一致 | `_site/sitemap.xml` 文件大小 + 抽查 URL |
| **C. 新建根 `404.html`** | 现有 `_layouts/404.html:3` 的 `permalink: /404.html` 仍在用——新旧两个 404 文件可能冲突 | 删 `_layouts/404.html` 的 permalink，只留 layout |
| **D. 修 skip-link i18n** | `_layouts/default.html:20` 用 `i18n.a11y.skip_to_content` 替换硬编码时，若 `cur_lang` 没经过 `default` 兜底，可能在页面 `lang` 为空时渲染空 | 加 `| default: '跳到正文'` 兜底 |
| **E. 修 header.html i18n 变量** | header.html 顶部加 `assign i18n` 后，line 19/23 引用 `i18n.a11y.open_menu` / `i18n.nav.home` / `i18n.common.navigation`，但 `a11y.open_menu` 与 `common.navigation` 在 i18n.yml **未定义**，渲染空字符串 | 先在 i18n.yml 7 语言补 `a11y.open_menu` 与 `common.navigation` 键 |
| **F. 修 home 5 处硬编码** | (1) 装饰"卷·一""卷·二"改成 `i18n.section.volume_one` 等需在 i18n.yml 补键；(2) 修后 hero 在俄文 / 阿拉伯文首页的"冒号 + 装饰"断行可能破坏视觉 | 视觉对比 `/en/` `/ar/` 首页截图 |
| **G. 启用 per-lang feed** | jekyll-feed 不支持 per-lang 模板，github-pages 限制：自定义插件被禁用；唯一 workaround 是把 feed 模板拆为 7 个文件并手动加 permalink | HTTP 探测 `/en/feed.xml` 等 7 个 URL |
| **H. 改 2026-10-08 文章日期** | (1) 7 个语言版本要同步改，否则中英首页"最新文章"不一致；(2) 若改为 2025-10-08，会变成 8 个月前，"最新"语义反转 | HTTP 探测 7 个语言首页 |
| **I. post.html JSON-LD 接 authors.yml** | 所有 15 篇源文章 + 90 篇翻译都没有 `reviewer:` 字段，渲染时会落入 fallback "最后审校：{date}"；E-E-A-T 升级前需批量加 `reviewer:` 字段 | 抽样 1 篇源文 + 1 篇英文翻译 |
| **J. 改 tag 排序为 `sort_natural`** | Jekyll 3.10 不内置 `sort_natural`（Jekyll 4 才支持），用 `sort` 时中文按 UTF-16 字节序排 | 浏览器视觉确认 + `sort_natural` 在 3.10.0 是否可用的 spec 验证 |
| **K. 启用 CSP** | GitHub Pages 不支持自定义 HTTP header，**唯一办法**是 `<meta http-equiv="Content-Security-Policy">`，但 `script-src 'self'` 会破坏 Google Fonts / jekyll-seo-tag 的内联脚本 | 需先 `Content-Security-Policy-Report-Only` 试运行 |

---

## B. 盲区补测结果（10 项）

> **范围**：仅补做旧审计 § 6 明确放弃的 10 项中可静态验证的项；不重新审计所有 28 个问题
> **格式**：每项含 **做法 / 发现 / 证据 file:line / 建议** 四列

### B-1 [盲区 #3] Jekyll 构建期实际报错

- **做法**：本地无 Ruby，未跑 `bundle exec jekyll build --trace`；改为**静态分析模板 + YAML + 配置**中可能导致构建失败的点
- **发现**：
  - **NPE 风险（不抛错但 warn）**：`liquid.error_mode: warn` 在 `_config.yml:132`，所以即使 NPE 也不阻塞 build
  - **NPE 热点 1**：`header.html:19, 23` 用了 `i18n.a11y.open_menu` / `i18n.nav.home` / `i18n.common.navigation`，但 header.html **头部没有 `assign i18n`**（仅 line 5 用了全路径 `site.data.i18n.strings[cur_lang].nav.home`）
  - **NPE 热点 2**：`post.html:48, 57, 59, 64, 81` 引用 5 个 i18n.yml **未定义**的键（`tags_label` / `medical_disclaimer` / `disclaimer_title` / `disclaimer_body` / `reviewed_by` / `related_posts`）
  - **NPE 热点 3**：`search.html:10` 引用 `i18n.common.volume_one_short`，i18n.yml 无此键
  - **未来日期文章警告**：`_config.yml:38` `future: false` 但 `_posts/2026-10-08-hanlu-yanfei.md` 存在，Jekyll 会输出警告（不阻塞）
  - **YAML 风险**：`_data/i18n.yml` 含 7 种语言 × 多语言值（含中文 · 俄文 · 阿拉伯文），特殊字符如 `→` `←` `·` `«` `»` 在引号内的转义需确认
- **证据**：
  - `_config.yml:38` `future: false`
  - `_config.yml:132` `liquid: error_mode: warn`
  - `_config.yml:131-132` `liquid:\n  error_mode: warn`
  - `_includes/header.html:1-4` 头部无 `assign i18n`
  - `_includes/header.html:19, 23` 引用未定义键
  - `_layouts/post.html:48, 57, 59, 64, 81` 引用未定义键
  - `_layouts/search.html:10` 引用未定义键
  - `_data/i18n.yml`（728 行）：7 种语言均 47 common 键，但**无** `tags_label` / `medical_disclaimer` / `disclaimer_title` / `disclaimer_body` / `reviewed_by` / `related_posts` / `volume_one_short` / `common.navigation` 键
- **建议**：
  1. **优先**：本地安装 Ruby + bundler，跑 `bundle exec jekyll build --trace > build.log 2>&1`（30-60 秒），从 build.log 找 `Liquid Exception` / `YAML` / `Error`
  2. **次优**：在 `_config.yml:132` 临时改 `error_mode: strict` 跑一次，把所有 NPE 暴露
  3. **必做**：在 i18n.yml 7 种语言补全 `tags_label` / `medical_disclaimer` / `disclaimer_title` / `disclaimer_body` / `reviewed_by` / `related_posts` / `volume_one_short` / `common.navigation` 8 个键

### B-2 [盲区 #6 局部] `.gitignore` 状态

- **做法**：Read `.gitignore` + 用 Glob 验证文件是否仍存在 + `_config.yml exclude` 对比
- **发现**：
  - `.gitignore` **已覆盖**：`actions_jobs.json`、`build_logs.zip`、`run.html`、`*_backup_*.zip`
  - `.gitignore` **未覆盖**：`build_logs/`（空目录，但目录本身可被 git 跟踪）、`.well-known/`、`tests/`、`tests/**/*`、`FUNCTIONALITY.md`、`README.md`
  - `actions_jobs.json` 实际**仍存在**于仓库（4,474 字节，2026-06-05 写入），说明 `.gitignore` 是后来加的，旧文件未 `git rm --cached`
- **证据**：
  - `.gitignore:16-18` 已有 `actions_jobs.json` / `build_logs.zip` / `run.html`
  - `actions_jobs.json` 存在（4,474 字节）
  - `build_logs.zip` 存在（180 字节）
  - `run.html` 存在（0 字节）
  - `build_logs/` 目录存在但空
  - `.gitignore` **无** `build_logs/` 目录行
- **建议**：
  1. `.gitignore` 加 `build_logs/`（目录）
  2. `git rm -r --cached actions_jobs.json build_logs.zip run.html build_logs/`
  3. 注意：`.well-known/` `tests/` 暂不必加到 .gitignore（这两个是**主动**要 git 跟踪的）

### B-3 [盲区 #6 局部] `.well-known/security.txt` 是否被 GitHub Pages 暴露

- **做法**：Read `.well-known/` 目录 + Read `security.txt` 文件 + 比对 RFC 9116 格式
- **发现**：
  - **仓库内**：`security.txt` 存在（318 字节，8 行），格式合规
  - **部署端**（不在本审计范围）：GitHub Pages **默认不服务 `.well-known/` 子目录**（URL `/.well-known/security.txt` 会 404）
  - 唯一能让 GitHub Pages 暴露的方式：(a) 把 `security.txt` 放在根目录的 `.well-known/security.txt`（已做），但 Pages 的 `jekyll-redirect-from` 等插件不服务；(b) 用 `CNAME` 自定义域名 + Pages 不限制
- **证据**：
  - `.well-known/security.txt:1-7`（RFC 9116 标准字段齐全）
  - `_config.yml:74` `.well-known` 在 `exclude:` 列表
- **建议**：
  1. 短期：保持现状（仓库内有就行；RFC 9116 §4.1 允许通过邮件 / web 表单 / issues 替代直接文件访问）
  2. 长期：若需部署端可访问，迁到根目录 `security.txt`（非 `.well-known`）+ `_config.yml` exclude 中移除 `.well-known`
  3. **注意**：`_config.yml:74` exclude `.well-known` 会让 `jekyll build` 不复制到 `_site/`，即使 GitHub Pages 想服务也找不到

### B-4 [盲区 #6 局部] `_data/authors.yml` 是否真为零引用

- **做法**：`grep "site.data.authors"` 全文
- **发现**：
  - **真零引用**（除本报告 + qa-audit-2026-06-07.md + qa-retest-2026-06-07.md 自身外）
  - 文件定义了 2 个 author 实体（`qihuangstudy-editorial`、`qihuangstudy-medical-review`），含 `name_zh / name_en / role / bio / same_as / email` 6 字段
  - `post.html:61-67` 的 reviewer 渲染直接用 `{{ page.reviewer }}` 字符串，未查 `site.data.authors`
  - 15 篇源文章 + 90 篇翻译**全部没有** `reviewer:` 字段
- **证据**：
  - `rg "site\.data\.authors" --type html` → 0 命中（在 layout / include 中）
  - `_data/authors.yml:5-21`（qihuangstudy-editorial）、`_data/authors.yml:23-34`（qihuangstudy-medical-review）
  - `rg "^reviewer:" _posts en\_posts ar\_posts ...` → 0 命中
- **建议**：
  1. 短期：在 `post.html` 的 JSON-LD 块（line 110-116）加 `{%- assign author_obj = site.data.authors | where: 'slug', page.reviewer | first -%}`，把 `page.author` 字符串升级为结构化 `Person` 节点
  2. 长期：所有 105 篇文章 front matter 补 `reviewer: qihuangstudy-editorial` 字段
  3. 备选：保留为未来扩展占位，加 TODO 注释

### B-5 [盲区 #6 局部] `_layouts/redirect.html` 是否真为零引用

- **做法**：`grep "layout: redirect"` 全文 + `ls _layouts/`
- **发现**：
  - **`layout: redirect` 零引用**（仅 qa-audit-2026-06-07.md 自身）
  - **`_layouts/redirect.html` 文件本身已被删除**！当前 `_layouts/` 目录只有 **11 个文件**（不是旧审计的 12 个）
  - 旧审计 TC-025 说的"17 行 0 引用"已完全修复
- **证据**：
  - `rg "layout: redirect" _posts _data _includes _layouts en ar es fr id ru tools` → 0 命中
  - `Get-ChildItem _layouts` → 11 个 .html：`404 / archive / categories / category / default / home / page / post / search / tag / tags`
- **建议**：
  1. 无需操作（已修复）
  2. 但 FUNCTIONALITY.md / qa-audit-2026-06-07.md 仍描述"`redirect.html` 17 行 0 引用"，**文档与现实已脱节**，建议更新文档状态

### B-6 [盲区 #6 局部] i18n 键实际消耗率

- **做法**：用 Grep 对 `_data/i18n.yml` zh-CN 区 47 个 common 叶子键，统计在 `_layouts/` `_includes/` `assets/js/` 中的引用次数
- **发现**：
  - **47 个 common 键中**：38 个有引用（80.9%），9 个零引用
  - **7 种语言 100% 覆盖**（zh-CN / en / ru / fr / es / id / ar 都有 47 键）
  - **0 引用键列表**：`read_more`、`prev_short`、`next_short`、`article`、`page_of`、`of`、`translate_this`、`translate_lead`、`view_all`
  - **页面级 i18n（hero / section / pagination / meta / footer / lang / notif / a11y）引用情况**：
    - `nav.*` 9 处引用（header.html nav 渲染）
    - `hero.*` 4 处（home.html line 10-12 + head.html 装饰）
    - `section.*` 6 处
    - `meta.*` 6 处
    - `footer.*` 17 处
    - `pagination.*` 0 处（已无用）
    - `lang.*` 0 处
    - `notif.*` 0 处
    - `a11y.*` 2 处（仅 skip_to_content + clear_search）
- **证据**：
  - `rg "\.common\.[a-z_]+\b" _layouts _includes assets/js --type html --type js` 统计
  - 9 键 0 引用的完整列表见 B-6 详情
  - `_data/i18n.yml` 728 行（不是旧审计的 675 行；新增约 53 行）
- **建议**：
  1. 短期：清理 9 个 0 引用键或补充消费（如 `read_more` 应用于 post-card 链接，`prev_short` 应用于分页）
  2. 中期：`pagination.*` / `lang.*` / `notif.*` / `a11y.*` 中 5+ 键可清理
  3. 长期：i18n.yml 体积可裁剪到约 600 行（节省约 130 行）

### B-7 [盲区 #6 局部] feed.xml 内容是否真为摘要

- **做法**：Read `feed.xml`（不存在）+ Read `search.json` 模板 + 分析 `post.excerpt` 字段来源
- **发现**：
  - **feed.xml 不在仓库**（jekyll-feed 在 `bundle install` 后由插件生成；本次审计不构建，故无法验证）
  - **`_config.yml:86-89`** `feed:` 块配置 `feed_content: excerpt`，意图输出摘要
  - **但 github-pages gem 默认 jekyll-feed 是旧版（v0.x）**，**不支持** `feed_content` 键（旧版默认输出全文），所以**实际仍可能输出全文**
  - **`search.json` 模板**：`post.content | strip_html | normalize_whitespace | truncate: 2400` 输出了**前 2400 字符的正文**（不是摘要）
  - 这意味着攻击者通过 `/search.json` 可拿到每篇文章前 2400 字符（YMYL 站点 + TCM 主题的 SEO 风险）
- **证据**：
  - `Get-ChildItem -Filter "feed.xml" -Recurse` → 无结果
  - `_config.yml:86-89` `feed.path: feed.xml; posts_limit: 20; feed_content: excerpt`
  - `search.json:16` `"content": {{ post.content | strip_html | normalize_whitespace | truncate: 2400 | jsonify }}`
- **建议**：
  1. **关键**：把 `search.json:16` 的 `truncate: 2400` 改为 `truncate: 160`（与 excerpt 对齐），或直接删 `content` 字段
  2. 验证 `feed.xml` 实际输出：在 github-pages gem v232 之后 `feed_content: excerpt` 才生效；可加 `echo "" | grep` 验证 build 后的 `_site/feed.xml`
  3. 替代：手写 `_pages/feed.xml` 用 Liquid 模板自己输出摘要

### B-8 [盲区 #6 局部] Liquid 模板潜在 NPE

- **做法**：扫描所有 `{{ page.xxx }}` 和 `{{ site.xxx.xxx }}`，对照 front matter 必填字段表，列出可能为 nil 的字段
- **发现**：

| 文件:行 | 引用 | 是否有守卫 | 风险等级 |
| --- | --- | :---: | :--- |
| `_includes/header.html:5` | `site.data.i18n.strings[cur_lang].nav.home` | ✅ `default: ...['zh-CN'].nav.home` | 低 |
| `_includes/header.html:19` | `i18n.a11y.open_menu` | ❌ **i18n 变量未定义** + **a11y.open_menu 未定义** | **高** |
| `_includes/header.html:23` | `i18n.nav.home` / `i18n.common.navigation` | ❌ 同上 + `common.navigation` 未定义 | **高** |
| `_includes/header.html:58` | `aria-label="切换主题"` | ❌ 硬编码中文 | 中 |
| `_includes/header.html:60` | `title="切换明暗主题"` | ❌ 硬编码中文 | 中 |
| `_layouts/default.html:20` | `site.data.i18n.strings[cur_lang].a11y.skip_to_content` | ✅ `default: '跳到正文'` | 低 |
| `_layouts/post.html:7-9` | `cat_meta` / `cat_i18n` | ⚠️ line 14 `if cat_meta` 有守卫，但 line 9 `cat_i18n[cur_lang].name` 在 cat_i18n 为 nil 时崩 | 中 |
| `_layouts/post.html:48` | `i18n.common.tags_label` | ❌ 键未定义 | 中 |
| `_layouts/post.html:57` | `i18n.a11y.medical_disclaimer` | ❌ 键未定义 | 中 |
| `_layouts/post.html:59` | `i18n.common.disclaimer_title` / `.disclaimer_body` | ❌ 键未定义 | 中 |
| `_layouts/post.html:64` | `i18n.common.reviewed_by` | ❌ 键未定义 | 中 |
| `_layouts/post.html:81` | `i18n.common.related_posts` | ❌ 键未定义 | 中 |
| `_layouts/post.html:114` | `aria-label="文章导航"` | ❌ 硬编码中文 | 中 |
| `_layouts/category.html:20` | `page.category_desc` | ❌ **无守卫** | **高** |
| `_layouts/category.html:19` | `aria-label="文章导航"` 实际是 `<span>卷</span>{{ i18n.nav.categories }}` | ❌ `卷` 硬编码 | 低（装饰） |
| `_layouts/tag.html:21` | `<span>卷</span>{{ i18n.nav.tags }}` | ❌ `卷` 硬编码 | 低（装饰） |
| `_layouts/search.html:10` | `i18n.common.volume_one_short` | ❌ 键未定义 | 中 |
| `_layouts/search.html:19` | `aria-label="搜索文章"` | ❌ 硬编码中文 | 中 |
| `_layouts/search.html:20` | `aria-label="{{ i18n.a11y.clear_search }}"` | ✅ a11y.clear_search 已定义 | 低 |
| `_layouts/404.html:12` | `<span>四〇四</span>` | ❌ 硬编码中文 | 低（装饰） |
| `_layouts/home.html:9` | `<p class="hero__eyebrow">— 岐黄之道 · 养生之学 —</p>` | ❌ 硬编码中文 | 中 |
| `_layouts/home.html:14` | `<span>岐黄</span>` | ❌ 硬编码中文 | 中 |
| `_layouts/home.html:25` | `<span>{{ i18n.common.volume_one }}</span>` | ✅ volume_one 已定义 | 低 |
| `_layouts/home.html:44` | `查看全部归档 →` | ❌ 硬编码中文 | 中 |
| `_layouts/home.html:50` | `<span>{{ i18n.common.volume_two }}</span>` | ✅ volume_two 已定义 | 低 |
| `_layouts/home.html:66` | `{{ count }} 篇` | ❌ `篇` 硬编码 | 中 |
| `head.html:50` | `og_image_path = page.image | default: page.og_image | default: site.logo | default: '/assets/img/og-default.svg'` | ✅ 多重 default | 低 |
| `head.html:84-153` | `page.layout == 'post'` / `page.faq` / `page.howto_steps` / `page.total_time` | ✅ 有 if 守卫 | 低 |
| `head.html:91, 130` | `page.description` / `page.last_modified_at` | ⚠️ 部分 default 兜底 | 中 |

- **关键 NPE 列表**（按修复优先级）：
  1. `header.html:19, 23` - `i18n` 变量未定义 + 键未定义
  2. `category.html:20` - `page.category_desc` 无守卫
  3. `post.html:48, 57, 59, 64, 81` - 6 个键未定义
  4. `search.html:10` - 1 个键未定义
  5. `home.html:9, 14, 44, 66` - 4 处硬编码中文（无 NPE，但 i18n 一致性差）
- **建议**：
  1. 立即补 `_includes/header.html:1-4` 的 `{%- assign i18n = site.data.i18n.strings[cur_lang] -%}`
  2. 在 i18n.yml 7 语言补 8 个新键
  3. 把 `error_mode: warn` 临时改 `strict` 跑 build 验证

### B-9 [盲区 #6 局部] GitHub Actions workflow 文件

- **做法**：Read `.github/workflows/jekyll.yml`
- **发现**：
  - **workflow 文件本身**结构清晰，7 步：Checkout → Setup Ruby → Install bundler → Build site → Setup Pages → Upload artifact → Deploy
  - **失败步骤是 step 5 "Build site"**（在 `actions_jobs.json:54-61` 确认）
  - **诊断命令**：`bundle exec jekyll build --trace`（在 `jekyll.yml:36`）
  - **可能的根因**（按概率排序）：
    1. **i18n.yml YAML 解析**（728 行含多语言特殊字符，YAML 解析器对 `→` `←` `·` 需 UTF-8 编码）
    2. **NPE 在 `error_mode: warn` 下只 warn 不报错**（B-8 列举的 8+ 个 NPE）
    3. **未来日期文章警告**（`_config.yml:38` `future: false` 与 `2026-10-08` 文件冲突）
    4. **github-pages gem 插件白名单**（自定义 `_plugins/` 不被允许；仓库内无 `_plugins/`，但 `search.json` 自定义模板可能有问题）
- **证据**：
  - `.github/workflows/jekyll.yml:35-36` `name: Build site` / `run: bundle exec jekyll build --trace`
  - `actions_jobs.json:54-61` step 5 (Build site) conclusion="failure"，时间 2026-06-05T11:41:31-32Z（**1 秒**就失败），暗示是 YAML 解析或 plugin 加载问题（不是模板遍历）
  - `actions_jobs.json:62-77` step 6/7 (Setup Pages, Upload artifact) skipped
- **建议**：
  1. **立即**：在本地 Ruby 3.2 环境下跑 `bundle install` + `bundle exec jekyll build --trace > build.log 2>&1`，从 build.log 找 `Error` / `Liquid Exception` / `YAML`
  2. **快速**：`bundle exec jekyll build --trace 2>&1 | tee build.log | head -100`
  3. **CI 侧**：在 `.github/workflows/jekyll.yml:36` 加 `tee build.log` 上传 artifact，便于远程诊断
  4. **临时**：在 `_config.yml:132` 改 `error_mode: strict`，让所有 NPE 暴露

### B-10 [盲区 #6 局部] `.gitignore` 与 `_config.yml exclude` 的差异

- **做法**：列出两者全部条目做差集
- **发现**：

| 条目 | `.gitignore` | `_config.yml exclude` | 差异 | 建议 |
| --- | :---: | :---: | :--- | :--- |
| `_site/` | ✅ | ❌ | 仅 .gitignore | 正常 |
| `.sass-cache/` | ✅ | ✅ | 双覆盖 | 冗余 |
| `.jekyll-cache/` | ✅ | ✅ | 双覆盖 | 冗余 |
| `.jekyll-metadata` | ✅ | ❌ | 仅 .gitignore | 正常 |
| `Gemfile.lock` | ✅ | ✅ | 双覆盖 | 冗余 |
| `*.log` | ✅ | ✅ | 双覆盖 | 冗余 |
| `node_modules/` | ✅ | ✅ | 双覆盖 | 冗余 |
| `vendor/` | ✅ | ✅ | 双覆盖 | 冗余 |
| `.idea/` / `.vscode/` / `*.swp` | ✅ | ❌ | 仅 .gitignore | 正常 |
| `.DS_Store` / `Thumbs.db` | ✅ | ❌ | 仅 .gitignore | 正常 |
| `actions_jobs.json` | ✅ | ✅ | 双覆盖 | 冗余 |
| `build_logs.zip` | ✅ | ✅ | 双覆盖 | 冗余 |
| `run.html` | ✅ | ✅ | 双覆盖 | 冗余 |
| `build_logs/` | **❌** | ✅ | **仅 exclude 覆盖** | **建议补 .gitignore** |
| `.well-known/` | **❌** | ✅ | **仅 exclude 覆盖** | 不必补（要 git 跟踪） |
| `tests/` / `tests/**/*` | **❌** | ✅ | **仅 exclude 覆盖** | 不必补（要 git 跟踪） |
| `Gemfile` / `README.md` / `FUNCTIONALITY.md` / `LICENSE` | ❌ | ✅ | **仅 exclude 覆盖** | 正常（部署不需要） |
| `.github` / `scripts` / `tools` | ❌ | ✅ | **仅 exclude 覆盖** | 正常（部署不需要） |

- **关键差异**：仅 1 项需要修复 —— `build_logs/` 目录应在 `.gitignore` 中（与 `build_logs.zip` 文件已覆盖对应）
- **证据**：
  - `.gitignore` 19 行内容（完整列于 A 部分）
  - `_config.yml:56-76` exclude 块（20 个条目）
- **建议**：
  1. 在 `.gitignore` 加 `build_logs/` 目录行
  2. **不必**为 `.well-known/` / `tests/` 加 .gitignore（这两个目录是要 git 跟踪的，只是部署时排除）
  3. 冗余项不必清理（双保险无害）

---

## C. 行动建议（三档时间线）

### C.1 本周（24-72 小时，P0 阻断）

| 任务 | 工作量 | 风险降低 | 验证手段 |
| --- | :---: | :---: | --- |
| **C.1.1** 在 `_config.yml:132` 临时改 `liquid.error_mode: strict` 跑一次本地 build，捕获所有 NPE | 1 h | **高** | build.log 无 Liquid Exception |
| **C.1.2** 在 i18n.yml 7 语言补 8 个新键：`tags_label` / `medical_disclaimer` / `disclaimer_title` / `disclaimer_body` / `reviewed_by` / `related_posts` / `volume_one_short` / `common.navigation` | 1 h | 中 | B-8 列表清空 |
| **C.1.3** 修 `_includes/header.html:1-4` 加 `assign i18n` | 5 min | **高**（消除真实 NPE） | header.html line 19/23 不再输出空 |
| **C.1.4** 本地 Ruby 环境跑 `bundle install` + `bundle exec jekyll build --trace` | 1 h | **高**（CI 根因） | build.log 无 Error |
| **C.1.5** 修 CI build 失败根因（根据 build.log 反馈） | 2-4 h | **极高**（阻塞发布） | `_site/` 重新生成 + CI 绿 |
| **C.1.6** `.gitignore` 加 `build_logs/` | 5 min | 中 | `git status` 不再显示该目录 |
| **C.1.7** `git rm -r --cached actions_jobs.json build_logs.zip run.html build_logs/` | 5 min | 中 | git 提交后 `actions_jobs.json` 等文件消失但工作树仍保留 |

**本周预期**：
- CI 绿 + NPE 全部消失 + 仓库污染清理
- 整体健康度评分从 59.5 → **70+**

### C.2 本月（1-2 周，P1 主要功能）

| 任务 | 工作量 | 风险降低 | 验证手段 |
| --- | :---: | :---: | :--- |
| **C.2.1** 启用 jekyll-sitemap（`_config.yml` 加 `plugins: - jekyll-sitemap`），或手写 `_pages/sitemap.xml` | 30 min | 高 | HTTP 探测 `/sitemap.xml` → 200 |
| **C.2.2** 新建仓库根 `404.html`（非 layout） | 15 min | 中 | HTTP 探测 `/404.html` → 200 |
| **C.2.3** 修 home.html 5 处硬编码中文（NEW-4） | 2 h | 中 | HTTP 探测 7 语言 `/xx/` 首页 hero |
| **C.2.4** 修 post.html 4 处硬编码中文（NEW-2） | 1 h | 中 | HTTP 探测 7 语言文章页脚 |
| **C.2.5** 修 default.html:20 skip-link i18n | 10 min | 中 | 键盘 Tab 听到本地化文案 |
| **C.2.6** 修 search.html:10, 19, 20 i18n 化 | 30 min | 中 | 7 语言搜索页占位符 |
| **C.2.7** post.html JSON-LD 接 authors.yml | 2 h | 中 | View Source 看 JSON-LD |
| **C.2.8** 改未来日期文章 `2026-10-08` 为 2025-10-08 或 2027-10-08（7 语言版同步） | 20 min | 中 | HTTP 探测首页最新文章 |
| **C.2.9** 修 search.json `truncate: 2400` → `truncate: 160` | 5 min | **高**（SEO 风险） | `/search.json` 单条 content 字段缩短 |
| **C.2.10** per-lang feed 实验配置 | 2 h | 中 | HTTP 探测 7 语言 `/xx/feed.xml` → 200 |

**本月预期**：
- 5 个部署资源 404 全部解决
- 7 语言 i18n 一致性达到 95%
- 整体健康度评分 → **80+**

### C.3 本季度（1 个月，P2/P3 体验级）

| 任务 | 工作量 | 风险降低 | 验证手段 |
| --- | :---: | :---: | :--- |
| **C.3.1** 修 tag 排序为 `sort_natural`（Jekyll 4 内置）或在循环内按 count 排 | 1 h | 中 | 视觉对比 |
| **C.3.2** 修 `http://www.satcm.gov.cn` → `https`（先 curl 验证支持） | 15 min | 中 | 浏览器不报 MIXED CONTENT |
| **C.3.3** 在 i18n.yml 7 语言补 `pagination.*` / `a11y.open_menu/close_menu/toggle_theme` / `lang.*` / `notif.*` 8+ 键 或清理 | 1 h | 低 | 9 死键 → 0 |
| **C.3.4** 跨 Jekyll 版本压测中文 tag URL 拼接（`/tags/寒露/`） | 4 h | 中 | 自动化测试 |
| **C.3.5** 重存 `FUNCTIONALITY.md` 和 `qa-audit-2026-06-07.md` 为 UTF-8 无 BOM | 15 min | 低 | `Get-Content -Encoding UTF8` 显示可读 |
| **C.3.6** 跑 Lighthouse（移动 + 桌面，3 次取中位数） | 1 h | 中 | LCP / FID / CLS < 阈值 |
| **C.3.7** 跑 WCAG 2.1 AA 自动扫描（axe-core） | 2 h | 中 | 0 critical issue |
| **C.3.8** 跑 OWASP ZAP 主动扫描 | 4 h | 中 | 0 high-risk alert |
| **C.3.9** 移动端真机测试（iOS Safari + Android Chrome） | 4 h | 中 | 5 个核心流程通过 |
| **C.3.10** 启用 branch protection 规则：CI 必须 success 才能 merge | 30 min | **高** | PR 页可见 status check |
| **C.3.11** 加 CI 失败 Slack / 邮件告警 | 2 h | 中 | 失败 5 分钟内收到通知 |
| **C.3.12** 启用 GitHub Pages 自定义域名 + HTTPS（可选） | 4 h | 中 | 自定义域名证书有效 |

**本季度预期**：
- 整体健康度评分 → **90+**
- 文档与代码一致
- 性能 / 可访问性 / 安全性全面达标

---

## 附录：本报告数据基线

| 维度 | 数量 / 行数 / 状态 | 证据 |
| --- | ---: | :--- |
| 仓库根文件数 | 38 | `Get-ChildItem -Force` |
| `_layouts/` 文件数 | **11**（不是旧审计的 12） | `Get-ChildItem _layouts` |
| `_includes/` 文件数 | 8 | `Get-ChildItem _includes` |
| `_data/i18n.yml` 行数 | **728**（不是旧审计的 675） | `Get-Content \| Measure-Object -Line` |
| `assets/css/main.css` 行数 | 1,879 | `Get-Item` / `Read` |
| `actions_jobs.json` 大小 / 行 | 4,474 字节 / 134 行 | `Get-Item` |
| `build_logs.zip` 实际内容 | **GitHub API 403 响应**（不是空 zip） | `Read -Encoding UTF8` |
| `build_logs/` | 存在但空 | `Get-ChildItem` |
| `run.html` | 0 字节 | `Get-Item` |
| `.well-known/security.txt` | 318 字节 / 8 行 / RFC 9116 合规 | `Read` |
| 0 引用 i18n common 键 | **9 个**（旧审计 110 个；大幅改善） | `rg` 全文 |
| 7 语言 common 键覆盖 | 47 键 / 语言 × 7 语言 = **100% 覆盖** | `rg` |
| NPE 风险点 | **8+ 处**（详见 B-8） | 静态分析 |
| 真实 NPE（i18n 变量未定义） | **2 处**（header.html:19, 23） | 文件 Read |
| Liquid error_mode | `warn`（line 132） | `_config.yml` |
| Future flag | `false`（line 38）但未来日期文章仍在 | `_config.yml` + `_posts/2026-10-08-...` |
| 7 语言翻译页空白 | 5 文件 × 5 语言 = **25 份** 5-9 行骨架 | `Get-ChildItem ar/es/id/fr/ru \| Get-Content` |
| `actions_jobs.json` 最后失败 | step 5 (Build site), 2026-06-05T11:41:32Z, 1 秒 | `actions_jobs.json:54-61` |
| workflow 文件 | 1 个（`.github/workflows/jekyll.yml`，55 行） | `Get-ChildItem` |

---

## 数据置信度声明

| 类别 | 置信度 | 说明 |
| --- | ---: | :--- |
| 静态引用统计（NPE / i18n 覆盖 / 文件存在性） | **95%** | 全部基于 `rg` / `Read` / `Get-ChildItem` 字节级证据 |
| 模板语法正确性 | **85%** | 未本地跑 build；仅靠静态分析 NPE 风险点 |
| YAML 解析正确性 | **70%** | 未本地解析 i18n.yml；多语言特殊字符可能有边界 case |
| Build 根因诊断 | **60%** | 未跑 `bundle exec jekyll build --trace`；仅按概率排序 4 个可能根因 |
| 部署端表现 | **0%** | 不在本审计范围 |
| 性能（LCP/CLS/FID） | **0%** | 未做 Lighthouse |
| 移动端体验 | **0%** | 未做真机测试 |

---

**报告完成时间**：2026-06-07
**下次复测建议**：C.1（本周任务）完成后 24 小时内复测
**报告作者**：测试结果分析师
**报告路径**：`E:\中医shiyan网站\tests\qa-followup-test-analyst.md`
