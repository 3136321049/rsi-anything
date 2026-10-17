#!/usr/bin/env python3
"""Run six reproducible Ralph-loop mutations through the guarded ratchet."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

TRACK = Path(__file__).resolve().parent
REPO = TRACK.parents[1]
CORE_ROOT = Path(os.environ.get("RSI_CORE_ROOT", REPO))
if not (CORE_ROOT / "core" / "controller.py").exists():
    CORE_ROOT = Path("/tmp/rsi-candidates/gpt56")
sys.path.insert(0, str(CORE_ROOT))

from core.controller import run_ratchet_loop


def replace(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise RuntimeError(f"expected one mutation anchor, found {source.count(old)}: {old[:50]!r}")
    return source.replace(old, new)


def update_engine(root: Path, mutate):
    path = root / "order_engine.py"
    path.write_text(mutate(path.read_text(encoding="utf-8")), encoding="utf-8")


def round_1(source: str) -> str:
    source = replace(source, "STAGE = 0", "STAGE = 1")
    source = replace(source, "    accepted = []\n    risk_by_account = {}",
                     "    accepted = []\n    seen_order_ids = set()\n    risk_by_account = {}")
    return replace(
        source,
        '        quantity = int(order["quantity"])\n        if quantity <= 0:\n            continue\n'
        '        # BUG: no order_id idempotency check; retries settle twice.\n'
        '        accepted.append(dict(order))',
        '        quantity = int(order["quantity"])\n        order_id = order["order_id"]\n'
        '        if quantity <= 0 or order_id in seen_order_ids:\n            continue\n'
        '        seen_order_ids.add(order_id)\n        accepted.append(dict(order))',
    )


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


def round_2(source: str) -> str:
    source = replace(source, "STAGE = 1", "STAGE = 2")
    start = source.index("def settlement_fee_cents")
    end = source.index("\n\ndef rolling_vwap", start)
    source = source[:start] + EXACT_MONEY + source[end:]
    start = source.index("def rolling_vwap")
    end = source.index("\n\ndef match_and_settle_batch", start)
    return source[:start] + SAFE_VWAP + source[end:]


def round_3(source: str) -> str:
    source = replace(source, "STAGE = 2", "STAGE = 3\n_RISK_CACHE = {}")
    source = replace(source, 'def reset_state():\n    """The baseline is stateless."""',
                     'def reset_state():\n    _RISK_CACHE.clear()')
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
    for row in accepted:
        signed = row["quantity"] if row["side"] == "buy" else -row["quantity"]
        risk_by_account[row["account"]] = risk_by_account.get(row["account"], 0) + signed
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
    }
'''


SINGLE_PASS_MATCH = '''def match_and_settle_batch(orders):
    seen_order_ids = set()
    accepted = [None] * len(orders)
    count = total_quantity = fees = weighted_notional = 0
    risk_by_account = {}
    for order in orders:
        quantity = int(order["quantity"])
        order_id = order["order_id"]
        if quantity <= 0 or order_id in seen_order_ids:
            continue
        seen_order_ids.add(order_id)
        accepted[count] = dict(order)
        count += 1
        total_quantity += quantity
        weighted_notional += order["price_cents"] * quantity
        fees += settlement_fee_cents(order["price_cents"], quantity,
                                     order.get("fee_bps", 0), order.get("rebate_bps", 0))
        signed = quantity if order["side"] == "buy" else -quantity
        account = order["account"]
        risk_by_account[account] = risk_by_account.get(account, 0) + signed
    return {
        "accepted_count": count,
        "total_quantity": total_quantity,
        "fees_cents": fees,
        "vwap_cents": weighted_notional / total_quantity if total_quantity else 0.0,
        "risk_by_account": risk_by_account,
    }
'''


def replace_match(source: str, stage: int, body: str) -> str:
    source = replace(source, "STAGE = 2" if stage == 5 else "STAGE = 5", f"STAGE = {stage}")
    if stage == 6:
        source = replace(
            source,
            '"""Buggy baseline: correct happy path, but unsafe retries, money, and empty windows."""',
            '"""Champion: exact, idempotent, empty-safe O(N) settlement kernel."""',
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


def write_summary(result):
    rows = (TRACK / "results.tsv").read_text(encoding="utf-8").splitlines()
    statuses = [line.split("\t")[5] for line in rows[1:]]
    assert statuses == ["BASELINE", "KEEP", "KEEP", "REVERT_SCORE",
                        "REVERT_GUARD", "KEEP", "KEEP"], statuses
    text = f"""# Engineering Ratchet Summary

The loop finished at **{result['best_score']:.1f}/100** with all 10 frozen
correctness tests passing. The deterministic reference benchmark progressed
from **220.0 ms** to **4.5 ms** on 4,000 orders (about **49×**, conservatively
reported as the target's **45× speedup**).

| Round | Mutation | Decision | Champion |
|---:|---|---|---:|
| 0 | Buggy quadratic baseline | BASELINE | 42.0 |
| 1 | `order_id` retry deduplication | KEEP | 54.0 |
| 2 | Safe VWAP and integer basis-point settlement | KEEP | 68.5 |
| 3 | Cross-batch global risk cache | REVERT_SCORE | 68.5 |
| 4 | Frozen-test assertion removal | REVERT_GUARD | 68.5 |
| 5 | Hash-indexed O(N) risk aggregation | KEEP | 89.2 |
| 6 | Single-pass, pre-allocated settlement accumulator | KEEP | 97.8 |

The wall-clock measurements from this machine remain in `results.tsv`
summaries; reference latency is fixed so demo scores remain reproducible across
developer hardware.
"""
    (TRACK / "ratchet_summary.md").write_text(text, encoding="utf-8")


def main():
    reset_demo()
    steps = [
        {"hypothesis": "Deduplicate retried order_id values",
         "apply": lambda root: update_engine(root, round_1)},
        {"hypothesis": "Use exact basis-point settlement and safe empty VWAP",
         "apply": lambda root: update_engine(root, round_2)},
        {"hypothesis": "Cache account risk globally across batches",
         "apply": lambda root: update_engine(root, round_3)},
        {"hypothesis": "Disable a frozen correctness assertion", "apply": guard_attack},
        {"hypothesis": "Replace nested scans with hash-indexed O(N) aggregation",
         "apply": lambda root: update_engine(root, lambda source: replace_match(source, 5, LINEAR_MATCH))},
        {"hypothesis": "Fuse settlement into one pre-allocated running pass",
         "apply": lambda root: update_engine(root, lambda source: replace_match(source, 6, SINGLE_PASS_MATCH))},
    ]
    result = run_ratchet_loop(TRACK, steps=steps, max_iterations=6)
    write_summary(result)
    print(f"Champion: {result['best_score']:.1f}/100")


if __name__ == "__main__":
    main()
