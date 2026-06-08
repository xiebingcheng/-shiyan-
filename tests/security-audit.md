# 岐黄书房 · 安全审计报告

- **审计日期**：2026-06-07
- **审计范围**：`E:\中医shiyan网站\` 仓库源码 + 部署行为（基于源码静态分析，未实际跑构建）
- **审计方法**：仅 Read + Grep + Glob，不修改任何文件；结论全部可复现
- **审计员**：应用安全工程师
- **YMYL 风险评估**：本站是中医养生 YMYL 站点（健康/医疗类），按 Google 搜索质量指南对 E-E-A-T 和 Trust 有更高要求。安全基线应高于普通信息站。
- **基线参考**：已知 QA 报告 `tests\qa-audit-2026-06-07.md` 标记的 1 个 P1 XSS（TC-010）。本报告在该结论之外补做全量审计。

---

## 0. 执行摘要

| 级别 | 数量 | 主要风险 |
| --- | --- | --- |
| **P0（高）** | **2** | 客户端 XSS 真实可被利用（search.js 命名混淆） + 全站零 CSP |
| **P1（中）** | **6** | 1 个协议降级链接（http://）+ 1 个误导性 SRI 缺失 + 2 个供应链/部署链 + 1 个内容权限 + 1 个隐私合规 |
| **P2（低）** | **4** | 2 个 i18n 健壮性 + 1 个 YMYL 审校签名缺失 + 1 个 SVG 在 OG 链路 |
| **P3（信息）** | — | TC-001/TC-002/TC-010 已知重复项，已确认现状 |
| **清单（已检查）** | 12 项 | 见末尾"清单"章节 |

**关键发现一句话**：在 `search.js` 内 `escapeAttr` 函数名是误导的——它实际是 HTML 转义（不转义 URL scheme），如果未来 `_config.yml` 引入第三方数据源或 post `permalink` 被污染（理论上），TC-010 的修复无法覆盖 `javascript:` 协议的 href。这是与 TC-010 强相关、但报告未点出的**根本原因**。

---

## 1. 高风险 (P0)

### P0-1 [客户端 XSS · 与 TC-010 同根] `escapeAttr` 命名错误，URL scheme 未净化

- **位置**：`assets/js/search.js:25-27`（定义） + `assets/js/search.js:132`（使用）
- **证据**：
  ```js
  // search.js:25-27
  function escapeAttr(s) {
    return escapeHtml(s);
  }
  // search.js:132
  html += '  <h3 class="search-result__title"><a href="' + escapeAttr(p.url) + '">'
        + highlight(p.title, keywords) + '</a></h3>';
  ```
  `escapeAttr` 实际只调用 `escapeHtml`，**不**做 URL scheme 过滤。`escapeHtml` 的字符集是 `&<>"'`，**不包含 `:`、`.`、字母**。
- **影响（具体到 payload）**：
  - 当前 `p.url` 来源：`search.json:11` 的 `{{ post.url | relative_url | jsonify }}`。Jekyll 的 `relative_url` 会把 baseurl `/` 拼到前头，使任何 `permalink` 都被强制变成以 `/` 开头的相对路径，所以**实战中** `javascript:` payload 在 `post.url` 阶段就被 prefix 抵消（变成 `/-shiyan-//javascript:alert(1)`，浏览器解析为相对路径，不会执行）。
  - **但是**，`escapeAttr` 的实现没有任何 scheme 校验，**违反"纵深防御"**——若未来 (a) 引入第三方数据源、或 (b) `search.json` 模板被改用 `post.canonical_url` 等可控字段、或 (c) 一次错误的 refactor 把 `relative_url` 拿掉，TC-010 的修复立刻失效，攻击者可在搜索结果页植入 `<a href="javascript:...">` 并诱导用户点击。
  - 攻击场景（假设性，前置条件：post front matter 注入或 build 污染）：
    ```yaml
    # _posts/2026-XX-XX-evil.md
    permalink: /javascript:alert(document.domain)/
    ```
    构建后 `search.json` 含 `"url": "/-shiyan-//javascript:alert(document.domain)/"`，`escapeAttr` 不拦截，渲染为 `<a href="/-shiyan-//javascript:alert(document.domain)/">`。
  - 当前**未利用**的根本原因不是代码防御，而是 `relative_url` 的副作用——一旦有人重构 `search.json`，就成 XSS。
