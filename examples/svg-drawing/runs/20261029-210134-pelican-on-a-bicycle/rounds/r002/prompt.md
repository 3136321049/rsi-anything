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
Direction: maximize. Current best score: 68.

Judge feedback on the current best:
drawing.svg: 20 shapes, 1923 bytes
bicycle 6.0/10: It has every element the 7 anchor lists (wheels, saddle, handlebars, crank and pedals), but the frame is just an L plus a seat post with no down tube or stays, and there is no chain, spokes or hubs, so it is not yet a mechanically convincing bike.
craft 6.0/10: The shapes are clean and the palette is pleasant. Below 7 because the detail is uneven (a shaded, feathered bird on a bare stick-line bike with empty wheels) and the composition leaves a lot of dead space above the subject.
[cli:claude] Give the bike a proper diamond frame (top tube, down tube, seat stays and chainstays) plus spokes or hubs and a chain loop from the chainring to the rear hub. That would lift the bicycle score and also bring its level of detail closer to the pelican's, which would help craft.

## Recent rounds (newest last)
- r0 BASELINE score=37: (baseline)
- r1 KEEP score=68: 补全鹈鹕特征及身体与自行车的接触关系，应能提高物种辨识度和骑乘可信度。

## Lessons from earlier rounds and runs
- KEEP score=68: 补全鹈鹕特征及身体与自行车的接触关系，应能提高物种辨识度和骑乘可信度。 -- score 37 -> 68; head-to-head 2/2

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
