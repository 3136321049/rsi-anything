You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
为教育研究读书会写一篇关于“数字工具怎样改变我们记忆信息与信息位置”的中文资料综述。
修改 review.md 和 evidence.json，只使用 judge/sources.json 的三份摘要。
围绕一个问题综合比较实验、理论综述和政策建议，分清支持的结论与仍需研究的假设。
每个来源使用 [S1] 等引用；evidence.json 中 claim 必须是正文的一句原话，sources 对应来源编号。
至少三条证据映射并覆盖三个来源，不能把旧检索研究写成生成式AI的直接效果证明。

## What you may change
Only these paths (relative to the current directory): `review.md`, `evidence.json`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
An LLM jury (cli:codex:gpt-6.1-sol) scores the artifact against the rubric in `judge/rubric.yaml` (read it). A higher score must also win a head-to-head comparison against the current best.
Direction: maximize. Current best score: 61.

Judge feedback on the current best:
程序核对真实来源编号、引用位置和正文映射；来源是否真正支持论断、证据类型是否混淆由模型评委判断。
question 5.0/10: 结尾提出了可讨论的问题，但正文仍按资料逐篇介绍，缺少统领全篇的中心判断，未达到围绕明确问题组织全篇的水平。
synthesis 5.0/10: 指出了共同主题、研究差异及内容记忆与位置记忆的区别，但没有用认知外包框架解释这些发现如何关联，综合判断仍较笼统。
[cli:codex:gpt-6.1-sol] 把逐篇介绍改为围绕一个中心判断展开：工具可能改变人们记忆内容与获取位置的分工；用S1说明现象、用S2解释其与认知外包的联系，再明确说明把S3的能动性要求联系到课堂学习属于作者推论。

## Recent rounds (newest last)
- r0 BASELINE score=61: (baseline)

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
