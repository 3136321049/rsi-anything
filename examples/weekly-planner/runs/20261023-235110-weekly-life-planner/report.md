# RSI run `20261023-235110-weekly-life-planner`

**Goal:** 修改 schedule.json，在 judge/requirements.json 的固定工作、通勤、晚饭之外安排这一周。
所有活动需无冲突、在清醒时段内、满足各任务时长与可用日期，且每天可安排活动不超过 240 分钟。
尽可能完成全部 14 次活动，优先满足权重更高的学习、家人时间与锻炼，同时符合偏好时间。
得分=70%加权任务覆盖+30%加权偏好覆盖。缺少任务会扣分，重复超出次数不合法。
task 为任务 ID；day 为 1..7（周一到周日）；start/end 使用 HH:MM。每轮根据评审报告改善安排。

Agent `codex` · judge `command` · branch `rsi/20261023-235110-weekly-life-planner`

| round | status | score | best | change | why |
|---:|---|---:|---:|---|---|
| 0 | BASELINE | 38.08 | 38.08 | baseline |  |
| 1 | KEEP | 100 | 100 | 补齐缺少的活动并统一安排在偏好时段，提高任务覆盖和偏好覆盖，评审已验证两项均达 100%。 | score 38.08 -> 100 |

Stopped: target 100 reached.

运行状态：finished。调用费用：工具未提供。

[任务配置](config/rsi.yaml) · [模型与运行参数](config/execution.json)

## 产物版本

- 初始产物：[out/metrics.json](artifacts/baseline/files/out/metrics.json) · [out/schedule.html](artifacts/baseline/files/out/schedule.html) · [out/schedule.json](artifacts/baseline/files/out/schedule.json) · [out/schedule.md](artifacts/baseline/files/out/schedule.md) · [schedule.json](artifacts/baseline/files/schedule.json)
- 第 1 轮 · KEEP：[out/metrics.json](rounds/r001/artifacts/files/out/metrics.json) · [out/schedule.html](rounds/r001/artifacts/files/out/schedule.html) · [out/schedule.json](rounds/r001/artifacts/files/out/schedule.json) · [out/schedule.md](rounds/r001/artifacts/files/out/schedule.md) · [schedule.json](rounds/r001/artifacts/files/schedule.json)
- 最终产物：[out/metrics.json](artifacts/final/files/out/metrics.json) · [out/schedule.html](artifacts/final/files/out/schedule.html) · [out/schedule.json](artifacts/final/files/out/schedule.json) · [out/schedule.md](artifacts/final/files/out/schedule.md) · [schedule.json](artifacts/final/files/schedule.json)
