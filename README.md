# 大模型排行榜 · LLM Leaderboard

> 📊 **每日自动更新**的大模型能力榜单 —— 聚合 Arena 人类盲测、Artificial Analysis 评测与 OpenRouter 定价。
>
> 数据源：[17nas.com](https://17nas.com/llm-leaderboard.php) ｜ 快照 **2026-09-20**

[![Daily Update](https://github.com/AmigaMeow/llm-leaderboard-data/actions/workflows/update.yml/badge.svg)](https://github.com/AmigaMeow/llm-leaderboard-data/actions/workflows/update.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 快照概览

| 指标 | 值 |
|---|---:|
| 收录模型 | **58** |
| 开源权重 | 18 |
| 闭源 | 40 |
| 覆盖厂商 | 15 |
| 数据源 | lmarena ✅ ｜ openrouter ✅ ｜ aa ✅ |
| 最近更新 | 2026-09-20 |

厂商分布：OpenAI (10)、Anthropic (9)、Google (8)、Alibaba (5)、Z.AI (4)、Moonshot AI (4)

---

## 榜单索引

| 榜单 | 说明 | 完整榜 |
|---|---|---|
| **综合榜** | Arena 人类盲测偏好 | [查看](leaderboard/all.md) |
| **智能指数榜** | Artificial Analysis 综合能力 | [查看](leaderboard/intel.md) |
| **编程榜** | AA 编程分项 | [查看](leaderboard/coding.md) |
| **性价比榜** | 智能指数 ÷ 混合价格 | [查看](leaderboard/cheap.md) |
| **速度榜** | 实测输出速度 t/s | [查看](leaderboard/speed.md) |
| **开源权重榜** | 仅开放权重模型 | [查看](leaderboard/open.md) |
| **长上下文榜** | 最大上下文窗口 | [查看](leaderboard/ctx.md) |
| **价格榜** | 混合价格升序 | [查看](leaderboard/price.md) |

---

## 🏆 综合榜 Top 10

| # | 模型 | 厂商 | Arena | 票数 |
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

> 智能指数 ÷ 混合价格（输入:输出 = 3:1）。**单位花费换来的能力**，比单纯比价格更有参考价值。

| # | 模型 | 厂商 | 智能/美元 | 混合价格 | 权重 |
|---:|:---|:---|---:|---:|:---|
| 🥇 | DeepSeek V4 Flash | DeepSeek | 583.5 | $0.059 | 开源 |
| 🥈 | GLM-5.3 Flash | Z.AI | 294.0 | $0.143 | 开源 |
| 🥉 | DeepSeek V4.1 Flash | DeepSeek | 150.5 | $0.262 | 开源 |
| 4 | MiMo V2.5 | Xiaomi | 127.4 | $0.175 | 开源 |
| 5 | Hy3 | Tencent | 111.7 | $0.231 | 开源 |
| 6 | GPT-5.6 Luna | OpenAI | 83.3 | $0.450 | 闭源 |
| 7 | MiniMax M3 | MiniMax | 56.4 | $0.525 | 开源 |
| 8 | DeepSeek V3.2 | DeepSeek | 53.0 | $0.302 | 开源 |
| 9 | DeepSeek V4 Pro | DeepSeek | 51.5 | $0.705 | 开源 |
| 10 | MiMo V2.5 Pro | Xiaomi | 48.6 | $0.544 | 开源 |

[→ 完整性价比榜](leaderboard/cheap.md)

## ⚡ 速度榜 Top 10

| # | 模型 | 厂商 | 速度(t/s) | 智能指数 |
|---:|:---|:---|---:|---:|
| 🥇 | Gemini 3.7 Flash | Google | 383.0 | 39.4 |
| 🥈 | Gemini 3.8 Flash | Google | 306.3 | 41.2 |
| 🥉 | DeepSeek V4 Flash | DeepSeek | 240.8 | 34.5 |
| 4 | Muse Spark 1.2 | Meta | 231.0 | 39.8 |
| 5 | DeepSeek V4.1 Flash | DeepSeek | 221.0 | 39.5 |
| 6 | Gemini 3.6 Flash | Google | 211.8 | 34.3 |
| 7 | Mistral Medium 3.5 | Mistral | 145.1 | 14.9 |
| 8 | GPT-5.6 Luna | OpenAI | 130.2 | 37.5 |
| 9 | Gemini 3.1 Pro Preview | Google | 123.8 | 30.4 |
| 10 | MiniMax M3 | MiniMax | 120.4 | 29.6 |

[→ 完整速度榜](leaderboard/speed.md)

---

## 数据说明

- **Arena 分数**：LMArena 人类盲测的 Bradley-Terry 评分，附 95% 置信区间。区间重叠时名次差异不必过度解读。
- **智能指数 / 编程 / 速度**：来自 Artificial Analysis 的实测评测。
- **价格**：OpenRouter 公开定价，单位美元 / 百万 token；混合价格按输入:输出 = 3:1 加权。
- **涨跌**：与上一份快照的名次对比。🆕 = 新进榜。

## 更新机制

本仓库由 GitHub Actions **每日自动更新**：拉取聚合数据 → 生成榜单 → 提交。
历史快照保存在 [`data/history/`](data/history/)，可用于回溯任意一天的榜单。

## 许可与数据条款

- 本仓库的**榜单生成代码**以 [MIT](LICENSE) 许可开放。
- **评测数据**来自 LMArena、Artificial Analysis、OpenRouter 等第三方，版权归各来源所有；本仓库仅聚合展示并标注来源，使用时请遵守各上游条款。
- 原始榜单与更多维度：[17nas.com/llm-leaderboard.php](https://17nas.com/llm-leaderboard.php)

---

*本页由 `scripts/render_readme.py` 自动生成，请勿手工编辑。*
