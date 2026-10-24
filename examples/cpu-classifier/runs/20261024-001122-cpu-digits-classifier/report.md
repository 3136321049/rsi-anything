# RSI run `20261024-001122-cpu-digits-classifier`

**Goal:** 修改 training.json，提高固定划分的手写数字验证集正确率；观察 out/report.md 和错例图选择下一次实验。
可改分类器和预处理：model 为 tree/knn/svm/random_forest，scaling 为 none/standard/minmax，pca_components 为 0 或 2..64。
各分类器允许参数及范围见 README.md。冻结的数据、划分、评分程序不能修改。
一次训练与预测需在 30 秒内完成；得分为验证集正确率百分数，至少提高 0.1 分才保留。
每轮优先测试一个有理由的参数或模型变化，不允许针对样本编号写死答案。

Agent `codex` · judge `command` · branch `rsi/20261024-001122-cpu-digits-classifier`

| round | status | score | best | change | why |
|---:|---|---:|---:|---|---|
| 0 | BASELINE | 46.889 | 46.889 | baseline |  |
| 1 | KEEP | 99.333 | 99.333 | 将三层决策树替换为 RBF 核 SVM（C=10、gamma=scale），保留原始像素且不降维，通过更灵活的分类边界提高正确率。 | score 46.889 -> 99.333 |
| 2 | NO_CHANGE | - | 99.333 | 测试增大 gamma，让分类边界更关注局部笔画差异，期望改善数字 5、9 的识别；评分未支持该假设，已撤销。 | no edits inside the artifact paths |
| 3 | NO_CHANGE | - | 99.333 | 测试将 pca_components 从 0 改为 40，希望减少像素噪声、改善数字 5 和 9 的识别；评分未支持该假设，已撤销。 | no edits inside the artifact paths |

Stopped: reached 3 rounds.

运行状态：finished。调用费用：工具未提供。

[任务配置](config/rsi.yaml) · [模型与运行参数](config/execution.json)

## 产物版本

- 初始产物：[out/confusion.png](artifacts/baseline/files/out/confusion.png) · [out/metrics.json](artifacts/baseline/files/out/metrics.json) · [out/mistakes.json](artifacts/baseline/files/out/mistakes.json) · [out/mistakes.png](artifacts/baseline/files/out/mistakes.png) · [out/predictions.json](artifacts/baseline/files/out/predictions.json) · [out/report.md](artifacts/baseline/files/out/report.md) · [out/split.json](artifacts/baseline/files/out/split.json) · [out/training.json](artifacts/baseline/files/out/training.json) · [training.json](artifacts/baseline/files/training.json)
- 第 1 轮 · KEEP：[out/confusion.png](rounds/r001/artifacts/files/out/confusion.png) · [out/metrics.json](rounds/r001/artifacts/files/out/metrics.json) · [out/mistakes.json](rounds/r001/artifacts/files/out/mistakes.json) · [out/mistakes.png](rounds/r001/artifacts/files/out/mistakes.png) · [out/predictions.json](rounds/r001/artifacts/files/out/predictions.json) · [out/report.md](rounds/r001/artifacts/files/out/report.md) · [out/split.json](rounds/r001/artifacts/files/out/split.json) · [out/training.json](rounds/r001/artifacts/files/out/training.json) · [training.json](rounds/r001/artifacts/files/training.json)
- 第 2 轮 · NO_CHANGE：[out/confusion.png](rounds/r002/artifacts/files/out/confusion.png) · [out/metrics.json](rounds/r002/artifacts/files/out/metrics.json) · [out/mistakes.json](rounds/r002/artifacts/files/out/mistakes.json) · [out/mistakes.png](rounds/r002/artifacts/files/out/mistakes.png) · [out/predictions.json](rounds/r002/artifacts/files/out/predictions.json) · [out/report.md](rounds/r002/artifacts/files/out/report.md) · [out/split.json](rounds/r002/artifacts/files/out/split.json) · [out/training.json](rounds/r002/artifacts/files/out/training.json) · [training.json](rounds/r002/artifacts/files/training.json)
- 第 3 轮 · NO_CHANGE：[out/confusion.png](rounds/r003/artifacts/files/out/confusion.png) · [out/metrics.json](rounds/r003/artifacts/files/out/metrics.json) · [out/mistakes.json](rounds/r003/artifacts/files/out/mistakes.json) · [out/mistakes.png](rounds/r003/artifacts/files/out/mistakes.png) · [out/predictions.json](rounds/r003/artifacts/files/out/predictions.json) · [out/report.md](rounds/r003/artifacts/files/out/report.md) · [out/split.json](rounds/r003/artifacts/files/out/split.json) · [out/training.json](rounds/r003/artifacts/files/out/training.json) · [training.json](rounds/r003/artifacts/files/training.json)
- 最终产物：[out/confusion.png](artifacts/final/files/out/confusion.png) · [out/metrics.json](artifacts/final/files/out/metrics.json) · [out/mistakes.json](artifacts/final/files/out/mistakes.json) · [out/mistakes.png](artifacts/final/files/out/mistakes.png) · [out/predictions.json](artifacts/final/files/out/predictions.json) · [out/report.md](artifacts/final/files/out/report.md) · [out/split.json](artifacts/final/files/out/split.json) · [out/training.json](artifacts/final/files/out/training.json) · [training.json](artifacts/final/files/training.json)
