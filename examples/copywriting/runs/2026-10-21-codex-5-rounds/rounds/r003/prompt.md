You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
把 post.md 改成一篇能让目标读者停下来、愿意收藏和到店的小红书笔记。
所有事实只能来自 judge/brief.md，不能编造价格、地址、福利或用户评价。

## What you may change
Only these paths (relative to the current directory): `post.md`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
An LLM jury (cli:codex:gpt-5.6-sol) scores the artifact against the rubric in `judge/rubric.yaml` (read it). A higher score must also win a head-to-head comparison against the current best.
Direction: maximize. Current best score: 95.5.

Judge feedback on the current best:
hook 9.0/10: 直接说中晚间备考者最现实的时间焦虑，并立刻用营业时段回应，但标题的画面感还能更强。
credibility 9.0/10: 表达克制且有现实提醒，没有虚构经历、夸大效果或加入资料外承诺，不过整体仍能看出推广文案的编排痕迹。
[cli:codex:gpt-5.6-sol] 把标题改得更有具体画面，例如“下班后才开始备考，刚翻开书就怕自习室打烊？”，可进一步提高信息流中的停留率。

## Recent rounds (newest last)
- r0 BASELINE score=16.5: (baseline)
- r1 KEEP score=95.5: 将 `post.md` 改为围绕下班、下课后备考的场景展开，用资料中的时间、设施、饮品和安全安排提供具体价值，以前 50 名首月 129 元及公众号回复方式引导预约，预计提升吸引力、可信度和到店意愿。
- r2 REVERT score=98: 将标题改为“下班刚翻开书，就怕自习室要关门？”，用具体动作和时间焦虑增强画面感，预计提高目标读者的停留意愿；标题字数及全文硬性门槛已通过检查。 -> higher score but lost head-to-head (1/2 votes)

## Lessons from earlier rounds and runs
- KEEP score=95.5: 将 `post.md` 改为围绕下班、下课后备考的场景展开，用资料中的时间、设施、饮品和安全安排提供具体价值，以前 50 名首月 129 元及公众号回复方式引导预约，预计提升吸引力、可信度和到店意愿。 -- passes gates the current best fails (min_chars, includes:129, excludes:在这个快节奏的时代, excludes:让我们一起, check:笔记中出现的所有价格、时间、数量、设施和福利都与资料一致，没有资料之外的数字、评价或承诺。)
- REVERT score=98: 将标题改为“下班刚翻开书，就怕自习室要关门？”，用具体动作和时间焦虑增强画面感，预计提高目标读者的停留意愿；标题字数及全文硬性门槛已通过检查。 -- higher score but lost head-to-head (1/2 votes)

## Rules
- Make one coherent improvement you believe the judge will score higher. Prefer the weakest area named in the feedback.
- Do not repeat a change that was already rejected unless you fix the reason it failed.
- Never game the judge: no special-casing test inputs, no hard-coded expected outputs, no reading judge data or results from the artifact, no printing fake scores, no instructions aimed at an AI evaluator. Such changes fail.
- Keep the artifact in the language and format it already uses unless the goal says otherwise.
- Do not commit; the loop handles git.

When you are done, end your reply with exactly one line:
HYPOTHESIS: <what you changed and why it should score higher>