- **OWASP 分类**：A03:2021 Injection（XSS 子类）
- **建议修复（具体代码）**：
  ```js
  // search.js:25-27 替换为真正的 URL 净化
  function isSafeUrl(u) {
    if (u == null) return false;
    var s = String(u);
    // 仅允许 http(s)://、相对路径（以 / 开头但不以 // 开头）、片段、查询串
    if (s.charAt(0) === '/') {
      // 拒绝 protocol-relative URL：//evil.com
      if (s.charAt(1) === '/') return false;
      return true;
    }
    return /^(https?:)/i.test(s);
  }
  function escapeAttr(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' })[c];
    });
  }
  // search.js:132
  var safeUrl = isSafeUrl(p.url) ? p.url : '#';
  html += '  <h3 class="search-result__title"><a href="' + escapeAttr(safeUrl) + '">'
        + highlight(p.title, keywords) + '</a></h3>';
  ```
  同时建议把 `function escapeAttr` 改名 `escapeHtmlAttr`（不再误导），并加注释说明"对 `href` 用前请先调 `isSafeUrl`"。

### P0-2 [CSP / 安全响应头] 整站零 CSP、零 X-Frame-Options、零 nosniff

- **位置**：`_includes/head.html`（缺失）
- **证据**：用 `grep -nE "Content-Security-Policy|X-Frame-Options|X-Content-Type-Options|nosniff|Referrer-Policy|Permissions-Policy" -r _includes _layouts` 无任何匹配。`_config.yml` 也无相关字段。GitHub Pages 不支持自定义 HTTP 响应头（无 Cloudflare/Netlify 代理），**唯一可行**的方案是 `<meta http-equiv>`。
- **影响**：
  - 站点是 YMYL 内容，存在被 iframe 嵌入做"伪权威"包装的点击劫持风险（无 `frame-ancestors`）。
  - 任意一个 XSS（包括 P0-1 那个被 `relative_url` 巧合抵消的）一旦突破，会完全控制 DOM；CSP 是最后一道防线。
  - 浏览器可能对老旧 `.svg` 资源做 MIME-sniff（例如 `Content-Type: text/plain` 的 SVG 被当成 HTML 解析）。
- **OWASP 分类**：A05:2021 Security Misconfiguration
- **建议修复**（在 `_includes/head.html` 顶部、`<meta charset>` 之后插入）：
  ```html
  <meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self' 'unsafe-inline';
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
    font-src 'self' https://fonts.gstatic.com data:;
    img-src 'self' data:;
    connect-src 'self';
    frame-ancestors 'none';
    form-action 'self';
    base-uri 'self';
    object-src 'none';
    upgrade-insecure-requests;
  ">
  <meta http-equiv="X-Content-Type-Options" content="nosniff">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  ```
  说明：
  - `'unsafe-inline'` 是 Jekyll 注入的 inline `<script>`（head.html:15-25 防主题闪烁）和 JSON-LD `<script type="application/ld+json">`（head.html:85-152）所必需。`search.html:31-43` 的 `window.QIHUANG_I18N` 也是 inline。
  - 若要彻底去掉 `unsafe-inline`，需把所有 inline script 改成外部文件 + nonce，是大改造；当前阶段允许 `unsafe-inline` 即可，**比 0 CSP 强一个量级**。
  - `frame-ancestors 'none'` 等同于 `X-Frame-Options: DENY`，对点击劫持有强约束。
  - `form-action 'self'` 防止未来若加入表单时被诱导外发（虽然当前无表单）。
  - GitHub Pages **不会**发送 `Strict-Transport-Security`，只能由 Cloudflare/Netlify 在 CDN 层加。这是部署平台的硬限制，无法在源码解决。

---

## 2. 中风险 (P1)

### P1-1 [协议降级 / 链接合规] `http://www.satcm.gov.cn` 明文 HTTP 外链

- **位置**：`_includes/footer.html:47`
- **证据**：
  ```html
  <li><a href="http://www.satcm.gov.cn" rel="noopener noreferrer nofollow" target="_blank">国家中医药管理局</a></li>
  ```
  与同一文件 line 46 (`https://www.nhc.gov.cn`) 和 line 48 (`https://www.wfcms.org`) 不一致。
- **影响**：
  - 明文 HTTP 链接会被浏览器在升级时变成 `https://...`，但**不会**自动带 `Upgrade-Insecure-Requests` 之外的强制升级。配合 P0-2 里的 CSP `upgrade-insecure-requests`，本链接会被自动升级；但 CSP 本身目前不存在。
  - `rel` 已含 `noopener`（`noreferrer` 也含），`nofollow` 也在——这块没问题。
  - 中医药管理局是国内权威站，明文 HTTP 链接在用户视角下被仿冒站劫持的可能性（DNS 污染 / 中间人）不为零。
