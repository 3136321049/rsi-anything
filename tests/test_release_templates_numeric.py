"""Check the domain judges and outputs; these fixed tests do not stand for real multi-round model runs."""
import importlib.util
import datetime
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from rsi_anything.contract import load

TEMPLATES = Path(__file__).resolve().parents[1] / "src/rsi_anything/templates"


def project(tmp_path, name):
    target = tmp_path / name
    shutil.copytree(TEMPLATES / name, target, ignore=shutil.ignore_patterns("out", "__pycache__"))
    return target


def evaluate(root):
    result = root / "result.json"
    completed = subprocess.run([sys.executable, "judge/evaluate.py"], cwd=root, text=True, capture_output=True,
                               timeout=90, env={**os.environ, "RSI_RESULT": str(result), "MPLBACKEND": "Agg"})
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert result.exists(), completed.stdout + completed.stderr
    return json.loads(result.read_text())


@pytest.mark.parametrize("name", ["code-repair", "cpu-classifier", "weekly-planner", "quant-backtest"])
def test_numeric_template_contract(name):
    contract = load(TEMPLATES / name)
    assert contract.judge.type == "command"
    assert contract.judge.run == "{python} judge/evaluate.py"
    assert contract.budget.rounds >= 2


def test_repair_reports_real_partial_failures_and_example(tmp_path):
    root = project(tmp_path, "code-repair")
    result = evaluate(root)
    assert all(result["gates"].values())
    assert 0 < result["score"] < 100
    details = json.loads((root / "out/tests.json").read_text())
    assert details["total"] == 15
    assert details["passed"] + len(details["failed"]) == 15
    assert any("test_month_refund" in row["test"] for row in details["failed"])
    assert json.loads((root / "out/example.json").read_text())["month"] == "2026-10"
    (root / "expense.py").write_text("this is invalid Python !\n")
    broken = evaluate(root)
    assert broken["score"] == 0 and not broken["gates"]["tests_executed"]


def test_repair_accepts_correct_general_business_implementation(tmp_path):
    root = project(tmp_path, "code-repair")
    (root / "expense.py").write_text('''import re
from decimal import Decimal
from datetime import datetime

def amount_to_cents(text):
    if not re.fullmatch(r"[+-]?\\d+(?:\\.\\d{1,2})?", str(text).strip()):
        raise ValueError("invalid amount")
    return int(Decimal(str(text).strip()) * 100)

def split_bill(cents, people):
    if type(cents) is not int or type(people) is not int or cents < 0 or people <= 0:
        raise ValueError("invalid split")
    q, r = divmod(cents, people)
    return [q + (i < r) for i in range(people)]

def monthly_totals(entries, month):
    if not re.fullmatch(r"\\d{4}-\\d{2}", month):
        raise ValueError("invalid month")
    datetime.strptime(month, "%Y-%m")
    totals = {}
    for entry in entries:
        date = datetime.strptime(entry["date"], "%Y-%m-%d")
        if date.strftime("%Y-%m") == month:
            category = entry["category"]
            totals[category] = totals.get(category, 0) + amount_to_cents(entry["amount"])
    return totals
''')
    result = evaluate(root)
    assert result["score"] == 100
    assert result["metrics"]["all_tests_passed"]
    sample = json.loads((root / "out/example.json").read_text())
    assert sample["totals_cents"] == {"dining": 3740, "transport": 420}
    assert sum(sample["dinner_split_cents"]) == 10000


def test_schedule_rejects_conflicts_and_duplicate_sessions(tmp_path):
    root = project(tmp_path, "weekly-planner")
    baseline = evaluate(root)
    assert all(baseline["gates"].values()) and 0 < baseline["score"] < 100
    schedule = {"sessions": [{"task": "exercise", "day": 1, "start": "09:00", "end": "09:45"}] * 4}
    (root / "schedule.json").write_text(json.dumps(schedule))
    result = evaluate(root)
    assert not result["gates"]["no_conflicts"]
    assert not result["gates"]["session_limits"]
    assert result["score"] <= 100
    assert "Work" in (root / "out/schedule.html").read_text()


