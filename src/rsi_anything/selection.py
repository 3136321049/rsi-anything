"""Selection: given a judged candidate and the champion, keep it or throw it away.

Scoring (judges) and selection are separate concerns. A judge turns a workspace
into a `Verdict`; a selector compares two verdicts, and may ask the judge for
more evidence (a head-to-head comparison) before deciding. Selectors stack:

    HeadToHead(GatesThenScore(spec), judge.head_to_head)

The engine takes any object with `decide(...) -> Decision`, so a new rule (a
significance test for noisy timings, a human approval step...) is a new class
here, not an edit to the loop or the judges.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Protocol

from .domain import Decision, Verdict


class Margin(Protocol):
    direction: str
    min_delta: float
    min_gain: float

    def better(self, candidate: float, champion: float) -> bool: ...


class Selector(Protocol):
    def decide(self, candidate_ws: Path, champion_ws: Path, candidate: Verdict, champion: Verdict) -> Decision: ...


class GatesThenScore:
    """Gates first, then the score must clear the configured margin."""

    def __init__(self, margin: Margin):
        self.margin = margin

    def decide(self, candidate_ws: Path, champion_ws: Path, candidate: Verdict, champion: Verdict) -> Decision:
        if not candidate.ok:
            return Decision(False, f"judge error: {candidate.error}")
        if not candidate.passed:
            return Decision(False, "failed gates: " + ", ".join(candidate.failed_gates()))
        if champion.score is None:
            return Decision(True, "champion had no valid score")
        if not champion.passed:  # gates come first: fixing a broken gate is progress whatever the score
            return Decision(True, "passes gates the current best fails (" + ", ".join(champion.failed_gates()) + ")")
        if not self.margin.better(candidate.score, champion.score):
            return Decision(False, f"score {candidate.score:g} is not better than {champion.score:g} "
                                   f"(required margin: {self.margin.min_delta:g} or {self.margin.min_gain:.0%})")
        return Decision(True, f"score {champion.score:g} -> {candidate.score:g}")


@dataclass
class Comparison:
    """Votes from a head-to-head comparison, or why there are none."""
    wins: int = 0
    votes: int = 0
    skipped: str = ""   # comparison not possible for these inputs; the inner decision stands
    error: str = ""     # comparison attempted and failed; the candidate is not kept


Compare = Callable[[Path, Path], Comparison]


class HeadToHead:
    """A higher score is not enough: the candidate must also win most head-to-head votes."""

    def __init__(self, inner: Selector, compare: Compare):
        self.inner = inner
        self.compare = compare

    def decide(self, candidate_ws: Path, champion_ws: Path, candidate: Verdict, champion: Verdict) -> Decision:
        decision = self.inner.decide(candidate_ws, champion_ws, candidate, champion)
        if not decision.keep or not champion.passed:
            return decision
        result = self.compare(candidate_ws, champion_ws)
        if result.skipped:
            return Decision(decision.keep, f"{decision.reason} ({result.skipped})")
        if result.error:
            return Decision(False, f"pairwise check failed: {result.error}")
        if result.wins * 2 > result.votes:
            return Decision(True, f"{decision.reason}; head-to-head {result.wins}/{result.votes}")
        return Decision(False, f"higher score but lost head-to-head ({result.wins}/{result.votes} votes)")


class JudgeSelector:
    """The judge's own selection rule (`Judge.prefers`), as a selector. The engine's default."""

    def __init__(self, judge):
        self.judge = judge

    def decide(self, candidate_ws: Path, champion_ws: Path, candidate: Verdict, champion: Verdict) -> Decision:
        keep, reason = self.judge.prefers(candidate_ws, champion_ws, candidate, champion)
        return Decision(keep, reason)


def default(margin: Margin, compare: Optional[Compare] = None) -> Selector:
    """Gates, then margin, then (when the judge can compare) head-to-head."""
    base = GatesThenScore(margin)
    return HeadToHead(base, compare) if compare is not None else base
