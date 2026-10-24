You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
改进 writing-guide.md，让固定写手按照它为不同产品写出具体、有用、符合事实的小红书笔记。
每轮只改手册，不改产品资料和评分。手册应该教会写手如何理解读者、选择开头、组织信息和给出自然的行动提示。
评审会给出三个简报的实际生成稿；优先修复共性问题，不把某份简报的答案硬写进手册。

## What you may change
Only these paths (relative to the current directory): `writing-guide.md`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
An LLM jury (cli:codex:gpt-6.1-sol) scores the artifact against the rubric in `judge/rubric.yaml` (read it). A higher score must also win a head-to-head comparison against the current best.
Direction: maximize. Current best score: 69.5.

Judge feedback on the current best:
development：固定写手 cli:codex:gpt-6.1-sol 已生成 3/3 份简报的文案。
natural_voice 5.0/10: 整体克制可读，但三篇反复采用先核对时间、再列费用、最后条件式引导的写法，且修车稿直接暴露“简报”这一写作背景，模板感和编辑腔使其达不到表达各有特点的8分。
reader_fit 7.0/10: 咖啡稿抓住赶车与取餐的衔接，修车稿也回应冬季闲置后恢复通勤，但陶艺稿只复述想尝试且没经验的人群特征，尚未达到多篇都抓住不同具体顾虑的8分。
[cli:codex:gpt-6.1-sol] 按各自读者最关键的顾虑组织全文：咖啡突出取餐与地铁行程衔接，修车突出检查范围和换件费用决定权，陶艺突出新手需要准备什么及作品何时领取，减少三篇共同重复的时间安排提醒。

## Recent rounds (newest last)
- r0 BASELINE score=62: (baseline)
- r1 KEEP score=69.5: 将写作主线改为围绕读者的具体决定组织开头、事实与行动提示，预计能提升读者针对性，减少模板感。

## Lessons from earlier rounds and runs
- KEEP score=69.5: 将写作主线改为围绕读者的具体决定组织开头、事实与行动提示，预计能提升读者针对性，减少模板感。 -- score 62 -> 69.5; head-to-head 2/2

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