def test_schedule_full_feasible_plan_and_malformed_input(tmp_path):
    root = project(tmp_path, "weekly-planner")
    entries = []
    for task, days, start, end in [
        ("exercise", [1, 3, 5], "07:00", "07:45"),
        ("reading", [1, 2, 5], "21:30", "22:15"),
        ("study", [2, 4], "20:00", "21:30"),
        ("groceries", [6], "09:00", "10:00"),
        ("mealprep", [7], "15:00", "16:30"),
        ("family", [7], "10:00", "12:00"),
        ("admin", [3], "18:30", "19:00"),
        ("rest", [6], "14:00", "15:00"),
        ("rest", [6], "16:00", "17:00"),
    ]:
        entries.extend({"task": task, "day": day, "start": start, "end": end} for day in days)
    (root / "schedule.json").write_text(json.dumps({"sessions": entries}))
    result = evaluate(root)
    assert all(result["gates"].values()) and result["score"] == 100
    assert result["metrics"]["coverage"] == 1
    assert (root / "out/schedule.html").read_text().count("<section>") == 7
    (root / "schedule.json").write_text('{"sessions": [{"task": "exercise", "day": 8}]}')
    assert not evaluate(root)["gates"]["valid_schedule"]


@pytest.mark.skipif(not importlib.util.find_spec("sklearn") or not importlib.util.find_spec("matplotlib"),
                    reason="D04 optional dependencies: install cpu-classifier/requirements.txt to check real training")
def test_classifier_actual_training_fixed_split_and_invalid_config(tmp_path):
    root = project(tmp_path, "cpu-classifier")
    baseline = evaluate(root)
    assert all(baseline["gates"].values()) and 20 < baseline["score"] < 90
    baseline_split = baseline["metrics"]["split_sha256"]
    split = json.loads((root / "out/split.json").read_text())
    assert not set(split["train"]) & set(split["validation"])
    assert len(split["train"]) + len(split["validation"]) == 1797
    (root / "training.json").write_text(json.dumps({"model": "svm", "scaling": "standard",
                                                     "params": {"C": 3, "kernel": "rbf", "gamma": "scale"}}))
    improved = evaluate(root)
    assert all(improved["gates"].values()) and improved["score"] > baseline["score"]
    assert improved["metrics"]["split_sha256"] == baseline_split
    predictions = json.loads((root / "out/predictions.json").read_text())
    assert improved["score"] == round(100 * sum(row["correct"] for row in predictions) / len(predictions), 3)
    for image in ("confusion.png", "mistakes.png"):
        assert (root / "out" / image).read_bytes().startswith(b"\x89PNG")
    (root / "training.json").write_text('{"model": "not-a-classifier"}')
    failed = evaluate(root)
    assert failed["score"] == 0 and not failed["gates"]["training_completed"]
    assert not (root / "out/confusion.png").exists()


def test_backtest_next_day_execution_costs_and_future_independence():
    path = TEMPLATES / "quant-backtest/judge/evaluate.py"
    spec = importlib.util.spec_from_file_location("test_quant_evaluator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = []
    for index in range(200):
        opening = 100 + index * 0.1 + 8 * math.sin(index / 8)
        rows.append({"date": (datetime.date(2023, 1, 1) + datetime.timedelta(days=index)).isoformat(),
                     "open": opening, "high": opening + 2, "low": opening - 2,
                     "close": opening + math.cos(index / 5), "volume": 1000})
    config = {"fast_window": 3, "slow_window": 8, "allocation": 0.5, "threshold_bps": 0}
    settings = {"evaluation_start": rows[120]["date"], "evaluation_end": rows[-1]["date"],
                "initial_cash": 10000, "fee_bps": 10, "slippage_bps": 5, "drawdown_penalty": 1.5,
                "minimum_trade_orders": 2}
    payload, curve, trades = module.backtest(rows, config, settings)
    assert all(payload["gates"].values())
    assert trades and all(row["signal_date"] < row["date"] for row in trades if row["side"] != "close_at_end")
    assert curve[-1]["position_units"] == 0
    no_cost, _, _ = module.backtest(rows, config, {**settings, "fee_bps": 0, "slippage_bps": 0})
    assert no_cost["metrics"]["ending_equity"] > payload["metrics"]["ending_equity"]
    future = [dict(row) for row in rows]
    future[170]["close"] *= 1.2
    _, altered_curve, _ = module.backtest(future, config, settings)
    assert curve[:50] == altered_curve[:50]
    with pytest.raises(ValueError, match="slow_window"):
        module.backtest(rows, {**config, "fast_window": 8}, settings)
