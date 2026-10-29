from __future__ import annotations

from pathlib import Path
from typing import Optional

from .. import selection
from ..contract import JudgeSpec
from ..domain import Verdict  # noqa: F401  (re-exported: judges have always offered it)
from ..selection import Selector


class Judge:
    def __init__(self, spec: JudgeSpec):
        self.spec = spec

    def evaluate(self, workspace: Path, round_no: int) -> Verdict:
        """Run the optional `prepare` step, then score. Subclasses implement `score`."""
        prepared = self._prepare(workspace, round_no)
        if prepared is not None and (not prepared.ok or not all(prepared.gates.values())):
            return prepared  # a broken or out-of-bounds candidate is not worth a model call
        verdict = self.score(workspace, round_no)
        if prepared is not None:
            verdict.gates = {**prepared.gates, **verdict.gates}
            verdict.feedback = "\n".join(x for x in (prepared.feedback, verdict.feedback) if x)
            verdict.seconds += prepared.seconds
        return verdict

    def score(self, workspace: Path, round_no: int) -> Verdict:
        raise NotImplementedError

    def _prepare(self, workspace: Path, round_no: int) -> Optional[Verdict]:
        if not self.spec.prepare:
            return None
        import json
        import shlex
        import subprocess
        import sys
        import time

        from .command import judge_env
        from ..process import run as run_process

        started = time.perf_counter()
        command = self.spec.prepare.replace("{python}", shlex.quote(sys.executable))
        try:
            run = run_process(command, shell=True, cwd=workspace,
                              env=judge_env(workspace / ".unused", round_no), timeout=self.spec.timeout)
        except subprocess.TimeoutExpired:
            return Verdict(None, error=f"prepare step timed out after {self.spec.timeout}s")
        seconds = time.perf_counter() - started
        if run.returncode != 0:
            tail = (run.stdout[-800:] + "\n" + run.stderr[-800:]).strip()
            error_file = workspace / "out" / "error.json"
            if error_file.is_file():
                try:
                    detail = json.loads(error_file.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    detail = {}
                if detail.get("quality_result") == "unknown":
                    return Verdict(None, error=f"prepare unavailable: {detail.get('error') or tail}",
                                   metrics={"stage": detail.get("stage"), "quality_result": "unknown"}, seconds=seconds)
            return Verdict(0.0, {"prepare": False}, f"prepare step failed: {tail}", seconds=seconds)
        gates, notes = {}, ""
        gates_file, notes_file = workspace / "out" / "gates.json", workspace / "out" / "notes.txt"
        if gates_file.exists():
            gates = {str(k): bool(v) for k, v in json.loads(gates_file.read_text(encoding="utf-8")).items()}
        if notes_file.exists():
            notes = notes_file.read_text(encoding="utf-8").strip()
        return Verdict(0.0, gates, notes, seconds=seconds)

    def selection(self) -> Selector:
        """This judge's rule for keeping a candidate; `selection.py` holds the rules."""
        return selection.default(self.spec)

    def prefers(self, candidate_ws: Path, champion_ws: Path, candidate: Verdict, champion: Verdict) -> tuple[bool, str]:
        """Should the candidate replace the champion? Returns (decision, reason)."""
        keep, reason = self.selection().decide(candidate_ws, champion_ws, candidate, champion)
        return keep, reason
