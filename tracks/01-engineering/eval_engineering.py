#!/usr/bin/env python3
"""Frozen correctness harness and 4,000-order settlement benchmark.

Enforces a strict allowlist AST sandbox on mutable order_engine.py and runs
a streaming stdin/stdout worker where each challenge batch is read and answered
one at a time, and the 4,000-order benchmark is timed directly by the parent
judge process across the pipe.
"""

from __future__ import annotations

import ast
import hashlib
import json
import secrets
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FROZEN_TEST_FILE = ROOT / "test_order_engine.py"
FROZEN_EVAL_FILE = ROOT / "eval_engineering.py"
EXPECTED_TEST_SHA = hashlib.sha256(FROZEN_TEST_FILE.read_bytes()).hexdigest()
EXPECTED_EVAL_SHA = hashlib.sha256(FROZEN_EVAL_FILE.read_bytes()).hexdigest()

_ALLOWED_NODES = (
    ast.Module, ast.FunctionDef, ast.arguments, ast.arg,
    ast.Assign, ast.AugAssign, ast.Return, ast.For, ast.If, ast.Continue, ast.Pass, ast.Expr,
    ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.IfExp,
    ast.Call, ast.Subscript, ast.Attribute, ast.Name, ast.Constant,
    ast.Dict, ast.List, ast.Tuple, ast.ListComp, ast.GeneratorExp, ast.comprehension,
    ast.Load, ast.Store,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.USub, ast.UAdd,
    ast.And, ast.Or, ast.Not,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn,
)
_ALLOWED_BUILTINS = {"abs", "dict", "float", "int", "len", "max", "min", "range", "round", "set", "sum"}
_ALLOWED_ATTRS = {"add", "append", "clear", "copy", "get", "items", "keys", "pop", "setdefault", "update", "values"}
_ALLOWED_TOP_NAMES = {"_RISK_CACHE", "reset_state", "settlement_fee_cents", "rolling_vwap", "match_and_settle_batch"}

WORKER_SCRIPT = r"""
import copy, inspect, json, sys, time
import test_order_engine
import order_engine

for raw in sys.stdin:
    msg = json.loads(raw)
    op = msg["op"]
    if op == "tests":
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
        res = {"tests_total": len(tests), "failures": failures}
    elif op == "batch":
        if msg.get("reset", True):
            order_engine.reset_state()
        batch = msg["orders"]
        snap = copy.deepcopy(batch)
        t0 = time.perf_counter()
        out = order_engine.match_and_settle_batch(batch)
        elapsed_ms = round((time.perf_counter() - t0) * 1_000, 3)
        res = {"out": out, "mutated": batch != snap, "elapsed_ms": elapsed_ms}
    elif op == "fee":
        res = {"val": order_engine.settlement_fee_cents(*msg["args"])}
    elif op == "vwap":
        try:
            res = {"ok": True, "val": order_engine.rolling_vwap(msg["trades"])}
        except Exception as exc:
            res = {"ok": False, "err": f"{type(exc).__name__}: {exc}"}
    elif op == "quit":
        break
    sys.stdout.write(json.dumps(res, sort_keys=True) + "\n")
    sys.stdout.flush()
"""


