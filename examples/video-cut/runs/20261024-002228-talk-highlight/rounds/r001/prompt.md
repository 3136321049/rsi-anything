You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
从 judge/transcript.json 对应的真实口播中选出40到75秒的短片，只修改edit.json。按judge/keypoints.md给出的目标选句和安排顺序，保留原意，不拼接出相反含义。

## What you may change
Only these paths (relative to the current directory): `edit.json`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
An LLM jury (cli:codex:gpt-6.1-sol) scores the artifact against the rubric in `judge/rubric.yaml` (read it). A higher score must also win a head-to-head comparison against the current best.
Direction: maximize. Current best score: 18.5.

Judge feedback on the current best:
cut: 8 sentences, 56.8s (allowed 40-75s); order [1, 2, 3, 4, 5, 6, 7, 8]
hook 1.0/10: 以礼宾称呼开场，随后仍在列举致意对象，没有让观众知道值得看什么，未达到5分的话题明确开场。
ending 1.0/10: 结尾停在未完成的句子中，既未交代人类掌握什么，也未收束主题，未达到5分的完整结尾。
[cli:codex:gpt-6.1-sol] 整体替换为原稿中从“To those old allies”到“split asunder.”的完整合作段落，用团结与分裂的反差建立一个清楚主题，并按原音频核验40到75秒时长。

## Recent rounds (newest last)
- r0 BASELINE score=18.5: (baseline)

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
