# 上游数据条款核查

> **核查日期**：2026-09-20
> **核查对象**：本仓库榜单所用到的三家上游数据源
> **结论**：3 家已核查 —— 1 家禁止再分发（已移除）、1 家明确允许、1 家未见禁止但未逐条核实

---

## 结论速览

| 上游 | 用途 | 可否再分发 | 依据 |
|---|---|---|---|
| **Artificial Analysis** | 智能指数 / 编程 / 速度 | ❌ **禁止** | Terms of Use 明文禁止分发 |
| **LMArena** | Arena 人类偏好评分 | ✅ **可以** | 数据集采用 CC-BY-4.0 |
| **OpenRouter** | 模型定价与上下文长度 | ⚠️ **未见禁止，但未逐条核实** | ToS 中未出现禁止再分发的表述 |

**当前处置**：本仓库与公开 API **只包含 LMArena + OpenRouter 来源的字段**，不含任何 Artificial Analysis 数据。

---

## 一、Artificial Analysis —— ❌ 禁止再分发

**条款来源**：<https://artificialanalysis.ai/terms-of-use>（Last revised: September 15 2026）

**授权范围原文（节选）**：

> **2.1 License.** Subject to these Terms, Company grants you a non-transferable, non-exclusive, revocable, limited license to use and access the Site **solely for your own personal, noncommercial use**.

**限制条款原文（节选）**：

> **2.2 Certain Restrictions.** The rights granted to you in these Terms are subject to the following restrictions:
> (a) you shall not license, sell, rent, lease, transfer, assign, **distribute, host, or otherwise commercially exploit** the Site, whether in whole or in part, **or any content displayed on the Site**;
> …
> (d) except as expressly stated herein, **no part of the Site may be copied, reproduced, distributed, republished, downloaded, displayed, posted or transmitted in any form or by any means**.

**判定**：将 AA 的评分字段发布到公开仓库或公开 API，属于条款明令禁止的 distribute / republish 行为；授权亦仅限 personal, noncommercial use。

**处置**：本仓库**完全不含** AA 数据，包括但不限于：

- `aa_intelligence`、`aa_coding`、`aa_speed`、`aa_ttft`、`aa_variants` 字段
- 原先基于 AA 的「智能指数榜」「编程榜」「速度榜」三个榜单文件

上游站点页面（17nas.com）对 AA 数据的展示属另一场景，不在本仓库范围内，**需另行评估**。

---

## 二、LMArena —— ✅ CC-BY-4.0，允许再分发

**依据**：Hugging Face 数据集元数据中标注的许可证

```
数据集:  lmarena-ai/arena-human-preference-140k
license: cc-by-4.0
tags:    ["license:cc-by-4.0"]
```

查询方式：`GET https://huggingface.co/api/datasets/lmarena-ai/arena-human-preference-140k`

**CC-BY-4.0 的要求**：

- ✅ 允许复制、分发、改编，**包括商业用途**
- ✅ 义务：**署名（attribution）**、提供许可证链接、标明是否作出修改

**本仓库如何履行署名义务**：

1. README 的「数据说明」与「许可与数据条款」两节均标注 Arena 分数来自 LMArena
2. 每个榜单文件的首页保留数据快照日期与来源说明
3. 原站 [17nas.com/llm-leaderboard.php](https://17nas.com/llm-leaderboard.php) 标注数据来源

> **注**：LMArena 站点已迁移至 `arena.ai`。本核查基于**数据集许可证**（HF 元数据），
> 未获取到站点 ToS 原文（其帮助中心链接已变更），因此**站点层面的使用条款未逐条核实**。

---

## 三、OpenRouter —— ⚠️ 未见禁止，但未逐条核实

**条款来源**：<https://openrouter.ai/terms>（Last Updated: August 31, 2026）

**核查结果**：通读其 Terms of Service，**未发现**类似 AA 那样「禁止分发平台内容」的表述。
OpenRouter 自身提供公开的模型列表接口（`GET https://openrouter.ai/api/v1/models`），
其定价与上下文长度属于**公开商业信息**。

**但必须诚实说明**：

- 这**不等于**「明确授权再分发」
- 「未找到禁止条款」与「条款允许」是两种不同的证据强度
- 我们**没有**获得 OpenRouter 的书面许可

**当前判断**：保留价格与上下文数据。理由是定价属公开商业信息，且平台自身公开提供 API。
**如 OpenRouter 提出异议，应立即移除相关字段。**

---

## 四、核查方法（可复现）

1. 直接抓取各上游的 Terms of Service / Terms of Use 页面
2. 对条款全文做关键词匹配：`distribute` / `redistribute` / `reproduce` / `scrape` / `commercial` / `license`
3. 对数据集类来源，改用 Hugging Face API 读取 `cardData.license` 元数据
4. 交叉验证：字段级检查公开产物中是否残留受限字段

**字段级校验**（以下命令应返回 0 或空）：

```bash
# 校验仓库中不含 AA 数据
grep -rniE "aa_intelligence|aa_coding|aa_speed|aa_ttft|aa_variants" . --include='*.json' --include='*.md'

# 校验公开 API 输出字段
curl -s https://17nas.com/api/public/llm-leaderboard.php \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print([k for k in d['models'][0] if k.startswith('aa_')])"
```

---

## 五、免责声明

本文件是**工程侧的合规记录**，记录「我们查了什么、依据是什么、做了什么处置」，**不构成法律意见**。

- 条款可能随时变更，本核查反映的是 2026-09-20 的状态
- 涉及商业发布或规模化使用时，请咨询专业法律人士
- 各上游的商标、数据集与内容版权归各自所有

---

*如发现本核查有误或上游条款更新，请开 issue 指出。*

