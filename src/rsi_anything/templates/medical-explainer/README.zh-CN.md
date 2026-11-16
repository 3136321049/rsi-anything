# D12：成人身体活动科普

[English](README.md)

把 WHO 公开指南转成一般健康成人看得懂的说明，演示从资料摘抄到准确、易读、有实际帮助的文章。助手只改 `explainer.md`。默认初稿由人编写，没有预设后续候选或分数。

## 启动

配置好个人编程助手或个人模型账号后执行：

```sh
rsi init medical-explainer demo-medical-explainer
cd demo-medical-explainer
python3 judge/prepare.py
rsi run --rounds 6
```

准备脚本不联网、不调用模型；实际多轮运行使用个人账号资源。可以用 `rsi run --agent codex --rounds 6` 指定助手，评委在 `rsi.yaml` 中设置。

## 来源与评价

冻结的 `judge/sources.json` 保存 WHO 来源、作者改写的简短摘要和用途边界。关键数量通过 `{{adult_age}}`、`{{moderate_minutes}}`、`{{vigorous_minutes}}`、`{{strength_days}}` 插值，来源标记为 `[W1]`、`[W2]`。不要另写阿拉伯数字。

程序检查数量、来源、少量起步与久坐说明、科普用途和部分明显违规表达。模型评委另行判断是否准确转述、是否过度承诺、是否给出了个体化医疗指令，并评价普通读者能否理解及开始行动。免责声明本身不会得到高分。

## 输出与替换输入

`out/explainer.html`、`explainer.md` 是可读成稿，`checklist.json` 保存数量和检查清单；另有评审用的 `evaluation.md`、`gates.json` 和 `notes.txt`。HTML 可离线阅读。`outputs: [out]` 交给主循环保存每轮产物，助手不直接改 `out/`。

换科普主题时，需要先由人核对权威来源、数量和适用人群，再同步修改输入、准备脚本、目标、初稿与评分细则。只换标题不能完成主题迁移。此包不接收病历，不制定患者的诊疗或个人训练方案。

## 依赖与状态

准备脚本只用 Python 标准库，循环沿用项目的 PyYAML 和模型接口。未接入额外医疗服务、模型或公司资源。官方来源核查日期为 2026-10-23，运行按保存的资料快照执行。

已完成真实三轮实验，最终保留分数从 58.5 提高到 80；后两轮候选被拒绝。科普文本、来源、数量核对与复验记录保存在仓库 `examples/medical-explainer/`。该结果只说明给定资料下的科普表达，不构成临床有效性判断。
