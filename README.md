# openai-math-tracker

**OpenAI 722 篇 AI 数学手稿的结构化目录与社区验证追踪** · *A structured catalog & community verification tracker for the [openai/math](https://github.com/openai/math) manuscript collection.*

> 独立社区项目,与 OpenAI 无关。上游内容 Apache-2.0 © OpenAI。
> Independent community project, not affiliated with OpenAI. Upstream content Apache-2.0 © OpenAI.

[English](#english) · [中文](#中文)

---

## 中文

### 这是什么

2026-10-06,OpenAI 开源了 [openai/math](https://github.com/openai/math):由其**内部未发布模型**生成的数学手稿集。本仓库把它变成**可查询的数据 + 可协作的验证追踪**:

- 📊 **结构化数据库**:722 篇手稿 × 372 个结果家族 × 17 个学科,全部解析成 [JSON](data/catalog.json) / [CSV](data/manuscripts.csv)
- ✅ **验证状态追踪**:[docs/VERIFICATION.md](docs/VERIFICATION.md) —— 每个家族:有没有 Lean 形式化?社区独立检查结论是什么?
- 🔄 **可复现**:`scripts/` 一键从上游同步并重建全部数据

### 关键数字(同步自上游 `adc7f1241b42`)

| 指标 | 数值 |
|---|---|
| 手稿总数 | **722** |
| 结果家族 | **372** |
| 学科 | 17(数论 31 · 代数与复几何 36 · TCS 40 · 组合 37 · 概率与统计力学 29 · 微分几何 29 · …) |
| 有 Lean 形式化的手稿 | **162**(22%) |
| Lean 主定理声明 | 185 条 |
| **上游自报的审查状态** | **`unchecked`**(形式化范围:*Partial progress*) |
| 公开的推理过程摘要 | 10 篇 |

⚠️ **冷静一下**:上游 `formalization.yaml` 明确写着 `review: unchecked`、"Not all have accompanying Lean formalizations"、"Some of the unformalized results could have issues"。**"AI 生成了论文" ≠ "定理为真"**。这正是本仓库存在的意义。

### 十个值得先看的家族

| # | 结果 | 为什么重要 | Lean |
|---|---|---|---|
| 003 | 拟黎曼猜想 (Quasi-Riemann hypothesis) | 黎曼猜想相关,含 Comparator 验证配置 | 2/3 |
| 002 | 低 Selmer 余秩下的完整 BSD 公式 | 千禧难题 BSD 猜想的重大部分结果 | — |
| 004 | ℚ 上的希尔伯特第十问题 | 百年级开放问题 | — |
| 017 | π 的无理性指数 = 2 | 附公开推理摘要 | — |
| 032 | CM 阿贝尔簇的有理 Hodge 猜想 | 千禧难题 Hodge 猜想的重要情形 | — |
| 109 | 整数乘法快过 n log n | [HN 上已吵了 60+ 楼](https://news.ycombinator.com/item?id=49985524) | — |
| 196/197 | Kaplansky 零因子/直接有限性猜想反例 | 直接推翻经典猜想,197 已部分形式化 | 1/1 |
| 254 | Artin 群 K(π,1) 猜想 | 群论著名难题 | 2/3 |
| 338 | Yau 单值化猜想 | 微分几何顶级猜想 | — |
| 376 | 受迫 Navier–Stokes 流中的通用计算 | 与此前的署名争议直接相关 | — |

完整清单见 [docs/VERIFICATION.md](docs/VERIFICATION.md)。

### 如何贡献验证结果

1. 挑一个家族,读论文或编译其 Lean 代码(方法见[下方](#复现上游的-lean-验证))
2. PR 修改 [data/verification_overrides.json](data/verification_overrides.json),填 `status`(confirmed / partial / issue-found / refuted)+ `evidence`(证据链接)
3. CI 会自动重新生成追踪表

**最稀缺的贡献**:实际运行上游的 Lean 验证并公布日志 —— 目前全世界几乎没人做过。

### 复现上游的 Lean 验证

```bash
git clone https://github.com/openai/math.git && cd math/lean
lake update && lake exe cache get
# 验证单个结果(需先装 comparator / landrun / lean4export):
lake env comparator ComparatorChallenges/QuasiRiemannHypothesis.json
# 全库编译审计(注意:官方提示内存映射可能爆炸,见 lean/README.md):
lake build
```

注意:上游自己建议"一次只编译一小部分";全量编译在 Linux 上可能需要 `-DMMAP=OFF`。

### 数据更新

```bash
scripts/fetch_upstream.sh      # 从 GitHub API 同步上游最新文件
python3 scripts/build_catalog.py  # 重建 catalog.json / CSV / VERIFICATION.md
```

---

## English

### What this is

On 2026-10-06 OpenAI released [openai/math](https://github.com/openai/math): **722 AI-generated mathematical manuscripts** (372 result families, 17 disciplines) produced by an unreleased internal model, partially formalized in Lean. This repo turns it into **queryable data + a collaborative verification tracker**:

- 📊 **Structured data**: every manuscript parsed into [JSON](data/catalog.json) / [CSV](data/manuscripts.csv) with discipline, abstract, PDF link, formalization flag
- ✅ **Verification tracker**: [docs/VERIFICATION.md](docs/VERIFICATION.md) — per-family Lean coverage and independent community check status
- 🔄 **Reproducible**: `scripts/fetch_upstream.sh` + `scripts/build_catalog.py` rebuild everything from upstream

### Headline facts

- 722 manuscripts / 372 families / 17 disciplines
- 162 manuscripts (22%) have Lean formalizations; 185 main-result declarations
- **Upstream self-reported review status: `unchecked`**, scope *"Partial progress"* — treat every result as an unverified claim until checked
- 10 abridged reasoning traces released (π irrationality exponent, Mézard–Parisi formula, Kaplansky characteristic-two counterexample, …)

### Contribute a verification

Read a paper or build its Lean code, then PR [data/verification_overrides.json](data/verification_overrides.json) with `status` + `evidence` link. CI regenerates the tracker table. The scarcest contribution right now: **actually running the upstream Lean builds and publishing the logs**.

### License

Tracker code & generated data: Apache-2.0. Upstream manuscripts and Lean code: Apache-2.0 © OpenAI — see [data/README-upstream.md](data/README-upstream.md). Cite individual manuscripts using the BibTeX block in their upstream directories.
