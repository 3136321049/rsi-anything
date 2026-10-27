# D09: Three rounds of strategy-parameter tuning on fixed history

[简体中文](README.md)

On 2026-10-24, the Codex CLI on a personal ChatGPT account ran 3 real rounds. The AI edited `strategy.json`, and a fixed Python backtest program computed the results; there was no model judge and no real trading. Initialization downloaded 731 BTCUSDT daily bars through the official public API. The evaluation period is 2023-07-01 to 2024-12-31, 550 days in total; earlier prices are used to warm up the moving averages.

| Version | Score | Cumulative return | Max drawdown | Trades | Total costs (USDT) | Configuration change |
|---|---:|---:|---:|---:|---:|---|
| Starting | 7.567 | 27.7220% | 13.4370% | 76 | 638.4787 | 3/8-day moving averages, half position |
| Round 1, kept | 31.215 | 63.2489% | 21.3557% | 16 | 167.3999 | Lengthened to 10/30-day moving averages |
| Round 2, kept | 39.857 | 77.0542% | 24.7979% | 16 | 210.5015 | Position size raised from 50% to 60% |
| Round 3, kept | 49.058 | 91.1240% | 28.0442% | 16 | 256.8869 | Position size raised from 60% to 70% |

The score is fixed as "cumulative return in percentage points − 1.5 × max drawdown in percentage points". Round 1 cut whipsaw trading and costs. The next two rounds raised the position size: **returns went up, and so did max drawdown**. This case shows parameter iteration under a fixed score, not lower risk. Over the same period, buy-and-hold at full position had a cumulative return of 206.1687%. The charts always keep that reference, and there's no claim that the strategy beat holding.

[Full run report](runs/20261024-001517-historical-sma-backtest/report.html) · [Starting curve](runs/20261024-001517-historical-sma-backtest/artifacts/baseline/files/out/equity-drawdown.png) · [Final equity and drawdown](runs/20261024-001517-historical-sma-backtest/artifacts/final/files/out/equity-drawdown.png) · [Final report and trade table](runs/20261024-001517-historical-sma-backtest/artifacts/final/files/out/report.md) · [Final strategy](runs/20261024-001517-historical-sma-backtest/artifacts/final/files/strategy.json) · [Independent re-verification](runs/20261024-001517-historical-sma-backtest/verification.json)

Starting cash is 10000 USDT, long-only or cash, with no leverage and no short selling. Signals use only closing prices from the previous day and earlier, and trades fill at the next day's open. Every trade is charged a 10 bps fee and 5 bps slippage, and the final close-out is charged the same way. These are fixed assumptions, not any platform's current fees.

The AI explicitly requested `gpt-6.1-sol` with `medium` reasoning effort, using an isolated configuration. The CLI didn't return the model the service actually used, so `actual_model` is `null`; usage is recorded as returned, and the cost in US dollars wasn't returned. Each round's candidate was a real edit by the model. All three rounds were kept, and the run ended normally on reaching its round count.

The exported starting configuration, the three candidates and the final configuration were each placed in a fresh temporary directory with the frozen prices, costs and backtest program, old outputs were deleted, and each was rerun independently. Every score, return, drawdown and trade count matched the original records. Each trade was checked to confirm that its signal date comes before its fill date, and the final close-out is marked separately. The data SHA256 is `b9dd21e29974b4c13babd79214e43a15829abf52580d3d23c0c6450c1053b8d3`.

To reproduce it, sign in to your own Codex, install the template's `requirements.txt` into the Python that runs `rsi`, and run this from the repository root:

```bash
python scripts/run_demo.py quant-backtest --model gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

Set `RSI_CODEX_BIN` if you need to point to a specific CLI path. Template initialization downloads the public history once; every round after that is reviewed offline. The source links, collection time, and the SHA256 of the raw response and of the CSV are kept in `source.json` in the exported record.

This experiment tuned parameters repeatedly on the same stretch of history, with no independent out-of-sample check. It doesn't indicate future returns and isn't investment advice. Market data comes from [Binance's official market data API](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints). The data, curves and derived analysis follow [CC BY-NC-SA 4.0 and the official data terms](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md) and are for non-commercial research, teaching and open-source demos; these data rights are separate from this project's code license. The template package doesn't bundle market data; this experiment record keeps the data actually used, with attribution.
