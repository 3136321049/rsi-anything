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
Direction: maximize. Current best score: 74.5.

Judge feedback on the current best:
development：固定写手 cli:codex:gpt-6.1-sol 已生成 3/3 份简报的文案。
reader_fit 7.0/10: 咖啡和自行车稿抓住赶车安排、换件费用等具体顾虑，但陶艺稿优先谈领取时间，对零经验读者如何开始的顾虑回应不足，未达到多篇都切中核心顾虑的8分。
natural_voice 7.0/10: 整体克制且没有空泛赞美，各篇也有不同切口，但反复使用安排时间、先弄清楚和考虑进去等说明式表达，陶艺稿尤其重复，尚未达到8分所需的各有表达。
[cli:codex:gpt-6.1-sol] 重写陶艺稿开头，从零经验读者需要准备什么切入，用已包含材料、工具及提供围裙的事实回应顾虑，并将烧制后约两周领取集中说明一次。

## Recent rounds (newest last)
- r0 BASELINE score=62: (baseline)
- r1 KEEP score=69.5: 将写作主线改为围绕读者的具体决定组织开头、事实与行动提示，预计能提升读者针对性，减少模板感。
- r2 KEEP score=74.5: 让正文顺序和篇幅取决于读者最具体的顾虑，并要求删除通用套句与写作背景，预计能减少模板感，提升读者针对性和表达自然度。
- r3 REVERT score=72: 让写手按读者所处阶段选择首要顾虑，用事实直接回答，并集中交代同一条件，预计能提升读者匹配度、减少说明式套话和重复。 -> score 72 is not better than 74.5 (required margin: 0 or 0%)
- r4 REVERT score=72: 让开头优先用事实回应尝试或使用产品的顾虑，避免过早转向流程条件和泛泛提醒，预计能提升读者匹配度与表达自然度。 -> score 72 is not better than 74.5 (required margin: 0 or 0%)

## Lessons from earlier rounds and runs
- KEEP score=69.5: 将写作主线改为围绕读者的具体决定组织开头、事实与行动提示，预计能提升读者针对性，减少模板感。 -- score 62 -> 69.5; head-to-head 2/2
- KEEP score=74.5: 让正文顺序和篇幅取决于读者最具体的顾虑，并要求删除通用套句与写作背景，预计能减少模板感，提升读者针对性和表达自然度。 -- score 69.5 -> 74.5; head-to-head 2/2
- REVERT score=72: 让写手按读者所处阶段选择首要顾虑，用事实直接回答，并集中交代同一条件，预计能提升读者匹配度、减少说明式套话和重复。 -- score 72 is not better than 74.5 (required margin: 0 or 0%)
- REVERT score=72: 让开头优先用事实回应尝试或使用产品的顾虑，避免过早转向流程条件和泛泛提醒，预计能提升读者匹配度与表达自然度。 -- score 72 is not better than 74.5 (required margin: 0 or 0%)

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
