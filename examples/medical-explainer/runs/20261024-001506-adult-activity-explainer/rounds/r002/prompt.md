You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
面向久坐办公的一般健康成人，改进 explainer.md，解释 WHO 身体活动建议，帮助读者理解并开始行动。
只使用 judge/sources.json：中高强度有氧活动、肌肉强化、减少久坐、从少量逐步增加。
关键数量必须通过 {{资料键}} 写入，资料键在 judge/sources.json 的 values 中；来源用 [W1]、[W2]。
可以写一般生活场景例子，不制定个人训练处方，不加入药物、诊断或疾病治疗承诺。
保留一般健康成人、健康科普及不能替代个体医疗建议的适用说明。

## What you may change
Only these paths (relative to the current directory): `explainer.md`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
An LLM jury (cli:codex:gpt-6.1-sol) scores the artifact against the rubric in `judge/rubric.yaml` (read it). A higher score must also win a head-to-head comparison against the current best.
Direction: maximize. Current best score: 80.

Judge feedback on the current best:
程序检查固定数量、来源编号及用途说明；是否准确转述、是否给出了个体化医疗指令由模型评委另行检查。
accuracy 8.0/10: 推荐量、替代关系、肌肉强化和减少久坐均解释准确，但等量组合没有给出明确的换算示例，距离更高档的直观理解还有一步。
plain_language 8.0/10: 用走路、通勤和接水解释术语，普通读者容易理解，但等量组合一段仍偏抽象，开头结尾的重复用途说明也影响简洁度。
[cli:codex:gpt-6.1-sol] 把等量组合的抽象解释改成简短换算例子：计算每周有氧量时，1分钟高强度约相当于2分钟中等强度，例如100分钟中等强度加25分钟高强度，相当于150分钟中等强度；注明这只是计算示例。

## Recent rounds (newest last)
- r0 BASELINE score=58.5: (baseline)
- r1 KEEP score=80: 用办公日场景解释术语和常见误读，让读者更容易理解建议并开始行动，预计提升通俗性、准确性和实用性评分。

## Lessons from earlier rounds and runs
- KEEP score=80: 用办公日场景解释术语和常见误读，让读者更容易理解建议并开始行动，预计提升通俗性、准确性和实用性评分。 -- score 58.5 -> 80; head-to-head 2/2

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
