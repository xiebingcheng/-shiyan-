# 岐黄小筑

> 一卷《内经》，半盏清茶
> 中医养生科普专题站

以《黄帝内经》为宗，传播节气养生、食疗本草、经络穴位、四季调养、情志起居等中医智慧。

## 在线访问

部署后访问： **https://xiebingcheng.github.io/-shiyan-/**

## 启用 GitHub Pages

代码已推送到 `main` 分支，**最后一步** 手动启用 Pages：

1. 打开 https://github.com/xiebingcheng/-shiyan-/settings/pages
2. **Source** 选 **Deploy from a branch**
3. **Branch** 选 `main` / `(root)`
4. 点击 **Save**
5. 等待 1-2 分钟构建完成

构建日志在：https://github.com/xiebingcheng/-shiyan-/actions

## 本地预览

```bash
# 安装依赖（需要 Ruby 2.7+）
bundle install

# 启动本地服务
bundle exec jekyll serve

# 访问 http://127.0.0.1:4000/-shiyan-/
```

> Windows 上若 Gem 慢可换源：`bundle config mirror.https://rubygems.org https://gems.ruby-china.com`

## 项目结构

```
.
├── _config.yml              # 站点配置
├── _data/
│   ├── categories.yml       # 6 大分类元数据
│   └── nav.yml              # 顶部导航
├── _layouts/                # 布局层
│   ├── default.html         # 全局
│   ├── home.html            # 首页（带分页）
│   ├── post.html            # 文章详情
│   ├── page.html            # 通用 page
│   ├── archive.html         # 归档
│   ├── categories.html      # 分类总览
│   ├── category.html        # 单个分类
│   ├── tags.html            # 标签总览
│   ├── tag.html             # 单个标签
│   ├── search.html          # 搜索页
│   └── 404.html             # 404
├── _includes/               # 组件层
│   ├── head.html
│   ├── header.html
│   ├── footer.html
│   ├── post-card.html
│   ├── post-meta.html
│   └── pagination.html      # 10 篇/页分页
├── _posts/                  # 15 篇示例文章
│   └── 2026-*.md
├── categories/              # 6 个分类页（自动生成）
├── tags/                    # 55 个标签页（自动生成）
├── about.md                 # 关于小筑
├── about-zhongyi.md         # 什么是中医
├── archive.md               # 文章归档
├── categories.md            # 分类总览
├── tags.md                  # 标签云
├── search.md                # 搜索页
├── search.json              # 搜索数据（构建期生成）
├── index.html               # 首页（带分页）
├── 404.html                 # 404 页面
├── feed.xml                 # RSS（jekyll-feed 自动生成）
├── sitemap.xml              # sitemap（jekyll-sitemap 自动生成）
├── assets/
│   ├── css/main.css         # 古风主题
│   ├── js/theme.js          # 暗色模式
│   ├── js/nav.js            # 移动端菜单
│   ├── js/search.js         # 客户端搜索
│   └── img/                 # SVG 资源
├── tools/
│   └── generate_archives.py # 自动生成分类/标签页
├── robots.txt
└── Gemfile
```

## 功能特性

- ✅ **古风中式主题** —— 宣纸底色 / 墨色 / 朱红 / 黛青，楷体 + 宋体
- ✅ **6 大分类** —— 节气养生 / 食疗本草 / 四季调养 / 经络穴位 / 起居有常 / 情志养生
- ✅ **15 篇示例文章** —— 平均 1500-2000 字
- ✅ **分页系统** —— 10 篇/页（首页 + 自动分页）
- ✅ **客户端搜索** —— 关键词高亮，标题/标签/摘要/正文多字段加权
- ✅ **暗色模式** —— 手动切换 + 跟随系统
- ✅ **RSS 订阅** —— `/feed.xml`
- ✅ **Sitemap** —— `/sitemap.xml`
- ✅ **响应式** —— 桌面 / 平板 / 手机
- ✅ **可访问性** —— ARIA 标签 / 键盘导航 / 跳到正文
- ✅ **GitHub Pages 部署** —— 零配置

## 内容维护

### 添加新文章

在 `_posts/` 创建 `YYYY-MM-DD-slug.md`：

```markdown
---
layout: post
title: 文章标题
subtitle: 副标题（可选）
date: 2026-04-01 09:00:00 +0800
author: 作者
category: jieqi       # 6 选 1: jieqi / shiliao / siji / jingluo / qiju / qingzhi
tags: [节气, 春季, 养肝]
excerpt: 摘要文本（用于卡片和搜索）
---

正文 Markdown...
```

### 重新生成分类/标签页

每次添加/修改文章后：

```bash
python tools/generate_archives.py
```

脚本会扫描 `_posts/` 下的所有 front matter，自动生成 `categories/<slug>.md` 和 `tags/<tag>.md`。

### 修改分类信息

编辑 `_data/categories.yml` 调整分类名称、描述、颜色、图标。

## 免责声明

本站内容仅供科普参考，**不作为任何疾病诊断或治疗的依据**。
如有不适，请及时就医，遵从医嘱。

## 致谢

- [Jekyll](https://jekyllrb.com) —— 静态站点生成
- [Noto Serif SC](https://fonts.google.com/noto/specimen/Noto+Serif+SC) —— 思源宋体
- [Ma Shan Zheng](https://fonts.google.com/specimen/Ma+Shan+Zheng) —— 马善政楷体
- 致敬《黄帝内经》与历代中医先贤

## 许可证

MIT License
