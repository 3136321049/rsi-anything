# RSI run `20261024-003730-percent-lesson`

**Goal:** 修改 lesson.md，为初中学生解释百分比、变化率、还原原量、连续变化和百分点的区别。
可以调整结构、例题与逐步解释，遵循 judge/brief.md；不要逐题抄写 judge/exercises.json 的测试题答案。
评分时受限学生模型只看到讲义和题目，需给答案、推理及讲义原句依据；程序按固定答案实际判分。

Agent `codex` · judge `command` · branch `rsi/20261024-003730-percent-lesson`

| round | status | score | best | change | why |
|---:|---|---:|---:|---|---|
| 0 | BASELINE | 20 | 20 | baseline |  |
| 1 | KEEP | 100 | 100 | 围绕“部分＝整体×比例”补齐逆向求解和整体变化的判断方法，应能减少因讲义缺少方法而无法作答的情况，提高得分。 | score 20 -> 100 |
| 2 | REVERT | 100 | 100 | 补清“各步倍数连乘后与1比较”的方法，减少连续变化中误加减百分比的错误，提高作答稳定性。 | score 100 is not better than 100 (required margin: 1 or 0%) |
| 3 | REVERT | 100 | 100 | 补清变化量与变化后数量的区别，减少还原原量时选错比例的错误，提高作答稳定性；当前已满分，无法进一步提高分数。 | score 100 is not better than 100 (required margin: 1 or 0%) |

Stopped: reached 3 rounds.

运行状态：finished。已保存 4 条模型调用记录；调用费用：工具未提供。

[任务配置](config/rsi.yaml) · [模型与运行参数](config/execution.json)

## 产物版本

- 初始产物：[lesson.md](artifacts/baseline/files/lesson.md) · [out/exercise-results.md](artifacts/baseline/files/out/exercise-results.md) · [out/gates.json](artifacts/baseline/files/out/gates.json) · [out/lesson.html](artifacts/baseline/files/out/lesson.html) · [out/lesson.md](artifacts/baseline/files/out/lesson.md) · [out/mistakes.json](artifacts/baseline/files/out/mistakes.json) · [out/results.json](artifacts/baseline/files/out/results.json) · [out/student-response.txt](artifacts/baseline/files/out/student-response.txt)
  来源：独立评审目录。正式分数以账本记录和评审结论为准。
- 第 1 轮 · KEEP：[lesson.md](rounds/r001/artifacts/files/lesson.md) · [out/exercise-results.md](rounds/r001/artifacts/files/out/exercise-results.md) · [out/gates.json](rounds/r001/artifacts/files/out/gates.json) · [out/lesson.html](rounds/r001/artifacts/files/out/lesson.html) · [out/lesson.md](rounds/r001/artifacts/files/out/lesson.md) · [out/mistakes.json](rounds/r001/artifacts/files/out/mistakes.json) · [out/results.json](rounds/r001/artifacts/files/out/results.json) · [out/student-response.txt](rounds/r001/artifacts/files/out/student-response.txt)
  来源：独立评审目录。正式分数以账本记录和评审结论为准。
- 第 2 轮 · REVERT：[lesson.md](rounds/r002/artifacts/files/lesson.md) · [out/exercise-results.md](rounds/r002/artifacts/files/out/exercise-results.md) · [out/gates.json](rounds/r002/artifacts/files/out/gates.json) · [out/lesson.html](rounds/r002/artifacts/files/out/lesson.html) · [out/lesson.md](rounds/r002/artifacts/files/out/lesson.md) · [out/mistakes.json](rounds/r002/artifacts/files/out/mistakes.json) · [out/results.json](rounds/r002/artifacts/files/out/results.json) · [out/student-response.txt](rounds/r002/artifacts/files/out/student-response.txt)
  来源：独立评审目录。正式分数以账本记录和评审结论为准。
- 第 3 轮 · REVERT：[lesson.md](rounds/r003/artifacts/files/lesson.md) · [out/exercise-results.md](rounds/r003/artifacts/files/out/exercise-results.md) · [out/gates.json](rounds/r003/artifacts/files/out/gates.json) · [out/lesson.html](rounds/r003/artifacts/files/out/lesson.html) · [out/lesson.md](rounds/r003/artifacts/files/out/lesson.md) · [out/mistakes.json](rounds/r003/artifacts/files/out/mistakes.json) · [out/results.json](rounds/r003/artifacts/files/out/results.json) · [out/student-response.txt](rounds/r003/artifacts/files/out/student-response.txt)
  来源：独立评审目录。正式分数以账本记录和评审结论为准。
- 最终产物：[lesson.md](artifacts/final/files/lesson.md) · [out/exercise-results.md](artifacts/final/files/out/exercise-results.md) · [out/gates.json](artifacts/final/files/out/gates.json) · [out/lesson.html](artifacts/final/files/out/lesson.html) · [out/lesson.md](artifacts/final/files/out/lesson.md) · [out/mistakes.json](artifacts/final/files/out/mistakes.json) · [out/results.json](artifacts/final/files/out/results.json) · [out/student-response.txt](artifacts/final/files/out/student-response.txt)
  来源：已保存的评审版本 rounds/r001/artifacts。复制最终作品不会新增评分；正式分数以账本和评审结论为准。
