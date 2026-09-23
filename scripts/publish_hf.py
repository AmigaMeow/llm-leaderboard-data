#!/usr/bin/env python3
"""把榜单数据发布到 Hugging Face Datasets。

设计原则：
  · 「构建」全部用标准库（与 scripts/ 下其它脚本一致，零第三方依赖）；
  · 只有「上传」这一步用官方客户端 huggingface_hub —— 因为上传协议细节多，
    用官方客户端比手搓 HTTP 更可靠。未配置 token 时本脚本直接跳过上传，
    所以日常 CI 路径仍然零依赖。

用法：
  python3 scripts/publish_hf.py --dry-run                    # 只构建到本地目录，不上传
  python3 scripts/publish_hf.py --repo <user>/<name>         # 构建并上传（需 HF_TOKEN）

环境变量：
  HF_TOKEN   Hugging Face 写权限 token（在 GitHub 仓库 Secrets 里配置）
"""
import argparse
import json
import os
import shutil
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CARD = """---
license: cc-by-4.0
language:
- en
- zh
pretty_name: LLM Leaderboard (Arena preference x API pricing)
size_categories:
- n<1K
tags:
- llm
- leaderboard
- benchmark
- evaluation
- lmarena
- openrouter
- model-comparison
configs:
- config_name: models
  data_files: data/models.jsonl
---

# LLM Leaderboard (Arena x API pricing)

Daily-updated LLM leaderboard combining **LMArena human-preference (Arena) scores**
with **OpenRouter public pricing**, so you can answer *"what should I use at $X?"* —
a question neither source answers on its own.

> Source of truth: [17nas.com/llm-leaderboard.php](https://17nas.com/llm-leaderboard.php)
> ｜ Upstream repo: [AmigaMeow/llm-leaderboard-data](https://github.com/AmigaMeow/llm-leaderboard-data)

## Files

| Path | 内容 |
|---|---|
| `data/models.jsonl` | **推荐入口**：一行一个模型（扁平结构，可直接 `load_dataset`） |
| `data/latest.json` | 最近一次快照的原始结构（含 sources 元信息） |
| `data/history/YYYY-MM-DD.json` | 按天归档的历史快照，可做差分 |

## Fields

- `id` / `display_name` / `org` — 模型标识
- `arena_score` / `arena_ci_low` / `arena_ci_high` / `arena_votes` / `arena_rank`
  — LMArena Bradley-Terry 评分与 95% 置信区间。**区间重叠时名次差没有统计意义**，
  请据此判断，不要只看名次。
- `price_in` / `price_out` — OpenRouter 报价，**美元 / 百万 token**
- `blended_price` — 便捷派生值 `(3 * price_in + price_out) / 4`（假设输入:输出 = 3:1，
  按你自己负载调整）
- `context_length` / `open_weights` / `license` / `hf_repo` / `listed_at_iso` / `sources_hit`
- `snapshot_date` / `snapshot_generated_at` — 本行所属快照
- `lmarena_publish_date` — **上游 Arena 榜的发布日期**，与抓取日期是两回事，见下

## Important: two different dates

`snapshot_date` is when **this repository** fetched the data.
`lmarena_publish_date` is when **LMArena** published the leaderboard snapshot being used.

LMArena publishes on its own schedule — there can be long gaps. Always check
`lmarena_publish_date` before treating Arena scores as current.

## Usage

```python
from datasets import load_dataset
ds = load_dataset("<this-dataset>", "models", split="train")
print(ds[0])
```

## Attribution and licensing

- **LMArena** leaderboard data — licensed **CC-BY-4.0**; attribution required (given here).
- **OpenRouter** public pricing API.
- **Artificial Analysis is deliberately NOT included** — their terms prohibit redistribution.
- This compilation is published under **CC-BY-4.0** to match the most restrictive
  upstream source. See the upstream repo's `docs/UPSTREAM-TOS.md`.

## Update cadence

Rebuilt daily by a GitHub Actions workflow right after the upstream repository fetches
fresh data. See `data/history/` for per-day snapshots.
"""


def blended(m):
    a, b = m.get("price_in"), m.get("price_out")
    if a is None or b is None:
        return None
    try:
        return round((3.0 * float(a) + float(b)) / 4.0, 6)
    except (TypeError, ValueError):
        return None


def build(latest_path, out_dir):
    """构建 HF 数据集目录。返回 (模型行数, 历史文件数, 上游发布日)。"""
    with open(latest_path, encoding="utf-8") as fh:
        d = json.load(fh)

    date = d.get("date") or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    gen_at = d.get("generated_at")
    srcs = d.get("sources") or {}
    arena_pub = ((srcs.get("lmarena") or {}).get("publish_date")) or None

    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(os.path.join(out_dir, "data", "history"), exist_ok=True)

    # 1) 扁平 JSONL：一行一个模型（load_dataset 的推荐入口）
    rows = 0
    with open(os.path.join(out_dir, "data", "models.jsonl"), "w", encoding="utf-8") as fh:
        for m in d.get("models", []):
            row = dict(m)
            row["blended_price"] = blended(m)
            row["snapshot_date"] = date
            row["snapshot_generated_at"] = gen_at
            row["lmarena_publish_date"] = arena_pub
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            rows += 1

    # 2) 原始快照（保留 sources 元信息）
    shutil.copyfile(latest_path, os.path.join(out_dir, "data", "latest.json"))

    # 3) 历史快照
    hist_src = os.path.join(ROOT, "data", "history")
    hist_n = 0
    if os.path.isdir(hist_src):
        for name in sorted(os.listdir(hist_src)):
            if name.endswith(".json"):
                shutil.copyfile(os.path.join(hist_src, name),
                                os.path.join(out_dir, "data", "history", name))
                hist_n += 1

    # 4) 数据集卡片
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(CARD)

    return rows, hist_n, arena_pub


def upload(out_dir, repo_id, token):
    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("  ! 未安装 huggingface_hub（pip install huggingface_hub），跳过上传", file=sys.stderr)
        return False
    api = HfApi(token=token)
    api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)
    api.upload_folder(repo_id=repo_id, repo_type="dataset", folder_path=out_dir,
                      commit_message="data: update from 17nas.com/llm-leaderboard")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(ROOT, "data", "latest.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, ".hf-build"))
    ap.add_argument("--repo", default=os.environ.get("HF_DATASET_REPO", ""))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.isfile(args.data):
        print("找不到数据文件: " + args.data, file=sys.stderr)
        return 2

    rows, hist, pub = build(args.data, args.out)
    print("  构建完成: %d 个模型行 / %d 个历史快照 -> %s" % (rows, hist, args.out))
    print("  上游 Arena 发布日: %s" % (pub or "(无)"))

    token = os.environ.get("HF_TOKEN", "")
    if args.dry_run or not args.repo or not token:
        why = "dry-run" if args.dry_run else ("未配置 --repo" if not args.repo else "未配置 HF_TOKEN")
        print("  跳过上传（%s）" % why)
        return 0

    ok = upload(args.out, args.repo, token)
    print("  已上传到 https://huggingface.co/datasets/%s" % args.repo if ok else "  上传未执行")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
