You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
把 post.md 改成一篇能让目标读者停下来、愿意收藏和到店的小红书笔记。
所有事实只能来自 judge/brief.md，不能编造价格、地址、福利或用户评价。

## What you may change
Only these paths (relative to the current directory): `post.md`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
An LLM jury (cli:codex:gpt-5.6-sol) scores the artifact against the rubric in `judge/rubric.yaml` (read it). A higher score must also win a head-to-head comparison against the current best.
Direction: maximize. Current best score: 16.5.

Judge feedback on the current best:
Failed gates on the current best: min_chars, includes:129, excludes:在这个快节奏的时代, excludes:让我们一起, check:笔记中出现的所有价格、时间、数量、设施和福利都与资料一致，没有资料之外的数字、评价或承诺。
failed gates: min_chars, includes:129, excludes:在这个快节奏的时代, excludes:让我们一起, check:笔记中出现的所有价格、时间、数量、设施和福利都与资料一致，没有资料之外的数字、评价或承诺。
hook 1.0/10: 标题和开头都是空泛宣传，没有说中白天忙、只能晚上备考的具体处境。
concrete_value 1.0/10: 没有提供开放时间、价格、隔间设施、夜间饮品或安全措施等任何具体价值。
[cli:codex:gpt-5.6-sol] 围绕「白天上班或上课、只能晚上备考」重写全文，把18:00至次日02:00、129元前50名体验价、独立隔间设施、夜间饮品和安全安排放进具体晚间场景，并以“公众号「夜航自习室」回复「夜间」”收尾。

## Recent rounds (newest last)
- r0 BASELINE score=16.5: (baseline)

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
