#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render README.md portal for the leaderboard repo.

Only LMArena + OpenRouter derived metrics are published (see generate.py).
"""
from __future__ import annotations
import argparse, json, os
from datetime import datetime, timezone

MEDALS = {1: "\U0001F947", 2: "\U0001F948", 3: "\U0001F949"}

def num(v, nd=1, dash="-"):
    if v is None:
        return dash
    try:
        return ("{:,.%df}" % nd).format(float(v))
    except (TypeError, ValueError):
        return str(v)

def money(v):
    if v is None:
        return "-"
    try:
        v = float(v)
    except (TypeError, ValueError):
        return str(v)
    if v == 0:
        return "free"
    return ("$%.4f" if v < 0.01 else ("$%.3f" if v < 1 else "$%.2f")) % v

def bp(m):
    a, b = m.get("price_in"), m.get("price_out")
    if a is None or b is None:
        return None
    try:
        return (3.0 * float(a) + float(b)) / 4.0
    except (TypeError, ValueError):
        return None

def apd(m):
    s, p = m.get("arena_score"), bp(m)
    if s is None or not p or p <= 0:
        return None
    return float(s) / p

def ctxt(cl):
    if not cl:
        return "-"
    if cl >= 1000000:
        return "%.1fM" % (cl / 1000000.0)
    if cl >= 1000:
        return "%dK" % (cl // 1000)
    return str(cl)

VIEW_META = [
    ("all",   "Overall",      "Arena human preference",        "arena_score"),
    ("cheap", "Best value",   "Arena score / blended price",   None),
    ("price", "Lowest price", "Blended price ascending",       None),
    ("ctx",   "Long context", "Maximum context window",        "context_length"),
    ("open",  "Open weights", "Open-weight models only",       "arena_score"),
]

def top_rows(models, key, n=10):
    if key == "cheap":
        rows = [m for m in models if apd(m) is not None]
        rows.sort(key=apd, reverse=True)
    elif key == "price":
        rows = [m for m in models if bp(m) is not None]
        rows.sort(key=bp)
    elif key == "open":
        rows = [m for m in models if m.get("open_weights") and m.get("arena_score") is not None]
        rows.sort(key=lambda m: m["arena_score"], reverse=True)
    else:
        f = {"all": "arena_score", "ctx": "context_length"}.get(key)
        if f is None:
            return []
        rows = [m for m in models if m.get(f) is not None]
        rows.sort(key=lambda m: m[f], reverse=True)
    return rows[:n]

def render_top(models, key, limit=10):
    rows = top_rows(models, key, limit)
    out = []
    if key == "cheap":
        out.append("| # | Model | Org | Arena/$ | Blended | Weights |")
        out.append("|---:|:---|:---|---:|---:|:---|")
        for i, m in enumerate(rows, 1):
            out.append("| %s | %s | %s | %s | %s | %s |" % (MEDALS.get(i, i), m.get("display_name"), m.get("org"), num(apd(m), 1), money(bp(m)), "open" if m.get("open_weights") else "closed"))
    elif key == "ctx":
        out.append("| # | Model | Org | Context | Arena | Blended |")
        out.append("|---:|:---|:---|---:|---:|---:|")
        for i, m in enumerate(rows, 1):
            out.append("| %s | %s | %s | %s | %s | %s |" % (MEDALS.get(i, i), m.get("display_name"), m.get("org"), ctxt(m.get("context_length")), num(m.get("arena_score")), money(bp(m))))
    else:
        out.append("| # | Model | Org | Arena | Votes |")
        out.append("|---:|:---|:---|---:|---:|")
        for i, m in enumerate(rows, 1):
            out.append("| %s | %s | %s | %s | %s |" % (MEDALS.get(i, i), m.get("display_name"), m.get("org"), num(m.get("arena_score")), integer(m.get("arena_votes"))))
    return chr(10).join(out)

def integer(v):
    if v is None:
        return "-"
    try:
        return "{:,}".format(int(v))
    except (TypeError, ValueError):
        return str(v)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/latest.json")
    ap.add_argument("--repo", default="AmigaMeow/llm-leaderboard-data")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()

    d = json.load(open(args.data, encoding="utf-8"))
    models = d["models"]
    date = d.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    srcs = d.get("sources", {})
    n_open = sum(1 for m in models if m.get("open_weights"))
    n_arena = sum(1 for m in models if m.get("arena_score") is not None)
    n_price = sum(1 for m in models if bp(m) is not None)
    orgs = {}
    for m in models:
        k = m.get("org") or "?"
        orgs[k] = orgs.get(k, 0) + 1
    top_orgs = sorted(orgs.items(), key=lambda kv: -kv[1])[:6]
    src_txt = " | ".join("%s %s" % (k, "ok" if (v.get("ok") if isinstance(v, dict) else v) else "fail") for k, v in srcs.items())

    nl = chr(10)
    r = []
    r.append("# 大模型排行榜 · LLM Leaderboard · AI 模型能力与性价比榜单")
    r.append("")
    r.append("> 📊 **每日自动更新**的大模型排行榜（LLM Leaderboard）：聚合 Arena 人类盲测偏好与 OpenRouter 定价，")
    r.append(">")
    r.append("> 数据源：[17nas.com](https://17nas.com/llm-leaderboard.php) ｜ 快照 **" + date + "**")
    r.append("")
    r.append("[![Daily Update](https://github.com/%s/actions/workflows/update.yml/badge.svg)](https://github.com/%s/actions/workflows/update.yml)" % (args.repo, args.repo))
    r.append("[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)");
    r.append("")
    r.append("")
    r.append("涵盖 **闭源商用模型**（GPT / Claude / Gemini / Grok / Qwen / GLM / Kimi …）与 **开源权重模型**")
    r.append("（Llama / DeepSeek / Qwen / GLM / Mistral / MiniMax …），可按能力、价格、性价比、上下文长度筛选对比。")
    r.append("")
    r.append("---")
    r.append("")
    r.append("## 快照概览")
    r.append("")
    r.append("| 指标 | 值 |")
    r.append("|---|---:|")
    r.append("| 收录模型 | **%d** |" % len(models))
    r.append("| 有 Arena 评分 | %d |" % n_arena)
    r.append("| 有定价数据 | %d |" % n_price)
    r.append("| 开源权重 | %d |" % n_open)
    r.append("| 覆盖厂商 | %d |" % len(orgs))
    r.append("| 数据源 | %s |" % src_txt)
    r.append("| 最近更新 | %s |" % date)
    r.append("")
    r.append("厂商分布：" + "、".join("%s (%d)" % (k, v) for k, v in top_orgs))
    r.append("")
    r.append("---")
    r.append("")
    r.append("## 榜单索引（5 个维度的模型对比）")
    r.append("")
    r.append("| 榜单 | 说明 | 完整榜 |")
    r.append("|---|---|---|")
    for key, title, desc, _ in VIEW_META:
        r.append("| **%s** | %s | [查看](leaderboard/%s.md) |" % (title, desc, key))
    r.append("")
    r.append("---")
    r.append("")
    r.append("## 📈 榜单可视化")
    r.append("")
    r.append("![Arena Top 10](docs/charts/arena-top10.svg)")
    r.append("")
    r.append("![Best value Top 10](docs/charts/value-top10.svg)")
    r.append("")
    r.append("> 图表随主题自动切换明暗；由 `scripts/render_charts.py` 每日生成。")
    r.append("")
    r.append("---")
    r.append("")
    r.append("## 🏆 综合榜 Top 10：Arena 人类偏好评分的模型排名")
    r.append("")
    r.append(render_top(models, "all", 10))
    r.append("")
    r.append("[→ 完整综合榜](leaderboard/all.md)")
    r.append("")
    r.append("## 💰 性价比榜 Top 10：最划算的大模型")
    r.append("")
    r.append("> 性价比 = Arena 分数 ÷ 混合价格（输入:输出 = 3:1）。**衡量单位花费换来的人类偏好得分**，比单纯比价格更有参考价值。")
    r.append("")
    r.append(render_top(models, "cheap", 10))
    r.append("")
    r.append("[→ 完整性价比榜](leaderboard/cheap.md)")
    r.append("")
    r.append("## 📄 长上下文榜 Top 10：最大上下文窗口的模型")
    r.append("")
    r.append(render_top(models, "ctx", 10))
    r.append("")
    r.append("[→ 完整长上下文榜](leaderboard/ctx.md)")
    r.append("")
    r.append("---")
    r.append("")
    r.append("## 数据说明")
    r.append("")
    r.append("- **Arena 分数**：LMArena 人类盲测的 Bradley-Terry 评分，附 95% 置信区间。两个模型的区间重叠时，名次差异不必过度解读。")
    r.append("- **票数**：参与投票的样本量。票数越高，分数越稳定。")
    r.append("- **价格**：OpenRouter 公开定价，单位美元 / 百万 token；混合价格按输入:输出 = 3:1 加权。")
    r.append("- **涨跌**：与上一份快照的名次对比。NEW = 新进榜。")
    r.append("")
    r.append("## 常见问题")
    r.append("")
    r.append("**这是什么榜单？** 一个每日自动更新的大模型排行榜，用 Arena 人类盲测偏好衡量模型能力，用 OpenRouter 公开定价衡量成本。")
    r.append("")
    r.append("**排名依据什么？** 综合榜按 LMArena 的 Bradley-Terry 评分（人类盲测胜率推导）排序，并给出 95% 置信区间；")
    r.append("性价比榜按「Arena 分数 ÷ 混合价格」排序，衡量单位花费换来的人类偏好得分。")
    r.append("")
    r.append("**为什么两个模型分数接近时不宜直接比名次？** 因为评分带有置信区间。区间重叠时，名次差异可能只是采样波动。")
    r.append("")
    r.append("**数据多久更新一次？** 每日一次，由 GitHub Actions 自动拉取并提交；历史快照保留在 [`data/history/`](data/history/)。")
    r.append("")
    r.append("**可以商用或二次分发吗？** 生成代码为 MIT；Arena 数据为 CC-BY-4.0（需署名）；请勿再分发 Artificial Analysis 数据。")
    r.append("")
    r.append("## 更新机制")
    r.append("")
    r.append("本仓库由 GitHub Actions **每日自动更新**：拉取聚合数据 → 生成榜单 → 提交。")
    r.append("历史快照保存在 [`data/history/`](data/history/)，可用于回溯任意一天的榜单。")
    r.append("")
    r.append("## 相关项目")
    r.append("")
    r.append("| 项目 | 说明 |")
    r.append("|---|---|")
    r.append("| [llm-benchmark-leaderboard](https://github.com/AmigaMeow/llm-benchmark-leaderboard) | 自托管的排行榜程序（PHP + 无数据库依赖），可基于本仓库的数据自行部署 |")
    r.append("| [cpu-benchmark-leaderboard](https://github.com/AmigaMeow/cpu-benchmark-leaderboard) | 自托管的 CPU 性能天梯榜 |")
    r.append("| [17nas.com/llm-leaderboard.php](https://17nas.com/llm-leaderboard.php) | 在线版榜单（含更多维度与历史趋势） |")
    r.append("")
    r.append("## 许可与数据条款")
    r.append("")
    r.append("- 本仓库的**榜单生成代码**以 [MIT](LICENSE) 许可开放。")
    r.append("- **Arena 评分**来自 LMArena（CC-BY-4.0 数据集），**价格数据**来自 OpenRouter 公开 API。")
    r.append("- 本仓库**不包含** Artificial Analysis 的数据：其 Terms of Use 明确禁止再分发，故未纳入。")
    r.append("- 完整的条款核查记录（含条款原文引用）见 [docs/UPSTREAM-TOS.md](docs/UPSTREAM-TOS.md)。")
    r.append("- 原始榜单与更多维度：[17nas.com/llm-leaderboard.php](https://17nas.com/llm-leaderboard.php)")
    r.append("")
    r.append("---")
    r.append("")
    r.append("*本页由 `scripts/render_readme.py` 自动生成，请勿手工编辑。*")

    with open(os.path.join(args.out, "README.md"), "w", encoding="utf-8") as f:
        f.write(chr(10).join(r) + chr(10))
    print("README.md 已生成：%d 行" % len(r))

if __name__ == "__main__":
    main()