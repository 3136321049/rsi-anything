#!/usr/bin/env python3
"""CLI for the minimal RSI ratchet."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from core.controller import run_ratchet_loop
from core.guard import load_frozen_hashes, parse_goal, snapshot_hashes, verify_guard
from core.rubric_inducer import induce_rubric

TRACKS = {
    "engineering": Path("tracks/01-engineering"),
    "finance": Path("tracks/03-finance-quant-research"),
}


def _find_track(rel: Path) -> Path:
    roots = [Path.cwd(), Path(__file__).resolve().parent, *Path(__file__).resolve().parents]
    for root in roots:
        candidate = root / rel
        if candidate.exists():
            return candidate
    return rel


def status(track: Path):
    ledger = track / "results.tsv"
    if not ledger.exists():
        print("No ratchet results.")
        return
    lines = ledger.read_text(encoding="utf-8").splitlines()
    if len(lines) < 2:
        print("No ratchet results.")
        return
    header = lines[0].split("\t")
    rows = [dict(zip(header, line.split("\t"))) for line in lines[1:]]
    scores = [float(row["score"]) for row in rows]
    low, high = min(scores), max(scores)
    span = high - low or 1.0
    print("Ratchet progression")
    print("ROUND  SCORE   BEST    STATUS        CHART")
    for row in rows:
        score = float(row["score"])
        filled = 1 + round(18 * (score - low) / span)
        bar = "█" * filled + "░" * (20 - filled)
        print(f"{row['round']:>5}  {float(row['score']):>6.2f}  {float(row['best_score']):>6.2f}  "
              f"{row['status']:<12}  {bar}")


def run_demo(track: Path):
    script = track / "run_demo.py"
    if not script.exists():
        raise SystemExit(f"no demo script at {script}")
    subprocess.run([sys.executable, str(script)], cwd=track, check=True)


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(prog="rsi")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("track_dir", type=Path)
    run.add_argument("--demo", action="store_true")
    run.add_argument("--agent-cmd")
    run.add_argument("--max-iterations", type=int)
    demo = commands.add_parser("demo")
    demo.add_argument("--track", choices=["engineering", "finance", "all"], default="all")
    stat = commands.add_parser("status")
    stat.add_argument("track_dir", type=Path)
    rubric = commands.add_parser("induce-rubric")
    rubric.add_argument("domain")
    rubric.add_argument("topic")
    rubric.add_argument("--output", type=Path)
    guard = commands.add_parser("verify-guard")
    guard.add_argument("track_dir", type=Path)
    args = parser.parse_args(argv)
    if args.command == "run":
        if args.demo:
            run_demo(args.track_dir)
        else:
            run_ratchet_loop(args.track_dir, agent_cmd=args.agent_cmd, max_iterations=args.max_iterations)
    elif args.command == "demo":
        missing = []
        for name, rel in TRACKS.items():
            if args.track not in {name, "all"}:
                continue
            track = _find_track(rel)
            if not (track / "run_demo.py").exists():
                missing.append(f"{name}: no run_demo.py under {track}")
                continue
            run_demo(track)
        if missing and args.track != "all":
            raise SystemExit("\n".join(missing))
        if missing and args.track == "all":
            print("Skipped: " + "; ".join(missing))
    elif args.command == "status":
        status(args.track_dir)
    elif args.command == "induce-rubric":
        print(json.dumps(induce_rubric(args.domain, args.topic, args.output), ensure_ascii=False, indent=2))
    else:
        try:
            goal = parse_goal(args.track_dir / "GOAL.md")
            expected = load_frozen_hashes(args.track_dir)
            current = snapshot_hashes(args.track_dir, goal["frozen_paths"])
            ok, message = verify_guard(args.track_dir, expected, goal["mutable_paths"])
            if ok and current != expected:
                ok, message = False, "frozen path modified or added"
        except ValueError as exc:
            ok, message = False, str(exc)
        print(("OK: " if ok else "FAIL: ") + message)
        raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
