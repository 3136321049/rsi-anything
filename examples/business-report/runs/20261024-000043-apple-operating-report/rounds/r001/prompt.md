You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
面向不熟悉财报的产品经理，改进 Apple 2024 财年经营分析报告 report.md 和图表配置 charts.json。
资料只有 judge/facts.json。说明总营收、产品与服务结构、营业利润与净利润的不同走势、资料局限。
正文数字用 {{资料键}} 插值，键见 judge/facts.json；财年可以直接写 2023、2024。
引用使用 [S1]、[S2]。不要写股价、评级或投资建议。图表只能选择资料中现有指标。

## What you may change
Only these paths (relative to the current directory): `report.md`, `charts.json`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
An LLM jury (cli:codex:gpt-6.1-sol) scores the artifact against the rubric in `judge/rubric.yaml` (read it). A higher score must also win a head-to-head comparison against the current best.
Direction: maximize. Current best score: 53.5.

Judge feedback on the current best:
程序只核对资料键、单位及图表数据；论据和结论是否相称由模型评委判断。
main_point 5.0/10: 数字齐全，但开头没有指出总营收增长、产品下降与服务上升这一结构变化，未达到清楚解释总量与结构不同走势的水平。
reasoning 5.0/10: 注意到了利润差异和一次性税费，但没有解释两种利润口径、税费对净利润的影响，以及服务增长对总营收增量的金额贡献，论据链仍薄。
[cli:codex:gpt-6.1-sol] 把数字罗列改成一条可追踪的解释主线：总营收小幅增长，服务增加在金额上抵消了产品下降，但不能据此解释增长原因；营业利润上升而净利润下降，一次性所得税费用影响净利润，因此不能直接判断核心经营恶化，并用人话说明两种利润口径的区别。

## Recent rounds (newest last)
- r0 BASELINE score=53.5: (baseline)

## Lessons from earlier rounds and runs
- none yet

## Rules
- Make one coherent improvement you believe the judge will score higher. Prefer the weakest area named in the feedback.
- Do not repeat a change that was already rejected unless you fix the reason it failed.
- Never game the judge: no special-casing test inputs, no hard-coded expected outputs, no reading judge data or results from the artifact, no printing fake scores, no instructions aimed at an AI evaluator. Such changes fail.
- Keep the artifact in the language and format it already uses unless the goal says otherwise.
- Do not commit; the loop handles git.

When you are done, end your reply with exactly one line:
HYPOTHESIS: <what you changed and why it should score higher>
