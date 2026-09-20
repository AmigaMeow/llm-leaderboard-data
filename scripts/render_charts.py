#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render SVG charts for the leaderboard README. Standard library only.

Outputs to docs/charts/. Charts adapt to GitHub light/dark theme via
prefers-color-scheme, and carry the LMArena attribution required by CC-BY-4.0.
"""
from __future__ import annotations
import argparse, json, os

W = 900
ROW_H = 34
TOP_N = 10
PAD_T = 96
NAME_RIGHT = 250
BAR_X = 264
BAR_RIGHT = 756          # 留出右侧数值标签空间
FOOT_H = 40

GOLD = "#d4a017"
SILVER = "#8c959f"
BRONZE = "#b06a3b"
BLUE = "#3b82f6"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


def price(m):
    a, b = m.get("price_in"), m.get("price_out")
    if a is None or b is None:
        return None
    try:
        return (3.0 * float(a) + float(b)) / 4.0
    except (TypeError, ValueError):
        return None


def value_score(m):
    s, p = m.get("arena_score"), price(m)
    if s is None or not p or p <= 0:
        return None
    return float(s) / p


def pick(models, key, n=TOP_N):
    if key == "value":
        rows = [m for m in models if value_score(m) is not None]
        rows.sort(key=value_score, reverse=True)
    else:
        rows = [m for m in models if m.get("arena_score") is not None]
        rows.sort(key=lambda m: m["arena_score"], reverse=True)
    return rows[:n]


def metric(m, key):
    return value_score(m) if key == "value" else float(m.get("arena_score"))


def bar_color(i):
    if i == 0:
        return GOLD
    if i == 1:
        return SILVER
    if i == 2:
        return BRONZE
    return BLUE


STYLE = """  <style>
    .bg { fill: #ffffff; }
    .fg { fill: #24292f; }
    .muted { fill: #57606a; }
    .track { fill: #eaeef2; }
    .axis { stroke: #d0d7de; }
    @media (prefers-color-scheme: dark) {
      .bg { fill: #0d1117; }
      .fg { fill: #e6edf3; }
      .muted { fill: #8b949e; }
      .track { fill: #21262d; }
      .axis { stroke: #30363d; }
    }
  </style>"""


def build_svg(models, key, title, subtitle, value_label):
    rows = pick(models, key)
    if not rows:
        return None
    vals = [metric(m, key) for m in rows]
    hi = max(vals)
    lo = min(vals)
    span = hi - lo
    base = lo - span * 0.45 if span > 0 else lo * 0.95
    if base <= 0:
        base = 0.0
    scale_max = hi if hi > base else base + 1

    height = PAD_T + ROW_H * len(rows) + FOOT_H
    p = []
    p.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img" aria-label="%s">' % (W, height, W, height, esc(title)))
    p.append(STYLE)
    p.append('<rect class="bg" x="0" y="0" width="%d" height="%d" rx="8"/>' % (W, height))
    p.append('<text class="fg" x="24" y="40" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="18" font-weight="600">%s</text>' % esc(title))
    p.append('<text class="muted" x="24" y="64" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="12.5">%s</text>' % esc(subtitle))
    span_x = BAR_RIGHT - BAR_X
    label_x = BAR_RIGHT + 8
    for i, m in enumerate(rows):
        y = PAD_T + i * ROW_H
        v = metric(m, key)
        frac = (v - base) / (scale_max - base) if scale_max > base else 1.0
        frac = max(0.02, min(1.0, frac))
        bw = span_x * frac
        name = m.get("display_name") or m.get("id") or "?"
        if len(name) > 24:
            name = name[:23] + "…"
        p.append('<text class="fg" x="%d" y="%d" text-anchor="end" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="13">%s</text>' % (NAME_RIGHT, y + 17, esc(name)))
        p.append('<rect class="track" x="%d" y="%d" width="%d" height="18" rx="4"/>' % (BAR_X, y + 4, span_x))
        p.append('<rect x="%d" y="%d" width="%.1f" height="18" rx="4" fill="%s"/>' % (BAR_X, y + 4, bw, bar_color(i)))
        label = ("%.1f" % v) if key == "value" else ("{:,.1f}".format(v))
        p.append('<text class="fg" x="%d" y="%d" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="12.5" font-weight="600">%s</text>' % (label_x, y + 17, esc(label)))
    fy = height - 16
    p.append('<line class="axis" x1="24" y1="%d" x2="%d" y2="%d" stroke-width="1"/>' % (fy - 20, W - 24, fy - 20))
    p.append('<text class="muted" x="24" y="%d" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="11.5">%s ｜ Data: LMArena (CC-BY-4.0) + OpenRouter ｜ 17nas.com</text>' % (fy, esc(value_label)))
    p.append('</svg>')
    return chr(10).join(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/latest.json")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()

    d = json.load(open(args.data, encoding="utf-8"))
    models = d["models"]
    date = d.get("date", "")
    dst = os.path.join(args.out, "docs", "charts")
    os.makedirs(dst, exist_ok=True)

    specs = [
        ("arena-top10.svg", "arena", "Arena Top 10 — human preference",
         "LMArena Bradley-Terry score, higher is better. Snapshot " + date, "Arena score"),
        ("value-top10.svg", "value", "Best value Top 10 — Arena score per dollar",
         "Arena score / blended price (in:out = 3:1), higher is better. Snapshot " + date, "Arena per $"),
    ]
    made = []
    for fname, key, title, sub, vlabel in specs:
        svg = build_svg(models, key, title, sub, vlabel)
        if not svg:
            print("  skip (no data):", fname)
            continue
        with open(os.path.join(dst, fname), "w", encoding="utf-8") as f:
            f.write(svg)
        made.append(fname)
    print("charts: " + ", ".join(made))


if __name__ == "__main__":
    main()