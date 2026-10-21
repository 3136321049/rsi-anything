---
name: "2026人形机器人核心零部件（谐波减速器与行星滚柱丝杠）商业化拐点深度研报"
track: finance
direction: maximize
target_score: 92.0
max_iterations: 6
eval_cmd: "python3 eval_report.py"
mutable_paths: ["report.md"]
frozen_paths:
  - eval_report.py
  - rubric.yaml
  - sources/verified_sources.json
upstream_credits:
  - karpathy/autoresearch
  - stanford-oval/storm
  - assafelovic/gpt-researcher
  - Future-House/paper-qa
---

# 金融深度研报棘轮

只改 `report.md`。`eval_report.py`、`rubric.yaml` 和 `sources/verified_sources.json` 在开跑前做 SHA-256 快照，改动会触发 `REVERT_GUARD`。

裁判是冻结的机构研报量表：至少 12 条已核验 `[SRC-xx]`、零空话、必须有看空章节、必须有毛利率/产能对照表，且份额列加总为 100。变好且过门禁才 `KEEP`，否则回滚到冠军稿。

演示从 58 分的空话底稿走到 94.5 分的冠军稿，中间有一次假引用回滚和一次篡改量表被守卫拦住。在本目录运行：

```bash
python3 run_demo.py
```
