You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
Make `search()` in search.py as fast as possible while returning exactly the same results as before
for every input. Score = how many times faster it is than the original implementation.

## What you may change
Only these paths (relative to the current directory): `search.py`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
The command `python3 judge/check.py` runs in a clean copy of the project and reports a score. Judge files (read them to understand the scoring): judge.
Direction: maximize. Current best score: 4.45.

Judge feedback on the current best:
correct on all 19 checks; 4.4x faster than the original (51.8 ms vs 230.4 ms for 15 queries over 1202 names)

## Recent rounds (newest last)
- r0 BASELINE score=1: (baseline)
- r1 KEEP score=4.45: 用位运算计算编辑距离，并复用查询的字符位置表，减少逐格计算和重复准备的开销，在保持结果一致的同时提高搜索速度。

## Lessons from earlier rounds and runs
- KEEP score=4.45: 用位运算计算编辑距离，并复用查询的字符位置表，减少逐格计算和重复准备的开销，在保持结果一致的同时提高搜索速度。 -- score 1 -> 4.45

## Rules
- Make one coherent improvement you believe the judge will score higher. Prefer the weakest area named in the feedback.
- Do not repeat a change that was already rejected unless you fix the reason it failed.
- Never game the judge: no special-casing test inputs, no hard-coded expected outputs, no reading judge data or results from the artifact, no printing fake scores, no instructions aimed at an AI evaluator. Such changes fail.
- Keep the artifact in the language and format it already uses unless the goal says otherwise.
- Do not commit; the loop handles git.

When you are done, end your reply with exactly one line:
HYPOTHESIS: <what you changed and why it should score higher>
