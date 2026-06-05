#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为每种语言生成 archive/categories/tags/search 翻译页面"""
import os

LANGS = {
    'ru': {
        'archive': 'Архив',
        'categories': 'Категории',
        'tags': 'Теги',
        'search': 'Поиск',
    },
    'fr': {
        'archive': 'Archives',
        'categories': 'Catégories',
        'tags': 'Étiquettes',
        'search': 'Recherche',
    },
    'es': {
        'archive': 'Archivo',
        'categories': 'Categorías',
        'tags': 'Etiquetas',
        'search': 'Buscar',
    },
    'id': {
        'archive': 'Arsip',
        'categories': 'Kategori',
        'tags': 'Tag',
        'search': 'Cari',
    },
    'ar': {
        'archive': 'الأرشيف',
        'categories': 'التصنيفات',
        'tags': 'الوسوم',
        'search': 'بحث',
    },
}

ROOT = r'E:\中医shiyan网站'

for lang, titles in LANGS.items():
    lang_dir = os.path.join(ROOT, lang)
    os.makedirs(lang_dir, exist_ok=True)
    for page, title in titles.items():
        content = f"""---
layout: {page}
title: {title}
permalink: /{lang}/{page}/
---
"""
        path = os.path.join(lang_dir, f'{page}.md')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'OK: {lang}/{page}.md')

print('\nDone.')
