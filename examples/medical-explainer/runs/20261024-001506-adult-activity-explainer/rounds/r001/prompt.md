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
Direction: maximize. Current best score: 58.5.

Judge feedback on the current best:
程序检查固定数量、来源编号及用途说明；是否准确转述、是否给出了个体化医疗指令由模型评委另行检查。
plain_language 5.0/10: 文字通顺，但解释仍像指南摘要，没有用日常语言说清有氧、主要肌群和等量组合等术语，未达到8分要求。
accuracy 6.0/10: 推荐量、替代关系和强化频次准确，但没有解释如何理解强度和等量组合，减少久坐也仅被提及，尚未达到准确清楚且避免常见误读的8分水平。
[cli:codex:gpt-6.1-sol] 将“怎么理解”改成一个简短的办公日场景：提供通勤步行、工作间隙起身等可选入口，说明可从少量逐步增加，并解释这些活动何时计入有氧量，以及为何肌肉强化和减少久坐仍需分别关注。

## Recent rounds (newest last)
- r0 BASELINE score=58.5: (baseline)

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
