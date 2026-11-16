# D10：围绕一个问题组织资料综述

[English](README.md)

这次实验把两篇认知研究摘要和 UNESCO 指南组织成读书会文章，讨论数字工具怎样改变内容记忆与信息位置记忆。最终稿明确区分实验发现、理论框架、政策要求和作者推论，提出可检验的后续问题，没有把旧检索研究直接当作生成式 AI 效果的证据。

| 版本 | 得分 | 处理结果 |
|---|---:|---|
| 初始 | 61 | 建立基线 |
| 第 1 轮 | 91.5 | 保留；建立中心问题，用认知外包框架串联资料 |
| 第 2 轮 | 68.5 | 拒绝，保留候选全文与原因 |
| 第 3 轮 | 70 | 拒绝，最终仍使用第 1 轮 |

[打开完整实验报告](runs/20261024-000801-cognitive-offloading-review/report.html) · [阅读最终综述与来源映射](runs/20261024-000801-cognitive-offloading-review/artifacts/final/files/out/review.html) · [最终 Markdown](runs/20261024-000801-cognitive-offloading-review/artifacts/final/files/out/review.md) · [核验记录](runs/20261024-000801-cognitive-offloading-review/verification.json)

已阅读最终全文，独立核对五条证据映射都确实出现在正文，引用位于相同段落并覆盖三份资料。导出的五个版本分别重新执行原冻结准备脚本，所有生成文件逐字节一致；浏览器中正文、来源类型和证据映射可以阅读。

第 2、3 轮各有两项评委引文没有通过当时的原文匹配，触发最高 3 分的限制。旧规则可能误判多处原句拼接引用，本次没有保留原始评委 JSON，无法继续确认具体原因。因此这两轮分数不能单独用于判断文章质量下降。全部正式结果保留，未用重评覆盖。

写手和评委都通过个人 Codex 显式请求 `gpt-6.1-sol`、`medium`；实际型号和费用未返回，保持未知。这里展示给定摘要下的文章组织与改写能力，不是系统综述、真实教育实验或独立专家认可。

从项目根目录使用自己的个人 Codex 登录另开实验：

```bash
python3 scripts/run_demo.py literature-review --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

来源为 [Sparrow 等人的记忆实验](https://pubmed.ncbi.nlm.nih.gov/21764755/)、[Risko 与 Gilbert 的认知外包综述](https://pubmed.ncbi.nlm.nih.gov/27542527/) 和 [UNESCO 生成式 AI 教育与研究指南](https://www.unesco.org/en/articles/guidance-generative-ai-education-and-research?hub=387)。本次在 2026-10-24 核对了官方索引；生成时使用的摘要、来源与局限完整冻结在实验记录中。
