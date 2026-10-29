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
Direction: maximize. Current best score: 25.

Judge feedback on the current best:
index.html: 960 bytes
visual_craft 1.0/10: Everything is browser defaults (black system font on white, default bullets and margins), with no colour, type scale, spacing system or any mood suited to a calm late-night study room.
first_impression 2.0/10: Above the fold there is only a black browser-default H1 and a generic availability line; the page never says it is for people who work by day and prepare for exams at night, and nothing draws the eye or works as a call to action, so it falls short of the 4 anchor where the offer is stated.
[cli:claude] Replace the default H1 opening with a designed above-the-fold hero for night-time exam takers. It should say who the page is for (e.g., working by day and preparing for graduate-school, civil-service or certification exams at night, 18:00–02:00), show '¥129 first month, first 50 sign-ups only' prominently, and end in a clear call-to-action block telling visitors to reply 'NIGHT' to the official account, all in a calm, coherent night-themed style.

## Recent rounds (newest last)
- r0 BASELINE score=25: (baseline)

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
