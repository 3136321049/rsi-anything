"""The loop's vocabulary as plain data: verdicts, decisions, proposals and ledger rows.

Nothing here touches disk, git, processes or models, so every other layer can
depend on it. See docs/PLAN.md for the layers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

# Round outcomes. Only KEEP moves the champion.
BASELINE = "BASELINE"
KEEP = "KEEP"
REVERT = "REVERT"            # judged, not better (or a gate failed)
NO_CHANGE = "NO_CHANGE"      # the agent changed nothing inside the artifact paths
AGENT_FAIL = "AGENT_FAIL"    # the agent crashed or timed out
JUDGE_FAIL = "JUDGE_FAIL"    # the judge could not produce a verdict
INTERRUPTED = "INTERRUPTED"  # An interrupted round keeps its state; resuming never silently repeats it.


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


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


@dataclass
class Decision:
    """Whether a judged candidate replaces the champion, and why. Unpacks as `(keep, reason)`."""
    keep: bool
    reason: str
    tie: bool = False  # neither score beats the other by the margin; a later rule may break the tie

    def __iter__(self):
        return iter((self.keep, self.reason))


@dataclass
class Proposal:
    """What one agent attempt left behind, before any judging."""
    round: int
    hypothesis: str = ""
    changed: list[str] = field(default_factory=list)     # edits inside the artifact paths
    ignored: list[str] = field(default_factory=list)     # edits elsewhere, discarded
    overlay: dict[str, Optional[bytes]] = field(default_factory=dict)  # path -> new bytes (None = deleted)
    agent_seconds: float = 0.0
    cost_usd: Optional[float] = None
    snapshot: str = ""                                   # run-relative folder holding the saved attempt
    failure: str = ""                                    # AGENT_FAIL or NO_CHANGE when nothing can be judged
    note: str = ""


@dataclass
class Row:
    round: int
    status: str
    hypothesis: str = ""
    score: Optional[float] = None
    best: Optional[float] = None
    gates: dict[str, bool] = field(default_factory=dict)
    feedback: str = ""
    commit: str = ""
    changed: list[str] = field(default_factory=list)
    ignored: list[str] = field(default_factory=list)
    agent_seconds: float = 0.0
    judge_seconds: float = 0.0
    cost_usd: Optional[float] = None
    judge_cost_usd: Optional[float] = None
    artifacts: str = ""
    holdout: Optional[float] = None
    note: str = ""
    time: str = field(default_factory=now)