def audit_candidate_ast(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"SyntaxError: {exc}"]
    violations = []
    local_names = set(_ALLOWED_TOP_NAMES) | _ALLOWED_BUILTINS
    seen_top: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        if isinstance(node, ast.FunctionDef) and node.name in _ALLOWED_TOP_NAMES:
            if node.name in seen_top:
                violations.append(f"duplicate top-level definition: {node.name}")
            if (node.decorator_list or node.returns or node.args.vararg
                    or node.args.kwarg or node.args.kwonlyargs or node.args.posonlyargs
                    or any(not isinstance(d, ast.Constant) for d in node.args.defaults)):
                violations.append(f"disallowed function signature/decorator: {node.name}")
            seen_top.add(node.name)
            continue
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "_RISK_CACHE"
                and isinstance(node.value, ast.Dict) and not node.value.keys):
            if "_RISK_CACHE" in seen_top:
                violations.append("duplicate top-level assignment: _RISK_CACHE")
            seen_top.add("_RISK_CACHE")
            continue
        violations.append(f"disallowed top-level statement: {type(node).__name__}")
    required_fns = {"reset_state", "settlement_fee_cents", "rolling_vwap", "match_and_settle_batch"}
    if not required_fns.issubset(seen_top):
        violations.append("missing required top-level function")
    top_fns = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    for helper in ("reset_state", "settlement_fee_cents"):
        if helper in top_fns:
            for sub in ast.walk(top_fns[helper]):
                if isinstance(sub, (ast.For, ast.ListComp, ast.GeneratorExp, ast.Dict, ast.Subscript)):
                    violations.append(f"disallowed construct in {helper}: {type(sub).__name__}")
                elif isinstance(sub, ast.Attribute) and (helper != "reset_state" or sub.attr != "clear"):
                    violations.append(f"disallowed attribute in {helper}: .{sub.attr}")
                elif isinstance(sub, ast.Name) and sub.id in (required_fns | {"dict", "set"}):
                    violations.append(f"disallowed reference in {helper}: {sub.id}")
    if "rolling_vwap" in top_fns:
        vwap_fn = top_fns["rolling_vwap"]
        comp_count = 0
        for sub in ast.walk(vwap_fn):
            if isinstance(sub, (ast.ListComp, ast.GeneratorExp)):
                comp_count += 1
            elif isinstance(sub, (ast.For, ast.Dict, ast.AugAssign, ast.Attribute)):
                violations.append(f"disallowed construct in rolling_vwap: {type(sub).__name__}")
            elif isinstance(sub, ast.Name) and sub.id in (required_fns | {"dict", "set", "_RISK_CACHE"}):
                violations.append(f"disallowed reference in rolling_vwap: {sub.id}")
        if comp_count > 3:
            violations.append("too many comprehensions in rolling_vwap")
    if "match_and_settle_batch" in top_fns:
        for sub in ast.walk(top_fns["match_and_settle_batch"]):
            if isinstance(sub, ast.Name) and sub.id in {"match_and_settle_batch", "reset_state"}:
                violations.append(f"disallowed call/ref in match_and_settle_batch: {sub.id}")
            elif isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store) and sub.id == "_RISK_CACHE":
                violations.append("disallowed local store to _RISK_CACHE")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            violations.append(f"disallowed AST node: {type(node).__name__}")
            continue
        if isinstance(node, ast.FunctionDef) and node not in tree.body:
            violations.append(f"disallowed nested function: {node.name}")
        if isinstance(node, ast.arg):
            if node.arg.startswith("_"):
                violations.append(f"disallowed arg name: {node.arg}")
            local_names.add(node.arg)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in required_fns or (node.id.startswith("_") and node.id != "_RISK_CACHE"):
                violations.append(f"disallowed variable name: {node.id}")
            local_names.add(node.id)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if (node.id.startswith("_") and node.id != "_RISK_CACHE") or node.id not in local_names:
                violations.append(f"disallowed identifier: {node.id}")
        elif isinstance(node, ast.Attribute):
            if node.attr.startswith("_") or node.attr not in _ALLOWED_ATTRS:
                violations.append(f"disallowed attribute access: .{node.attr}")
    return violations


