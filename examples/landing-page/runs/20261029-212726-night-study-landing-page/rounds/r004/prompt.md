You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
Improve index.html into a landing page that converts: someone who can only study at night should see
in seconds that the Night Membership is for them, what they get, and how to claim a ¥129 trial spot.
Use only the facts in judge/brief.md and keep every fact listed in judge/facts.json in the visible text.
The page must be self-contained (inline CSS, inline SVG or data you write yourself; no external fonts,
images or scripts) and work on a 390px phone. One focused improvement per round.

## What you may change
Only these paths (relative to the current directory): `index.html`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
An LLM jury (cli:claude) scores the artifact against the rubric in `judge/rubric.yaml` (read it). A higher score must also win a head-to-head comparison against the current best.
Direction: maximize. Current best score: 72.5.

Judge feedback on the current best:
index.html: 9855 bytes
layout 7.0/10: The page runs in a clear order with good spacing: hero with price card, three feature columns, practical info, a closing CTA panel. It misses 8 because the 'Close to the metro / Stay focused into the night' row is styled more weakly than the columns above it (no gold eyebrow, smaller titles), so it 
visual_craft 7.0/10: The deep green, cream and gold palette with serif headlines suits a calm late-night study room. It misses 8 because of small low-contrast grey body text on the dark background, italic headline lines that hang past the left margin, and a '↗' external-link icon used on a 'Copy keyword' action.
[cli:claude] Turn the location/safety row into a styled block that answers the late-night worries (e.g. 'Safe to stay late: key card entry after 01:30, staff on duty until 02:00 · 6 minutes' walk to the metro'), using the same eyebrow and title treatment as the three feature columns. This raises both persuasion and layout.

## Recent rounds (newest last)
- r0 BASELINE score=25: (baseline)
- r1 KEEP score=70: 用清晰的夜间主题首屏串联目标人群、试学价格和领取步骤，提升第一印象、视觉完成度与转化意愿。
- r2 KEEP score=72.5: 用完整的底部领取区明确优惠、名额限制和领取步骤，减少用户行动时的疑惑，提升转化说服力与页面完整度。
- r3 REVERT score=70: 将夜间安全与交通信息整合为视觉统一的醒目区块，直接回应晚间学习者的顾虑，提升信息层次与转化说服力。 -> score 70 is not better than 72.5 (required margin: 0 or 0%)

## Lessons from earlier rounds and runs
- KEEP score=70: 用清晰的夜间主题首屏串联目标人群、试学价格和领取步骤，提升第一印象、视觉完成度与转化意愿。 -- score 25 -> 70; head-to-head 2/2
- KEEP score=72.5: 用完整的底部领取区明确优惠、名额限制和领取步骤，减少用户行动时的疑惑，提升转化说服力与页面完整度。 -- score 70 -> 72.5; head-to-head 2/2
- REVERT score=70: 将夜间安全与交通信息整合为视觉统一的醒目区块，直接回应晚间学习者的顾虑，提升信息层次与转化说服力。 -- score 70 is not better than 72.5 (required margin: 0 or 0%)

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
