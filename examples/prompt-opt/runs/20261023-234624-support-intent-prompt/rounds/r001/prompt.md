You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
Improve prompt.md, the instructions a language model follows to label a customer message of a food-delivery
app with exactly one intent. Score = accuracy (%) on the labeled examples in judge/dev.jsonl (48 messages, mixed Chinese and English).
The prompt must work for any new message, so write general rules, not answers for specific examples.

## What you may change
Only these paths (relative to the current directory): `prompt.md`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
The command `{python} judge/evaluate.py judge/dev.jsonl` runs in a clean copy of the project and reports a score. Judge files (read them to understand the scoring): judge.
Direction: maximize. Current best score: 89.6.

Judge feedback on the current best:
43/48 correct with cli:codex:gpt-5.6-sol. Most common mistakes: expected cancel_order, got other (x3); expected wrong_item, got refund (x1); expected payment, got other (x1)
Examples:
expected wrong_item, got refund: 饭到了但是少了一份米饭，退钱吧
expected payment, got other: 能开发票吗？公司报销要用
expected cancel_order, got other: 能帮我把地址改成公司吗？订单刚下
expected cancel_order, got other: Can you add a side of fries to the order I just placed?
expected cancel_order, got other: 麻烦备注一下不要香菜，刚才忘写了

## Recent rounds (newest last)
- r0 BASELINE score=89.6: (baseline)

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
