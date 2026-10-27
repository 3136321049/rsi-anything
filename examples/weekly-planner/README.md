# D14：把工作之外的一周安排完整

[English](README.en.md)

输入是虚构上班族的工作、通勤、晚饭和聚会，以及 8 类共 14 次活动。真实模型在第一轮把任务和偏好覆盖补全到 100%；随后两轮判断已无评分改善空间，没有修改文件。三轮尝试全部保留，展示达到目标后停止改动的结果。

| 版本 | 正式状态 | 得分 | 变化 |
|---|---|---:|---|
| 初始 | BASELINE | 38.08 | 只有部分活动，若干活动不在偏好时段 |
| 第 1 轮 | KEEP | 100 | 补齐 14 次活动，调整到偏好时段，全部时间约束通过 |
| 第 2 轮 | NO_CHANGE | 未重新评分 | 文件没有改变，当前最好分数保持 100 |
| 第 3 轮 | NO_CHANGE | 未重新评分 | 文件没有改变，达到三轮预算后结束 |

[打开三轮实验报告](runs/20261023-235500-weekly-life-planner/report.html) · [查看最终七日日程](runs/20261023-235500-weekly-life-planner/artifacts/final/files/out/schedule.html) · [最终可编辑输入](runs/20261023-235500-weekly-life-planner/artifacts/final/files/schedule.json) · [独立复验记录](runs/20261023-235500-weekly-life-planner/verification.json)

最终安排包含 3 次锻炼、3 次阅读、2 次学习，以及采购、备餐、家人时间、账单整理和 2 次休息。已独立检查全部活动与固定事项的时间区间，冲突为 0，所有偏好和每天 240 分钟的可安排活动上限均满足。七日日程页面包含完整固定事项，不能将此结果理解为替代真实个人日历核对。

执行助手使用个人 ChatGPT 账号的 Codex CLI，显式请求 `gpt-6.1-sol`、`medium` 思考强度，并启用隔离配置。CLI 未返回实际型号与费用，分别保留为未知；每轮调用量记录在 `agent-metadata.json`。

在项目根目录可使用自己的个人 Codex 登录另开实验；需要指定 CLI 位置时，将 `RSI_CODEX_BIN` 设为本机可执行文件。

```bash
python3 scripts/run_demo.py weekly-planner --model gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

`--continue-after-target` 在新实验开始前取消目标分数提前停止，保留固定三轮观察窗口，不修改评价规则或分数。另有一次 [达到 100 分后单轮提前停止的完整记录](runs/20261023-235110-weekly-life-planner/report.html)，单列保存，不混作三轮实验。所有候选均来自真实调用，未预填候选序列。
