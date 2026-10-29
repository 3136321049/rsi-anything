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
Direction: maximize. Current best score: 75.

Judge feedback on the current best:
drawing.svg: 26 shapes, 2562 bytes
pelican 7.0/10: The artifact has no text, so there is nothing to quote; in the image the bird is clearly a pelican, with a long yellow beak, a large pouch, an S-curved white neck, a grey feathered wing, a tail, orange legs and yellow triangular feet, but the body is shaped like a duck's and the legs are plain stick
craft 7.0/10: The artifact has no text, so there is nothing to quote; the flat shapes are tidy with consistent dark outlines and a pleasant muted palette (teal frame, orange legs, golden beak), but there is no ground or background, the drawing sits low with a lot of empty space above, and the stick legs and stub 
[cli:claude] Make the pelican look like it's moving: tilt its body forward, wrap its wingtip around a proper raised handlebar with grips, and add a ground shadow and speed lines. This would improve both the riding and the craft scores.

## Recent rounds (newest last)
- r0 BASELINE score=37: (baseline)
- r1 KEEP score=68: 补全鹈鹕特征及身体与自行车的接触关系，应能提高物种辨识度和骑乘可信度。
- r2 KEEP score=75: 补全车架与传动结构，让自行车更符合机械常识，并使细节与鹈鹕更协调，应能提高自行车和画面完成度评分。
- r3 REVERT score=75: 抬高车把并加粗握把，让翅膀向前伸展、翼尖包住握把，使骑乘接触更清楚、姿态更自然，预计提高骑乘和画面完成度评分。 -> score 75 is not better than 75 (required margin: 0 or 0%)

## Lessons from earlier rounds and runs
- KEEP score=68: 补全鹈鹕特征及身体与自行车的接触关系，应能提高物种辨识度和骑乘可信度。 -- score 37 -> 68; head-to-head 2/2
- KEEP score=75: 补全车架与传动结构，让自行车更符合机械常识，并使细节与鹈鹕更协调，应能提高自行车和画面完成度评分。 -- score 68 -> 75; head-to-head 2/2
- REVERT score=75: 抬高车把并加粗握把，让翅膀向前伸展、翼尖包住握把，使骑乘接触更清楚、姿态更自然，预计提高骑乘和画面完成度评分。 -- score 75 is not better than 75 (required margin: 0 or 0%)

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
