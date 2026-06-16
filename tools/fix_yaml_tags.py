#!/usr/bin/env python3
"""修复所有多语言 _posts/ 中 tags 行的 YAML 解析问题。

给含特殊字符 (& * : 等) 的 tag 元素加双引号包裹,
避免 YAML 把它们当作 anchor/alias 标记。
"""
import re
import os
import sys

# 特殊字符集合 - 这些字符在 YAML flow sequence 中需要被引号包裹
SPECIAL_CHARS = set('&*:?,#{}[]|>%@`!')

# 已知有问题的子目录
TARGET_DIRS = ['en/_posts', 'ru/_posts', 'fr/_posts', 'es/_posts', 'id/_posts', 'ar/_posts']

def fix_tags_line(content: str) -> str:
    """找到 tags: [...] 那一行,将含特殊字符的元素加双引号。"""
    def _quote_item(item: str) -> str:
        item = item.strip()
        if not item:
            return item
        # 已带引号则跳过
        if (item.startswith('"') and item.endswith('"')) or \
           (item.startswith("'") and item.endswith("'")):
            return item
        # 含特殊字符则加引号
        if any(c in item for c in SPECIAL_CHARS):
            # 内部双引号转义
            escaped = item.replace('"', '\\"')
            return f'"{escaped}"'
        return item

    def _replacer(m: re.Match) -> str:
        inner = m.group(1)
        # 简单按逗号拆分 (tags 中不含嵌套逗号)
        items = [_quote_item(s) for s in inner.split(',')]
        return f'tags: [{", ".join(items)}]'

    return re.sub(r'^tags:\s*\[(.*?)\]\s*$', _replacer, content, flags=re.MULTILINE)


def main() -> int:
    fixed_files = 0
    scanned_files = 0
    root = os.getcwd()
    for sub in TARGET_DIRS:
        dir_path = os.path.join(root, sub)
        if not os.path.isdir(dir_path):
            continue
        for name in os.listdir(dir_path):
            if not (name.endswith('.md') and name.startswith('2026-06-14-')):
                continue
            path = os.path.join(dir_path, name)
            scanned_files += 1
            with open(path, 'r', encoding='utf-8') as fp:
                content = fp.read()
            new_content = fix_tags_line(content)
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as fp:
                    fp.write(new_content)
                fixed_files += 1
                print(f'[FIX] {sub}/{name}')
    print(f'\n扫描: {scanned_files} 个文件, 修复: {fixed_files} 个')
    return 0


if __name__ == '__main__':
    sys.exit(main())
