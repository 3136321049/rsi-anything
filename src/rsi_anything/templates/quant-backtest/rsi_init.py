"""Download public historical prices once and record the source; every round reads only the frozen local data."""
import csv
import hashlib
import io
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = ("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d"
       "&startTime=1672531200000&endTime=1735689599999&limit=1000")


def save_data(raw, root):
    rows = json.loads(raw)
    if not isinstance(rows, list) or len(rows) != 731 or any(not isinstance(row, list) or len(row) < 6 for row in rows):
        raise ValueError("the public API did not return the expected 731 daily bars; no substitute or synthetic data is used")
    dates = [datetime.fromtimestamp(row[0] / 1000, timezone.utc).date().isoformat() for row in rows]
    if dates[0] != "2023-01-01" or dates[-1] != "2024-12-31" or len(set(dates)) != 731:
        raise ValueError("the historical data date range does not match")
    text = io.StringIO(newline="")
    writer = csv.writer(text, lineterminator="\n")
    writer.writerow(["date", "open", "high", "low", "close", "volume"])
    for date, row in zip(dates, rows):
        writer.writerow([date, *row[1:6]])
    data = text.getvalue().encode("utf-8")
    (root / "judge/prices.csv").write_bytes(data)
    source = {"provider": "Binance Vision", "symbol": "BTCUSDT", "interval": "1d", "timezone": "UTC",
              "url": URL, "accessed_utc": datetime.now(timezone.utc).isoformat(), "first_date": dates[0],
              "last_date": dates[-1], "rows": len(rows), "raw_sha256": hashlib.sha256(raw).hexdigest(),
              "csv_sha256": hashlib.sha256(data).hexdigest(), "license": "CC BY-NC-SA 4.0",
              "terms_url": "https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md"}
    (root / "judge/source.json").write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return source


def main():
    root = Path(__file__).resolve().parent
    target = root / "judge/prices.csv"
    if target.exists() and (root / "judge/source.json").exists():
        print("Frozen historical prices already exist; not downloading again.")
        return
    try:
        request = urllib.request.Request(URL, headers={"User-Agent": "RSI-Anything historical demo"})
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read()
        source = save_data(raw, root)
    except Exception as exc:
        raise SystemExit(f"Preparing the historical data failed: {exc}. Fix the network, then run python rsi_init.py in this folder.")
    print(f"Saved {source['rows']} public daily bars; the data and derived outputs are labeled CC BY-NC-SA 4.0.")


if __name__ == "__main__":
    main()
