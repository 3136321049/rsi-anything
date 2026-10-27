# D08：固定资料经营分析

[English](README.en.md)

用 Apple 官方历史财报演示报告逐轮改进：助手修改 `report.md` 和 `charts.json`，程序计算数字与图表，模型评委评价结论、解释和阅读体验。默认初稿由人编写；没有预设后续候选或分数。

## 启动

配置好个人编程助手或个人模型账号后执行：

```sh
rsi init business-report demo-business-report
cd demo-business-report
python3 judge/prepare.py
rsi run --rounds 6
```

准备脚本不联网、不调用模型；实际多轮运行使用个人账号资源。可以用 `rsi run --agent codex --rounds 6` 指定助手，评委在 `rsi.yaml` 中设置。

## 资料与数字

`judge/facts.json` 保存 Apple 官方发布的全年 GAAP 数字、来源和口径说明。正文里的 `{{revenue_2024}}` 等键会被替换成含单位的数值；同比与服务占比实际计算。财年 2023、2024 可以直接写，其余阿拉伯数字需使用资料键。全部键的命名见输入中的 `template_keys`。

`charts.json` 的 `metrics` 可选择一至三个不同指标：`revenue`、`products`、`services`、`operating_income`、`net_income`。图表数据来自冻结资料，助手不能另填数字。

程序核对数字键、引用编号、关键指标和图表选择；模型评委判断论点是否有依据，是否区分营业利润与净利润、季度与全年、事实与推论。提高模型分数后还需赢过旧稿才保留。

## 输出与替换输入

`out/report.html` 和 `out/report.md` 是成稿，`chart-*.mmd` 是 Mermaid 图表，`metrics.json` 是核对用数字；`evaluation.md`、`gates.json`、`notes.txt` 供评审使用。HTML 图形需联网加载 Mermaid 11，离线时正文与同页数据表仍可阅读。`outputs: [out]` 交给主循环保存每轮产物，助手不直接改 `out/`。

换公司或年份时先更新 `judge/facts.json` 的来源、数据、单位与说明，再同步修改准备脚本中的两年口径、初稿、目标和评分细则；保持原指标结构最省事。提交新输入后开新运行，不在一次运行中修改资料。

## 依赖与状态

准备脚本只用 Python 标准库，循环沿用项目的 PyYAML 和模型接口。未接入额外优化框架或公司服务。来源核查日期为 2026-10-23；演示使用保存的历史资料，不是最新财报，不构成投资建议。

已完成真实三轮实验，最终保留分数从 53.5 提高到 74；后两轮候选被拒绝。报告版本、图表与数值核对记录保存在仓库 `examples/business-report/`。分数反映固定资料下的报告评价，不代表投资收益。
