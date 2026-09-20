#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 README.md 门户（索引 + Top 榜摘要）。"""
from __future__ import annotations
import argparse, json, os
from datetime import datetime, timezone

MEDALS = {1: '🥇', 2: '🥈', 3: '🥉'}

def num(v, nd=1, dash='—'):
    if v is None:
        return dash
    try:
        return ('{:,.%df}' % nd).format(float(v))
    except (TypeError, ValueError):
        return str(v)

def money(v):
    if v is None:
        return '—'
    try:
        v = float(v)
    except (TypeError, ValueError):
        return str(v)
    if v == 0:
        return '免费'
    return ('$%.4f' if v < 0.01 else ('$%.3f' if v < 1 else '$%.2f')) % v

def bp(m):
    a, b = m.get('price_in'), m.get('price_out')
    if a is None or b is None:
        return None
    try:
        return (3.0 * float(a) + float(b)) / 4.0
    except (TypeError, ValueError):
        return None

def ce(m):
    i, p = m.get('aa_intelligence'), bp(m)
    if i is None or not p or p <= 0:
        return None
    return float(i) / p

def ctxt(cl):
    if not cl:
        return '—'
    if cl >= 1000000:
        return '%.1fM' % (cl / 1000000.0)
    if cl >= 1000:
        return '%dK' % (cl // 1000)
    return str(cl)

VIEW_META = [
    ('all', '综合榜', 'Arena 人类盲测偏好', 'arena_score'),
    ('intel', '智能指数榜', 'Artificial Analysis 综合能力', 'aa_intelligence'),
    ('coding', '编程榜', 'AA 编程分项', 'aa_coding'),
    ('cheap', '性价比榜', '智能指数 ÷ 混合价格', None),
    ('speed', '速度榜', '实测输出速度 t/s', 'aa_speed'),
    ('open', '开源权重榜', '仅开放权重模型', 'aa_intelligence'),
    ('ctx', '长上下文榜', '最大上下文窗口', 'context_length'),
    ('price', '价格榜', '混合价格升序', None),
]

# 视图名 -> 真实数据字段名（render_top / top_rows 必须用字段名排序）
FIELD = {
    'all': 'arena_score',
    'intel': 'aa_intelligence',
    'coding': 'aa_coding',
    'speed': 'aa_speed',
    'open': 'aa_intelligence',
    'ctx': 'context_length',
}

def top_rows(models, key, n=10):
    if key == 'cheap':
        rows = [m for m in models if ce(m) is not None]
        rows.sort(key=ce, reverse=True)
    elif key == 'price':
        rows = [m for m in models if bp(m) is not None]
        rows.sort(key=bp)
    elif key == 'open':
        f = FIELD['open']
        rows = [m for m in models if m.get('open_weights') and m.get(f) is not None]
        rows.sort(key=lambda m: m[f], reverse=True)
    else:
        f = FIELD.get(key)
        if f is None:
            return []
        rows = [m for m in models if m.get(f) is not None]
        rows.sort(key=lambda m: m[f], reverse=True)
    return rows[:n]

def render_top(models, key, limit=10):
    rows = top_rows(models, key, limit)
    out = []
    if key == 'all':
        out.append('| # | 模型 | 厂商 | Arena | 票数 |')
        out.append('|---:|:---|:---|---:|---:|')
        for i, m in enumerate(rows, 1):
            out.append('| %s | %s | %s | %s | %s |' % (MEDALS.get(i, i), m.get('display_name'), m.get('org'), num(m.get('arena_score')), format(int(m.get('arena_votes') or 0), ',')))
    elif key == 'cheap':
        out.append('| # | 模型 | 厂商 | 智能/美元 | 混合价格 | 权重 |')
        out.append('|---:|:---|:---|---:|---:|:---|')
        for i, m in enumerate(rows, 1):
            out.append('| %s | %s | %s | %s | %s | %s |' % (MEDALS.get(i, i), m.get('display_name'), m.get('org'), num(ce(m), 1), money(bp(m)), '开源' if m.get('open_weights') else '闭源'))
    elif key == 'speed':
        out.append('| # | 模型 | 厂商 | 速度(t/s) | 智能指数 |')
        out.append('|---:|:---|:---|---:|---:|')
        for i, m in enumerate(rows, 1):
            out.append('| %s | %s | %s | %s | %s |' % (MEDALS.get(i, i), m.get('display_name'), m.get('org'), num(m.get('aa_speed')), num(m.get('aa_intelligence'))))
    else:
        out.append('| # | 模型 | 厂商 | 智能指数 | 编程 | 上下文 |')
        out.append('|---:|:---|:---|---:|---:|---:|')
        for i, m in enumerate(rows, 1):
            out.append('| %s | %s | %s | %s | %s | %s |' % (MEDALS.get(i, i), m.get('display_name'), m.get('org'), num(m.get('aa_intelligence')), num(m.get('aa_coding')), ctxt(m.get('context_length'))))
    return '\n'.join(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default='data/latest.json')
    ap.add_argument('--repo', default='AmigaMeow/llm-leaderboard-data')
    ap.add_argument('--out', default='.')
    args = ap.parse_args()

    d = json.load(open(args.data, encoding='utf-8'))
    models = d['models']
    date = d.get('date', datetime.now(timezone.utc).strftime('%Y-%m-%d'))
    srcs = d.get('sources', {})
    n_open = sum(1 for m in models if m.get('open_weights'))
    orgs = {}
    for m in models:
        orgs[m.get('org') or '?'] = orgs.get(m.get('org') or '?', 0) + 1
    top_orgs = sorted(orgs.items(), key=lambda kv: -kv[1])[:6]
    src_txt = ' ｜ '.join('%s %s' % (k, '✅' if (v.get('ok') if isinstance(v, dict) else v) else '❌') for k, v in srcs.items())

    r = []
    r.append('# 大模型排行榜 · LLM Leaderboard')
    r.append('')
    r.append('> 📊 **每日自动更新**的大模型能力榜单 —— 聚合 Arena 人类盲测、Artificial Analysis 评测与 OpenRouter 定价。')
    r.append('>')
    r.append('> 数据源：[17nas.com](https://17nas.com/llm-leaderboard.php) ｜ 快照 **%s**' % date)
    r.append('')
    r.append('[![Daily Update](https://github.com/%s/actions/workflows/update.yml/badge.svg)](https://github.com/%s/actions/workflows/update.yml)' % (args.repo, args.repo))
    r.append('[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)')
    r.append('')
    r.append('---')
    r.append('')
    r.append('## 快照概览')
    r.append('')
    r.append('| 指标 | 值 |')
    r.append('|---|---:|')
    r.append('| 收录模型 | **%d** |' % len(models))
    r.append('| 开源权重 | %d |' % n_open)
    r.append('| 闭源 | %d |' % (len(models) - n_open))
    r.append('| 覆盖厂商 | %d |' % len(orgs))
    r.append('| 数据源 | %s |' % src_txt)
    r.append('| 最近更新 | %s |' % date)
    r.append('')
    r.append('厂商分布：%s' % '、'.join('%s (%d)' % (k, v) for k, v in top_orgs))
    r.append('')
    r.append('---')
    r.append('')
    r.append('## 榜单索引')
    r.append('')
    r.append('| 榜单 | 说明 | 完整榜 |')
    r.append('|---|---|---|')
    for key, title, desc, _ in VIEW_META:
        r.append('| **%s** | %s | [查看](leaderboard/%s.md) |' % (title, desc, key))
    r.append('')
    r.append('---')
    r.append('')
    r.append('## 🏆 综合榜 Top 10')
    r.append('')
    r.append(render_top(models, 'all', 10))
    r.append('')
    r.append('[→ 完整综合榜](leaderboard/all.md)')
    r.append('')
    r.append('## 💰 性价比榜 Top 10')
    r.append('')
    r.append('> 智能指数 ÷ 混合价格（输入:输出 = 3:1）。**单位花费换来的能力**，比单纯比价格更有参考价值。')
    r.append('')
    r.append(render_top(models, 'cheap', 10))
    r.append('')
    r.append('[→ 完整性价比榜](leaderboard/cheap.md)')
    r.append('')
    r.append('## ⚡ 速度榜 Top 10')
    r.append('')
    r.append(render_top(models, 'speed', 10))
    r.append('')
    r.append('[→ 完整速度榜](leaderboard/speed.md)')
    r.append('')
    r.append('---')
    r.append('')
    r.append('## 数据说明')
    r.append('')
    r.append('- **Arena 分数**：LMArena 人类盲测的 Bradley-Terry 评分，附 95% 置信区间。区间重叠时名次差异不必过度解读。')
    r.append('- **智能指数 / 编程 / 速度**：来自 Artificial Analysis 的实测评测。')
    r.append('- **价格**：OpenRouter 公开定价，单位美元 / 百万 token；混合价格按输入:输出 = 3:1 加权。')
    r.append('- **涨跌**：与上一份快照的名次对比。🆕 = 新进榜。')
    r.append('')
    r.append('## 更新机制')
    r.append('')
    r.append('本仓库由 GitHub Actions **每日自动更新**：拉取聚合数据 → 生成榜单 → 提交。')
    r.append('历史快照保存在 [`data/history/`](data/history/)，可用于回溯任意一天的榜单。')
    r.append('')
    r.append('## 许可与数据条款')
    r.append('')
    r.append('- 本仓库的**榜单生成代码**以 [MIT](LICENSE) 许可开放。')
    r.append('- **评测数据**来自 LMArena、Artificial Analysis、OpenRouter 等第三方，版权归各来源所有；本仓库仅聚合展示并标注来源，使用时请遵守各上游条款。')
    r.append('- 原始榜单与更多维度：[17nas.com/llm-leaderboard.php](https://17nas.com/llm-leaderboard.php)')
    r.append('')
    r.append('---')
    r.append('')
    r.append('*本页由 `scripts/render_readme.py` 自动生成，请勿手工编辑。*')

    with open(os.path.join(args.out, 'README.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(r) + '\n')
    print('README.md 已生成：%d 行' % len(r))

if __name__ == '__main__':
    main()