# RSI run `20261024-001517-historical-sma-backtest`

**Goal:** 修改 strategy.json 的均线窗口、入场差值和仓位比例，在冻结历史数据上改善收益与回撤的折中。
fast_window 为 2..60，slow_window 为 5..120 且大于 fast_window，threshold_bps 为 0..300，allocation 为 0.1..1。
只做多或持有现金，前一天收盘产生信号，次日开盘成交；交易成本和评测期间固定，不能修改。
得分=累计收益百分点-1.5倍最大回撤百分点。至少完成一次买入和卖出，净值必须有限且为正。
阅读 out/report.md 的收益、回撤、成本和交易表后再尝试；这是固定历史上的参数优化演示，不是投资建议或未来收益承诺。

Agent `codex` · judge `command` · branch `rsi/20261024-001517-historical-sma-backtest`

| round | status | score | best | change | why |
|---:|---|---:|---:|---|---|
| 0 | BASELINE | 7.567 | 7.567 | baseline |  |
| 1 | KEEP | 31.215 | 31.215 | 将均线窗口从 3/8 日延长至 10/30 日，保持零入场差值和半仓，预期减少短期反复交易及成本，提高收益减去 1.5 倍最大回撤的得分。 | score 7.567 -> 31.215 |
| 2 | KEEP | 39.857 | 39.857 | 保持 10/30 日均线和零入场差值，将仓位提高至 60%，预期收益增量超过最大回撤增量的 1.5 倍，从而提高得分。 | score 31.215 -> 39.857 |
| 3 | KEEP | 49.058 | 49.058 | 保持 10/30 日均线和零入场差值，将仓位提高至 70%，预期收益增量超过最大回撤增量的 1.5 倍，从而提高得分。 | score 39.857 -> 49.058 |

Stopped: reached 3 rounds.

运行状态：finished。调用费用：工具未提供。

[任务配置](config/rsi.yaml) · [模型与运行参数](config/execution.json)

## 产物版本

- 初始产物：[out/equity-drawdown.png](artifacts/baseline/files/out/equity-drawdown.png) · [out/equity.csv](artifacts/baseline/files/out/equity.csv) · [out/metrics.json](artifacts/baseline/files/out/metrics.json) · [out/report.md](artifacts/baseline/files/out/report.md) · [out/source.json](artifacts/baseline/files/out/source.json) · [out/strategy.json](artifacts/baseline/files/out/strategy.json) · [out/trades.json](artifacts/baseline/files/out/trades.json) · [strategy.json](artifacts/baseline/files/strategy.json)
- 第 1 轮 · KEEP：[out/equity-drawdown.png](rounds/r001/artifacts/files/out/equity-drawdown.png) · [out/equity.csv](rounds/r001/artifacts/files/out/equity.csv) · [out/metrics.json](rounds/r001/artifacts/files/out/metrics.json) · [out/report.md](rounds/r001/artifacts/files/out/report.md) · [out/source.json](rounds/r001/artifacts/files/out/source.json) · [out/strategy.json](rounds/r001/artifacts/files/out/strategy.json) · [out/trades.json](rounds/r001/artifacts/files/out/trades.json) · [strategy.json](rounds/r001/artifacts/files/strategy.json)
- 第 2 轮 · KEEP：[out/equity-drawdown.png](rounds/r002/artifacts/files/out/equity-drawdown.png) · [out/equity.csv](rounds/r002/artifacts/files/out/equity.csv) · [out/metrics.json](rounds/r002/artifacts/files/out/metrics.json) · [out/report.md](rounds/r002/artifacts/files/out/report.md) · [out/source.json](rounds/r002/artifacts/files/out/source.json) · [out/strategy.json](rounds/r002/artifacts/files/out/strategy.json) · [out/trades.json](rounds/r002/artifacts/files/out/trades.json) · [strategy.json](rounds/r002/artifacts/files/strategy.json)
- 第 3 轮 · KEEP：[out/equity-drawdown.png](rounds/r003/artifacts/files/out/equity-drawdown.png) · [out/equity.csv](rounds/r003/artifacts/files/out/equity.csv) · [out/metrics.json](rounds/r003/artifacts/files/out/metrics.json) · [out/report.md](rounds/r003/artifacts/files/out/report.md) · [out/source.json](rounds/r003/artifacts/files/out/source.json) · [out/strategy.json](rounds/r003/artifacts/files/out/strategy.json) · [out/trades.json](rounds/r003/artifacts/files/out/trades.json) · [strategy.json](rounds/r003/artifacts/files/strategy.json)
- 最终产物：[out/equity-drawdown.png](artifacts/final/files/out/equity-drawdown.png) · [out/equity.csv](artifacts/final/files/out/equity.csv) · [out/metrics.json](artifacts/final/files/out/metrics.json) · [out/report.md](artifacts/final/files/out/report.md) · [out/source.json](artifacts/final/files/out/source.json) · [out/strategy.json](artifacts/final/files/out/strategy.json) · [out/trades.json](artifacts/final/files/out/trades.json) · [strategy.json](artifacts/final/files/strategy.json)
