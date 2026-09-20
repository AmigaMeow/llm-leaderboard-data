#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17NAS LLM Leaderboard generator.

Upstream terms constraint: only LMArena (human preference) and OpenRouter
(pricing/context) fields are used. Artificial Analysis data may not be
redistributed per its Terms of Use, so no aa_* field is emitted here or by
the public API.
"""
from __future__ import annotations
import argparse, json, os, urllib.request
from datetime import datetime, timezone

API_DEFAULT = "https://17nas.com/api/public/llm-leaderboard.php"
UA = "17nas-llm-leaderboard/1.0 (+https://17nas.com)"
MEDALS = {1: "\U0001F947", 2: "\U0001F948", 3: "\U0001F949"}
SNAPSHOT_DATE = ""

def fetch(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

def money(v):
    if v is None:
        return "-"
    try:
        v = float(v)
    except (TypeError, ValueError):
        return str(v)
    if v == 0:
        return "free"
    if v < 0.01:
        return "$%.4f" % v
    if v < 1:
        return "$%.3f" % v
    return "$%.2f" % v

def num(v, nd=1):
    if v is None:
        return "-"
    try:
        return ("{:,.%df}" % nd).format(float(v))
    except (TypeError, ValueError):
        return str(v)

def integer(v):
    if v is None:
        return "-"
    try:
        return "{:,}".format(int(v))
    except (TypeError, ValueError):
        return str(v)

def ctx(v):
    if v is None:
        return "-"
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
    return "open" if m.get("open_weights") else "closed"

def blended_price(m):
    pin, pout = m.get("price_in"), m.get("price_out")
    if pin is None or pout is None:
        return None
    try:
        return (3.0 * float(pin) + float(pout)) / 4.0
    except (TypeError, ValueError):
        return None

def arena_per_dollar(m):
    a, p = m.get("arena_score"), blended_price(m)
    if a is None or not p or p <= 0:
        return None
    return float(a) / p

def delta_cell(cur, prev):
    if prev is None:
        return "NEW"
    d = prev - cur
    if d > 0:
        return "UP%d" % d
    if d < 0:
        return "DOWN%d" % abs(d)
    return "-"

def view_all(models):
    return [m for m in models if m.get("arena_score") is not None], lambda m: m["arena_score"]

def view_cheap(models):
    return [m for m in models if arena_per_dollar(m) is not None], lambda m: arena_per_dollar(m)

def view_price(models):
    return [m for m in models if blended_price(m) is not None], None

def view_ctx(models):
    return [m for m in models if m.get("context_length") is not None], lambda m: m["context_length"]

def view_open(models):
    return [m for m in models if m.get("open_weights") and m.get("arena_score") is not None], lambda m: m["arena_score"]

VIEWS = [
    ("all",   "Overall (Arena human preference)", view_all,   "LMArena Bradley-Terry score."),
    ("cheap", "Best value",  view_cheap, "Value = Arena score / blended price (in:out = 3:1)."),
    ("price", "Lowest price", view_price, "Sorted by blended price ascending."),
    ("ctx",   "Long context", view_ctx,  "Sorted by maximum context window."),
    ("open",  "Open weights", view_open, "Open-weight models only, by Arena score."),
]

COLS = {
    "all":   ["#", "Model", "Org", "Weights", "Arena", "95% CI", "Votes", "Change"],
    "cheap": ["#", "Model", "Org", "Weights", "Arena/$", "Blended", "Arena", "Change"],
    "price": ["#", "Model", "Org", "Weights", "Blended", "Input", "Output", "Change"],
    "ctx":   ["#", "Model", "Org", "Weights", "Context", "Arena", "Blended", "Change"],
    "open":  ["#", "Model", "Org", "License", "Arena", "Votes", "Context", "Change"],
}

def sort_rows(rows, key, keyfn):
    if key == "price":
        rows.sort(key=blended_price)
    elif key == "cheap":
        rows.sort(key=arena_per_dollar, reverse=True)
    elif keyfn:
        rows.sort(key=keyfn, reverse=True)
    return rows

def render_view(key, title, fn, desc, models, prev_ranks, limit):
    rows, keyfn = fn(models)
    rows = sort_rows(rows, key, keyfn)[:limit]
    cols = COLS[key]
    out = ["| " + " | ".join(cols) + " |"]
    out.append("|" + "|".join(["---:"] + [":---"] * (len(cols) - 2) + ["---:"]) + "|")
    prev = prev_ranks.get(key, {})
    for i, m in enumerate(rows, 1):
        rank_txt = MEDALS.get(i, str(i))
        name = m.get("display_name") or m.get("id")
        org = m.get("org") or "-"
        w = weights(m)
        dl = delta_cell(i, prev.get(m.get("id")))
        if key == "all":
            ci = "-"
            if m.get("arena_ci_low") is not None and m.get("arena_ci_high") is not None:
                ci = "%.0f ~ %.0f" % (m["arena_ci_low"], m["arena_ci_high"])
            row = [rank_txt, name, org, w, num(m.get("arena_score")), ci, integer(m.get("arena_votes")), dl]
        elif key == "cheap":
            row = [rank_txt, name, org, w, num(arena_per_dollar(m), 2), money(blended_price(m)), num(m.get("arena_score")), dl]
        elif key == "price":
            row = [rank_txt, name, org, w, money(blended_price(m)), money(m.get("price_in")), money(m.get("price_out")), dl]
        elif key == "ctx":
            row = [rank_txt, name, org, w, ctx(m.get("context_length")), num(m.get("arena_score")), money(blended_price(m)), dl]
        else:
            row = [rank_txt, name, org, m.get("license") or "-", num(m.get("arena_score")), integer(m.get("arena_votes")), ctx(m.get("context_length")), dl]
        out.append("| " + " | ".join(str(c) for c in row) + " |")
    nl = chr(10)
    header = "# " + title + nl + nl + "> " + desc + nl + nl
    header += "> Snapshot: " + SNAPSHOT_DATE + " | " + str(len(rows)) + " models" + nl + nl
    return header + nl.join(out) + nl

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
    for m in models:
        for k in [k for k in list(m.keys()) if k.startswith("aa_")]:
            m.pop(k, None)
    out = args.out
    os.makedirs(os.path.join(out, "leaderboard"), exist_ok=True)
    os.makedirs(os.path.join(out, "data", "history"), exist_ok=True)
    prev_models = []
    latest = os.path.join(out, "data", "latest.json")
    if os.path.isfile(latest):
        try:
            prev_models = json.load(open(latest, encoding="utf-8")).get("models", [])
        except Exception:
            prev_models = []
    prev_ranks = {}
    for key, title, fn, desc in VIEWS:
        rows, keyfn = fn(prev_models)
        rows = sort_rows(rows, key, keyfn)
        prev_ranks[key] = {m.get("id"): i for i, m in enumerate(rows, 1)}
    for key, title, fn, desc in VIEWS:
        with open(os.path.join(out, "leaderboard", key + ".md"), "w", encoding="utf-8") as f:
            f.write(render_view(key, title, fn, desc, models, prev_ranks, args.limit))
    for stale in ("intel.md", "coding.md", "speed.md"):
        p = os.path.join(out, "leaderboard", stale)
        if os.path.isfile(p):
            os.remove(p)
    snapshot = {"generated_at": gen_at, "date": date,
                "schema_version": data.get("schema_version", 1),
                "sources": data.get("sources", {}), "count": len(models), "models": models}
    for p in (latest, os.path.join(out, "data", "history", date + ".json")):
        with open(p, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=1)
    print(json.dumps({"ok": True, "date": date, "models": len(models),
                      "views": [v[0] for v in VIEWS],
                      "sources": {k: (v.get("ok") if isinstance(v, dict) else v)
                                  for k, v in data.get("sources", {}).items()}}, ensure_ascii=False))

if __name__ == "__main__":
    main()