"""A judge that runs your own command (tests, benchmark, eval script).

The command reports through a result file, not stdout, so printed text from the
code under test cannot pose as a score. Write JSON to the path in `$RSI_RESULT`:

    {"score": 87.5, "gates": {"tests": true}, "feedback": "p95 still 4ms", "metrics": {...}}

`rsi_anything.report_result(...)` does this for Python judges. A non-zero exit
code fails the `exit_code` gate. `{python}` in the command is replaced by the
interpreter running rsi, so judges can `import rsi_anything` wherever rsi is installed.
"""
from __future__ import annotations

import json
import os
import shlex
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from .base import Judge, Verdict

# Engine-internal variables never leak into a judge; user settings such as RSI_TASK_MODEL do.
_INTERNAL = {"RSI_RESULT", "RSI_ROUND", "RSI_HYPOTHESIS", "RSI_LESSONS", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT"}


def judge_env(result_file: Path, round_no: int) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in _INTERNAL}
    env.update(RSI_RESULT=str(result_file), RSI_ROUND=str(round_no), PYTHONDONTWRITEBYTECODE="1")
    return env


class CommandJudge(Judge):
    def _once(self, workspace: Path, round_no: int) -> Verdict:
        started = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix="rsi-result-") as box:
            result_file = Path(box) / "result.json"
            try:
                command = self.spec.run.replace("{python}", shlex.quote(sys.executable))
                run = subprocess.run(command, shell=True, cwd=workspace, env=judge_env(result_file, round_no),
                                     capture_output=True, text=True, timeout=self.spec.timeout)
            except subprocess.TimeoutExpired:
                return Verdict(None, error=f"judge timed out after {self.spec.timeout}s",
                               seconds=time.perf_counter() - started)
            seconds = time.perf_counter() - started
            tail = (run.stdout[-1500:] + "\n" + run.stderr[-1500:]).strip()
            if not result_file.exists():
                return Verdict(None, error=f"judge wrote no result to $RSI_RESULT (exit {run.returncode})",
                               metrics={"output_tail": tail}, seconds=seconds)
            try:
                data = json.loads(result_file.read_text(encoding="utf-8"))
                score = float(data["score"])
            except (ValueError, KeyError, TypeError) as exc:
                return Verdict(None, error=f"bad result file: {exc}", seconds=seconds)
        gates = {str(k): bool(v) for k, v in (data.get("gates") or {}).items()}
        gates["exit_code"] = run.returncode == 0
        metrics = dict(data.get("metrics") or {})
        if run.returncode != 0:
            metrics["output_tail"] = tail
        return Verdict(score, gates, str(data.get("feedback", "")), metrics, seconds)

    def score(self, workspace: Path, round_no: int) -> Verdict:
        runs = [self._once(workspace, round_no) for _ in range(self.spec.repeats)]
        bad = next((v for v in runs if not v.ok), None)
        if bad:
            return bad
        first = runs[0]
        gates = {name: all(v.gates.get(name, False) for v in runs) for name in first.gates}
        scores = [v.score for v in runs]
        metrics = dict(first.metrics)
        if len(runs) > 1:
            metrics["repeat_scores"] = scores
        return Verdict(statistics.median(scores), gates, first.feedback, metrics, sum(v.seconds for v in runs))
