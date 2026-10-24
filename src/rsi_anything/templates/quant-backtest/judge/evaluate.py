"""只读冻结历史日线，在下一日开盘成交的均线回测。"""
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
            raise ValueError(f"{name} 应为 {lower}..{upper} 的整数")
    if config["fast_window"] >= config["slow_window"]:
        raise ValueError("slow_window 必须大于 fast_window")
    for name, lower, upper in (("allocation", 0.1, 1), ("threshold_bps", 0, 300)):
        value = config[name]
        if type(value) not in (int, float) or not lower <= value <= upper:
            raise ValueError(f"{name} 应在 {lower}..{upper} 之间")


def load_prices(path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = [{"date": row["date"], **{key: float(row[key]) for key in ("open", "high", "low", "close", "volume")}}
                for row in csv.DictReader(handle)]
    dates = [row["date"] for row in rows]
    if not rows or dates != sorted(set(dates)):
        raise ValueError("价格日期必须非空、升序、无重复")
    for row in rows:
        date.fromisoformat(row["date"])
        if not all(math.isfinite(row[key]) and row[key] > 0 for key in ("open", "high", "low", "close")):
            raise ValueError("价格必须有限且为正")
        if not row["low"] <= min(row["open"], row["close"]) <= max(row["open"], row["close"]) <= row["high"]:
            raise ValueError("开高低收关系不合法")
    return rows


def backtest(prices, config, settings):
    validate(config)
    chosen = [index for index, row in enumerate(prices)
              if settings["evaluation_start"] <= row["date"] <= settings["evaluation_end"]]
    if len(chosen) < 30 or chosen[0] < config["slow_window"]:
        raise ValueError("评测区间至少 30 条，且区间之前需要足够的均线预热数据")
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
        # 信号只用昨天及更早收盘价，当前日开盘成交。
        if wanted and units == 0:
            notional = cash * config["allocation"] / (1 + cost_rate)
            fee = notional * cost_rate
            units = notional / row["open"]
            cash -= notional + fee
            total_cost += fee
            trades.append({"date": row["date"], "side": "买入", "price": row["open"], "units": units,
                           "cost": fee, "signal_date": prices[index - 1]["date"]})
        elif not wanted and units:
            notional = units * row["open"]
            fee = notional * cost_rate
            cash += notional - fee
            total_cost += fee
            trades.append({"date": row["date"], "side": "卖出", "price": row["open"], "units": units,
                           "cost": fee, "signal_date": prices[index - 1]["date"]})
            units = 0.0
        equity = cash + units * row["close"]
        benchmark = benchmark_units * row["close"]
        if index == chosen[-1]:
            if units:
                fee = units * row["close"] * cost_rate
                trades.append({"date": row["date"], "side": "期末平仓", "price": row["close"],
                               "units": units, "cost": fee, "signal_date": "评测期末"})
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
    feedback = (f"累计收益 {gain:.2f}%，最大回撤 {drawdown:.2f}%，模拟成交 {len(trades)} 笔，"
                f"费用与滑点合计 {total_cost:.2f} USDT。得分为收益减去 {settings['drawdown_penalty']} 倍回撤。")
    return {"score": round(gain - settings["drawdown_penalty"] * drawdown, 3), "gates": gates,
            "feedback": feedback, "metrics": metrics}, curve, trades


def plot(curve, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    available = {font.name for font in font_manager.fontManager.ttflist}
    font = next((name for name in ("PingFang SC", "Arial Unicode MS", "Noto Sans CJK SC", "Microsoft YaHei")
                 if name in available), None)
    if font:
        plt.rcParams["font.sans-serif"] = [font]
    dates = [date.fromisoformat(row["date"]) for row in curve]
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    axes[0].plot(dates, [row["equity"] for row in curve], color="#287758", label="策略" if font else "1")
    axes[0].plot(dates, [row["buy_hold"] for row in curve], color="#a0a7b2", label="持有基准" if font else "2")
    axes[0].legend()
    axes[0].set_ylabel("资产 / USDT" if font else "USDT")
    axes[1].fill_between(dates, [-row["drawdown_percent"] for row in curve], 0, color="#ca7964", alpha=0.6)
    axes[1].set_ylabel("回撤 / %" if font else "%")
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
            raise ValueError("价格数据 SHA256 与来源记录不符，请在新实验中重新冻结输入")
        payload, curve, trades = backtest(load_prices(path), config, settings)
        payload["metrics"]["data_sha256"] = actual_sha
        for name, content in (("trades.json", trades), ("strategy.json", config), ("source.json", source)):
            (out / name).write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with (out / "equity.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(curve[0]))
            writer.writeheader()
            writer.writerows(curve)
        plot(curve, out)
        report = ("# 固定历史上的均线回测\n\n" + payload["feedback"] + "\n\n"
                  "![资产与回撤](equity-drawdown.png)\n\n绿色为策略，灰色为同期买入持有；下图为策略回撤。"
                  "初始资产 10000 USDT，无杠杆、无卖空；每次成交按 10 基点费用加 5 基点滑点计算。"
                  "信号在前一日收盘形成，次日开盘执行，期末按收盘价平仓并计成本。\n\n"
                  "这些结果来自同一段固定历史上的反复调参，只用于展示程序和参数迭代。"
                  "它不是独立样本外回测，不代表未来收益，也不提供投资建议。\n\n"
                  "数据来源：Binance Vision BTCUSDT 日线。数据、图表及派生分析按 CC BY-NC-SA 4.0 提供，"
                  "仅用于非商业研究与教学；来源链接及 SHA256 见 source.json。\n\n"
                  "## 当前策略\n\n```json\n" + json.dumps(config, ensure_ascii=False, indent=2) + "\n```\n")
        report += "\n## 模拟成交\n\n| 日期 | 方向 | 成交价 | 数量 | 成本 | 信号日期 |\n|---|---|---:|---:|---:|---|\n"
        report += "\n".join(f"| {row['date']} | {row['side']} | {row['price']:.2f} | {row['units']:.6f} | "
                            f"{row['cost']:.2f} | {row['signal_date']} |" for row in trades) + "\n"
        (out / "report.md").write_text(report, encoding="utf-8")
    except Exception as exc:
        payload = {"score": 0, "gates": {"backtest_completed": False},
                   "feedback": f"回测未完成：{type(exc).__name__}: {exc}。检查历史数据和 requirements.txt 依赖。", "metrics": {}}
        (out / "report.md").write_text("# 回测检查\n\n" + payload["feedback"] + "\n", encoding="utf-8")
    (out / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.environ.get("RSI_RESULT"):
        Path(os.environ["RSI_RESULT"]).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
