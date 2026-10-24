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
Direction: maximize. Current best score: 30.

Judge feedback on the current best:
development：固定写手 cli:codex:gpt-6.1-sol 已生成 3/3 份简报的文案。
reader_fit 3.0/10: 三篇都点明了目标人群，但主要复述简报中的身份和处境，尚未进一步抓住赶时间、担心额外维修费用或初学准备等具体顾虑，未达到多篇都有具体切入的8分水平。
useful_structure 3.0/10: 三篇都交代了安排、费用和使用方式，维修与陶艺尤其明确了限制，但咖啡稿重复取杯步骤、陶艺稿增加“留出完整的上课时间”等低信息量提醒，距离8分所要求的决策顺序和信息效率仍有差距。
[cli:codex:gpt-6.1-sol] 删除三篇自行补写的行动入口，仅用简报已有信息提示下一步，例如先确定取餐时段、整点或半点的检查时间，以及能否接受约两周后领取作品。

## Recent rounds (newest last)
- r0 BASELINE score=30: (baseline)
- r1 REVERT score=30: 将产品特点罗列改为围绕读者具体顾虑组织事实，减少重复和无依据的行动提示，预计能提高读者匹配与信息组织得分。 -> score 30 is not better than 30 (required margin: 0 or 0%)
- r2 REVERT score=30: 用可执行的事实与读者问题配对、首段作答和逐段检查，替代泛泛的写作要求，预计能改善开头的具体程度和正文的信息效率。 -> score 30 is not better than 30 (required margin: 0 or 0%)

## Lessons from earlier rounds and runs
- REVERT score=30: 将产品特点罗列改为围绕读者具体顾虑组织事实，减少重复和无依据的行动提示，预计能提高读者匹配与信息组织得分。 -- score 30 is not better than 30 (required margin: 0 or 0%)
- REVERT score=30: 用可执行的事实与读者问题配对、首段作答和逐段检查，替代泛泛的写作要求，预计能改善开头的具体程度和正文的信息效率。 -- score 30 is not better than 30 (required margin: 0 or 0%)

## Rules
- Make one coherent improvement you believe the judge will score higher. Prefer the weakest area named in the feedback.
- Do not repeat a change that was already rejected unless you fix the reason it failed.
- Never game the judge: no special-casing test inputs, no hard-coded expected outputs, no reading judge data or results from the artifact, no printing fake scores, no instructions aimed at an AI evaluator. Such changes fail.
- Keep the artifact in the language and format it already uses unless the goal says otherwise.
- Do not commit; the loop handles git.

When you are done, end your reply with exactly one line:
HYPOTHESIS: <what you changed and why it should score higher>
