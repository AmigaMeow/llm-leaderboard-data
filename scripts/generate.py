#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
17NAS LLM Leaderboard —— 榜单生成器

从 17nas.com 公开接口拉取聚合后的模型评测数据，生成：
  - README.md            门户 + 索引 + Top 榜
  - leaderboard/*.md     各维度榜单
  - data/latest.json     最新完整快照（供次日计算涨跌）
  - data/history/*.json  每日归档
  - CHANGELOG.md         版本化更新记录

零第三方依赖（仅标准库），可在 GitHub Actions 中直接运行。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

API_DEFAULT = "https://17nas.com/api/public/llm-leaderboard.php"
UA = "17nas-llm-leaderboard/1.0 (+https://17nas.com)"

MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


def fetch(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def money(v):
    if v is None:
        return "—"
    try:
        v = float(v)
    except (TypeError, ValueError):
        return str(v)
    if v == 0:
        return "免费"
    if v < 0.01:
        return "$%.4f" % v
    if v < 1:
        return "$%.3f" % v
    return "$%.2f" % v


def num(v, nd=1):
    if v is None:
        return "—"
    try:
        return ("{:,.%df}" % nd).format(float(v))
    except (TypeError, ValueError):
        return str(v)


def integer(v):
    if v is None:
        return "—"
    try:
        return "{:,}".format(int(v))
    except (TypeError, ValueError):
        return str(v)


def ctx(v):
    if v is None:
        return "—"
    try:
        v = int(v)
    except (TypeError, ValueError):
        return str(v)
    if v >= 1000000:
        return "%.1fM" % (v / 1000000.0)
    if v >= 1000:
        return "%dK" % (v // 1000)
    return str(v)


def weights(m):
    return "开源" if m.get("open_weights") else "闭源"


def blended_price(m):
    """混合价格（输入:输出 = 3:1），单位：美元 / 百万 token。"""
    pin, pout = m.get("price_in"), m.get("price_out")
    if pin is None or pout is None:
        return None
    try:
        return (3.0 * float(pin) + float(pout)) / 4.0
    except (TypeError, ValueError):
        return None


def cost_effective(m):
    """性价比 = 智能指数 / 混合价格。"""
    intel = m.get("aa_intelligence")
    bp = blended_price(m)
    if intel is None or bp is None or bp <= 0:
        return None
    return float(intel) / bp


def delta_cell(cur_rank, prev_rank):
    if prev_rank is None:
        return "🆕"
    d = prev_rank - cur_rank
    if d > 0:
        return "🔺%d" % d
    if d < 0:
        return "🔻%d" % abs(d)
    return "—"


# ---------- 视图定义 ----------

def view_all(models):
    return [m for m in models if m.get("arena_score") is not None], lambda m: m["arena_score"]


def view_intel(models):
    return [m for m in models if m.get("aa_intelligence") is not None], lambda m: m["aa_intelligence"]


def view_coding(models):
    return [m for m in models if m.get("aa_coding") is not None], lambda m: m["aa_coding"]


def view_speed(models):
    return [m for m in models if m.get("aa_speed") is not None], lambda m: m["aa_speed"]


def view_cheap(models):
    rows = [m for m in models if cost_effective(m) is not None]
    return rows, lambda m: cost_effective(m)


def view_open(models):
    rows = [m for m in models if m.get("open_weights") and m.get("aa_intelligence") is not None]
    return rows, lambda m: m["aa_intelligence"]


def view_ctx(models):
    return [m for m in models if m.get("context_length") is not None], lambda m: m["context_length"]


def view_price(models):
    rows = [m for m in models if blended_price(m) is not None]
    return rows, None  # 升序，价格低者在前


VIEWS = [
    ("all", "综合榜（Arena 人类偏好）", view_all,
     "LMArena Arena 分数（Bradley-Terry 口径），反映人类盲测偏好。"),
    ("intel", "智能指数榜", view_intel,
     "Artificial Analysis 综合智能指数，覆盖推理、知识与编码能力。"),
    ("coding", "编程榜", view_coding,
     "Artificial Analysis 编程能力分项。"),
    ("cheap", "性价比榜", view_cheap,
     "性价比 = 智能指数 ÷ 混合价格（输入:输出 = 3:1）。分数越高，单位花费换来的能力越强。"),
    ("speed", "速度榜", view_speed,
     "Artificial Analysis 实测输出速度（token/秒）。"),
    ("open", "开源权重榜", view_open,
     "仅收录开放权重模型，按智能指数排序。"),
    ("ctx", "长上下文榜", view_ctx,
     "按最大上下文窗口排序，适合长文档与代码库场景。"),
    ("price", "价格榜", view_price,
     "按混合价格升序。注意：便宜不等于划算，请同时参考性价比榜。"),
]


def render_view(key, title, fn, desc, models, prev_ranks, limit):
    rows, keyfn = fn(models)
    if key == "price":
        rows.sort(key=lambda m: blended_price(m))
    elif key == "cheap":
        rows.sort(key=lambda m: cost_effective(m), reverse=True)
    else:
        rows.sort(key=keyfn, reverse=True)
    rows = rows[:limit]

    if key == "all":
        cols = ["排名", "模型", "厂商", "权重", "Arena", "95% 置信区间", "票数", "涨跌"]
    elif key == "intel":
        cols = ["排名", "模型", "厂商", "权重", "智能指数", "编程", "速度(t/s)", "涨跌"]
    elif key == "coding":
        cols = ["排名", "模型", "厂商", "权重", "编程分", "智能指数", "涨跌"]
    elif key == "cheap":
        cols = ["排名", "模型", "厂商", "权重", "智能/美元", "智能指数", "混合价格", "涨跌"]
    elif key == "speed":
        cols = ["排名", "模型", "厂商", "权重", "速度(t/s)", "首 token(s)", "智能指数", "涨跌"]
    elif key == "open":
        cols = ["排名", "模型", "厂商", "许可", "智能指数", "编程", "上下文", "涨跌"]
    elif key == "ctx":
        cols = ["排名", "模型", "厂商", "权重", "上下文", "智能指数", "混合价格", "涨跌"]
    else:
        cols = ["排名", "模型", "厂商", "权重", "混合价格", "输入", "输出", "涨跌"]

    out = []
    out.append("| " + " | ".join(cols) + " |")
    out.append("|" + "|".join(["---:"] + [":---"] * (len(cols) - 2) + ["---:"]) + "|")

    prev = prev_ranks.get(key, {})
    for i, m in enumerate(rows, 1):
        mi = m.get("id")
        rank_txt = MEDALS.get(i, str(i))
        name = m.get("display_name") or mi
        org = m.get("org") or "—"
        w = weights(m)
        dl = delta_cell(i, prev.get(mi))

        if key == "all":
            ci = "—"
            if m.get("arena_ci_low") is not None and m.get("arena_ci_high") is not None:
                ci = "%.0f ~ %.0f" % (m["arena_ci_low"], m["arena_ci_high"])
            row = [rank_txt, name, org, w, num(m.get("arena_score")), ci, integer(m.get("arena_votes")), dl]
        elif key == "intel":
            row = [rank_txt, name, org, w, num(m.get("aa_intelligence")), num(m.get("aa_coding")),
                   num(m.get("aa_speed")), dl]
        elif key == "coding":
            row = [rank_txt, name, org, w, num(m.get("aa_coding")), num(m.get("aa_intelligence")), dl]
        elif key == "cheap":
            row = [rank_txt, name, org, w, num(cost_effective(m), 2), num(m.get("aa_intelligence")),
                   money(blended_price(m)), dl]
        elif key == "speed":
            row = [rank_txt, name, org, w, num(m.get("aa_speed")), num(m.get("aa_ttft"), 2),
                   num(m.get("aa_intelligence")), dl]
        elif key == "open":
            row = [rank_txt, name, org, m.get("license") or "—", num(m.get("aa_intelligence")),
                   num(m.get("aa_coding")), ctx(m.get("context_length")), dl]
        elif key == "ctx":
            row = [rank_txt, name, org, w, ctx(m.get("context_length")),
                   num(m.get("aa_intelligence")), money(blended_price(m)), dl]
        else:
            row = [rank_txt, name, org, w, money(blended_price(m)),
                   money(m.get("price_in")), money(m.get("price_out")), dl]
        out.append("| " + " | ".join(str(c) for c in row) + " |")

    body = "\n".join(out)
    header = "# %s\n\n> %s\n\n" % (title, desc)
    header += "> 数据快照：%s ｜ 共 %d 个模型进入本榜\n\n" % (SNAPSHOT_DATE, len(rows))
    return header + body + "\n"


SNAPSHOT_DATE = ""


def main():
    global SNAPSHOT_DATE
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default=API_DEFAULT)
    ap.add_argument("--out", default=".")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--date", default="")
    args = ap.parse_args()

    data = fetch(args.api)
    models = data["models"]
    gen_at = data.get("generated_at") or datetime.now(timezone.utc).isoformat()
    date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    SNAPSHOT_DATE = date

    out = args.out
    os.makedirs(os.path.join(out, "leaderboard"), exist_ok=True)
    os.makedirs(os.path.join(out, "data", "history"), exist_ok=True)

    # 上一份快照（用于涨跌）
    prev_models = []
    prev_path = os.path.join(out, "data", "latest.json")
    if os.path.isfile(prev_path):
        try:
            with open(prev_path, encoding="utf-8") as f:
                prev_models = json.load(f).get("models", [])
        except Exception:
            prev_models = []

    prev_ranks = {}
    for key, title, fn, desc in VIEWS:
        rows, keyfn = fn(prev_models)
        if key == "price":
            rows.sort(key=lambda m: blended_price(m))
        elif key == "cheap":
            rows.sort(key=lambda m: cost_effective(m), reverse=True)
        elif keyfn:
            rows.sort(key=keyfn, reverse=True)
        prev_ranks[key] = {m.get("id"): i for i, m in enumerate(rows, 1)}

    # 榜单文件
    for key, title, fn, desc in VIEWS:
        content = render_view(key, title, fn, desc, models, prev_ranks, args.limit)
        with open(os.path.join(out, "leaderboard", key + ".md"), "w", encoding="utf-8") as f:
            f.write(content)

    # 数据快照
    snapshot = {
        "generated_at": gen_at,
        "date": date,
        "schema_version": data.get("schema_version", 1),
        "sources": data.get("sources", {}),
        "count": len(models),
        "models": models,
    }
    with open(prev_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "data", "history", date + ".json"), "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "data", "history", date + ".json"), "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=1)

    print(json.dumps({
        "ok": True, "date": date, "models": len(models),
        "sources": {k: (v.get("ok") if isinstance(v, dict) else v) for k, v in data.get("sources", {}).items()},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
