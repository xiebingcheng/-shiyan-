/* ==========================================================
   客户端搜索
   - 不依赖 lunr：中文用 substring 匹配 + 多关键词 AND 逻辑
   - 评分：标题 4 / 标签 3 / 分类 3 / 摘要 2 / 正文 1
   - 自动高亮命中片段
   ========================================================== */
(function () {
  'use strict';

  var input, clearBtn, results, hint, dataPromise;
  var DATA_URL = (window.SEARCH_DATA_URL || '/search.json');

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  function escapeReg(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function loadData() {
    if (!dataPromise) {
      dataPromise = fetch(DATA_URL, { credentials: 'same-origin' })
        .then(function (r) {
          if (!r.ok) throw new Error('HTTP ' + r.status);
          return r.json();
        });
    }
    return dataPromise;
  }

  function highlight(text, keywords) {
    if (!text) return '';
    var safe = escapeHtml(text);
    if (!keywords.length) return safe;
    // 合并所有关键词做一次性高亮（按长度降序避免短词吃掉长词）
    var sorted = keywords.slice().sort(function (a, b) { return b.length - a.length; });
    var pattern = new RegExp('(' + sorted.map(escapeReg).join('|') + ')', 'gi');
    return safe.replace(pattern, '<mark>$1</mark>');
  }

  function excerpt(text, keywords, len) {
    if (!text) return '';
    var lower = text.toLowerCase();
    var pos = -1;
    for (var i = 0; i < keywords.length; i++) {
      var p = lower.indexOf(keywords[i].toLowerCase());
      if (p >= 0 && (pos < 0 || p < pos)) pos = p;
    }
    var start, end;
    if (pos < 0) {
      start = 0;
      end = Math.min(text.length, len);
    } else {
      var half = Math.floor(len / 2);
      start = Math.max(0, pos - half);
      end = Math.min(text.length, start + len);
      start = Math.max(0, end - len);
    }
    var slice = (start > 0 ? '…' : '') + text.slice(start, end) + (end < text.length ? '…' : '');
    return highlight(slice, keywords);
  }

  function score(post, keywords) {
    var s = 0;
    var title = (post.title || '').toLowerCase();
    var excerpt = (post.excerpt || '').toLowerCase();
    var content = (post.content || '').toLowerCase();
    var tags = (post.tags || []).join(' ').toLowerCase();
    var cat = (post.category || '').toLowerCase();
    keywords.forEach(function (k) {
      k = k.toLowerCase();
      if (!k) return;
      if (title.indexOf(k) >= 0)   s += 8;
      if (tags.indexOf(k) >= 0)    s += 5;
      if (cat.indexOf(k) >= 0)     s += 5;
      if (excerpt.indexOf(k) >= 0) s += 3;
      if (content.indexOf(k) >= 0) s += 1;
    });
    // 完全包含所有关键词加分
    var allIn = keywords.every(function (k) {
      k = k.toLowerCase();
      return title.indexOf(k) >= 0 || excerpt.indexOf(k) >= 0 || content.indexOf(k) >= 0 || tags.indexOf(k) >= 0 || cat.indexOf(k) >= 0;
    });
    if (allIn) s += 4;
    return s;
  }

  function search(posts, query) {
    var keywords = query.trim().split(/\s+/).filter(Boolean);
    if (!keywords.length) return [];
    return posts
      .map(function (p) { return { post: p, s: score(p, keywords) }; })
      .filter(function (r) { return r.s > 0; })
      .sort(function (a, b) { return b.s - a.s; })
      .slice(0, 50)
      .map(function (r) { return r.post; });
  }

  function render(posts, query) {
    if (!query) {
      results.innerHTML = '<p class="empty-tip">请输入关键词开始检索。</p>';
      hint.textContent = '提示：支持搜索标题、摘要、分类、标签与正文。';
      return;
    }
    if (!posts.length) {
      results.innerHTML = '<p class="empty-tip">未在 ' + (window.__totalPosts || '所有') + ' 篇文章中找到与「' + escapeHtml(query) + '」相关的内容。</p>';
      hint.textContent = '未找到结果';
      return;
    }
    var keywords = query.trim().split(/\s+/).filter(Boolean);
    var stats = '找到 <strong>' + posts.length + '</strong> 篇相关';
    if (posts.length === 50) stats += '（前 50）';
    hint.innerHTML = stats + ' · 关键词：' + keywords.map(function (k) { return '<em>' + escapeHtml(k) + '</em>'; }).join(' ');

    var html = '<ul class="search-results__list">';
    posts.forEach(function (p) {
      html += '<li class="search-result">';
      html += '  <h3 class="search-result__title"><a href="' + p.url + '">' + highlight(p.title, keywords) + '</a></h3>';
      html += '  <p class="search-result__meta">';
      html += '    <span class="search-result__cat">' + escapeHtml(p.category || '') + '</span>';
      html += '    <span> · ' + escapeHtml(p.date || '') + '</span>';
      if (p.tags && p.tags.length) {
        html += '<span> · ' + p.tags.map(function (t) { return '#' + escapeHtml(t); }).join(' ') + '</span>';
      }
      html += '  </p>';
      html += '  <p class="search-result__excerpt">' + excerpt(p.excerpt || p.content, keywords, 140) + '</p>';
      html += '</li>';
    });
    html += '</ul>';
    results.innerHTML = html;
  }

  function debounce(fn, wait) {
    var t;
    return function () {
      var args = arguments, ctx = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(ctx, args); }, wait);
    };
  }

  function init() {
    input = document.getElementById('search-input');
    clearBtn = document.getElementById('search-clear');
    results = document.getElementById('search-results');
    hint = document.getElementById('search-hint');
    if (!input || !results) return;

    var allPosts = null;

    var doSearch = debounce(function () {
      var q = input.value.trim();
      if (clearBtn) clearBtn.hidden = q.length === 0;
      if (!q) { render([], ''); return; }
      loadData().then(function (posts) {
        allPosts = posts;
        window.__totalPosts = posts.length;
        var found = search(posts, q);
        render(found, q);
      }).catch(function (err) {
        results.innerHTML = '<p class="empty-tip">搜索数据加载失败：' + escapeHtml(err.message) + '</p>';
      });
    }, 200);

    input.addEventListener('input', doSearch);

    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        input.value = '';
        clearBtn.hidden = true;
        render([], '');
        input.focus();
      });
    }

    // 支持 URL ?q=xxx 自动填充并搜索
    try {
      var params = new URLSearchParams(window.location.search);
      var q0 = params.get('q');
      if (q0) {
        input.value = q0;
        clearBtn.hidden = false;
        doSearch();
      }
    } catch (e) {}

    // 快捷键：/ 聚焦
    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && document.activeElement !== input &&
          !(document.activeElement && /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName))) {
        e.preventDefault();
        input.focus();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
