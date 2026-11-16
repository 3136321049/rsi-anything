"""Moving-average backtest on frozen historical daily bars only, filling at the next day's open."""
import csv
import hashlib
import json
import math
import os
import statistics
from datetime import date
from pathlib import Path


def validate(config):
    for name, lower, upper in (("fast_window", 2, 60), ("slow_window", 5, 120)):
        value = config[name]
        if type(value) is not int or not lower <= value <= upper:
            raise ValueError(f"{name} must be an integer in {lower}..{upper}")
    if config["fast_window"] >= config["slow_window"]:
        raise ValueError("slow_window must be greater than fast_window")
    for name, lower, upper in (("allocation", 0.1, 1), ("threshold_bps", 0, 300)):
        value = config[name]
        if type(value) not in (int, float) or not lower <= value <= upper:
            raise ValueError(f"{name} must be between {lower} and {upper}")


def load_prices(path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = [{"date": row["date"], **{key: float(row[key]) for key in ("open", "high", "low", "close", "volume")}}
                for row in csv.DictReader(handle)]
    dates = [row["date"] for row in rows]
    if not rows or dates != sorted(set(dates)):
        raise ValueError("price dates must be non-empty, ascending and without duplicates")
    for row in rows:
        date.fromisoformat(row["date"])
        if not all(math.isfinite(row[key]) and row[key] > 0 for key in ("open", "high", "low", "close")):
            raise ValueError("prices must be finite and positive")
        if not row["low"] <= min(row["open"], row["close"]) <= max(row["open"], row["close"]) <= row["high"]:
            raise ValueError("invalid open/high/low/close relationship")
    return rows


def backtest(prices, config, settings):
    validate(config)
    chosen = [index for index, row in enumerate(prices)
              if settings["evaluation_start"] <= row["date"] <= settings["evaluation_end"]]
    if len(chosen) < 30 or chosen[0] < config["slow_window"]:
        raise ValueError("the evaluation window needs at least 30 bars and enough moving-average warm-up data before it")
    cost_rate = (settings["fee_bps"] + settings["slippage_bps"]) / 10000
    cash, units = float(settings["initial_cash"]), 0.0
    trades, curve, closes = [], [], [row["close"] for row in prices]
    total_cost, peak = 0.0, cash
    benchmark_units = cash / (prices[chosen[0]]["open"] * (1 + cost_rate))
    for index in chosen:
        row = prices[index]
        fast = statistics.mean(closes[index - config["fast_window"]:index])
        slow = statistics.mean(closes[index - config["slow_window"]:index])
        wanted = fast > slow * (1 + config["threshold_bps"] / 10000)
        # Signals use only yesterday's and earlier closes; orders fill at today's open.
        if wanted and units == 0:
            notional = cash * config["allocation"] / (1 + cost_rate)
            fee = notional * cost_rate
            units = notional / row["open"]
            cash -= notional + fee
            total_cost += fee
            trades.append({"date": row["date"], "side": "buy", "price": row["open"], "units": units,
                           "cost": fee, "signal_date": prices[index - 1]["date"]})
        elif not wanted and units:
            notional = units * row["open"]
            fee = notional * cost_rate
            cash += notional - fee
            total_cost += fee
            trades.append({"date": row["date"], "side": "sell", "price": row["open"], "units": units,
                           "cost": fee, "signal_date": prices[index - 1]["date"]})
            units = 0.0
        equity = cash + units * row["close"]
        benchmark = benchmark_units * row["close"]
        if index == chosen[-1]:
            if units:
                fee = units * row["close"] * cost_rate
                trades.append({"date": row["date"], "side": "close_at_end", "price": row["close"],
                               "units": units, "cost": fee, "signal_date": "end_of_evaluation"})
                total_cost += fee
                equity -= fee
                units = 0.0
            benchmark *= 1 - cost_rate
        peak = max(peak, equity)
        curve.append({"date": row["date"], "equity": equity, "buy_hold": benchmark,
                      "drawdown_percent": 100 * (1 - equity / peak), "position_units": units})
    gain = 100 * (curve[-1]["equity"] / settings["initial_cash"] - 1)
    drawdown = max(row["drawdown_percent"] for row in curve)
    metrics = {"return_percent": round(gain, 4), "max_drawdown_percent": round(drawdown, 4),
               "buy_hold_return_percent": round(100 * (curve[-1]["buy_hold"] / settings["initial_cash"] - 1), 4),
               "trade_orders": len(trades), "total_cost": round(total_cost, 4),
               "starting_cash": settings["initial_cash"], "ending_equity": round(curve[-1]["equity"], 4),
               "evaluation_start": curve[0]["date"], "evaluation_end": curve[-1]["date"],
               "observations": len(curve), "cost_bps_per_side": cost_rate * 10000, "configuration": config}
    gates = {"positive_finite_equity": all(math.isfinite(row["equity"]) and row["equity"] > 0 for row in curve),
             "minimum_trades": len(trades) >= settings["minimum_trade_orders"]}
    feedback = (f"Cumulative return {gain:.2f}%, maximum drawdown {drawdown:.2f}%, {len(trades)} simulated fills, "
                f"fees and slippage {total_cost:.2f} USDT in total. Score = return minus {settings['drawdown_penalty']} x drawdown.")
    return {"score": round(gain - settings["drawdown_penalty"] * drawdown, 3), "gates": gates,
            "feedback": feedback, "metrics": metrics}, curve, trades


def plot(curve, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dates = [date.fromisoformat(row["date"]) for row in curve]
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    axes[0].plot(dates, [row["equity"] for row in curve], color="#287758", label="Strategy")
    axes[0].plot(dates, [row["buy_hold"] for row in curve], color="#a0a7b2", label="Buy and hold")
    axes[0].legend()
    axes[0].set_ylabel("Equity / USDT")
    axes[1].fill_between(dates, [-row["drawdown_percent"] for row in curve], 0, color="#ca7964", alpha=0.6)
    axes[1].set_ylabel("Drawdown / %")
    for axis in axes:
        axis.grid(alpha=0.2)
    fig.autofmt_xdate()
    fig.text(0.5, 0.01, "Binance Vision · CC BY-NC-SA 4.0", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(out / "equity-drawdown.png", dpi=140)
    plt.close(fig)


def main():
    out = Path("out")
    out.mkdir(exist_ok=True)
    for name in ("metrics.json", "report.md", "equity.csv", "trades.json", "strategy.json", "source.json", "equity-drawdown.png"):
        if (out / name).is_file():
            (out / name).unlink()
    try:
        config = json.loads(Path("strategy.json").read_text())
        settings = json.loads(Path("judge/settings.json").read_text())
        source = json.loads(Path("judge/source.json").read_text())
        path = Path("judge/prices.csv")
        actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_sha != source["csv_sha256"]:
            raise ValueError("the price data SHA256 does not match the source record; freeze the inputs again in a new experiment")
        payload, curve, trades = backtest(load_prices(path), config, settings)
        payload["metrics"]["data_sha256"] = actual_sha
        for name, content in (("trades.json", trades), ("strategy.json", config), ("source.json", source)):
            (out / name).write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with (out / "equity.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(curve[0]))
            writer.writeheader()
            writer.writerows(curve)
        plot(curve, out)
        report = ("# Moving-average backtest on fixed history\n\n" + payload["feedback"] + "\n\n"
                  "![Equity and drawdown](equity-drawdown.png)\n\nGreen is the strategy and grey is buy-and-hold over the same period; "
                  "the lower panel is the strategy's drawdown. Starting equity is 10000 USDT, with no leverage and no short selling; "
                  "every fill is charged a 10 basis point fee plus 5 basis points of slippage. "
                  "Signals form at the previous day's close and execute at the next day's open; the position is closed at the "
                  "final close, with costs.\n\n"
                  "These results come from repeated parameter tuning on the same fixed stretch of history and only demonstrate "
                  "the program and the parameter iteration. This is not an independent out-of-sample backtest, does not "
                  "represent future returns and is not investment advice.\n\n"
                  "Data source: Binance Vision BTCUSDT daily bars. The data, charts and derived analysis are provided under "
                  "CC BY-NC-SA 4.0 for non-commercial research and teaching only; the source link and SHA256 are in source.json.\n\n"
                  "## Current strategy\n\n```json\n" + json.dumps(config, ensure_ascii=False, indent=2) + "\n```\n")
        report += "\n## Simulated fills\n\n| Date | Side | Price | Units | Cost | Signal date |\n|---|---|---:|---:|---:|---|\n"
        report += "\n".join(f"| {row['date']} | {row['side']} | {row['price']:.2f} | {row['units']:.6f} | "
                            f"{row['cost']:.2f} | {row['signal_date']} |" for row in trades) + "\n"
        (out / "report.md").write_text(report, encoding="utf-8")
    except Exception as exc:
        payload = {"score": 0, "gates": {"backtest_completed": False},
                   "feedback": f"The backtest did not finish: {type(exc).__name__}: {exc}. Check the historical data and the requirements.txt dependencies.", "metrics": {}}
        (out / "report.md").write_text("# Backtest check\n\n" + payload["feedback"] + "\n", encoding="utf-8")
    (out / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.environ.get("RSI_RESULT"):
        Path(os.environ["RSI_RESULT"]).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
