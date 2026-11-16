# D09: Moving-average backtest on fixed historical daily bars

[简体中文](README.zh-CN.md)

This template uses real public historical daily bars for BTCUSDT to show how AI adjusts moving-average windows and position size, then compares results on the same data at the same costs. The strategy is long-only or holds cash. The code doesn't connect to a trading account and places no orders.

```bash
rsi init quant-backtest my-backtest
cd my-backtest
python -m pip install -r requirements.txt
python judge/evaluate.py
rsi check
rsi run --agent codex --rounds 6
```

At initialization, `rsi_init.py` downloads 731 UTC daily bars from 2023-01-01 to 2024-12-31 through the official public API; no account or API key is needed. The template package doesn't bundle market data. If the download fails, it stops with a clear error and doesn't generate synthetic prices to pass off as history; once the network is back, run `python rsi_init.py`. After initialization, the data is written to `judge/prices.csv`, and the source, dates, raw-response SHA256 and CSV SHA256 are written to `judge/source.json`. Every round uses this fixed data offline.

## How it's evaluated

`strategy.json` is the only editable file. `fast_window` is 2–60; `slow_window` is 5–120 and greater than the fast window; `threshold_bps` is 0–300, the minimum margin by which the fast average must exceed the slow one; `allocation` is 0.1–1, the share of cash invested on entry. The default 3/8-day averages at half position are a common short-term starting point. From there, trading frequency, entry conditions and risk exposure can all change.

The evaluation period is fixed at 2023-07-01 to 2024-12-31; earlier data is used only to warm up the moving averages. A trade at today's open uses only closing prices from yesterday and earlier; intraday highs and lows aren't used for strategy decisions. Every buy and sell is charged a 10 bps fee and 5 bps slippage, and the final close-out is charged too. The score is cumulative return in percentage points minus 1.5 × max drawdown in percentage points; there must be at least two trades, and equity must be positive and finite. These costs are demo assumptions, not the current fees of any platform.

`out/report.md` contains the explanation and charts; `equity-drawdown.png` shows equity and drawdown; `equity.csv` holds the full daily curve; `trades.json` holds every simulated trade and its signal date; `strategy.json`, `metrics.json` and `source.json` keep the configuration, metrics and data provenance. In environments without a Chinese font, legend item 1 is the strategy and 2 is buy-and-hold. `outputs: [out]` lets the engine save each round's outputs.

This experiment tunes parameters repeatedly on the same stretch of history, with no independent out-of-sample check. It doesn't indicate future returns and isn't investment advice. The default data covers only one trading pair and two years, so don't draw general conclusions from it.

## Using your own data

Replace `judge/prices.csv` before a new experiment starts. The columns are `date,open,high,low,close,volume`, with `YYYY-MM-DD` dates in ascending order and no duplicates. Keep at least 120 warm-up rows, set the evaluation range, costs and starting cash in `judge/settings.json`, and update the data source and `csv_sha256` in `judge/source.json`. Confirm the data's license and commit before starting a new experiment; don't change the data or scoring within a run.

## Sources, versions and data license

Consulted on 2026-10-23: [Binance's official public data notes](https://github.com/binance/binance-public-data) and [the official Kline API fields](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints). `rsi_init.py` calls `data-api.binance.vision/api/v3/klines` and extracts only the date, open, high, low, close and volume; it doesn't use any trading endpoint. The backtest is implemented with the Python 3.9+ standard library, and the charts use Matplotlib 3.9.4's [subplots](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html); no additional backtest engine is used.

The official data is provided under [CC BY-NC-SA 4.0 and the Binance Vision Dataset Terms](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md). The downloaded data, and the charts and analysis this package derives from it, must keep the attribution, non-commercial and share-alike conditions; they aren't covered by the MIT license of this project's code. The template package distributes only the downloader and the backtest code. The default case is for non-commercial open-source demos, personal historical backtests and teaching.

Real multi-round model records should be saved separately under `examples/quant-backtest/runs/`. The baseline and the program's tests don't count as the model completing an optimization.
