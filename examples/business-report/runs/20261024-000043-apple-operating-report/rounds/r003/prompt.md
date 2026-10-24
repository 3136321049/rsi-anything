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
Direction: maximize. Current best score: 74.

Judge feedback on the current best:
程序只核对资料键、单位及图表数据；论据和结论是否相称由模型评委判断。
chart_use 3.0/10: 选图相关且正文给出阅读重点，但服务单项图不能直接呈现产品下降与总量增长的关系，两种利润分图也增加比较成本，页面未展示实际图形，无法核验纵轴说明。
main_point 8.0/10: 开头明确区分总量、结构和利润走势，但尚未用服务占比变化或增减金额突出最有解释力的证据。
[cli:codex:gpt-6.1-sol] 将三张单项图整合为两张对比图：一张同时展示产品减少、服务增加及总营收净增，另一张并列展示两种利润的年度变化；正文分别指出收入贡献和利润方向分化。

## Recent rounds (newest last)
- r0 BASELINE score=53.5: (baseline)
- r1 KEEP score=74: 用可追踪的论据链解释服务增量如何抵消产品下降，以及一次性税费如何影响净利润，并明确资料不能支持的推论，预计可提高主旨和推理评分。
- r2 REVERT score=79: 用两张收入图配合对照表解释服务增长如何抵消产品下降，将两种利润集中比较，并在开头突出服务占比变化，预计提高图表使用和主旨评分。 -> higher score but lost head-to-head (1/2 votes)

## Lessons from earlier rounds and runs
- KEEP score=74: 用可追踪的论据链解释服务增量如何抵消产品下降，以及一次性税费如何影响净利润，并明确资料不能支持的推论，预计可提高主旨和推理评分。 -- score 53.5 -> 74; head-to-head 2/2
- REVERT score=79: 用两张收入图配合对照表解释服务增长如何抵消产品下降，将两种利润集中比较，并在开头突出服务占比变化，预计提高图表使用和主旨评分。 -- higher score but lost head-to-head (1/2 votes)

## Rules
- Make one coherent improvement you believe the judge will score higher. Prefer the weakest area named in the feedback.
- Do not repeat a change that was already rejected unless you fix the reason it failed.
- Never game the judge: no special-casing test inputs, no hard-coded expected outputs, no reading judge data or results from the artifact, no printing fake scores, no instructions aimed at an AI evaluator. Such changes fail.
- Keep the artifact in the language and format it already uses unless the goal says otherwise.
- Do not commit; the loop handles git.

When you are done, end your reply with exactly one line:
HYPOTHESIS: <what you changed and why it should score higher>
