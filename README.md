# 大模型排行榜 · LLM Leaderboard

> 📊 **每日自动更新**的大模型能力与价格榜单 —— 聚合 Arena 人类盲测偏好与 OpenRouter 定价。
>
> 数据源：[17nas.com](https://17nas.com/llm-leaderboard.php) ｜ 快照 **2026-09-20**

[![Daily Update](https://github.com/AmigaMeow/llm-leaderboard-data/actions/workflows/update.yml/badge.svg)](https://github.com/AmigaMeow/llm-leaderboard-data/actions/workflows/update.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 快照概览

| 指标 | 值 |
|---|---:|
| 收录模型 | **58** |
| 有 Arena 评分 | 43 |
| 有定价数据 | 57 |
| 开源权重 | 18 |
| 覆盖厂商 | 15 |
| 数据源 | lmarena ok | openrouter ok |
| 最近更新 | 2026-09-20 |

厂商分布：OpenAI (10)、Anthropic (9)、Google (8)、Alibaba (5)、Z.AI (4)、Moonshot AI (4)

---

## 榜单索引

| 榜单 | 说明 | 完整榜 |
|---|---|---|
| **Overall** | Arena human preference | [查看](leaderboard/all.md) |
| **Best value** | Arena score / blended price | [查看](leaderboard/cheap.md) |
| **Lowest price** | Blended price ascending | [查看](leaderboard/price.md) |
| **Long context** | Maximum context window | [查看](leaderboard/ctx.md) |
| **Open weights** | Open-weight models only | [查看](leaderboard/open.md) |

---

## 🏆 综合榜 Top 10（Arena 人类偏好）

| # | Model | Org | Arena | Votes |
|---:|:---|:---|---:|---:|
| 🥇 | Claude Fable 5.1 | Anthropic | 1,507.6 | 5,783 |
| 🥈 | Claude Opus 5 | Anthropic | 1,505.0 | 20,706 |
| 🥉 | Claude Opus 4.6 | Anthropic | 1,503.0 | 71,993 |
| 4 | Gemini 3.8 Flash | Google | 1,494.7 | 5,076 |
| 5 | Claude Fable 5 | Anthropic | 1,492.6 | 30,057 |
| 6 | Gemini 3.7 Flash | Google | 1,490.5 | 5,640 |
| 7 | Claude Opus 4.7 | Anthropic | 1,490.0 | 60,002 |
| 8 | Muse Spark 1.2 | Meta | 1,489.4 | 3,227 |
| 9 | Gemini 3.5 Flash | Google | 1,482.1 | 38,257 |
| 10 | Qwen3.8 Max | Alibaba | 1,480.6 | 16,670 |

[→ 完整综合榜](leaderboard/all.md)

## 💰 性价比榜 Top 10

> 性价比 = Arena 分数 ÷ 混合价格（输入:输出 = 3:1）。**衡量单位花费换来的人类偏好得分**，比单纯比价格更有参考价值。

| # | Model | Org | Arena/$ | Blended | Weights |
|---:|:---|:---|---:|---:|:---|
| 🥇 | DeepSeek V4 Flash | DeepSeek | 24,216.5 | $0.059 | open |
| 🥈 | GLM-5.3 Flash | Z.AI | 10,329.1 | $0.143 | open |
| 🥉 | MiMo V2.5 | Xiaomi | 8,156.6 | $0.175 | open |
| 4 | Hy3 | Tencent | 6,236.4 | $0.231 | open |
| 5 | GPT-5.6 Luna | OpenAI | 3,177.6 | $0.450 | closed |
| 6 | MiniMax M3 | MiniMax | 2,730.5 | $0.525 | open |
| 7 | MiMo V2.5 Pro | Xiaomi | 2,693.7 | $0.544 | open |
| 8 | Qwen3.7 Plus | Alibaba | 2,596.8 | $0.560 | closed |
| 9 | DeepSeek V4 Pro | DeepSeek | 2,056.5 | $0.705 | open |
| 10 | GLM-5.2 | Z.AI | 1,722.9 | $0.851 | open |

[→ 完整性价比榜](leaderboard/cheap.md)

## 📄 长上下文榜 Top 10

| # | Model | Org | Context | Arena | Blended |
|---:|:---|:---|---:|---:|---:|
| 🥇 | Grok 4.20 | xAI | 2.0M | - | $1.56 |
| 🥈 | GLM-5.3 | Z.AI | 1.3M | 1,475.1 | $1.40 |
| 🥉 | GLM-5.3 Flash | Z.AI | 1.3M | 1,471.9 | $0.143 |
| 4 | GPT-5.5 | OpenAI | 1.1M | 1,470.9 | $11.25 |
| 5 | GPT-5.4 | OpenAI | 1.1M | 1,469.6 | $5.62 |
| 6 | MiMo V2.5 Pro | Xiaomi | 1.1M | 1,464.7 | $0.544 |
| 7 | GPT-5.6 Sol | OpenAI | 1.1M | 1,455.0 | $4.00 |
| 8 | GPT-5.6 Terra | OpenAI | 1.1M | 1,446.2 | $4.50 |
| 9 | GPT-5.6 Luna | OpenAI | 1.1M | 1,429.9 | $0.450 |
| 10 | MiMo V2.5 | Xiaomi | 1.1M | 1,427.4 | $0.175 |

[→ 完整长上下文榜](leaderboard/ctx.md)

---

## 数据说明

- **Arena 分数**：LMArena 人类盲测的 Bradley-Terry 评分，附 95% 置信区间。两个模型的区间重叠时，名次差异不必过度解读。
- **票数**：参与投票的样本量。票数越高，分数越稳定。
- **价格**：OpenRouter 公开定价，单位美元 / 百万 token；混合价格按输入:输出 = 3:1 加权。
- **涨跌**：与上一份快照的名次对比。NEW = 新进榜。

## 更新机制

本仓库由 GitHub Actions **每日自动更新**：拉取聚合数据 → 生成榜单 → 提交。
历史快照保存在 [`data/history/`](data/history/)，可用于回溯任意一天的榜单。

## 许可与数据条款

- 本仓库的**榜单生成代码**以 [MIT](LICENSE) 许可开放。
- **Arena 评分**来自 LMArena（CC-BY-4.0 数据集），**价格数据**来自 OpenRouter 公开 API。
- 本仓库**不包含** Artificial Analysis 的数据：其 Terms of Use 明确禁止再分发，故未纳入。
- 完整的条款核查记录（含条款原文引用）见 [docs/UPSTREAM-TOS.md](docs/UPSTREAM-TOS.md)。
- 原始榜单与更多维度：[17nas.com/llm-leaderboard.php](https://17nas.com/llm-leaderboard.php)

---

*本页由 `scripts/render_readme.py` 自动生成，请勿手工编辑。*
