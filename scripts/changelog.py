#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把当日快照摘要追加进 CHANGELOG.md。"""
from __future__ import annotations
import argparse, json, os
from datetime import datetime, timezone

def num(v, nd=1):
    if v is None:
        return '—'
    try:
        return ('{:,.%df}' % nd).format(float(v))
    except (TypeError, ValueError):
        return str(v)

def bp(m):
    a, b = m.get('price_in'), m.get('price_out')
    if a is None or b is None:
        return None
    try:
        return (3.0 * float(a) + float(b)) / 4.0
    except (TypeError, ValueError):
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default='data/latest.json')
    ap.add_argument('--out', default='.')
    args = ap.parse_args()

    d = json.load(open(args.data, encoding='utf-8'))
    ms = d['models']
    date = d.get('date', datetime.now(timezone.utc).strftime('%Y-%m-%d'))
    srcs = d.get('sources', {})

    # 与历史快照对比，找出新进榜与名次变动
    hist_dir = os.path.join(args.out, 'data', 'history')
    prev = None
    if os.path.isdir(hist_dir):
        files = sorted(f for f in os.listdir(hist_dir) if f.endswith('.json') and f[:-5] < date)
        if files:
            try:
                prev = json.load(open(os.path.join(hist_dir, files[-1]), encoding='utf-8'))
            except Exception:
                prev = None

    lines = []
    lines.append('## %s' % date)
    lines.append('')
    lines.append('- 收录模型 **%d** 个（开源权重 %d）' % (len(ms), sum(1 for m in ms if m.get('open_weights'))))
    src_txt = '／'.join('%s %s' % (k, 'ok' if (v.get('ok') if isinstance(v, dict) else v) else 'fail') for k, v in srcs.items())
    lines.append('- 数据源：%s' % src_txt)

    if prev:
        prev_ids = {m.get('id') for m in prev.get('models', [])}
        new_ids = [m for m in ms if m.get('id') not in prev_ids]
        if new_ids:
            names = '、'.join(m.get('display_name') or m.get('id') for m in new_ids[:8])
            lines.append('- 新进榜：%s%s' % (names, '' if len(new_ids) <= 8 else ' 等 %d 个' % len(new_ids)))
    else:
    
        lines.append('- 首次快照')

    arena = [m for m in ms if m.get('arena_score') is not None]
    arena.sort(key=lambda m: m['arena_score'], reverse=True)
    if arena:
        t = arena[0]
        lines.append('- Arena 榜首：**%s**（%s，%s 票）' % (t.get('display_name'), num(t.get('arena_score')), format(int(t.get('arena_votes') or 0), ',')))

    lines.append('')
    entry = '\n'.join(lines)

    path = os.path.join(args.out, 'CHANGELOG.md')
    header = '# 更新日志\n\n本文件由 GitHub Actions 每次同步后自动追加。\n\n---\n\n'
    if os.path.isfile(path):
        old = open(path, encoding='utf-8').read()
        if old.startswith('# '):
            body = old.split('---', 1)[-1].lstrip('\n')
        else:
            body = old
        if ('## ' + date) in body:
            # 同日重复运行：替换当天条目
            parts = body.split('## ')
            parts = [p for p in parts if not p.startswith(date)]
            body = '## '.join(parts)
        new = header + entry + '\n' + body
    else:
        new = header + entry + '\n'
    open(path, 'w', encoding='utf-8').write(new)
    print('CHANGELOG.md 已更新：%s' % date)

if __name__ == '__main__':
    main()