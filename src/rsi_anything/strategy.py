"""Search strategies: what one round does.

The engine owns a run's lifecycle: the store, resuming, the baseline, budgets
and the final snapshot. Each round it hands the strategy an `Arena`, which can
propose a candidate from the champion, judge it in a clean copy, ask the
selector, and commit a winner. The strategy decides how to use those moves.

`Greedy` is the original ratchet: one proposal, judged, kept only if the
selector agrees. Strategies that try several candidates per round, or keep a
population, plug in here without touching the engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol

from .domain import JUDGE_FAIL, KEEP, NO_CHANGE, REVERT, Decision, Proposal, Row, Verdict
from .plugins import Registry


class Arena(Protocol):
    """The moves the engine offers a strategy within one round."""

    def propose(self, number: int) -> Proposal: ...

    def evaluate(self, proposal: Proposal) -> tuple[Verdict, Path]: ...  # verdict and its judge workspace

    def decide(self, workspace: Path, verdict: Verdict) -> Decision: ...

    def commit(self, proposal: Proposal, verdict: Verdict) -> str: ...

    def discard(self, workspace: Path) -> None: ...


@dataclass
class Outcome:
    row: Row
    win: Optional[tuple[str, Verdict, Path]] = None  # (commit, verdict, judge workspace) when the champion changes


class Strategy(Protocol):
    name: str

    def play(self, arena: Arena, number: int, best: Optional[float]) -> Outcome: ...


class Greedy:
    """One focused change per round from the current best; keep it only if it is proven better."""
    name = "greedy"

    def play(self, arena: Arena, number: int, best: Optional[float]) -> Outcome:
        proposal = arena.propose(number)
        if proposal.failure:
            extra = {"ignored": proposal.ignored} if proposal.failure == NO_CHANGE else {}
            return Outcome(Row(number, proposal.failure, proposal.hypothesis, best=best, agent_seconds=proposal.agent_seconds,
                               cost_usd=proposal.cost_usd, artifacts=proposal.snapshot, note=proposal.note, **extra))
        verdict, workspace = arena.evaluate(proposal)
        common = dict(hypothesis=proposal.hypothesis, changed=proposal.changed, ignored=proposal.ignored,
                      agent_seconds=round(proposal.agent_seconds, 1), judge_seconds=round(verdict.seconds, 1),
                      cost_usd=proposal.cost_usd, gates=verdict.gates, feedback=verdict.feedback[:1500],
                      artifacts=proposal.snapshot, judge_cost_usd=verdict.metrics.get("cost_usd"))
        if not verdict.ok:
            arena.discard(workspace)
            return Outcome(Row(number, JUDGE_FAIL, best=best, note=verdict.error[:300], **common))
        try:
            decision = arena.decide(workspace, verdict)
        except BaseException:
            arena.discard(workspace)
            raise
        if not decision.keep:
            arena.discard(workspace)
            return Outcome(Row(number, REVERT, score=verdict.score, best=best, note=decision.reason[:300], **common))
        commit = arena.commit(proposal, verdict)
        row = Row(number, KEEP, score=verdict.score, best=verdict.score, commit=commit[:12],
                  note=decision.reason[:300], **common)
        return Outcome(row, (commit, verdict, workspace))


# `strategy:` in rsi.yaml; packages add more through the `rsi_anything.strategies` entry point.
STRATEGIES = Registry("rsi_anything.strategies", "strategy")
STRATEGIES.register(Greedy.name, Greedy, "built-in")


def make_strategy(name: str = "greedy") -> Strategy:
    return STRATEGIES.get(name)()
