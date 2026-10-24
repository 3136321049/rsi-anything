You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
修改 strategy.json 的均线窗口、入场差值和仓位比例，在冻结历史数据上改善收益与回撤的折中。
fast_window 为 2..60，slow_window 为 5..120 且大于 fast_window，threshold_bps 为 0..300，allocation 为 0.1..1。
只做多或持有现金，前一天收盘产生信号，次日开盘成交；交易成本和评测期间固定，不能修改。
得分=累计收益百分点-1.5倍最大回撤百分点。至少完成一次买入和卖出，净值必须有限且为正。
阅读 out/report.md 的收益、回撤、成本和交易表后再尝试；这是固定历史上的参数优化演示，不是投资建议或未来收益承诺。

## What you may change
Only these paths (relative to the current directory): `strategy.json`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
The command `{python} judge/evaluate.py` runs in a clean copy of the project and reports a score. Judge files (read them to understand the scoring): judge.
Direction: maximize. Current best score: 31.215.

Judge feedback on the current best:
累计收益 63.25%，最大回撤 21.36%，模拟成交 16 笔，费用与滑点合计 167.40 USDT。得分为收益减去 1.5 倍回撤。

## Recent rounds (newest last)
- r0 BASELINE score=7.567: (baseline)
- r1 KEEP score=31.215: 将均线窗口从 3/8 日延长至 10/30 日，保持零入场差值和半仓，预期减少短期反复交易及成本，提高收益减去 1.5 倍最大回撤的得分。

## Lessons from earlier rounds and runs
- KEEP score=31.215: 将均线窗口从 3/8 日延长至 10/30 日，保持零入场差值和半仓，预期减少短期反复交易及成本，提高收益减去 1.5 倍最大回撤的得分。 -- score 7.567 -> 31.215

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
