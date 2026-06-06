#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为所有翻译页面（en/ru/fr/es/id/ar 目录下）添加 lang 字段"""
import os
import re

LANGS = {
    'en': 'en', 'ru': 'ru', 'fr': 'fr', 'es': 'es', 'id': 'id', 'ar': 'ar',
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for lang_dir, lang_code in LANGS.items():
    base = os.path.join(ROOT, lang_dir)
    if not os.path.isdir(base):
        continue
    for root, dirs, files in os.walk(base):
        for f in files:
            if not f.endswith('.md'):
                continue
            path = os.path.join(root, f)
            text = open(path, encoding='utf-8').read()
            if not text.startswith('---'):
                continue
            # 检查是否已有 lang
            if re.search(r'^lang:\s*' + re.escape(lang_code) + r'\s*$', text, re.MULTILINE):
                continue
            # 在 front matter 末尾加 lang
            end = text.find('---', 3)
            if end < 0:
                continue
            new_text = text[:end] + f'lang: {lang_code}\n' + text[end:]
            with open(path, 'w', encoding='utf-8') as fp:
                fp.write(new_text)
            print(f'Updated: {path}')

print('Done.')
