You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
从 judge/transcript.json 对应的真实口播中选出40到75秒的短片，只修改edit.json。按judge/keypoints.md给出的目标选句和安排顺序，保留原意，不拼接出相反含义。

## What you may change
Only these paths (relative to the current directory): `edit.json`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
An LLM jury (cli:codex:gpt-6.1-sol) scores the artifact against the rubric in `judge/rubric.yaml` (read it). A higher score must also win a head-to-head comparison against the current best.
Direction: maximize. Current best score: 75.5.

Judge feedback on the current best:
cut: 10 sentences, 56.0s (allowed 40-75s); order [22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
hook 6.0/10: 开头承诺鲜明、语势强，但前两句没有具体呈现冲突或反差，尚未达到8分的吸引力。
value 7.0/10: 观众能理解维护自由需要盟友合作，但开头较多篇幅用于总体宣誓，合作面对的挑战仍然笼统，尚未达到8分所要求的重要信息讲清楚。
[cli:codex:gpt-6.1-sol] 将开头两句替换为原稿中“The world is very different now.”及紧随其后的完整句“For man holds…”：用消除贫困与毁灭人类的具体反差吸引观众，再接盟友合作段落，让合作的必要性更清楚。

## Recent rounds (newest last)
- r0 BASELINE score=18.5: (baseline)
- r1 KEEP score=75.5: 仅修改 `edit.json`，按原序选取第 22–31 段，共 56.002 秒；以捍卫自由的决心开场，以团结与分裂的反差完整收尾，预计能提高开场吸引力、连贯性和结尾得分。
- r2 REVERT score=68: 仅修改 `edit.json`，选取第 8–13、27–31 段，共 64.624 秒；以消除贫困与毁灭人类的具体反差开场，完整保留权利信念及盟友合作段落，预计提升开场吸引力和信息价值。 -> score 68 is not better than 75.5 (required margin: 0 or 0%)

## Lessons from earlier rounds and runs
- KEEP score=75.5: 仅修改 `edit.json`，按原序选取第 22–31 段，共 56.002 秒；以捍卫自由的决心开场，以团结与分裂的反差完整收尾，预计能提高开场吸引力、连贯性和结尾得分。 -- score 18.5 -> 75.5; head-to-head 2/2
- REVERT score=68: 仅修改 `edit.json`，选取第 8–13、27–31 段，共 64.624 秒；以消除贫困与毁灭人类的具体反差开场，完整保留权利信念及盟友合作段落，预计提升开场吸引力和信息价值。 -- score 68 is not better than 75.5 (required margin: 0 or 0%)

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
