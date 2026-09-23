# 发布到 Hugging Face Datasets

本目录的数据可以自动同步一份到 Hugging Face —— 那里是 ML 使用者找数据集的地方，
且能直接用 `datasets.load_dataset()` 读取。

**当前状态：代码已就绪，等你配一次 token 就会自动跑。** 未配置时该步骤自动跳过，
不影响每日更新。

---

## 一、你只需要做一次（约 5 分钟）

### 1. 注册 Hugging Face 账号

https://huggingface.co/join

> 实测 `AmigaMeow` 这个用户名**还没被占用**（2026-09-24 查）。
> 用户名会出现在数据集地址里，所以建议就用它。

### 2. 建一个**写权限**的 token

Settings → Access Tokens → **New token** → 类型选 **Write**
（只读 token 不能上传）。

建好后**只显示一次**，先复制下来。

### 3. 在 GitHub 仓库里加 Secret

仓库 → Settings → Secrets and variables → Actions → **New repository secret**

| 名称 | 值 |
|---|---|
| `HF_TOKEN` | 刚才那个写权限 token |

### 4.（可选）改数据集仓库名

默认发布到 `AmigaMeow/llm-leaderboard`。想换名字就加一个 **repository variable**：

Actions → Variables → New repository variable

| 名称 | 值 |
|---|---|
| `HF_DATASET_REPO` | `<你的用户名>/<数据集名>` |

---

## 二、配好之后会发生什么

每日的 `Daily Update` 工作流在最后多跑一步：

```
- name: Publish to Hugging Face
  if: env.HF_TOKEN != ''
  run: |
    pip install --quiet huggingface_hub
    python3 scripts/publish_hf.py --repo "<HF_DATASET_REPO>"
```

**首次运行会自动创建数据集仓库**（`exist_ok=True`），不需要你先去建。

想立刻跑一次：Actions → Daily Update → **Run workflow**。

---

## 三、本地手动跑（不上传）

```bash
# 只构建到 .hf-build/，看看会发布什么
python3 scripts/publish_hf.py --dry-run

# 构建并上传（需要 HF_TOKEN 环境变量）
HF_TOKEN=hf_xxx python3 scripts/publish_hf.py --repo AmigaMeow/llm-leaderboard
```

---

## 四、会发布什么

| 路径 | 内容 |
|---|---|
| `README.md` | 数据集卡片（含 YAML frontmatter：license / language / tags / configs） |
| `data/models.jsonl` | **推荐入口**：一行一个模型，可直接 `load_dataset` |
| `data/latest.json` | 最近快照的原始结构（含 sources 元信息） |
| `data/history/YYYY-MM-DD.json` | 按天归档的历史快照 |

`models.jsonl` 相比原始快照额外带上：

- `blended_price` —— `(3 × price_in + price_out) / 4`，**输入:输出 = 3:1 的假设**，
  按自己负载调整；卡片里已注明
- `snapshot_date` / `snapshot_generated_at` —— 本行所属快照
- `lmarena_publish_date` —— **上游 Arena 榜的发布日期**（与抓取日期是两回事，
  上游可能长期不更新，见仓库 README 的说明）

---

## 五、许可与归属（⚠️ 需要你确认的一项）

数据集卡片声明的是 **`license: cc-by-4.0`**，取舍如下：

| 来源 | 情况 |
|---|---|
| **LMArena** | CC-BY-4.0 —— 要求署名，我们已在卡片与本仓库署名 |
| **OpenRouter 定价** | 公开 API；未找到明文条款 |
| **Artificial Analysis** | **刻意不纳入** —— 其条款禁止再分发 |

**为什么选 CC-BY-4.0 而不是仓库代码的 MIT**：
本数据集是从 LMArena 的 CC-BY-4.0 材料派生的，声明为同款许可最稳妥、也最清晰。
如果你希望改用别的许可（例如 MIT + 单独署名声明），改 `scripts/publish_hf.py` 里
卡片模板的 `license` 字段即可 —— **但这是许可决策，建议你确认后再改。**

---

## 六、怎么验证成功

1. Actions 里那一步是**绿色**（不是 skipped）
2. 打开 `https://huggingface.co/datasets/<你的用户名>/<数据集名>` —— 应能看到卡片与文件
3. 本地跑一次 `load_dataset`：

```python
from datasets import load_dataset
ds = load_dataset("<你的用户名>/<数据集名>", "models", split="train")
print(ds[0])
```

---

## 七、出问题怎么查

| 症状 | 可能原因 |
|---|---|
| 那一步显示 **skipped** | `HF_TOKEN` secret 没配好（或名字拼错） |
| `401 Unauthorized` | token 不是 **Write** 类型，或已失效 |
| `403 Forbidden` | token 属于另一个账号，无权写目标仓库 |
| 卡片报 YAML 错 | 改卡片模板后 frontmatter 被破坏 —— 用任意 YAML 解析器过一遍 |