def _settle_reference(orders: list[dict]) -> dict:
    seen = set()
    count = total_qty = fees = weighted = 0
    risk, gross = {}, {}
    for row in orders:
        qty = int(row["quantity"])
        oid = row["order_id"]
        if qty <= 0 or oid in seen:
            continue
        seen.add(oid)
        price = row["price_cents"]
        count += 1
        total_qty += qty
        weighted += price * qty
        num = price * qty * (row.get("fee_bps", 0) - row.get("rebate_bps", 0))
        sign = 1 if num >= 0 else -1
        fees += sign * ((abs(num) + 5_000) // 10_000)
        signed = qty if row["side"] == "buy" else -qty
        acct = row["account"]
        risk[acct] = risk.get(acct, 0) + signed
        gross[acct] = gross.get(acct, 0) + qty
    return {
        "accepted_count": count,
        "total_quantity": total_qty,
        "fees_cents": fees,
        "vwap_cents": weighted / total_qty if total_qty else 0.0,
        "risk_by_account": risk,
        "gross_by_account": gross,
    }


def _matches_expected(actual: dict, expected: dict) -> bool:
    if not isinstance(actual, dict):
        return False
    for key in ("accepted_count", "total_quantity", "fees_cents", "risk_by_account", "gross_by_account"):
        if actual.get(key) != expected[key]:
            return False
    return abs(float(actual.get("vwap_cents", -1.0)) - expected["vwap_cents"]) <= 1e-6


def verify_disk_integrity() -> list[str]:
    errors = []
    if not FROZEN_TEST_FILE.is_file() or hashlib.sha256(FROZEN_TEST_FILE.read_bytes()).hexdigest() != EXPECTED_TEST_SHA:
        errors.append("test_order_engine.py modified during evaluation")
    if not FROZEN_EVAL_FILE.is_file() or hashlib.sha256(FROZEN_EVAL_FILE.read_bytes()).hexdigest() != EXPECTED_EVAL_SHA:
        errors.append("eval_engineering.py modified during evaluation")
    return errors


def analyze_structure(source: str):
    tree = ast.parse(source)
    fns = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    fn = fns["match_and_settle_batch"]
    loop_types = (ast.For, ast.GeneratorExp, ast.ListComp)
    nested_orders = nested_accounts = top_loops = 0
    for node in ast.walk(fn):
        if isinstance(node, loop_types):
            top_loops += 1
        if isinstance(node, ast.For):
            iter_src = ast.unparse(node.iter)
            inner = [
                child for child in ast.walk(node)
                if child is not node and isinstance(child, loop_types)
            ]
            if "orders" in iter_src:
                nested_orders += len(inner)
            else:
                nested_accounts += len(inner)
    if any(isinstance(n, ast.Name) and n.id == "rolling_vwap" for n in ast.walk(fn)):
        top_loops += 2
    copies_orders = any(
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "dict"
        for node in ast.walk(fn)
    ) or any(
        isinstance(sub, ast.Dict) and sub.keys
        for n in ast.walk(fn) if isinstance(n, loop_types)
        for sub in ast.walk(n)
    )
    linear_passes = max(1, top_loops - nested_orders - nested_accounts)
    return {
        "nested_orders": nested_orders,
        "nested_accounts": nested_accounts,
        "linear_passes": linear_passes,
        "copies_orders": copies_orders,
    }


def _build_challenge():
    q_single = 2 + secrets.randbelow(7)
    q_buy = 6 + secrets.randbelow(7)
    q_sell = 1 + secrets.randbelow(4)
    q_retry = 4 + secrets.randbelow(8)
    p_base = 1_000 + 100 * secrets.randbelow(9)
    p_off = secrets.randbelow(53)

    def mk(oid, account="acct-a", side="buy", price=p_base, quantity=2, fee_bps=25, rebate_bps=0):
        return {
            "order_id": oid, "account": account, "side": side,
            "price_cents": price, "quantity": quantity,
            "fee_bps": fee_bps, "rebate_bps": rebate_bps,
        }

    retry_adj = mk("r-adj", quantity=q_retry)
    retry_sep = mk("r-sep", quantity=q_retry + 1)
    probes = {
        "single": [mk("one", quantity=q_single)],
        "signed": [mk("b", quantity=q_buy), mk("s", side="sell", quantity=q_sell)],
        "isolation_a": [mk("ia", account="acct-a", quantity=q_buy + 3)],
        "isolation_b": [mk("ib", account="acct-a", quantity=q_sell)],
        "fee": [mk("fee", price=2_000, quantity=2, fee_bps=25, rebate_bps=0)],
        "rebate": [mk("reb", price=2_000, quantity=1, fee_bps=20, rebate_bps=5)],
        "vwap": [mk("v1", price=100 + p_off, quantity=2), mk("v2", price=110 + p_off, quantity=1)],
        "adj_retry": [retry_adj, dict(retry_adj)],
        "sep_retry": [retry_sep, mk("mid", quantity=2), dict(retry_sep)],
    }
    fee_probes = {"half_pos": [100, 1, 50, 0], "half_neg": [100, 1, 0, 50]}
    vwap_probes = {"empty": [], "nonpos": [mk("z", quantity=0), mk("n", quantity=-2)]}
    bench_orders = [
        mk(
            f"bench-{index}",
            account=f"acct-{index % 200}",
            side="buy" if index % 3 else "sell",
            price=9_500 + p_off + (index % 1_001),
            quantity=1 + (index % 9),
            fee_bps=12,
            rebate_bps=2,
        )
        for index in range(4_000)
    ]
    return probes, fee_probes, vwap_probes, bench_orders


def main():
    source = (ROOT / "order_engine.py").read_text(encoding="utf-8")
    ast_violations = audit_candidate_ast(source)
    if ast_violations:
        print(json.dumps({
            "score": 0.0,
            "passed_gates": False,
            "summary": "AST sandbox rejected forbidden construct in order_engine.py",
            "critique": {"failed_tests": ast_violations},
        }, sort_keys=True))
        return

    probes, fee_probes, vwap_probes, bench_orders = _build_challenge()
    proc = subprocess.Popen(
        [sys.executable, "-c", WORKER_SCRIPT],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    def rpc(msg: dict) -> dict:
        assert proc.stdin and proc.stdout
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError("worker closed stdout unexpectedly")
        return json.loads(line)

    try:
        test_res = rpc({"op": "tests"})
        total = int(test_res.get("tests_total", 0))
        failures = list(test_res.get("failures", []))

        probe_errors = []
        for key, batch in probes.items():
            r = rpc({"op": "batch", "orders": batch, "reset": True})
            if r.get("mutated") or not _matches_expected(r.get("out"), _settle_reference(batch)):
                probe_errors.append(f"parent_probe_{key}: mismatch")

        if rpc({"op": "fee", "args": fee_probes["half_pos"]}).get("val") != 1:
            probe_errors.append("parent_probe_half_pos: mismatch")
        if rpc({"op": "fee", "args": fee_probes["half_neg"]}).get("val") != -1:
            probe_errors.append("parent_probe_half_neg: mismatch")
        for key, trades in vwap_probes.items():
            vr = rpc({"op": "vwap", "trades": trades})
            if not vr.get("ok") or vr.get("val") != 0.0:
                probe_errors.append(f"parent_probe_vwap_{key}: mismatch")

        expected_bench = _settle_reference(bench_orders)
        samples = []
        for _ in range(3):
            br = rpc({"op": "batch", "orders": bench_orders, "reset": True})
            samples.append(float(br.get("elapsed_ms", 999.0)))
            if not _matches_expected(br.get("out"), expected_bench):
                probe_errors.append("parent_probe_benchmark: mismatch")
        wall_p95 = round(sorted(samples)[-1], 3)
        proc.stdin.write(json.dumps({"op": "quit"}) + "\n")
        proc.stdin.flush()
        proc.wait(timeout=5)
    except Exception as exc:
        proc.kill()
        print(json.dumps({
            "score": 0.0,
            "passed_gates": False,
            "summary": f"worker RPC failed: {exc}",
            "critique": {"failed_tests": [str(exc)]},
        }, sort_keys=True))
        return

    integrity_errors = verify_disk_integrity()
    if not failures and probe_errors:
        failures.extend(probe_errors)
    if total != 10:
        failures.append(f"expected 10 tests, worker ran {total}")
        total = 10

    passed = max(0, total - len(failures))
    if integrity_errors:
        failures.extend(integrity_errors)
        passed = 0

    meta = analyze_structure(source)
    nested_orders = meta["nested_orders"]
    nested_accounts = meta["nested_accounts"]
    linear_passes = meta["linear_passes"]
    copies_orders = meta["copies_orders"]

    correctness_pts = 60.0 * (passed / total)
    ceiling_ms = 350.0 if nested_orders else (60.0 if nested_accounts else 15.0)
    if passed < total or integrity_errors:
        efficiency_pts = 0.0
    else:
        complexity_pts = 24.0 / (1.0 + 1.0 * nested_accounts + 10.0 * nested_orders)
        fusion_pts = 12.0 / linear_passes
        alloc_pts = 0.0 if copies_orders else 1.8
        wall_factor = 1.0 if wall_p95 <= ceiling_ms else max(0.0, ceiling_ms / wall_p95)
        efficiency_pts = (complexity_pts + fusion_pts + alloc_pts) * wall_factor

    score = round(correctness_pts + efficiency_pts, 1)
    passed_gates = (passed == total) and not integrity_errors and (wall_p95 <= ceiling_ms)
    summary = (
        f"{passed}/{total} correctness tests; wall-clock p95 {wall_p95:.2f}ms "
        f"(ceiling {ceiling_ms:.0f}ms); passes={linear_passes} "
        f"nested_orders={nested_orders} nested_accounts={nested_accounts}"
    )
    print(json.dumps({
        "score": score,
        "passed_gates": passed_gates,
        "summary": summary,
        "critique": {
            "tests_passed": passed,
            "tests_total": total,
            "wall_p95_ms": wall_p95,
            "ceiling_ms": ceiling_ms,
            "linear_passes": linear_passes,
            "nested_orders": nested_orders,
            "nested_accounts": nested_accounts,
            "copies_orders": copies_orders,
            "failed_tests": failures,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
