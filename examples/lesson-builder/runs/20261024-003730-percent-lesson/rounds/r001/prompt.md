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
Direction: maximize. Current best score: 20.

Judge feedback on the current best:
P2（还原原量）：回答None；正确值90；原句依据找到；可以确定72元是原价的80%，但讲义只讲了已知整体后用乘法求部分，没有讲已知部分和比例怎样反求整体。
P3（增长率）：回答None；正确值25；原句依据找到；人数增加了50-40=10人，但讲义没有说明增长率应以哪个量为整体，也没有讲怎样根据增加量和原人数求增长率。
P4（减少率）：回答None；正确值20；原句依据找到；人数减少了125-100=25人，但讲义没有讲怎样根据减少量和原人数求减少率。
P6（百分点）：回答None；正确值12；原句依据找到；讲义没有解释“百分点”的含义，也没有提供计算百分点变化的方法。
P7（变化后还原）：回答None；正确值24；原句依据找到；取出25%后剩下的是原有重量的75%，但讲义只讲了已知整体求部分，没有讲已知剩余部分和比例怎样反求原有重量。
P8（整体变化）：回答None；正确值34；原句依据找到；按讲义可算出甲班参加合唱的有30×0.4=12人，乙班有20×0.25=5人，合计17人、总人数50人；但讲义没有讲怎样由部分人数和总人数反求百分比。
P9（反向变化率）：回答None；正确值25；原句依据找到；可以把原来的数设为一个整体，并算出减少后剩下原来的80%，但讲义没有讲以减少后的数量为新整体时，怎样反求恢复所需的增长百分比。
P10（比例与部分）：回答None；正确值9；原句依据找到；按讲义可算出糖有150×0.12=18克，加水后总重为200克；但讲义没有讲怎样由糖的重量和新的总重量反求糖所占的百分比。

## Recent rounds (newest last)
- r0 BASELINE score=20: (baseline)

## Lessons from earlier rounds and runs
- none yet

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
