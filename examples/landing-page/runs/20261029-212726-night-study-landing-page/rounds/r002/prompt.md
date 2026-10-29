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
Direction: maximize. Current best score: 70.

Judge feedback on the current best:
index.html: 7046 bytes
first_impression 7.0/10: The first screen meets the 7 anchor: a large serif headline with a gold italic accent, a supporting line that names the exams, the 18:00–02:00 hours, and a cream price card with ¥129 and a prominent NIGHT keyword block. It falls short of 8–10 because the headline 'Make room for your future' is a gen
layout 7.0/10: The order is clear: a two-column hero (pitch on the left, offer card on the right), then a three-column benefits row with gold labels, then a two-column logistics row, separated by rules with steady spacing. It isn't higher because the location and safety row is set as small as a footnote, and the p
[cli:claude] Replace the tiny footer link with a full closing call-to-action section that repeats the ¥129 first-month offer, says plainly that only 50 trial spots exist, and gives explicit steps (1. open the official account 'Night Voyage Study Room', 2. send NIGHT) with a working copy-keyword button. That gives the page a strong, honest final push to act instead of ending on a footnote.

## Recent rounds (newest last)
- r0 BASELINE score=25: (baseline)
- r1 KEEP score=70: 用清晰的夜间主题首屏串联目标人群、试学价格和领取步骤，提升第一印象、视觉完成度与转化意愿。

## Lessons from earlier rounds and runs
- KEEP score=70: 用清晰的夜间主题首屏串联目标人群、试学价格和领取步骤，提升第一印象、视觉完成度与转化意愿。 -- score 25 -> 70; head-to-head 2/2

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
