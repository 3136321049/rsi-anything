# RSI run `20261024-001506-adult-activity-explainer`

**Goal:** 面向久坐办公的一般健康成人，改进 explainer.md，解释 WHO 身体活动建议，帮助读者理解并开始行动。
只使用 judge/sources.json：中高强度有氧活动、肌肉强化、减少久坐、从少量逐步增加。
关键数量必须通过 {{资料键}} 写入，资料键在 judge/sources.json 的 values 中；来源用 [W1]、[W2]。
可以写一般生活场景例子，不制定个人训练处方，不加入药物、诊断或疾病治疗承诺。
保留一般健康成人、健康科普及不能替代个体医疗建议的适用说明。

Agent `codex` · judge `rubric` · jury cli:codex:gpt-6.1-sol · branch `rsi/20261024-001506-adult-activity-explainer`

| round | status | score | best | change | why |
|---:|---|---:|---:|---|---|
| 0 | BASELINE | 58.5 | 58.5 | baseline |  |
| 1 | KEEP | 80 | 80 | 用办公日场景解释术语和常见误读，让读者更容易理解建议并开始行动，预计提升通俗性、准确性和实用性评分。 | score 58.5 -> 80; head-to-head 2/2 |
| 2 | REVERT | 77.5 | 80 | 用具体换算示例解释中高强度活动的等量关系，帮助读者理解混合活动如何计入每周总量，预计提高准确性和通俗性评分。 | score 77.5 is not better than 80 (required margin: 0 or 0%) |
| 3 | REVERT | 77.5 | 80 | 将起步建议具体化，兼顾工作限制、少量活动的价值和逐步增加的方法，预计提高实用性与通俗性评分。 | score 77.5 is not better than 80 (required margin: 0 or 0%) |

Stopped: reached 3 rounds.

运行状态：finished。已保存 6 条模型调用记录；调用费用：工具未提供。

[任务配置](config/rsi.yaml) · [模型与运行参数](config/execution.json)

## 产物版本

- 初始产物：[explainer.md](artifacts/baseline/files/explainer.md) · [out/checklist.json](artifacts/baseline/files/out/checklist.json) · [out/evaluation.md](artifacts/baseline/files/out/evaluation.md) · [out/explainer.html](artifacts/baseline/files/out/explainer.html) · [out/explainer.md](artifacts/baseline/files/out/explainer.md) · [out/gates.json](artifacts/baseline/files/out/gates.json) · [out/notes.txt](artifacts/baseline/files/out/notes.txt)
- 第 1 轮 · KEEP：[explainer.md](rounds/r001/artifacts/files/explainer.md) · [out/checklist.json](rounds/r001/artifacts/files/out/checklist.json) · [out/evaluation.md](rounds/r001/artifacts/files/out/evaluation.md) · [out/explainer.html](rounds/r001/artifacts/files/out/explainer.html) · [out/explainer.md](rounds/r001/artifacts/files/out/explainer.md) · [out/gates.json](rounds/r001/artifacts/files/out/gates.json) · [out/notes.txt](rounds/r001/artifacts/files/out/notes.txt)
- 第 2 轮 · REVERT：[explainer.md](rounds/r002/artifacts/files/explainer.md) · [out/checklist.json](rounds/r002/artifacts/files/out/checklist.json) · [out/evaluation.md](rounds/r002/artifacts/files/out/evaluation.md) · [out/explainer.html](rounds/r002/artifacts/files/out/explainer.html) · [out/explainer.md](rounds/r002/artifacts/files/out/explainer.md) · [out/gates.json](rounds/r002/artifacts/files/out/gates.json) · [out/notes.txt](rounds/r002/artifacts/files/out/notes.txt)
- 第 3 轮 · REVERT：[explainer.md](rounds/r003/artifacts/files/explainer.md) · [out/checklist.json](rounds/r003/artifacts/files/out/checklist.json) · [out/evaluation.md](rounds/r003/artifacts/files/out/evaluation.md) · [out/explainer.html](rounds/r003/artifacts/files/out/explainer.html) · [out/explainer.md](rounds/r003/artifacts/files/out/explainer.md) · [out/gates.json](rounds/r003/artifacts/files/out/gates.json) · [out/notes.txt](rounds/r003/artifacts/files/out/notes.txt)
- 最终产物：[explainer.md](artifacts/final/files/explainer.md) · [out/checklist.json](artifacts/final/files/out/checklist.json) · [out/evaluation.md](artifacts/final/files/out/evaluation.md) · [out/explainer.html](artifacts/final/files/out/explainer.html) · [out/explainer.md](artifacts/final/files/out/explainer.md) · [out/gates.json](artifacts/final/files/out/gates.json) · [out/notes.txt](artifacts/final/files/out/notes.txt)
