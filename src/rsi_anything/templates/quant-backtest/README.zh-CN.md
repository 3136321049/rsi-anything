# D09：固定历史日线上的均线回测

[English](README.md)

使用真实的 BTCUSDT 公开历史日线，演示 AI 如何调整均线窗口与仓位，再用相同数据、相同成本比较结果。策略只做多或持有现金，代码不连接交易账户，不下单。

```bash
rsi init quant-backtest my-backtest
cd my-backtest
python -m pip install -r requirements.txt
python judge/evaluate.py
rsi check
rsi run --agent codex --rounds 6
```

初始化时，`rsi_init.py` 从官方公开接口下载 2023-01-01 至 2024-12-31 的 731 条 UTC 日线，不需要账号或 API Key。模板包不捆绑行情。下载失败会明确停止，不生成合成行情冒充历史；网络恢复后运行 `python rsi_init.py`。初始化完成后，数据写入 `judge/prices.csv`，来源、日期、原始响应 SHA256 与 CSV SHA256 写入 `judge/source.json`，每轮离线使用这份固定数据。

## 怎么评价

`strategy.json` 是唯一可改文件。`fast_window` 为 2–60，`slow_window` 为 5–120 且大于快窗口；`threshold_bps` 为 0–300，表示快均线超过慢均线的最小幅度；`allocation` 为 0.1–1，表示入场时投入多少现金。默认 3/8 日均线配半仓是常见的短周期起点，可以改变交易频率、入场条件和风险暴露。

评价区间固定为 2023-07-01 至 2024-12-31，之前数据只用于均线预热。当前开盘成交只使用昨天及更早的收盘价；日内最高/最低价不用于策略决策。每次买卖扣 10 基点费用与 5 基点滑点，期末平仓也收费。得分为累计收益百分点减去 1.5 倍最大回撤百分点；至少有两笔成交，净值须为正且有限。这些成本是演示假设，不代表当前任何平台的费率。

`out/report.md` 包含解释与图；`equity-drawdown.png` 是净值和回撤；`equity.csv` 保存每日完整曲线；`trades.json` 保存每笔模拟成交及对应信号日期；`strategy.json`、`metrics.json`、`source.json` 保留配置、指标及数据凭证。使用无中文字体的环境时，图例 1 为策略、2 为买入持有。`outputs: [out]` 供引擎保存每轮产物。

本实验在同一段历史上反复调参，没有独立样本外验收，不代表未来收益，也不提供投资建议。默认数据仅涵盖一个交易对和两年，不据此归纳普遍效果。

## 换自己的数据

在新实验开始前替换 `judge/prices.csv`：列为 `date,open,high,low,close,volume`，日期 `YYYY-MM-DD` 升序且无重复。保留至少 120 条预热记录，在 `judge/settings.json` 设置评测范围、成本和初始现金，并更新 `judge/source.json` 的数据来源与 `csv_sha256`。先核实数据使用许可并提交，再开新实验；不在一条运行中改变数据或评分。

## 来源、版本与数据授权

2026-10-23 查阅 [Binance 官方公共数据说明](https://github.com/binance/binance-public-data) 和 [Kline 官方接口字段](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints)。`rsi_init.py` 实际调用 `data-api.binance.vision/api/v3/klines`，只提取日期与开高低收成交量，不使用交易接口。回测由 Python 3.9+ 标准库实现，绘图使用 Matplotlib 3.9.4 的 [subplots](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html)，没有引入额外回测引擎。

官方数据按 [CC BY-NC-SA 4.0 及 Binance Vision Dataset Terms](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md) 提供。下载的数据与本包生成的派生图表、分析需要保留来源、非商业及相同方式共享条件；不属于本项目代码的 MIT 许可。模板包只分发下载器与回测代码。默认案例供非商业开源演示、个人历史回测与教学使用。

真实模型多轮记录应另存 `examples/quant-backtest/runs/`。基线和程序测试不算模型完成了优化。
