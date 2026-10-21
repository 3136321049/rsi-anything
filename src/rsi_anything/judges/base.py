from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ..contract import JudgeSpec


@dataclass
class Verdict:
    score: Optional[float]
    gates: dict[str, bool] = field(default_factory=dict)
    feedback: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    seconds: float = 0.0
    error: str = ""

    @property
    def ok(self) -> bool:
        return self.score is not None and not self.error

    @property
    def passed(self) -> bool:
        return self.ok and all(self.gates.values())

    def failed_gates(self) -> list[str]:
        return [name for name, good in self.gates.items() if not good]


class Judge:
    def __init__(self, spec: JudgeSpec):
        self.spec = spec

    def evaluate(self, workspace: Path, round_no: int) -> Verdict:
        raise NotImplementedError

    def prefers(self, candidate_ws: Path, champion_ws: Path, candidate: Verdict, champion: Verdict) -> tuple[bool, str]:
        """Should the candidate replace the champion? Returns (decision, reason)."""
        if not candidate.ok:
            return False, f"judge error: {candidate.error}"
        if not candidate.passed:
            return False, "failed gates: " + ", ".join(candidate.failed_gates())
        if champion.score is None:
            return True, "champion had no valid score"
        if not champion.passed:  # gates come first: fixing a broken gate is progress whatever the score
            return True, "passes gates the current best fails (" + ", ".join(champion.failed_gates()) + ")"
        if not self.spec.better(candidate.score, champion.score):
            return False, f"score {candidate.score:g} is not better than {champion.score:g} (required margin: {self.spec.min_delta:g} or {self.spec.min_gain:.0%})"
        return True, f"score {champion.score:g} -> {candidate.score:g}"
