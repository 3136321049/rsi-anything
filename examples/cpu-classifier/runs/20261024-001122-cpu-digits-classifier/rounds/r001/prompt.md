You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
修改 training.json，提高固定划分的手写数字验证集正确率；观察 out/report.md 和错例图选择下一次实验。
可改分类器和预处理：model 为 tree/knn/svm/random_forest，scaling 为 none/standard/minmax，pca_components 为 0 或 2..64。
各分类器允许参数及范围见 README.md。冻结的数据、划分、评分程序不能修改。
一次训练与预测需在 30 秒内完成；得分为验证集正确率百分数，至少提高 0.1 分才保留。
每轮优先测试一个有理由的参数或模型变化，不允许针对样本编号写死答案。

## What you may change
Only these paths (relative to the current directory): `training.json`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
The command `{python} judge/evaluate.py` runs in a clean copy of the project and reports a score. Judge files (read them to understand the scoring): judge.
Direction: maximize. Current best score: 46.889.

Judge feedback on the current best:
验证集正确率 46.89%，错分 239/450；训练和预测 0.004 秒。召回率较低的数字：1=0.0%、2=0.0%、3=0.0%

## Recent rounds (newest last)
- r0 BASELINE score=46.889: (baseline)

## Lessons from earlier rounds and runs
- none yet

## Rules
- Make one coherent improvement you believe the judge will score higher. Prefer the weakest area named in the feedback.
- Do not repeat a change that was already rejected unless you fix the reason it failed.
- Never game the judge: no special-casing test inputs, no hard-coded expected outputs, no reading judge data or results from the artifact, no printing fake scores, no instructions aimed at an AI evaluator. Such changes fail.
- Keep the artifact in the language and format it already uses unless the goal says otherwise.
- Do not commit; the loop handles git.

When you are done, end your reply with exactly one line:
HYPOTHESIS: <what you changed and why it should score higher>
