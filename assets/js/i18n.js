/* ==========================================================
   客户端语言切换
   - 读取 URL 路径中的 /xx/ 前缀作为当前语言
   - 也支持 ?lang=xx 查询参数或 localStorage
   - 点击切换器：跳转对应语言的等价 URL
   - 阿拉伯语：设置 html[dir="rtl"]
   ========================================================== */
(function () {
  'use strict';

  var SUPPORTED = ['zh-CN', 'en', 'ru', 'fr', 'es', 'id', 'ar'];
  var RTL = ['ar'];
  var DEFAULT = 'zh-CN';

  function getBaseurl() {
    return document.documentElement.getAttribute('data-baseurl') || '';
  }

  function stripBaseurl(path, baseurl) {
    if (baseurl && baseurl !== '/' && path.indexOf(baseurl) === 0) {
      var rest = path.substring(baseurl.length);
      return rest || '/';
    }
    return path;
  }

  // 当前语言
  function detectLang() {
    var path = window.location.pathname;
    var rest = stripBaseurl(path, getBaseurl());
    var m = rest.match(/^\/(en|ru|fr|es|id|ar)(?:\/|$)/);
    if (m) return m[1];
    // 查询参数优先
    try {
      var params = new URLSearchParams(window.location.search);
      var q = params.get('lang');
      if (q && SUPPORTED.indexOf(q) >= 0) return q;
    } catch (e) {}
    return getStoredLang() || DEFAULT;
  }

  // 读取用户语言偏好（新键 qhstudy-lang，兼容旧键 qihuang-lang）
  function getStoredLang() {
    try {
      var v = localStorage.getItem('qhstudy-lang');
      if (v) return v;
      // 向后兼容：迁移旧键值
      var legacy = localStorage.getItem('qihuang-lang');
      if (legacy) {
        try { localStorage.setItem('qhstudy-lang', legacy); } catch (e2) {}
        return legacy;
      }
    } catch (e) {}
    return null;
  }

  // 设置 HTML 标签
  function applyDir(lang) {
    document.documentElement.lang = lang;
    document.documentElement.setAttribute('data-lang', lang);
    if (RTL.indexOf(lang) >= 0) {
      document.documentElement.setAttribute('dir', 'rtl');
      document.documentElement.setAttribute('data-rtl', 'true');
    } else {
      document.documentElement.setAttribute('dir', 'ltr');
      document.documentElement.setAttribute('data-rtl', 'false');
    }
  }

  // 给定目标语言与当前 URL，构造目标 URL
  function buildTargetUrl(targetLang) {
    // 文章页：优先用服务器端注入的 7 语种 URL 映射（7 语种 slug 互不相同，不能靠 strip-and-re-add）
    if (window.QHSTUDY_TRANSLATIONS && Object.prototype.hasOwnProperty.call(window.QHSTUDY_TRANSLATIONS, targetLang)) {
      var targetUrl = window.QHSTUDY_TRANSLATIONS[targetLang];
      if (targetUrl) {
        return getBaseurl() + targetUrl;
      }
    }

    // 非文章页（首页 / 分类 / 标签 / about）：slug 跨语种一致，strip-and-re-add 即可
    var path = window.location.pathname;
    var baseurl = getBaseurl();
    var rest = stripBaseurl(path, baseurl);
    var stripped = rest.replace(/^\/(en|ru|fr|es|id|ar)(?=\/|$)/, '');
    if (stripped === '') stripped = '/';

    if (targetLang === DEFAULT) {
      return baseurl + stripped;
    }
    return baseurl + '/' + targetLang + (stripped === '/' ? '/' : stripped);
  }

  // 切换语言
  function switchLang(targetLang) {
    if (SUPPORTED.indexOf(targetLang) < 0) return;
    try { localStorage.setItem('qhstudy-lang', targetLang); } catch (e) {}
    var url = buildTargetUrl(targetLang);
    window.location.href = url;
  }

  // 初始化切换器交互
  function initSwitcher() {
    var switcher = document.querySelector('.lang-switcher');
    if (!switcher) return;
    var btn = switcher.querySelector('.lang-switcher__btn');
    var menu = switcher.querySelector('.lang-switcher__menu');
    if (!btn || !menu) return;

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = menu.hidden;
      menu.hidden = !open;
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    menu.querySelectorAll('[data-lang]').forEach(function (el) {
      el.addEventListener('click', function () {
        var target = this.getAttribute('data-lang');
        if (target) switchLang(target);
      });
    });

    // 点击外部关闭
    document.addEventListener('click', function (e) {
      if (!switcher.contains(e.target)) {
        menu.hidden = true;
        btn.setAttribute('aria-expanded', 'false');
      }
    });

    // ESC 关闭
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menu.hidden) {
        menu.hidden = true;
        btn.setAttribute('aria-expanded', 'false');
        btn.focus();
      }
    });
  }

  // 初始化
  var currentLang = detectLang();
  applyDir(currentLang);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSwitcher);
  } else {
    initSwitcher();
  }

  // 暴露给模板
  window.QihuangStudyI18n = {
    switchLang: switchLang,
    current: function () { return currentLang; },
    buildTargetUrl: buildTargetUrl,
    supported: SUPPORTED,
    isRtl: function (l) { return RTL.indexOf(l) >= 0; }
  };
})();
