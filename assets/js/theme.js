/* 主题切换：localStorage 持久化 + 系统偏好 */
(function () {
  'use strict';

  var STORAGE_KEY = 'theme';
  var root = document.documentElement;
  var btn;
  var a11y = (window.QIHUANG_I18N && window.QIHUANG_I18N.a11y) || {};

  function getStored() {
    try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
  }
  function setStored(v) {
    try { localStorage.setItem(STORAGE_KEY, v); } catch (e) {}
  }
  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    setStored(theme);
    if (btn) {
      var label = a11y.toggle_theme || 'Toggle theme';
      btn.setAttribute('aria-label', label);
      btn.setAttribute('title', label);
    }
  }
  function current() {
    return root.getAttribute('data-theme') || 'light';
  }
  function init() {
    btn = document.querySelector('.theme-toggle');
    if (btn) {
      btn.addEventListener('click', function () {
        applyTheme(current() === 'dark' ? 'light' : 'dark');
      });
    }
    applyTheme(current());

    // 监听系统主题变化（仅在用户未手动设置时响应）
    if (window.matchMedia) {
      var mq = window.matchMedia('(prefers-color-scheme: dark)');
      var listener = function (e) {
        if (!getStored()) {
          applyTheme(e.matches ? 'dark' : 'light');
        }
      };
      if (mq.addEventListener) mq.addEventListener('change', listener);
      else if (mq.addListener) mq.addListener(listener);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
