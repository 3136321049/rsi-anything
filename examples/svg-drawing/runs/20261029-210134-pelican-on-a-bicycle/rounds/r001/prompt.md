You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
Improve drawing.svg so it unmistakably shows a pelican riding a bicycle.
The pelican needs its long beak with a throat pouch, a body, wings, legs and feet; the bicycle needs two
wheels, a frame, a seat, handlebars, pedals and a chain. The bird must actually ride it: seated on the
saddle, feet on the pedals, wings on the handlebars. After that, work on proportions, composition and
craft. Vector shapes only, no text or labels, keep the viewBox. One focused visual change per round.

## What you may change
Only these paths (relative to the current directory): `drawing.svg`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
An LLM jury (cli:claude) scores the artifact against the rubric in `judge/rubric.yaml` (read it). A higher score must also win a head-to-head comparison against the current best.
Direction: maximize. Current best score: 37.

Judge feedback on the current best:
drawing.svg: 11 shapes, 942 bytes
pelican 3.0/10: The text part of the artifact is empty, so this score rests on the image alone: a gray oval body, a separate floating circle head with a dot eye and a thin orange triangle beak, but no throat pouch, wings, legs or feet, and the head is not joined to the body, so it reads below a generic bird; reachi
bicycle 4.0/10: The image shows two wheels, one horizontal bar between the hubs and two upright strokes for a seat post and a fork, with no saddle, handlebars, pedals, crank, chain or spokes; that matches the 4 anchor of 'two wheels and a few lines'.
[cli:claude] Connect the head to the body with a neck, then give the bird a long bill with a throat pouch, a wing reaching to new handlebars, and legs running down to pedals on a crank under a saddle. That would lift the pelican, riding and bicycle scores together.

## Recent rounds (newest last)
- r0 BASELINE score=37: (baseline)

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
