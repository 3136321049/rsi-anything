You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
修改 lesson.md，为初中学生解释百分比、变化率、还原原量、连续变化和百分点的区别。
可以调整结构、例题与逐步解释，遵循 judge/brief.md；不要逐题抄写 judge/exercises.json 的测试题答案。
评分时受限学生模型只看到讲义和题目，需给答案、推理及讲义原句依据；程序按固定答案实际判分。

## What you may change
Only these paths (relative to the current directory): `lesson.md`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
The command `{python} judge/evaluate.py` runs in a clean copy of the project and reports a score. Judge files (read them to understand the scoring): judge.
Direction: maximize. Current best score: 100.

Judge feedback on the current best:
固定练习全部答对且提供讲义原句依据。

## Recent rounds (newest last)
- r0 BASELINE score=20: (baseline)
- r1 KEEP score=100: 围绕“部分＝整体×比例”补齐逆向求解和整体变化的判断方法，应能减少因讲义缺少方法而无法作答的情况，提高得分。
- r2 REVERT score=100: 补清“各步倍数连乘后与1比较”的方法，减少连续变化中误加减百分比的错误，提高作答稳定性。 -> score 100 is not better than 100 (required margin: 1 or 0%)

## Lessons from earlier rounds and runs
- KEEP score=100: 围绕“部分＝整体×比例”补齐逆向求解和整体变化的判断方法，应能减少因讲义缺少方法而无法作答的情况，提高得分。 -- score 20 -> 100
- REVERT score=100: 补清“各步倍数连乘后与1比较”的方法，减少连续变化中误加减百分比的错误，提高作答稳定性。 -- score 100 is not better than 100 (required margin: 1 or 0%)

## Rules
- Make one coherent improvement you believe the judge will score higher. Prefer the weakest area named in the feedback.
- Do not repeat a change that was already rejected unless you fix the reason it failed.
- Never game the judge: no special-casing test inputs, no hard-coded expected outputs, no reading judge data or results from the artifact, no printing fake scores, no instructions aimed at an AI evaluator. Such changes fail.
- Keep the artifact in the language and format it already uses unless the goal says otherwise.
- Do not commit; the loop handles git.
- The loop runs the judge after you finish. Do not start extra model calls, model-backed evaluators,
  video generation, or paid/network services yourself. Local syntax and unit checks are fine.

When you are done, end your reply with exactly one line:
HYPOTHESIS: <what you changed and why it should score higher>
