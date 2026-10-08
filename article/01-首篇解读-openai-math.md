# [草稿] OpenAI 深夜开源 722 篇 AI 数学论文:我读完目录后,发现了 5 个没人说的细节

> 发布渠道:知乎 / 公众号 / 少数派。文末追踪仓库地址请替换为你的 GitHub 链接。
> 本文所有数字均来自对上游仓库的脚本化解析,可在 openai-math-tracker 仓库中复现。

---

**2026 年 10 月 6 日深夜,OpenAI 没有任何预告地开源了一个仓库:[github.com/openai/math](https://github.com/openai/math)。**

不是模型权重,不是 API,而是 **722 篇由 AI 独立撰写的数学论文**——从 BSD 猜想到希尔伯特第十问题,从推翻 Kaplansky 猜想的反例,到黎曼 zeta 函数的零自由区域。24 小时内,这个仓库冲上 Hacker News 头条(1000+ 赞,近千条评论),GitHub star 破 7000。

我第一时间把整个仓库的元数据全部解析了一遍(解析脚本和数据已开源,见文末)。热点新闻大家都看到了,这里说 **5 个我挖出来的、目前没什么人讨论的细节**。

## 细节一:OpenAI 自己标注了"未经检查"

这是我认为最重要的一点。在仓库的 `lean/formalization.yaml` 里,白纸黑字写着:

```yaml
status:
  scope: "Partial progress."
review:
  status: unchecked
```

README 也承认:"Some of the unformalized results could have issues"(未形式化的结果可能有问题)。

翻译成人话:**这 722 篇论文目前全部是"AI 声称",不是"已证定理"。** 真正附带 Lean 形式化证明的只有 162 篇(22%),而这 162 篇的审查状态也是 unchecked——意思是连"Lean 代码能不能编译通过、证明里有没有偷偷留 `sorry` 占位符",都还没有第三方验证过。

现在网上所有"AI 攻克 XXX 猜想"的标题,准确的说法应该是:"AI 生成了一份声称攻克 XXX 猜想的手稿"。这个差别,决定了接下来几个月整个数学界要干什么。

## 细节二:平均每篇论文只花了 3 小时"思考"

README 里藏着一个惊人的工程数字:绝大部分结果用的是**同一套固定流程**,每个结果平均消耗 **3 小时的 ChatGPT Pro thinking 算力**,总共向模型抛了约 4000 个问题,最终沉淀出 372 个"够格"的结果家族。

也就是说:这不是什么神秘的一次性奇迹,而是一条**可复用的"AI 数学生产线"**——问题进去,手稿出来。OpenAI 开源这个仓库,某种意义上是在展示这条产线的良率:4000 进,372 出。

## 细节三:数学家的"翻车预警"已经开始了

这 722 篇里有大量"反例"型结果——AI 声称推翻了 Kaplansky 零因子猜想、Ryser 覆盖猜想、Borsuk 覆盖断言(9 维!)、Eilenberg–Ganea 猜想等一批经典命题。

**历史上,推翻旧猜想比证明新定理更容易出错。** 已经有数学家开始逐篇检查:[整数乘法快过 n log n 那篇](https://github.com/openai/math/tree/main/preprints/Integer-multiplication-below-n-log-n-September-23-2026)在 HN 上被单独开帖吵了 60 多楼。再叠加一个月前 Scientific American 报道的["学术不端"争议](https://www.scientificamerican.com/article/openai-claims-blockbuster-math-breakthrough-amid-swirl-of-controversy/)(有数学家指控 OpenAI 的模型输出与他们未公开的工作高度重合),这个仓库与其说是"成果展",不如说是**一份为期数月的全球数学界集体作业的试卷**。

谁先查出第一个实质性错误,谁就上头条;谁先确认第一个重量级结果,谁也上头条。这是一场公开的竞赛。

## 细节四:真正适合普通人看的,是那 10 篇"推理摘要"

722 篇论文 99% 的人读不动,但 OpenAI 还放出了 10 篇 **reasoning traces**——模型解题时的(删节版)思考过程,包括:

- π 的无理性指数为什么是 2
- 特征 2 下 Kaplansky 猜想反例是怎么被构造出来的
- 自旋玻璃的 Mézard–Parisi 公式
- 量子 Heisenberg 铁磁体的自发磁化

这些是**历史上第一次,我们能"看到"一个 AI 系统如何做研究级数学**:它先试什么、在哪里卡住、怎么换路。比起证明本身,这可能是这个仓库对大众和 AI 从业者最有价值的部分——它回答的是"AI 到底会不会思考"。

## 细节五:OpenAI 在找"社区托管方"

README 最后一句很容易被忽略:

> We are also exploring community-hosted repositories for these materials.

OpenAI 明确在找社区力量来接管这批材料的整理和验证。这几乎是开源世界送上门的机会:**谁先建起权威的验证追踪,谁就可能成为官方引用的那个入口**——就像当年 huggingface 之于 transformer 模型。

## 所以我做了这个:openai-math-tracker

我把整个仓库解析成了结构化数据,并建了一个**社区验证追踪表**:

- 📊 722 篇手稿 × 372 个家族 × 17 个学科的完整数据库(JSON/CSV,附摘要和 PDF 直链)
- ✅ 每个家族一张验证状态卡:有没有 Lean 形式化、社区检查结论(欢迎 PR 提交你的验证结果,附上证据链接)
- 🔄 每 6 小时自动同步上游更新

仓库地址:**[替换成你的 GitHub 链接]**

如果你懂 Lean,现在最酷的事莫过于亲手编译其中一个形式化证明,把日志贴出来——你可能成为全世界第一个独立验证某个具体结果的人。如果你不懂数学,也可以把这篇转给懂数学的朋友:这 722 篇论文里,大概率藏着未来几年数学界最重要的新闻,无论它们最终被证实还是被推翻。

---

*声明:本文为独立社区项目,与 OpenAI 无关。所有结论以原始仓库和后续同行评审为准。上游内容遵循 Apache-2.0 协议。*

---

## 附:发布 checklist

- [ ] 替换文中 GitHub 链接
- [ ] 配图 1:学科分布条形图(数据在 data/stats.json)
- [ ] 配图 2:VERIFICATION.md 表格截图
- [ ] 知乎/公众号首发后,同步 dev.to / Reddit r/math 英文摘要版
- [ ] HN Show 帖建议在 Lean 审计结果出来后再发(第二波)
