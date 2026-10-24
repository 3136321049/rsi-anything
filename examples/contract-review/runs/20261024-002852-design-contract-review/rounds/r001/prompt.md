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
Direction: maximize. Current best score: 41.

Judge feedback on the current best:
已准确定位 2/7 类预设问题；尚缺：I3, I4, I5, I6, I7。

程序检查定位与内容长度；建议是否真正解决争议由模型评委判断。
coverage 3.0/10: 仅对交付和付款两类问题作了实质说明，且未涉及交付渠道、发票和额外费用，另外五类完全缺失，未达到覆盖约一半的5分标准。
revision 4.0/10: 建议给出了修改方向，却没有提供可讨论的付款触发事件、期限方案或确认流程，关键歧义仍留给双方自行解决，尚未达到5分以上的完整程度。
[cli:codex:gpt-6.1-sol] 补齐I3至I7，每类引用对应原句、说明双方会产生的具体分歧，并给出可直接讨论的替换条款，将新增期限、次数和金额明确标为待双方确认的方案。

## Recent rounds (newest last)
- r0 BASELINE score=41: (baseline)

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