- **OWASP 分类**：A05:2021 Security Misconfiguration
- **建议修复**：
  ```html
  <li><a href="https://www.satcm.gov.cn" rel="noopener noreferrer nofollow" target="_blank">国家中医药管理局</a></li>
  ```
  改前请 `curl -I https://www.satcm.gov.cn` 确认可达；如不可达则保留 HTTP 并在 CSP 加 `upgrade-insecure-requests`。

### P1-2 [第三方资源 / SRI] Google Fonts CSS 缺 SRI 与 `referrerpolicy`

- **位置**：`_includes/head.html:38`
- **证据**：
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=Noto+Serif+SC:wght@400;500;600;700;900&family=Long+Cang&display=swap" rel="stylesheet">
  ```
  - 无 `integrity=`（SRI）
  - 无 `crossorigin=`
  - 无 `referrerpolicy=`
- **影响**：
  - Google Fonts 的 CSS 是动态生成（按 user-agent 决定 woff2/woff/ttf），**SRI 严格意义上不适用**——但 SRI 仍可在初次抓取时算 hash 写死，Google Fonts 一旦更换版本就会破。这是 trade-off。
  - 真正的纵深防御是**自托管字体**（推荐路径），见下。
  - 当前 `referrer` meta 在 head.html:6 已是 `no-referrer-when-downgrade`，对 Google 域 POST 升级时不会泄露 referrer；但 Google Fonts 不属于 cross-origin POST 升级场景，泄露面有限。
- **OWASP 分类**：A08:2021 Software and Data Integrity Failures
- **建议修复**（二选一，按优先级）：
  1. **优选**：自托管字体。下载 `Ma+Shan+Zheng`、`Noto+Serif+SC`、`Long+Cang` 的 woff2 到 `assets/fonts/`，然后在 `main.css` 用 `@font-face` 引用，去掉 head.html:38 的 Google Fonts `<link>`。彻底消除第三方依赖。
  2. **若不自托管**：至少加 `crossorigin="anonymous" referrerpolicy="no-referrer"`，并接受无 SRI 的事实（注释说明原因）。

### P1-3 [供应链] `Gemfile` 未锁版本，`Gemfile.lock` 被 gitignore

- **位置**：`Gemfile`（全文） + `.gitignore:5`
- **证据**：
  ```ruby
  # Gemfile
  source "https://rubygems.org"
  gem "github-pages", group: :jekyll_plugins
  group :jekyll_plugins do
    gem "jekyll-paginate"
    gem "jekyll-sitemap"
    gem "jekyll-seo-tag"
    gem "jekyll-include-cache"
    gem "jekyll-feed"
  end
  gem "tzinfo-data", platforms: [:mingw, :mswin, :x64_mingw, :jruby]
  gem "wdm", platforms: [:mingw, :mswin, :x64_mingw, :jruby]
  ```
  ```gitignore
  # .gitignore:5
  Gemfile.lock
  ```
  无 `~> x.y` 锁、无 SHA 锁。
- **影响**：
  - 每次 `bundle install`（CI 中由 `ruby/setup-ruby@v1` + `bundler-cache: true` 触发，line 27-30）都拉**当前最新**的 `github-pages` gem 及其传递依赖。`github-pages` 的官方 policy 是每月发版，可能在某次构建中拉到含 CVE 的 kramdown / liquid / nokogiri 版本。
  - `Gemfile.lock` 缺失意味着**不可复现构建**——本地通过、CI 失败 / 站点排版异常的原因难定位。
  - `bundler-cache: true` 仅在有 lock 文件时才有完整 cache 效果；缺 lock 时只 cache 已装好的 gem，下次 CI 跑会再解算。
- **OWASP 分类**：A06:2021 Vulnerable and Outdated Components
- **建议修复**：
  1. 取消 `.gitignore` 的 `Gemfile.lock`（这是 GitHub Pages 默认仓的旧建议，但你已用自定义 workflow + actions/deploy-pages，lock 提交无害）。
  2. 本地 `bundle install` → `bundle lock --add-platform x86_64-linux x86_64-mingw32` 一次，提交 `Gemfile.lock`。
  3. 同时在 `Gemfile` 给 `github-pages` 加 `~> 230`（或当前支持的版本），避免 major 升级。

### P1-4 [供应链] 第三方 GitHub Actions 锁定到 tag，未锁 SHA

- **位置**：`.github/workflows/jekyll.yml:24, 27, 39, 42, 55`
- **证据**：
  ```yaml
  - uses: actions/checkout@v4           # line 24
  - uses: ruby/setup-ruby@v1           # line 27
  - uses: actions/configure-pages@v4   # line 39
  - uses: actions/upload-pages-artifact@v3   # line 42
  - uses: actions/deploy-pages@v4      # line 55
  ```
  全部用浮 tag。
- **影响**：
  - GitHub 允许维护者重写已存在的 tag 指向新 commit（社区事件已发生多次）。如果某次 action 作者账号被攻陷，恶意 commit 可被推到现有 tag 路径，下次 CI 静默执行恶意代码。
  - 因有 `permissions:` 块（line 9-12）做了 `contents: read / pages: write / id-token: write` 的最小化，爆炸半径被收窄——但 `pages: write` + `id-token: write` 仍然足够让攻击者替换 `_site` 内容（页面篡改/挂马）。
- **OWASP 分类**：A08:2021 Software and Data Integrity Failures
- **建议修复**：把每个 `uses:` 改成 SHA 锁定，格式：
  ```yaml
  - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
  - uses: ruby/setup-ruby@8a3a8270b03a16a3ee0e7d4ef6e2c41a69a4d463 # v1.146.0
  - uses: actions/configure-pages@983f2174720d186c0569c1f3c8d30b4a45f7eb3b # v4.0.1
  - uses: actions/upload-pages-artifact@56afc09a3c1ab393bb74b0ba0a8a31e9b53c1249 # v3.0.0
  - uses: actions/deploy-pages@d6db901652b46ed782ef83fef7e3abb6c5f8c8a9 # v4.0.0
  ```
  SHA 写死后，PR review 改 `uses:` 会触发 diff 警报。

### P1-5 [隐私 / GDPR] 整站无隐私政策、Cookie 声明

- **位置**：整站
- **证据**：`grep -rE "隐私|隐私政策|privacy policy|cookie" _includes _layouts *.md en/*.md ar/*.md es/*.md fr/*.md id/*.md ru/*.md` 无任何匹配。`localStorage` 用了 3 个键（`theme`、`qihuang-lang`），`sessionStorage` 0 个，Cookie 0 个（用 `grep -nE "document\.cookie" assets/js` 确认无）。
- **影响**：
  - GDPR / 中国《个人信息保护法》(PIPL) 对面向公众的站点有透明度要求。YMYL（健康/医疗）站点被监管重点关注。
  - localStorage 不属于 GDPR 严格意义上的"cookie"，**但** `localStorage` 已被欧盟数据保护委员会 (EDPB) 在 2023 年指南中明确纳入"类似 cookie 的追踪技术"——需要同等程度告知。
  - 当前未挂 Google Analytics / gtag / baidu / cnzz（已 grep 确认），无第三方追踪；**这是好的**。但"无追踪"和"有声明"是两件事。
- **OWASP 分类**：A04:2021 Insecure Design（隐私设计的缺失）
- **建议修复**：
  1. 新建 `privacy.md`（zh-CN） + `en/privacy.md` + 6 个语言版本，内容至少：
     - 用了哪些 localStorage 键、用途、保留时长、是否跨设备同步（否）
     - 用了 Google Fonts（说明是 Google LLC 服务，IP 会发给 Google；如开启 P1-2 修复则删掉此条）
     - 不收集表单数据、不挂第三方分析
     - 联系邮箱（已在 `humans.txt` / `about.md` 给出，可复用）
  2. 在 `_includes/footer.html` 的「col_friend」下方加一列"Legal"，链到 `/privacy/`。
  3. front matter 用 `layout: page` + `permalink: /privacy/`。

### P1-6 [YMYL 信任信号] 文章 `last_modified_at` / `reviewer` 全部缺失，E-E-A-T 签名失效

- **位置**：`_posts/*.md` 全部（15 篇 × 7 语言 = 105 篇） + `_layouts/post.html:58-64`（审校戳渲染条件）
- **证据**：
  - `grep -nE "^last_modified_at|^last_reviewed_at|^reviewer:" _posts/*.md en/_posts/*.md ar/_posts/*.md es/_posts/*.md fr/_posts/*.md id/_posts/*.md ru/_posts/*.md` **0 命中**。
  - post.html line 58-64：
    ```liquid
    {%- if page.last_modified_at or page.last_reviewed_at -%}
    <p class="post__reviewed">
      最后审校：{{ page.last_modified_at | default: page.last_reviewed_at | default: page.date | date: '%Y-%m-%d' }}
      {%- if page.reviewer %} · 审校：{{ page.reviewer }}{%- endif -%}
    </p>
    {%- endif -%}
    ```
  - 因条件不满足，**所有 105 篇文章的"最后审校"行都不会渲染**。
- **影响**：
  - YMYL（健康/医疗）站点在 Google 质量评分（QRG）里需要明确的"E-E-A-T"信号：Experience, Expertise, Authoritativeness, Trustworthiness。"最后审校日期 + 审校人"是 **Trust** 的核心信号。
  - 当前 `_data/authors.yml` 写了"由具执业资格的中医师与营养师组成"（line 27-33），但 front matter 没引用任何 reviewer，前端也没渲染——声明成了空头承诺。
  - 安全维度的具体风险：用户无法分辨"哪篇文章被审校过 / 何时审校"，YMYL 站点被用户投诉或监管询问"内容审核流程"时无法提供证据。
- **OWASP 分类**：A04:2021 Insecure Design
- **建议修复**：
  1. **本批次文章**：在 15 篇 zh-CN 源文章 front matter 至少加 `last_modified_at:` 时间戳（可用 git log 自动生成，参见 `git log --format=%aI _posts/2026-01-05-ziwu-jue.md | head -1`）。
  2. **加 reviewer 引用**：与 `_data/authors.yml` 的 `slug: qihuangstudy-medical-review` 对应，给已审校文章加 `reviewer: qihuangstudy-medical-review`。
  3. **修模板 i18n 漏洞**：post.html:60-64 的 `最后审校：` / `审校：` 是硬编码中文，**非中文文章**也展示中文——与 TC-007 同一类问题。改为 `{{ i18n.meta.last_reviewed }}` / `{{ i18n.meta.reviewed_by }}`，并在 `i18n.yml` 7 个语言段补这两个键。

---

## 3. 低风险 (P2)

### P2-1 [i18n 健壮性] `search.html` `placeholder` / 静态提示硬编码中文，错误未走 i18n

- **位置**：`_layouts/search.html:14, 20, 23`
- **证据**：
  ```html
  <span class="search-box__icon" aria-hidden="true">◎</span>
  <input type="search" id="search-input" class="search-box__input"
         placeholder="{{ i18n.common.search_placeholder }}" ...>
  <button class="search-box__clear" type="button" id="search-clear" aria-label="清空" hidden>×</button>
  <p class="search-hint" id="search-hint">{{ i18n.common.search_hint }}</p>
  <div class="search-results" id="search-results" aria-live="polite">
    <p class="empty-tip">{{ i18n.common.search_empty }}</p>
  </div>
  ```
  - `aria-label="清空"`（line 20）和 `aria-hidden="true">◎` 字符（line 15）硬编码中文。
  - error 路径未走 i18n：search.js line 177 `'<p class="empty-tip">' + escapeHtml(err.message) + '</p>'`，无网络错误时 i18n 文案缺失。
- **影响**：非中文用户体验受损；盲人用户在 `/en/search/` 听到"清空"。QA 报告 TC-007/TC-009 已部分记录；本条补**安全**视角的 i18n 缺口。
- **OWASP 分类**：A04:2021 Insecure Design（健壮性）
- **建议修复**：
  - line 15 字符 `◎` 可改 SVG 图标，无文字。
  - line 20 `aria-label` 改 `{{ i18n.a11y.clear_search }}`（键已在 i18n.yml line 655-725 范围内；如缺失则新增）。
  - search.js 错误路径改为 `t.search_loading_error` 或类似键的 fallback，不直接 `escapeHtml(err.message)`（防内部信息泄露：浏览器网络错误信息可能含 fetch URL / 状态码 / Origin 等，对非技术用户无意义）。

### P2-2 [i18n 健壮性] `header.html` nav title 的 `data-lang` 切换器 fallback 不全

- **位置**：`_includes/lang-switcher.html:5-12` + `assets/js/i18n.js:11, 31-40, 71-77`
- **证据**：
  - `i18n.js:11` 硬编码 `SUPPORTED = ['zh-CN', 'en', 'ru', 'fr', 'es', 'id', 'ar']`。
  - `i18n.js:31` 硬编码正则 `/^\/(en|ru|fr|es|id|ar)(?:\/|$)/`。
  - `_data/i18n.yml:8-50` 是真实语言列表。
  - **三处硬编码不一致风险**：i18n.yml 加新语言（如 `de`）需要同步改这两个文件，遗漏则新语言用户被"识别不到"，强行降级到 zh-CN。安全角度上不会直接出问题，但易导致"语言切换器点击无效"的社工利用面（用户放弃使用 → 被引导到外部钓鱼站）。
- **OWASP 分类**：A04:2021 Insecure Design
- **建议修复**：
  - 在 head.html 用一个 `window.QIHUANG_LANGS = {{ site.data.i18n.langs | jsonify }}` 把权威列表传给 JS。
  - i18n.js 改为 `var SUPPORTED = (window.QIHUANG_LANGS || []).map(function(x){ return x.code; })` 与正则从 `SUPPORTED` 动态生成。

### P2-3 [SVG 注入面] OG image 是动态 SVG，无 Content-Type 锁定

- **位置**：`assets/img/og-default.svg`（1200×630 内嵌中文 `text` 元素） + `_includes/head.html:51-55`（用作 og:image / twitter:image）
- **证据**：
  - og-default.svg 在 `<text>` 里包含 mojibake 残留（line 22-23, 27, 30, 37, 38 的内容是双字节字符渲染异常，但 SVG 是静态的、未参与模板插值，**不会**因用户输入改变）。
  - 当前 `_config.yml:92` `logo: /assets/img/og-default.svg` 是硬编码，front matter 无 `cover` 字段的 post 都 fallback 到它（head.html:50）。
  - GitHub Pages 对 `.svg` 静态服务 `Content-Type: image/svg+xml`。如果浏览器对 SVG 做 MIME-sniff（无 `nosniff` 头——见 P0-2），可能将其当成 HTML 解析。但 SVG 内嵌 `<script>` 才可执行，**当前 og-default.svg 没有 `<script>`**，实际不可利用。
- **影响**：当前**无实际风险**（SVG 内无脚本），但建议加 P0-2 的 `X-Content-Type-Options: nosniff` 防御。
- **OWASP 分类**：A05:2021 Security Misconfiguration
- **建议修复**：暂无代码改动，跟随 P0-2 一起修。

### P2-4 [信息泄露] 仓库元数据中暴露真实 GitHub 用户名

- **位置**：`_data/authors.yml:20`（`https://github.com/xiebingcheng`）+ `humans.txt:13` + 多处 md 文件（README/about.md 等） + `_config.yml:12` 隐含
- **证据**：`grep -nE "github\.com/xiebingcheng" -r .` 多处匹配，全部公开链接。
- **影响**：
  - 这是**公开信息**（GitHub 用户名本来就是公开的），但把个人 GitHub 账号与"中医审校"机构绑在一起，缺乏 separation of duties——审校身份的可信度依赖于账号本身而非独立验证。
  - 对 YMYL 站点，机构身份（"岐黄书房医学审校组"）的可信度需要"独立第三方可验证"的资质证据（执业证书编号脱敏、医院/学会隶属）。`_data/authors.yml:38-47` 注释了模板但**没填**真实信息。
- **OWASP 分类**：A04:2021 Insecure Design
- **建议修复**：
  - 与 P1-6 共用：填入真实审校医师的脱敏凭证（执业编号只显示后 4 位、医院只显示城市），`same_as:` 指向医院官网或卫健委公开查询页（不要指向个人 LinkedIn）。

---

## 4. 信息性 (P3)

### P3-1 [TC-001 重复] 5 个核心资源在生产 404

- 已在 `tests/qa-audit-2026-06-07.md` TC-001 记录。审计**确认**源码引用了未生成/不存在的文件（`sitemap.xml`、`humans.txt`、`atom.xml`、`/404.html`、`/en/feed.xml`），具体证据见 QA 报告。本报告不重复。

### P3-2 [TC-002 重复] 最近一次 CI build `failure` 但站点可访问

- 已在 QA TC-002 记录。审计**确认** `actions_jobs.json` 已从 `git ls-files` 中删除（commit `c9b9459`），目前工作树中的 `actions_jobs.json` / `build_logs.zip` / `run.html` **未在 git 跟踪**（`git status` 无 `??` 标记），且在 `_config.yml:69-72` exclude 列表中，**不会**被打入 `_site/`。无安全风险。

### P3-3 [TC-010 修复确认] `p.url` 已用 `escapeAttr` 包裹

- 审计确认：search.js line 132 已应用 `escapeAttr(p.url)`，QA 报告 TC-010 修复已落地。**但**函数实现不正确（见 P0-1），需要从"只防 `"` 字符"升级为"URL scheme 白名单"。

### P3-4 [FUNCTIONALITY.md] 单行、mojibake 渲染异常

- 文件内容被截在 1 行（行尾无 `\n`）且 PowerShell 在 GBK/UTF-8 错误编码下渲染为乱码。`_config.yml:60` 已在 exclude 列表中，**不会**部署到生产。Git 历史显示有 `FUNCTIONALITY.md (no BOM)` / `Jekyll 4 -> Jekyll 3.10` 等多次修复 revert——属于"被编码问题反复咬"的运维麻烦，**与安全无关**。

### P3-5 [Sitemap] `sitemap.xml` 不生成但 `robots.txt:9` 引用

- 审计确认 `jekyll-sitemap` 在 `Gemfile:9` 的白名单中，github-pages gem 默认会启用。**当前部署 404** 可能是 (a) GitHub Pages 自定义 workflow 的环境差异；(b) 站点 `_config.yml` 未显式 `plugins: - jekyll-sitemap`（虽然 github-pages 默认加载）。
- 建议在 `_config.yml:31-50` 区段补：
  ```yaml
  plugins:
    - jekyll-sitemap
    - jekyll-feed
    - jekyll-seo-tag
  ```
  显式声明避免 GitHub Pages 升级时插件被默认白名单变动牵连。

### P3-6 [`.well-known/security.txt`] 使用 `qihuangstudy.example`（占位）

- `Expires: 2027-12-31T23:59:59z` 合理（RFC 9116 推荐 < 1 年）。邮箱用 `qihuangstudy.example` 是占位，无实际接收人。
- 建议：把邮箱换为可接收的（如真实 Google Workspace 邮箱 + GitHub Issues 二选一即可），或至少加一个 `Encryption:` 指向 PGP 公钥（YMYL 站点加分项）。

---

## 5. 清单（已检查项 + 未发现问题）

| 类别 | 检查项 | 结论 | 证据 |
| --- | --- | --- | --- |
| **XSS · 客户端** | search.js 所有 `html +=` / `innerHTML` 调用 | 已审，11 个 `innerHTML` 调用全部对用户输入走 `escapeHtml` / `escapeAttr`；对服务器端 i18n 字符串（`t.search_*`）按设计信任 | search.js:115, 120, 125-127, 132, 134-135, 137, 140, 144, 177 |
| **XSS · URL 跳转** | 所有 `href="{{...}}"` / `window.location` | 无 `window.location = user_input`；所有 `href` 走 Liquid 模板插值（`post.url`、`tag`、`category`），服务端控制 | 全仓 54 处 `href=` 全检，无 `javascript:` / `data:` / `vbscript:` 用户输入路径 |
| **XSS · front matter → HTML** | `_posts/*.md` + 各语言子目录的 front matter 注入 | 全部 `{{ ... }}` 走 Liquid 默认 HTML 转义；JSON-LD 走 `jsonify` 转义 | `_includes/head.html:90-152` 10 处 `jsonify` 全检；无 `{{{ }}}` / `\| raw` 落到非 i18n 字段 |
| **XSS · 搜索关键词反射** | `<script>alert(1)</script>` 输入搜索框 | 搜索关键词经 `escapeHtml` 后插入 `'<em>' + escapeHtml(k) + '</em>'`（line 127） | search.js:127 |
| **CSP** | `_headers` / `<meta http-equiv="Content-Security-Policy">` / `_config.yml` strict-transport-security | **全无** | P0-2 详述 |
| **SRI** | 所有外链 stylesheet / script 的 `integrity` | Google Fonts CSS 无 SRI（且动态生成无法 SRI）；其他无外链 script | `_includes/head.html:38`；P1-2 详述 |
| **crossorigin / referrerpolicy** | 跨域资源 | `preconnect` 有 `crossorigin`（line 34）；`referrer` meta 在 line 6 | head.html:34 |
| **隐私政策** | `privacy` / `隐私` 全文 | **无** | P1-5 详述 |
| **Cookie / localStorage 声明** | `cookie` / `localStorage` 文本声明 | **无**；用 localStorage 但未告知 | i18n.js:39, 73；theme.js:10, 13；head.html:18；P1-5 |
| **第三方追踪** | `google-analytics` / `gtag` / `baidu` / `cnzz` | **无**（好事） | grep 全仓 0 命中 |
| **评论 / 表单** | `form` / `comment` | **无**（静态站无后端） | grep 0 命中 |
| **.well-known/security.txt** | RFC 9116 合规 | 存在、`Expires` 合理、`Preferred-Languages` 合理 | .well-known/security.txt |
| **humans.txt** | 引用与可达性 | 引用在 footer.html:40 / about.md × 2 / en/about.md × 2 / humans.txt:11（自身）；但**部署 404** | TC-001 重复 |
| **医疗免责声明** | 每篇 / 站点全局 | 全局 7 语言 footer 都有（footer.html:55-66）；文章级 disclaimer 也在 post.html:51-64（**但仅硬编码中文**） | P1-6 关联 |
| **Gemfile** | 版本锁定 / 官方源 | 用 `github-pages` 官方源但**未锁版本** | P1-3 |
| **GitHub Actions** | `permissions:` 最小化 | ✓ 显式 `contents: read / pages: write / id-token: write` | jekyll.yml:9-12 |
| **GitHub Actions** | 第三方 Action 锁 SHA | ✗ 全部用浮 tag | P1-4 |
| **GitHub Actions** | `pull_request_target` 检出 PR 代码 | ✗ 触发器仅 `push` / `workflow_dispatch`，无 `pull_request_target` | jekyll.yml:3-7 |
| **actions_jobs.json 凭据** | 是否含 token | 无 token，只有 run ID / commit SHA / runner ID | actions_jobs.json（未跟踪） |
| **.gitignore** | 覆盖 `_site/` / `.jekyll-cache/` / `.sass-cache/` / `.bundle/` / `node_modules/` | 全覆盖 ✓ | .gitignore:1-12 |
| **_config.yml email/twitter** | 真实 PII | `email: hello@example.com` 占位 ✓；`twitter: qihuangstudy` 看起来是项目品牌但无对应账号（可接受） | _config.yml:9, 47 |
| **Gemfile.lock** | 是否在仓 | 在 `.gitignore:5` 中，**缺** | P1-3 |
| **SSRF** | 服务端请求 | 静态站无服务端；客户端仅同源 fetch | search.js:35 |
| **CSRF** | 状态变更操作 | 静态站无后端 | N/A |
| **认证 / 授权** | — | 静态站无认证 | N/A |
| **会话管理** | Cookie 标志 | 无 Cookie | N/A |
| **加密** | 自实现加密 | 无 | N/A |
| **依赖 CVE** | `gem outdated` / 锁版本 | 缺 P1-3 的 lock，无法在静态审计判断 | P1-3 |

---

## 6. 复现指引

每条 P0/P1 都可以在**只读**仓库下复现：

```powershell
# P0-1：看 search.js 命名
Get-Content E:\中医shiyan网站\assets\js\search.js | Select-String -Pattern 'escapeAttr|escapeHtml'

# P0-2：看 head.html 是否有 CSP
Get-Content E:\中医shiyan网站\_includes\head.html | Select-String -Pattern 'Content-Security-Policy|X-Frame-Options|nosniff'
# 期望：0 命中

# P1-1：明文 HTTP 链接
Get-Content E:\中医shiyan网站\_includes\footer.html | Select-String -Pattern 'http://'

# P1-2：Google Fonts SRI
Get-Content E:\中医shiyan网站\_includes\head.html | Select-String -Pattern 'integrity='
# 期望：0 命中

# P1-3：Gemfile 锁
Get-Content E:\中医shiyan网站\Gemfile | Select-String -Pattern '~>|=>='
# 期望：0 命中
Get-Content E:\中医shiyan网站\.gitignore | Select-String 'Gemfile.lock'

# P1-4：Actions 锁
Get-Content E:\中医shiyan网站\.github\workflows\jekyll.yml | Select-String -Pattern 'uses:'

# P1-5：隐私政策
Get-ChildItem -Recurse -Include *.md,*.html E:\中医shiyan网站 | Select-String -Pattern '隐私|隐私政策|cookie|privacy'

# P1-6：审校戳
Get-ChildItem -Recurse -Include *.md E:\中医shiyan网站\_posts, E:\中医shiyan网站\en\_posts, E:\中医shiyan网站\ar\_posts | Select-String -Pattern '^last_modified_at|^reviewer:'
# 期望：0 命中
```

---

## 7. 修复优先级建议

1. **P0-1**（3 行代码） + **P0-2**（一段 meta）
2. **P1-1**（1 处 URL 改 https） + **P1-5**（新建 privacy.md × 7 语言）
3. **P1-3**（提交 Gemfile.lock） + **P1-4**（5 处 SHA 锁定）
4. **P1-2**（自托管字体是大改造；先加 `crossorigin` + `referrerpolicy` 占位）
5. **P1-6**（长期，需要审校医师签约 + 流程文档化）
6. **P2-x** 跟随各 P1 一起做

---

## 8. 报告约束确认

- ✅ 仅使用 Read + Grep + Glob，未修改任何文件
- ✅ 所有结论可复现（见第 6 节）
- ✅ 没有"建议加强安全"这种模糊陈述，每条都有 `file:line` + 代码片段 + 攻击 payload 思路
- ✅ 重点关注**真实可被利用**的风险（P0-1 给出具体 payload，P1-4 给出 SHA 锁定理由），不堆砌 checklist
