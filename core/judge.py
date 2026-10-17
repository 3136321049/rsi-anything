from __future__ import annotations
import json
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

@dataclass
class EvalResult:
    score: float
    passed_gates: bool
    summary: str
    critique: dict
    duration_ms: int

def run_evaluator(track_dir: Path, eval_cmd: str, timeout_sec: int = 60) -> EvalResult:
    started = time.perf_counter()
    try:
        run = subprocess.run(eval_cmd, cwd=track_dir, shell=True, text=True,
                             capture_output=True, timeout=timeout_sec)
        payload = None
        for line in reversed(run.stdout.strip().splitlines()):
            try:
                candidate = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(candidate, dict) and "score" in candidate:
                payload = candidate
                break
        if payload is None:
            match = re.search(r"SCORE:\s*(-?\d+(?:\.\d+)?)", run.stdout, re.I)
            if not match:
                raise ValueError("evaluator emitted neither JSON nor SCORE")
            payload = {"score": match.group(1), "passed_gates": run.returncode == 0,
                       "summary": run.stdout.strip(), "critique": {}}
        critique = payload.get("critique")
        elapsed = int(round((time.perf_counter() - started) * 1000))
        passed = bool(payload.get("passed_gates", run.returncode == 0)) and run.returncode == 0
        return EvalResult(float(payload["score"]), passed, str(payload.get("summary", "")),
                          critique if isinstance(critique, dict) else ({} if not critique else {"notes": critique}),
                          elapsed)
    except (subprocess.TimeoutExpired, ValueError, TypeError, OSError) as exc:
        elapsed = int(round((time.perf_counter() - started) * 1000))
        return EvalResult(0.0, False, str(exc), {"error": type(exc).__name__}, elapsed)
