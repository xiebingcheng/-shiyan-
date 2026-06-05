#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 categories-i18n.yml 和 nav-i18n.yml 中所有可能引起 YAML 解析问题的 value 加引号"""
import re
import yaml

def quote_yaml_values(path):
    text = open(path, encoding='utf-8').read()
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        # 匹配 "  key: value" 形式（key 可以是 slug/语言代码等）
        m = re.match(r'^(\s*-?\s*)([a-zA-Z_][a-zA-Z0-9_-]*:)\s+(.+)$', line)
        if not m:
            new_lines.append(line)
            continue
        prefix, key, value = m.groups()
        v = value.strip()
        if v.startswith('"') or v.startswith("'"):
            new_lines.append(line)
            continue
        if v.startswith('|') or v.startswith('>'):
            new_lines.append(line)
            continue
        if v == '':
            new_lines.append(line)
            continue
        # 加引号条件
        if any(c in v for c in [':', '#', '{', '}', '[', ']', '&', '*', '!', '|', '>', '%', '@', '`', '\n']):
            escaped = v.replace('\\', '\\\\').replace('"', '\\"')
            new_lines.append(f'{prefix}{key} "{escaped}"')
        else:
            new_lines.append(line)
    return '\n'.join(new_lines) + '\n'

for path in [
    r'E:\中医shiyan网站\_data\categories-i18n.yml',
    r'E:\中医shiyan网站\_data\nav-i18n.yml',
]:
    new = quote_yaml_values(path)
    open(path, 'w', encoding='utf-8').write(new)
    print(f'Updated: {path}')

# 测试
for path in [
    r'E:\中医shiyan网站\_data\categories-i18n.yml',
    r'E:\中医shiyan网站\_data\nav-i18n.yml',
]:
    try:
        data = yaml.safe_load(open(path, encoding='utf-8').read())
        print(f'OK: {path} ({len(data)} items)')
    except yaml.YAMLError as e:
        print(f'Error in {path}: {e}')
