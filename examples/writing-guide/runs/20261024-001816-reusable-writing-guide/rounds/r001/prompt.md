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
Direction: maximize. Current best score: 62.

Judge feedback on the current best:
development：固定写手 cli:codex:gpt-6.1-sol 已生成 3/3 份简报的文案。
natural_voice 5.0/10: 整体可读且没有夸张赞美，但三篇开头都使用“可以了解一下”引出产品，结尾又重复了解详情的表达，模板感明显，未达到下一档应有的表达变化。
reader_fit 6.0/10: 三篇都点明了各自人群和基本场景，但主要复述读者标签，没有进一步回应赶车时如何安排取杯、恢复骑行担心什么、零基础参与有哪些顾虑，尚未达到8分的具体程度。
[cli:codex:gpt-6.1-sol] 把三篇统一的“读者标签＋可以了解一下产品”开头改成各自最影响决策的具体问题，并立即用已有事实回应：赶地铁如何安排取杯、旧车检查是否另收配件费、首次陶艺需要准备什么。

## Recent rounds (newest last)
- r0 BASELINE score=62: (baseline)

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
