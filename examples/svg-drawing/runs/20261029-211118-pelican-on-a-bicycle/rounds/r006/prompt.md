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
Direction: maximize. Current best score: 78.

Judge feedback on the current best:
drawing.svg: 30 shapes, 3420 bytes
craft 7.0/10: The shapes are tidy and the palette is pleasant. It is not poster-level: the stick legs cross the frame tubes confusingly, the chain lines are messy, the body silhouette is lumpy, and the drawing floats with no ground or depth.
pelican 8.0/10: It is clearly a pelican with every listed part drawn. It falls short of 10 because the body is a lumpy, goose-like blob, the legs are thin sticks, and the pouch is a plain half-bowl rather than a charming, well-observed shape.
[cli:claude] Add a sense of motion and grounding: a ground line with a soft shadow under the wheels, a few speed lines behind the bike, and a slight forward tilt of the bird. This would raise both riding (pose suggests motion) and craft (finished composition).

## Recent rounds (newest last)
- r0 BASELINE score=75: (baseline)
- r1 KEEP score=75: 将鹈鹕和自行车整体放大 20% 并居中，平衡上下留白、增强主体表现，预计提高构图与完成度评分；SVG 语法检查通过，viewBox 保持不变。
- r2 KEEP score=78: 将双脚改为更大的三趾蹼脚，补出蹼膜、趾线和沿踏板弯曲的前趾，预计增强鹈鹕辨识度和踩踏可信度；SVG 语法检查通过，viewBox 保持不变。
- r3 REVERT score=75: 将翅膀改为有明显关节弯曲和羽毛走向的轮廓，翼尖弯扣现有握把，预计提升骑乘可信度和绘制质量；SVG 语法检查通过，viewBox 保持不变。 -> score 75 is not better than 78 (required margin: 0 or 0%)
- r4 KEEP score=78: 将喉囊改为自然下垂的圆润轮廓，加入暖色阴影和嘴根褶皱，预计提升鹈鹕特征的表现和绘制质感；SVG 语法检查通过，viewBox 保持不变。
- r5 REVERT score=78: 将身体轮廓调整为饱满流畅的背腹曲线，柔化颈根衔接，预计提升鹈鹕形态和画面精致度；仅修改 `drawing.svg`，语法检查通过，viewBox 保持不变。 -> tied at 78 and lost head-to-head (0/2 votes)

## Lessons from earlier rounds and runs
- KEEP score=68: 补全鹈鹕特征及身体与自行车的接触关系，应能提高物种辨识度和骑乘可信度。 -- score 37 -> 68; head-to-head 2/2
- KEEP score=75: 补全车架与传动结构，让自行车更符合机械常识，并使细节与鹈鹕更协调，应能提高自行车和画面完成度评分。 -- score 68 -> 75; head-to-head 2/2
- REVERT score=75: 抬高车把并加粗握把，让翅膀向前伸展、翼尖包住握把，使骑乘接触更清楚、姿态更自然，预计提高骑乘和画面完成度评分。 -- score 75 is not better than 75 (required margin: 0 or 0%)
- REVERT score=75: 将细线腿改为有粗细变化和关节转折的轮廓，补清踩在踏板上的蹼脚，预计提升鹈鹕细节和骑乘可信度；SVG 格式检查通过，viewBox 保持不变。 -- score 75 is not better than 75 (required margin: 0 or 0%)
- REVERT score=75: 添加车轮下的地面投影和身后的速度线，增强落地感与骑行动感，预计提高画面完成度和骑乘评分；SVG 格式检查通过，viewBox 保持不变。 -- score 75 is not better than 75 (required margin: 0 or 0%)
- KEEP score=75: 将鹈鹕和自行车整体放大 20% 并居中，平衡上下留白、增强主体表现，预计提高构图与完成度评分；SVG 语法检查通过，viewBox 保持不变。 -- tied at 75; won head-to-head 2/2
- KEEP score=78: 将双脚改为更大的三趾蹼脚，补出蹼膜、趾线和沿踏板弯曲的前趾，预计增强鹈鹕辨识度和踩踏可信度；SVG 语法检查通过，viewBox 保持不变。 -- score 75 -> 78; head-to-head 2/2
- REVERT score=75: 将翅膀改为有明显关节弯曲和羽毛走向的轮廓，翼尖弯扣现有握把，预计提升骑乘可信度和绘制质量；SVG 语法检查通过，viewBox 保持不变。 -- score 75 is not better than 78 (required margin: 0 or 0%)
- KEEP score=78: 将喉囊改为自然下垂的圆润轮廓，加入暖色阴影和嘴根褶皱，预计提升鹈鹕特征的表现和绘制质感；SVG 语法检查通过，viewBox 保持不变。 -- tied at 78; won head-to-head 2/2
- REVERT score=78: 将身体轮廓调整为饱满流畅的背腹曲线，柔化颈根衔接，预计提升鹈鹕形态和画面精致度；仅修改 `drawing.svg`，语法检查通过，viewBox 保持不变。 -- tied at 78 and lost head-to-head (0/2 votes)

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
