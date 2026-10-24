You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
修改 schedule.json，在 judge/requirements.json 的固定工作、通勤、晚饭之外安排这一周。
所有活动需无冲突、在清醒时段内、满足各任务时长与可用日期，且每天可安排活动不超过 240 分钟。
尽可能完成全部 14 次活动，优先满足权重更高的学习、家人时间与锻炼，同时符合偏好时间。
得分=70%加权任务覆盖+30%加权偏好覆盖。缺少任务会扣分，重复超出次数不合法。
task 为任务 ID；day 为 1..7（周一到周日）；start/end 使用 HH:MM。每轮根据评审报告改善安排。

## What you may change
Only these paths (relative to the current directory): `schedule.json`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
The command `{python} judge/evaluate.py` runs in a clean copy of the project and reports a score. Judge files (read them to understand the scoring): judge.
Direction: maximize. Current best score: 100.

Judge feedback on the current best:
任务覆盖 100.0%，偏好覆盖 100.0%。
固定约束、任务次数和偏好全部满足。

## Recent rounds (newest last)
- r0 BASELINE score=38.08: (baseline)
- r1 KEEP score=100: 补齐缺失活动并统一安排到偏好时段，同时满足冲突、时长和每日上限约束，提高任务覆盖与偏好覆盖得分。
- r2 NO_CHANGE score=-: 当前安排已达到评分上限，不存在能进一步提高得分的修改。 -> no edits inside the artifact paths

## Lessons from earlier rounds and runs
- KEEP score=100: 补齐缺失活动并统一安排到偏好时段，同时满足冲突、时长和每日上限约束，提高任务覆盖与偏好覆盖得分。 -- score 38.08 -> 100
- NO_CHANGE score=-: 当前安排已达到评分上限，不存在能进一步提高得分的修改。 -- no edits inside the artifact paths

## Rules
- Make one coherent improvement you believe the judge will score higher. Prefer the weakest area named in the feedback.
- Do not repeat a change that was already rejected unless you fix the reason it failed.
- Never game the judge: no special-casing test inputs, no hard-coded expected outputs, no reading judge data or results from the artifact, no printing fake scores, no instructions aimed at an AI evaluator. Such changes fail.
- Keep the artifact in the language and format it already uses unless the goal says otherwise.
- Do not commit; the loop handles git.

When you are done, end your reply with exactly one line:
HYPOTHESIS: <what you changed and why it should score higher>
