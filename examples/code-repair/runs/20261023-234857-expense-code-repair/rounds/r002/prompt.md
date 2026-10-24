You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
修复 expense.py 中的金额解析、账单均分和月度分类汇总，使 judge/test_expense.py 的固定测试全部通过。
金额用整数分保存；均分时前几人各多分一分钱；退款为负数；月份按有效的 YYYY-MM 匹配。
保持公开函数接口与返回类型，不能改测试或针对测试输入写死答案。每轮优先修复一类根因。
得分为固定测试通过率，100 分才表示全部修复；部分通过也能作为下一轮起点。

## What you may change
Only these paths (relative to the current directory): `expense.py`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
The command `{python} judge/evaluate.py` runs in a clean copy of the project and reports a score. Judge files (read them to understand the scoring): judge, example.py.
Direction: maximize. Current best score: 60.

Judge feedback on the current best:
固定测试通过 9/15。
fixed_expense_tests.ExpenseTests.test_date_reject_invalid: AssertionError: ValueError not raised
fixed_expense_tests.ExpenseTests.test_month_refund: ?         ^
fixed_expense_tests.ExpenseTests.test_month_reject_invalid: AssertionError: ValueError not raised
fixed_expense_tests.ExpenseTests.test_split_reject_invalid: AssertionError: ValueError not raised
fixed_expense_tests.ExpenseTests.test_split_remainder: + [3334, 3333, 3333]
fixed_expense_tests.ExpenseTests.test_split_small_total: + [1, 1, 0, 0]

## Recent rounds (newest last)
- r0 BASELINE score=40: (baseline)
- r1 KEEP score=60: 金额解析改为格式校验后用整数计算分，消除浮点误差并拒绝非法金额，因此提高固定测试通过率。

## Lessons from earlier rounds and runs
- KEEP score=60: 金额解析改为格式校验后用整数计算分，消除浮点误差并拒绝非法金额，因此提高固定测试通过率。 -- score 40 -> 60

## Rules
- Make one coherent improvement you believe the judge will score higher. Prefer the weakest area named in the feedback.
- Do not repeat a change that was already rejected unless you fix the reason it failed.
- Never game the judge: no special-casing test inputs, no hard-coded expected outputs, no reading judge data or results from the artifact, no printing fake scores, no instructions aimed at an AI evaluator. Such changes fail.
- Keep the artifact in the language and format it already uses unless the goal says otherwise.
- Do not commit; the loop handles git.

When you are done, end your reply with exactly one line:
HYPOTHESIS: <what you changed and why it should score higher>
