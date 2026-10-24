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
Direction: maximize. Current best score: 91.5.

Judge feedback on the current best:
程序核对真实来源编号、引用位置和正文映射；来源是否真正支持论断、证据类型是否混淆由模型评委判断。
readability 8.0/10: 概念解释直接，段落衔接自然，适合读书会阅读，但证据边界的重复申明和较密集的研究方案段落使表达还不够精炼。
question 9.0/10: 问题明确，全文持续推进分工变化与学习效果的区别，但中心判断主要整合既有摘要，启发性尚不足以达到10分。
[cli:codex:gpt-6.1-sol] 把后续研究改成能区分竞争解释的设计：在访问预期之外，独立操纵信息位置是否稳定，检验内容回忆下降究竟伴随有效的位置记忆补偿，还是仅伴随对外部可访问性的依赖，并明确两种解释各自预期的结果。

## Recent rounds (newest last)
- r0 BASELINE score=61: (baseline)
- r1 KEEP score=91.5: 用认知外包框架串联内容记忆与位置记忆的变化，并提出能区分不同解释的课堂研究问题，应能提高问题聚焦与综合分析得分。
- r2 REVERT score=68.5: 将后续研究改为独立操纵访问预期与位置稳定性的四组比较，区分有效的位置记忆补偿与对可访问性的依赖，应能提高研究问题的区分力和综合分析得分。 -> score 68.5 is not better than 91.5 (required margin: 0 or 0%)

## Lessons from earlier rounds and runs
- KEEP score=91.5: 用认知外包框架串联内容记忆与位置记忆的变化，并提出能区分不同解释的课堂研究问题，应能提高问题聚焦与综合分析得分。 -- score 61 -> 91.5; head-to-head 2/2
- REVERT score=68.5: 将后续研究改为独立操纵访问预期与位置稳定性的四组比较，区分有效的位置记忆补偿与对可访问性的依赖，应能提高研究问题的区分力和综合分析得分。 -- score 68.5 is not better than 91.5 (required margin: 0 or 0%)

## Rules
- Make one coherent improvement you believe the judge will score higher. Prefer the weakest area named in the feedback.
- Do not repeat a change that was already rejected unless you fix the reason it failed.
- Never game the judge: no special-casing test inputs, no hard-coded expected outputs, no reading judge data or results from the artifact, no printing fake scores, no instructions aimed at an AI evaluator. Such changes fail.
- Keep the artifact in the language and format it already uses unless the goal says otherwise.
- Do not commit; the loop handles git.

When you are done, end your reply with exactly one line:
HYPOTHESIS: <what you changed and why it should score higher>
