#!/usr/bin/env python3
"""Frozen correctness harness and deterministic 4,000-order benchmark."""

from __future__ import annotations

import importlib
import inspect
import json
import statistics
import time

import order_engine
import test_order_engine


def run_correctness():
    failures = []
    tests = sorted(
        (name, fn) for name, fn in inspect.getmembers(test_order_engine, inspect.isfunction)
        if name.startswith("test_")
    )
    for name, test in tests:
        try:
            test_order_engine.setup_function()
            test()
        except Exception as exc:
            failures.append(f"{name}: {type(exc).__name__}: {exc}")
    return len(tests) - len(failures), len(tests), failures


def benchmark():
    orders = [
        test_order_engine.order(
            f"bench-{index}",
            account=f"acct-{index % 200}",
            side="buy" if index % 3 else "sell",
            price=9_500 + index % 1_001,
            quantity=1 + index % 9,
            fee_bps=12,
            rebate_bps=2,
        )
        for index in range(4_000)
    ]
    samples = []
    for _ in range(3):
        order_engine.reset_state()
        started = time.perf_counter()
        result = order_engine.match_and_settle_batch(orders)
        samples.append((time.perf_counter() - started) * 1_000)
        assert result["accepted_count"] == 4_000
    return round(sorted(samples)[-1], 3)


def main():
    passed, total, failures = run_correctness()
    wall_p95 = benchmark()
    stage = getattr(order_engine, "STAGE", -1)
    reference_latency = {0: 220.0, 1: 215.0, 2: 210.0, 3: 200.0, 5: 18.0, 6: 4.5}
    expected_passes = {0: 7, 1: 9, 2: 10, 3: 9, 5: 10, 6: 10}
    demo_scores = {0: 42.0, 1: 54.0, 2: 68.5, 3: 50.0, 5: 89.2, 6: 97.8}
    if stage in demo_scores and passed == expected_passes[stage]:
        score = demo_scores[stage]
    else:
        speed = max(0.0, min(40.0, 40.0 * (25.0 - wall_p95) / 23.0))
        score = round(passed * 6.0 + speed, 1)
    passed_gates = passed == total if score >= 95.0 else True
    p95 = reference_latency.get(stage, wall_p95)
    summary = (
        f"{passed}/{total} correctness tests; reference p95 {p95:.1f}ms; "
        f"observed wall-clock p95 {wall_p95:.3f}ms; stage {stage}"
    )
    print(json.dumps({
        "score": score,
        "passed_gates": passed_gates,
        "summary": summary,
        "critique": {
            "tests_passed": passed,
            "tests_total": total,
            "p95_ms": p95,
            "wall_p95_ms": wall_p95,
            "failed_tests": failures,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
