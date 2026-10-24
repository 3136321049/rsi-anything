# RSI run `20261024-000801-cognitive-offloading-review`

**Goal:** 为教育研究读书会写一篇关于“数字工具怎样改变我们记忆信息与信息位置”的中文资料综述。
修改 review.md 和 evidence.json，只使用 judge/sources.json 的三份摘要。
围绕一个问题综合比较实验、理论综述和政策建议，分清支持的结论与仍需研究的假设。
每个来源使用 [S1] 等引用；evidence.json 中 claim 必须是正文的一句原话，sources 对应来源编号。
至少三条证据映射并覆盖三个来源，不能把旧检索研究写成生成式AI的直接效果证明。

Agent `codex` · judge `rubric` · jury cli:codex:gpt-6.1-sol · branch `rsi/20261024-000801-cognitive-offloading-review`

| round | status | score | best | change | why |
|---:|---|---:|---:|---|---|
| 0 | BASELINE | 61 | 61 | baseline |  |
| 1 | KEEP | 91.5 | 91.5 | 用认知外包框架串联内容记忆与位置记忆的变化，并提出能区分不同解释的课堂研究问题，应能提高问题聚焦与综合分析得分。 | score 61 -> 91.5; head-to-head 2/2 |
| 2 | REVERT | 68.5 | 91.5 | 将后续研究改为独立操纵访问预期与位置稳定性的四组比较，区分有效的位置记忆补偿与对可访问性的依赖，应能提高研究问题的区分力和综合分析得分。 | score 68.5 is not better than 91.5 (required margin: 0 or 0%) |
| 3 | REVERT | 70 | 91.5 | 压缩重复说明，让实验发现、理论解释与政策要求更紧凑地推进同一问题，在保留证据边界的同时提高可读性。 | score 70 is not better than 91.5 (required margin: 0 or 0%) |

Stopped: reached 3 rounds.

运行状态：finished。已保存 6 条模型调用记录；调用费用：工具未提供。

[任务配置](config/rsi.yaml) · [模型与运行参数](config/execution.json)

## 产物版本

- 初始产物：[evidence.json](artifacts/baseline/files/evidence.json) · [out/evaluation.md](artifacts/baseline/files/out/evaluation.md) · [out/gates.json](artifacts/baseline/files/out/gates.json) · [out/notes.txt](artifacts/baseline/files/out/notes.txt) · [out/review.html](artifacts/baseline/files/out/review.html) · [out/review.md](artifacts/baseline/files/out/review.md) · [out/source-map.json](artifacts/baseline/files/out/source-map.json) · [review.md](artifacts/baseline/files/review.md)
- 第 1 轮 · KEEP：[evidence.json](rounds/r001/artifacts/files/evidence.json) · [out/evaluation.md](rounds/r001/artifacts/files/out/evaluation.md) · [out/gates.json](rounds/r001/artifacts/files/out/gates.json) · [out/notes.txt](rounds/r001/artifacts/files/out/notes.txt) · [out/review.html](rounds/r001/artifacts/files/out/review.html) · [out/review.md](rounds/r001/artifacts/files/out/review.md) · [out/source-map.json](rounds/r001/artifacts/files/out/source-map.json) · [review.md](rounds/r001/artifacts/files/review.md)
- 第 2 轮 · REVERT：[evidence.json](rounds/r002/artifacts/files/evidence.json) · [out/evaluation.md](rounds/r002/artifacts/files/out/evaluation.md) · [out/gates.json](rounds/r002/artifacts/files/out/gates.json) · [out/notes.txt](rounds/r002/artifacts/files/out/notes.txt) · [out/review.html](rounds/r002/artifacts/files/out/review.html) · [out/review.md](rounds/r002/artifacts/files/out/review.md) · [out/source-map.json](rounds/r002/artifacts/files/out/source-map.json) · [review.md](rounds/r002/artifacts/files/review.md)
- 第 3 轮 · REVERT：[evidence.json](rounds/r003/artifacts/files/evidence.json) · [out/evaluation.md](rounds/r003/artifacts/files/out/evaluation.md) · [out/gates.json](rounds/r003/artifacts/files/out/gates.json) · [out/notes.txt](rounds/r003/artifacts/files/out/notes.txt) · [out/review.html](rounds/r003/artifacts/files/out/review.html) · [out/review.md](rounds/r003/artifacts/files/out/review.md) · [out/source-map.json](rounds/r003/artifacts/files/out/source-map.json) · [review.md](rounds/r003/artifacts/files/review.md)
- 最终产物：[evidence.json](artifacts/final/files/evidence.json) · [out/evaluation.md](artifacts/final/files/out/evaluation.md) · [out/gates.json](artifacts/final/files/out/gates.json) · [out/notes.txt](artifacts/final/files/out/notes.txt) · [out/review.html](artifacts/final/files/out/review.html) · [out/review.md](artifacts/final/files/out/review.md) · [out/source-map.json](artifacts/final/files/out/source-map.json) · [review.md](artifacts/final/files/review.md)
