# D14：安排工作之外的一周

[English](README.md)

输入是一名普通上班族的固定工作、通勤、晚饭与聚会，以及 8 类共 14 次可安排活动。初稿已经安排部分活动，但次数不足，有些时间不符合偏好。AI 只修改 `schedule.json`，逐步补全并调整。

```bash
rsi init weekly-planner my-week
cd my-week
python judge/evaluate.py
rsi check
rsi run --agent codex --rounds 6
```

`out/schedule.html` 是可在浏览器打开的七日日程，`out/schedule.md` 是文字版本，`out/schedule.json` 包含固定安排与候选安排，`out/metrics.json` 记录评分和具体问题。配置中的 `outputs: [out]` 供引擎保存每轮产物，便于比较安排变化。

评分前检查格式、时间冲突、清醒时间、允许日期、单次时长、次数上限与每天最多 240 分钟的活动。固定事项不能挪动，相邻事项的结束与开始可以相同。得分为 70 分的加权任务覆盖，加上 30 分的加权偏好覆盖；每类活动按所需次数封顶。少排活动可继续优化，多排重复活动不能刷分。空日程虽没有冲突，但得分为零。

替换输入：在开始新实验前编辑 `judge/requirements.json`，修改 `fixed`、`tasks`、`awake` 等，再提交。每个任务写清 `id`、名称、次数、分钟数、权重、允许星期和偏好时间窗口。`schedule.json` 使用 `sessions` 数组，每项如 `{"task":"exercise","day":1,"start":"07:00","end":"07:45"}`；星期 1–7 表示周一到周日，不跨午夜。当前按单周本地钟表时间评审，不处理日期、时区或夏令时转换。

数据为本项目编写的虚构生活需求，不访问个人日历。只用 Python 3.9+ 标准库，无额外依赖或服务费用。`judge/evaluate.py` 使用 [datetime.strptime](https://docs.python.org/3/library/datetime.html) 验证时间和 [html.escape](https://docs.python.org/3/library/html.html) 生成可读页面；官方资料查阅日期为 2026-10-23。当前规模直接逐项检查即可，没有引入额外排程求解器。

基线与验收器测试不代表真实模型完成了多轮规划。模型实验需另存 `examples/weekly-planner/runs/`，保留完整记录。
