You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
审阅 judge/contract.json 中完全虚构的设计服务合同，修改 review.json。
依据 judge/review-guide.json 的七类检查项定位条款、引用原句、解释潜在争议并提出可执行的文字建议。
不判断真实合同效力，不引入法条、判例或司法辖区；明确这是示例演练，不构成法律意见。
issue_id 使用给定检查项编号，clause_id 使用合同条款编号；建议可以是供双方讨论的条款草案。

## What you may change
Only these paths (relative to the current directory): `review.json`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
An LLM jury (cli:codex:gpt-6.1-sol) scores the artifact against the rubric in `judge/rubric.yaml` (read it). A higher score must also win a head-to-head comparison against the current best.
Direction: maximize. Current best score: 91.5.

Judge feedback on the current best:
已准确定位 7/7 类预设问题；尚缺：无。

程序检查定位与内容长度；建议是否真正解决争议由模型评委判断。
presentation 8.0/10: 编号、原句、争议和建议便于定位，且提供确认顺序，但替换条款篇幅较长，待双方决定的事项分散在长段落中，尚不能直接作为逐项确认的讨论清单。
consequence 9.0/10: 各条均紧扣原文，清楚说明双方不同理解及实际后果，但开头的确认顺序尚未充分说明哪些分歧会直接阻止开工、哪些可以后续处理，未达到最高档的决策优先级。
[cli:codex:gpt-6.1-sol] 补齐C6的结算争议处理：明确甲方逾期不回复、双方核对后仍有异议时，由谁在何期限内整理证据并启动双方预先选定的后续处理程序，同时持续履行无争议部分的付款和交接。

## Recent rounds (newest last)
- r0 BASELINE score=41: (baseline)
- r1 KEEP score=91.5: 补全七类问题并提供具体、相互协调的条款草案，预计提高覆盖度、争议解释和修改建议的评分。
- r2 REVERT score=0: 将 C6 改为逐项确认清单并补齐结算争议后续流程，预计提高建议的可执行性和可读性。 -> failed gates: 定位引用和建议完整

## Lessons from earlier rounds and runs
- KEEP score=91.5: 补全七类问题并提供具体、相互协调的条款草案，预计提高覆盖度、争议解释和修改建议的评分。 -- score 41 -> 91.5; head-to-head 2/2
- REVERT score=0: 将 C6 改为逐项确认清单并补齐结算争议后续流程，预计提高建议的可执行性和可读性。 -- failed gates: 定位引用和建议完整

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
