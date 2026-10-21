You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
把 post.md 改成一篇能让目标读者停下来、愿意收藏和到店的小红书笔记。
所有事实只能来自 judge/brief.md，不能编造价格、地址、福利或用户评价。

## What you may change
Only these paths (relative to the current directory): `post.md`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
An LLM jury (cli:codex:gpt-5.6-sol) scores the artifact against the rubric in `judge/rubric.yaml` (read it). A higher score must also win a head-to-head comparison against the current best.
Direction: maximize. Current best score: 96.

Judge feedback on the current best:
hook 9.0/10: 直接点中只能晚上备考的处境，并用营业时间问题制造继续阅读的理由。
platform_fit 9.0/10: 短段落、小标题和表情使用适度，并配有5个相关话题标签，手机阅读层次清楚。
[cli:codex:gpt-5.6-sol] 把标题进一步压缩成更有画面感的一句话，例如“下班才开始备考的人，终于不用刚翻开书就赶打烊”，会更直接地放大目标读者的真实痛点。

## Recent rounds (newest last)
- r0 BASELINE score=16.5: (baseline)
- r1 KEEP score=95.5: 将 `post.md` 改为围绕下班、下课后备考的场景展开，用资料中的时间、设施、饮品和安全安排提供具体价值，以前 50 名首月 129 元及公众号回复方式引导预约，预计提升吸引力、可信度和到店意愿。
- r2 REVERT score=98: 将标题改为“下班刚翻开书，就怕自习室要关门？”，用具体动作和时间焦虑增强画面感，预计提高目标读者的停留意愿；标题字数及全文硬性门槛已通过检查。 -> higher score but lost head-to-head (1/2 votes)
- r3 KEEP score=96: 调整收尾，去掉重复促销，把收藏与核对时间、路程联系起来，集中呈现体验价和领取方式，预计提升可信度与行动意愿；字数、标题和禁词检查通过。
- r4 REVERT score=95.5: 仅将标题改为“下班才翻开书？这里能学到凌晨2点”，用具体画面和资料中的可用时段同时呈现处境与价值，预计提升停留意愿；字数、必含词和禁词检查通过。 -> score 95.5 is not better than 96 (required margin: 0 or 0%)

## Lessons from earlier rounds and runs
- KEEP score=95.5: 将 `post.md` 改为围绕下班、下课后备考的场景展开，用资料中的时间、设施、饮品和安全安排提供具体价值，以前 50 名首月 129 元及公众号回复方式引导预约，预计提升吸引力、可信度和到店意愿。 -- passes gates the current best fails (min_chars, includes:129, excludes:在这个快节奏的时代, excludes:让我们一起, check:笔记中出现的所有价格、时间、数量、设施和福利都与资料一致，没有资料之外的数字、评价或承诺。)
- REVERT score=98: 将标题改为“下班刚翻开书，就怕自习室要关门？”，用具体动作和时间焦虑增强画面感，预计提高目标读者的停留意愿；标题字数及全文硬性门槛已通过检查。 -- higher score but lost head-to-head (1/2 votes)
- KEEP score=96: 调整收尾，去掉重复促销，把收藏与核对时间、路程联系起来，集中呈现体验价和领取方式，预计提升可信度与行动意愿；字数、标题和禁词检查通过。 -- score 95.5 -> 96; head-to-head 2/2
- REVERT score=95.5: 仅将标题改为“下班才翻开书？这里能学到凌晨2点”，用具体画面和资料中的可用时段同时呈现处境与价值，预计提升停留意愿；字数、必含词和禁词检查通过。 -- score 95.5 is not better than 96 (required margin: 0 or 0%)

## Rules
- Make one coherent improvement you believe the judge will score higher. Prefer the weakest area named in the feedback.
- Do not repeat a change that was already rejected unless you fix the reason it failed.
- Never game the judge: no special-casing test inputs, no hard-coded expected outputs, no reading judge data or results from the artifact, no printing fake scores, no instructions aimed at an AI evaluator. Such changes fail.
- Keep the artifact in the language and format it already uses unless the goal says otherwise.
- Do not commit; the loop handles git.

When you are done, end your reply with exactly one line:
HYPOTHESIS: <what you changed and why it should score higher>
