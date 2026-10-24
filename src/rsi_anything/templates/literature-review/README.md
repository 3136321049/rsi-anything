# D10：给定资料综述

围绕“数字工具怎样改变记忆内容与信息位置”，将两篇真实研究和 UNESCO 指南的摘要组织成读书会综述。助手修改 `review.md` 与 `evidence.json`，改善中心问题、证据组织和研究局限。默认初稿由人编写，没有预设后续候选或分数。

## 启动

配置好个人编程助手或个人模型账号后执行：

```sh
rsi init literature-review demo-literature-review
cd demo-literature-review
python3 judge/prepare.py
rsi run --rounds 6
```

准备脚本不联网、不调用模型；实际多轮运行使用个人账号资源。可以用 `rsi run --agent codex --rounds 6` 指定助手，评委在 `rsi.yaml` 中设置。

## 引用与评价

冻结的 `judge/sources.json` 包含来源标题、作者、年份、证据类型、摘要、局限及准确链接。摘要均由项目作者改写，不是原文引语。正文用 `[S1]`、`[S2]`、`[S3]` 引用。

`evidence.json` 的 `claims` 列表至少包含三条不同的正文原句，每条 `sources` 是相关来源编号，引用须与原句在同一段。程序检查编号、正文原句、引用位置和覆盖情况；模型检查来源是否支持相邻论断、实验与综述及政策是否混淆。不能把旧检索研究当成生成式 AI 效果的直接证明。

## 输出与替换输入

`out/review.html`、`review.md` 保存正文及来源，`source-map.json` 保存逐条证据映射；另有评审用的 `evaluation.md`、`gates.json` 和 `notes.txt`。HTML 可离线阅读。`outputs: [out]` 交给主循环保存每轮产物，助手不直接修改 `out/`。

换主题时先更新 `judge/sources.json` 的来源与摘要，再修改初稿、证据映射、目标和评分细则；资料数量变化时同步修改准备脚本中的最低映射条数。先提交新输入再开新运行。资料无法回答的问题应保留为研究问题，不能补造文献、数字或引语。

## 依赖与状态

准备脚本只用 Python 标准库，循环沿用项目的 PyYAML 和模型接口。未接入文献搜索服务或额外优化框架。来源核查日期为 2026-10-23，运行只使用保存的摘要。

已完成真实三轮实验，最终保留分数从 61 提高到 91.5；后两轮候选被拒绝。综述版本、来源映射及独立复验记录保存在仓库 `examples/literature-review/`。评价限于给定资料与本例规则。
