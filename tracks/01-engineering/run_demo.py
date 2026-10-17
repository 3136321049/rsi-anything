#!/usr/bin/env python3
"""Run six reproducible Ralph-loop mutations through the guarded ratchet."""

from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

TRACK = Path(__file__).resolve().parent
REPO = TRACK.parents[1]
CORE_ROOT = Path(os.environ.get("RSI_CORE_ROOT", REPO))
sys.path.insert(0, str(CORE_ROOT))

from core.controller import run_ratchet_loop


def replace(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise RuntimeError(f"expected one mutation anchor, found {source.count(old)}: {old[:50]!r}")
    return source.replace(old, new)


def update_engine(root: Path, mutate):
    path = root / "order_engine.py"
    path.write_text(mutate(path.read_text(encoding="utf-8")), encoding="utf-8")


EXACT_MONEY = '''def settlement_fee_cents(price_cents, quantity, fee_bps, rebate_bps=0):
    numerator = price_cents * quantity * (fee_bps - rebate_bps)
    sign = 1 if numerator >= 0 else -1
    return sign * ((abs(numerator) + 5_000) // 10_000)'''

SAFE_VWAP = '''def rolling_vwap(trades):
    positive = [trade for trade in trades if trade["quantity"] > 0]
    volume = sum(trade["quantity"] for trade in positive)
    if volume == 0:
        return 0.0
    return sum(trade["price_cents"] * trade["quantity"] for trade in positive) / volume'''

ROUND_1_MATCH = '''def match_and_settle_batch(orders):
    accepted = []
    seen_order_ids = set()
    risk_by_account = {}
    gross_by_account = {}
    for order in orders:
        quantity = int(order["quantity"])
        order_id = order["order_id"]
        if quantity <= 0 or order_id in seen_order_ids:
            continue
        seen_order_ids.add(order_id)
        accepted.append(dict(order))
        account = order["account"]
        acct_rows = [row for row in accepted if row["account"] == account]
        risk_by_account[account] = sum(
            row["quantity"] if row["side"] == "buy" else -row["quantity"]
            for row in acct_rows
        )
        gross_by_account[account] = sum(row["quantity"] for row in acct_rows)
    fees = sum(
        settlement_fee_cents(
            row["price_cents"],
            row["quantity"],
            row.get("fee_bps", 0),
            row.get("rebate_bps", 0),
        )
        for row in accepted
    )
    return {
        "accepted_count": len(accepted),
        "total_quantity": sum(row["quantity"] for row in accepted),
        "fees_cents": fees,
        "vwap_cents": rolling_vwap(accepted),
        "risk_by_account": risk_by_account,
        "gross_by_account": gross_by_account,
    }
'''


def round_1(source: str) -> str:
    start = source.index("def settlement_fee_cents")
    end = source.index("\n\ndef rolling_vwap", start)
    source = source[:start] + EXACT_MONEY + source[end:]
    start = source.index("def rolling_vwap")
    end = source.index("\n\ndef match_and_settle_batch", start)
    source = source[:start] + SAFE_VWAP + "\n\n\n" + ROUND_1_MATCH
    return source


ACCOUNT_SCAN_MATCH = '''def match_and_settle_batch(orders):
    accepted = []
    seen_order_ids = set()
    accounts = []
    seen_accounts = set()
    for order in orders:
        quantity = int(order["quantity"])
        order_id = order["order_id"]
        if quantity <= 0 or order_id in seen_order_ids:
            continue
        seen_order_ids.add(order_id)
        accepted.append(dict(order))
        account = order["account"]
        if account not in seen_accounts:
            seen_accounts.add(account)
            accounts.append(account)
    risk_by_account = {}
    gross_by_account = {}
    for account in accounts:
        risk_by_account[account] = sum(
            (1 if row["side"] == "buy" else -1) * row["quantity"]
            for row in accepted
            if row["account"] == account
        )
        gross_by_account[account] = sum(
            row["quantity"] for row in accepted if row["account"] == account
        )
    fees = sum(
        settlement_fee_cents(
            row["price_cents"],
            row["quantity"],
            row.get("fee_bps", 0),
            row.get("rebate_bps", 0),
        )
        for row in accepted
    )
    return {
        "accepted_count": len(accepted),
        "total_quantity": sum(row["quantity"] for row in accepted),
        "fees_cents": fees,
        "vwap_cents": rolling_vwap(accepted),
        "risk_by_account": risk_by_account,
        "gross_by_account": gross_by_account,
    }
'''


def round_2(source: str) -> str:
    start = source.index("def match_and_settle_batch")
    return source[:start] + ACCOUNT_SCAN_MATCH


def round_3(source: str) -> str:
    source = replace(
        source,
        'def reset_state():\n    """The baseline is stateless."""',
        '_RISK_CACHE = {}\n\n\ndef reset_state():\n    """BUG: forgot to clear _RISK_CACHE across batches."""',
    )
    source = replace(
        source,
        '        risk_by_account[account] = sum(\n',
        '        risk_by_account[account] = _RISK_CACHE.get(account, 0) + sum(\n',
    )
    return replace(source, "    fees = sum(\n",
                   "    _RISK_CACHE.update(risk_by_account)\n    fees = sum(\n")


LINEAR_MATCH = '''def match_and_settle_batch(orders):
    seen_order_ids = set()
    accepted = []
    for order in orders:
        quantity = int(order["quantity"])
        order_id = order["order_id"]
        if quantity <= 0 or order_id in seen_order_ids:
            continue
        seen_order_ids.add(order_id)
        accepted.append(dict(order))
    risk_by_account = {}
    gross_by_account = {}
    for row in accepted:
        signed = row["quantity"] if row["side"] == "buy" else -row["quantity"]
        risk_by_account[row["account"]] = risk_by_account.get(row["account"], 0) + signed
        gross_by_account[row["account"]] = gross_by_account.get(row["account"], 0) + row["quantity"]
    fees = sum(
        settlement_fee_cents(row["price_cents"], row["quantity"],
                             row.get("fee_bps", 0), row.get("rebate_bps", 0))
        for row in accepted
    )
    return {
        "accepted_count": len(accepted),
        "total_quantity": sum(row["quantity"] for row in accepted),
        "fees_cents": fees,
        "vwap_cents": rolling_vwap(accepted),
        "risk_by_account": risk_by_account,
        "gross_by_account": gross_by_account,
    }
'''


SINGLE_PASS_MATCH = '''def match_and_settle_batch(orders):
    seen_order_ids = set()
    seen_add = seen_order_ids.add
    count = total_quantity = fees = weighted_notional = 0
    risk_by_account = {}
    gross_by_account = {}
    risk_get = risk_by_account.get
    gross_get = gross_by_account.get
    fee_fn = settlement_fee_cents
    for order in orders:
        quantity = int(order["quantity"])
        order_id = order["order_id"]
        if quantity <= 0 or order_id in seen_order_ids:
            continue
        seen_add(order_id)
        price = order["price_cents"]
        count += 1
        total_quantity += quantity
        weighted_notional += price * quantity
        fees += fee_fn(price, quantity, order.get("fee_bps", 0), order.get("rebate_bps", 0))
        signed = quantity if order["side"] == "buy" else -quantity
        account = order["account"]
        risk_by_account[account] = risk_get(account, 0) + signed
        gross_by_account[account] = gross_get(account, 0) + quantity
    return {
        "accepted_count": count,
        "total_quantity": total_quantity,
        "fees_cents": fees,
        "vwap_cents": weighted_notional / total_quantity if total_quantity else 0.0,
        "risk_by_account": risk_by_account,
        "gross_by_account": gross_by_account,
    }
'''


def replace_match(source: str, stage: int, body: str) -> str:
    if stage == 6:
        source = replace(
            source,
            '"""Buggy baseline: correct happy path, but unsafe retries, money, and empty windows."""',
            '"""Champion: exact, idempotent, empty-safe single-pass O(N) settlement kernel."""',
        )
        source = replace(
            source,
            'def reset_state():\n    """The baseline is stateless."""',
            'def reset_state():\n    """The champion deliberately keeps no cross-batch cache."""',
        )
    start = source.index("def match_and_settle_batch")
    return source[:start] + body


def guard_attack(root: Path):
    path = root / "test_order_engine.py"
    source = path.read_text(encoding="utf-8")
    old = '    assert result["accepted_count"] == 1'
    if old not in source:
        raise RuntimeError("frozen assertion anchor missing")
    source = source.replace(
        old, '    # assert result["accepted_count"] == 1  # reward-hacking attempt', 1
    )
    path.write_text(source, encoding="utf-8")


def reset_demo():
    shutil.copyfile(TRACK / "before_order_engine.py", TRACK / "order_engine.py")
    for path in (TRACK / "results.tsv", TRACK / "ratchet_summary.md"):
        path.unlink(missing_ok=True)
    shutil.rmtree(TRACK / ".rsi", ignore_errors=True)
    shutil.rmtree(TRACK / "__pycache__", ignore_errors=True)


def _extract_p95(notes: str) -> str:
    m = re.search(r"wall-clock p95 ([0-9.]+ms)", notes)
    return m.group(1) if m else "—"


def write_summary(result):
    rows = [line.split("\t") for line in (TRACK / "results.tsv").read_text(encoding="utf-8").splitlines()[1:]]
    statuses = [cols[5] for cols in rows]
    assert statuses == ["BASELINE", "KEEP", "KEEP", "REVERT_SCORE",
                        "REVERT_GUARD", "KEEP", "KEEP"], statuses
    p95s = [_extract_p95(cols[8]) for cols in rows]
    text = f"""# Engineering Ratchet Summary

The loop finished at **{result['best_score']:.1f}/100** with all 10 frozen
correctness tests passing (`10/10` required on every accepted round). Measured
4,000-order batch wall-clock p95 progressed from **{p95s[0]}** (baseline) to
**{p95s[1]}** (Round 1), **{p95s[2]}** (Round 2), **{p95s[5]}** (Round 5), and
**{p95s[6]}** (Round 6).

| Round | Mutation | Decision | Score | Champion | Wall-Clock p95 |
|---:|---|---|---:|---:|---:|
| 0 | Buggy quadratic baseline (`7/10` tests) | {rows[0][5]} | {float(rows[0][3]):.1f} | {float(rows[0][4]):.1f} | {p95s[0]} |
| 1 | `order_id` dedup + exact integer bps + filtered prefix (`10/10`) | {rows[1][5]} | {float(rows[1][3]):.1f} | {float(rows[1][4]):.1f} | {p95s[1]} |
| 2 | Hoist prefix scans to per-account aggregation | {rows[2][5]} | {float(rows[2][3]):.1f} | {float(rows[2][4]):.1f} | {p95s[2]} |
| 3 | Cross-batch global risk cache (`8/10`, fails isolation gate) | {rows[3][5]} | {float(rows[3][3]):.1f} | {float(rows[3][4]):.1f} | {p95s[3]} |
| 4 | Frozen-test assertion removal | {rows[4][5]} | {float(rows[4][3]):.1f} | {float(rows[4][4]):.1f} | {p95s[4]} |
| 5 | Hash-indexed $O(N)$ risk aggregation | {rows[5][5]} | {float(rows[5][3]):.1f} | {float(rows[5][4]):.1f} | {p95s[5]} |
| 6 | Single-pass zero-copy settlement accumulator | {rows[6][5]} | {float(rows[6][3]):.1f} | {float(rows[6][4]):.1f} | {p95s[6]} |
"""
    (TRACK / "ratchet_summary.md").write_text(text, encoding="utf-8")


def main():
    reset_demo()
    steps = [
        {"hypothesis": "Fix retry deduplication, exact integer bps, and empty VWAP",
         "apply": lambda root: update_engine(root, round_1)},
        {"hypothesis": "Hoist per-order prefix scans to per-account aggregation",
         "apply": lambda root: update_engine(root, round_2)},
        {"hypothesis": "Cache account risk globally across batches",
         "apply": lambda root: update_engine(root, round_3)},
        {"hypothesis": "Disable a frozen correctness assertion", "apply": guard_attack},
        {"hypothesis": "Replace per-account scans with hash-indexed O(N) aggregation",
         "apply": lambda root: update_engine(root, lambda source: replace_match(source, 5, LINEAR_MATCH))},
        {"hypothesis": "Fuse settlement into one single-pass zero-copy accumulator",
         "apply": lambda root: update_engine(root, lambda source: replace_match(source, 6, SINGLE_PASS_MATCH))},
    ]
    result = run_ratchet_loop(TRACK, steps=steps, max_iterations=6)
    write_summary(result)
    print(f"Champion: {result['best_score']:.1f}/100")


if __name__ == "__main__":
    main()
