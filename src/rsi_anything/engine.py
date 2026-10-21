"""The ratchet: propose, judge in isolation, commit only proven gains.

One run lives on its own branch `rsi/<run-id>`. The champion is that branch's
tip. Each round resets a dedicated worktree to the champion, lets the agent edit
it, keeps only edits inside the artifact paths, judges them in a fresh copy with
the frozen judge files, and commits on a win. The user's own checkout is never
touched; they merge the branch when they like the result.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from . import gitops, ledger, prompt as briefing, workspace
from .agents import Agent
from .contract import Contract
from .judges import Judge, Verdict, make_judge
from .ledger import Row, RunStore
from .paths import matches, normalize

Log = Callable[[str], None]


class RunError(RuntimeError):
    pass


@dataclass
class Summary:
    run_id: str
    branch: str
    base: str
    champion: str
    baseline: Optional[float]
    best: Optional[float]
    rounds: int
    kept: int
    stop_reason: str
    holdout: dict = field(default_factory=dict)


def _prefix(rel_root: str, patterns: list[str]) -> list[str]:
    return [f"{rel_root}/{p}" if rel_root else p for p in patterns]


class Ratchet:
    def __init__(self, project: Path, contract: Contract, agent: Agent, log: Log = print,
                 judge: Optional[Judge] = None, holdout: Optional[Judge] = None):
        self.project = Path(project).resolve()
        self.repo = gitops.toplevel(self.project)
        self.rel_root = "" if self.project == self.repo else self.project.relative_to(self.repo).as_posix()
        self.contract = contract
        self.agent = agent
        self.agent.artifact = list(contract.artifact)
        self.judge = judge or make_judge(contract.judge)
        self.holdout = holdout if holdout is not None else (make_judge(contract.holdout) if contract.holdout else None)
        for one in filter(None, [self.judge, self.holdout]):
            if hasattr(one, "avoid"):
                one.avoid = agent.name  # an `auto` jury should not be the same model grading its own work
        self.log = log
        self.artifact = _prefix(self.rel_root, contract.artifact)
        self.frozen_patterns = _prefix(self.rel_root, contract.frozen_files)
        self.assets = _prefix(self.rel_root, contract.assets)
        # Hold-out judge files are removed from the agent's worktree every round; only judges see them.
        hidden = (contract.holdout.files + ([contract.holdout.rubric] if contract.holdout.rubric else [])) if contract.holdout else []
        self.hidden = _prefix(self.rel_root, hidden)

    # ------------------------------------------------------------------ setup

    def _preflight(self):
        dirty = gitops.dirty_paths(self.repo)
        blocking = [p for p in dirty if matches(p, self.frozen_patterns) or matches(p, self.artifact)]
        if blocking:
            raise RunError("commit these first so the baseline and the frozen judge are unambiguous: "
                           + ", ".join(sorted(blocking)[:10]))
        gitops.exclude_locally(self.repo, f"/{ledger.STATE_DIR}/")

    def _sub(self, root: Path) -> Path:
        return root / self.rel_root if self.rel_root else root

    def _evaluate(self, judge: Judge, commit: str, frozen: dict, overlay=None, round_no: int = 0) -> tuple[Verdict, Path]:
        ws = workspace.build(self.repo, commit, frozen, overlay, self.assets)
        return judge.evaluate(self._sub(ws), round_no), ws

    def _changes(self, worktree: Path) -> tuple[list[str], list[str]]:
        allowed, ignored = [], []
        for path in gitops.dirty_paths(worktree):
            path = normalize(path)
            if matches(path, self.assets) or matches(path, self.hidden):
                continue
            (allowed if matches(path, self.artifact) else ignored).append(path)
        return allowed, ignored

    # ------------------------------------------------------------------ run

    def run(self, resume: Optional[str] = None) -> Summary:
        budget = self.contract.budget
        self._preflight()
        if resume:
            store = RunStore(self.repo, resume)
            meta = store.meta()
            if not meta:
                raise RunError(f"no run named {resume}")
            if meta.get("contract_digest") != self.contract.digest:
                raise RunError("rsi.yaml changed since this run started; start a new run instead of resuming")
            base, branch = meta["base"], meta["branch"]
            champion = gitops.head(self.repo, branch)
        else:
            store = RunStore(self.repo, ledger.new_run_id(self.contract.name))
            base, branch = gitops.head(self.repo), f"rsi/{store.run_id}"
            champion = base
            store.write_meta({
                "run_id": store.run_id, "contract": self.contract.name, "contract_digest": self.contract.digest,
                "goal": self.contract.goal, "base": base, "branch": branch, "project": self.rel_root or ".",
                "agent": self.agent.name, "judge": self.contract.judge.type,
                "jury": getattr(self.judge, "models", []), "started": ledger.now(),
            })
        frozen = workspace.snapshot_frozen(self.repo, base, self.frozen_patterns)
        worktree = store.worktree
        gitops.add_worktree(self.repo, worktree, branch, champion)
        rows = store.rows()

        self.log(f"run {store.run_id}  branch {branch}  agent {self.agent.name}")
        champion_verdict, champion_ws = self._evaluate(self.judge, champion, frozen)
        if not champion_verdict.ok:
            workspace.discard(champion_ws)
            raise RunError(f"the judge cannot score the starting point: {champion_verdict.error}")
        if not rows:
            row = Row(0, ledger.BASELINE, score=champion_verdict.score, best=champion_verdict.score,
                      gates=champion_verdict.gates, feedback=champion_verdict.feedback, commit=champion[:12],
                      judge_seconds=champion_verdict.seconds)
            if self.holdout:
                row.holdout = self._holdout(champion, frozen, 0)
            store.append(row)
            rows = store.rows()
            self.log(f"r0  BASELINE  score {champion_verdict.score:g}"
                     + ("" if champion_verdict.passed else f"  failed gates: {', '.join(champion_verdict.failed_gates())}"))
        best = champion_verdict.score
        baseline = rows[0]["score"]
        kept = sum(1 for r in rows if r["status"] == ledger.KEEP)
        stagnant = 0
        for row in reversed(rows):
            if row["status"] in (ledger.KEEP, ledger.BASELINE):
                break
            stagnant += 1
        started = time.monotonic()
        number = rows[-1]["round"]
        stop = "round budget used"

        try:
            while True:
                if number >= budget.rounds:
                    stop = f"reached {budget.rounds} rounds"
                    break
                if (time.monotonic() - started) / 60 >= budget.minutes:
                    stop = f"time budget of {budget.minutes:g} min used"
                    break
                if stagnant >= budget.stagnation:
                    stop = f"no improvement in {stagnant} rounds"
                    break
                if budget.target is not None and best is not None and champion_verdict.passed and (
                        best >= budget.target if self.contract.judge.direction == "maximize" else best <= budget.target):
                    stop = f"target {budget.target:g} reached"
                    break
                number += 1
                row, win = self._round(number, store, worktree, champion, champion_verdict, champion_ws, frozen,
                                       best, store.rows())
                store.append(row)
                if win is not None:
                    workspace.discard(champion_ws)
                    champion, champion_verdict, champion_ws = win
                    best = row.score
                    kept += 1
                    stagnant = 0
                else:
                    stagnant += 1
                self._learn(row)
                self.log(self._line(row))
        finally:
            workspace.discard(champion_ws)
            gitops.reset_worktree(worktree, champion)
            gitops.git(self.repo, "worktree", "remove", "--force", str(worktree), check=False)

        holdout = {}
        if self.holdout:
            holdout = {"baseline": rows[0].get("holdout"), "final": self._holdout(champion, frozen, number)}
        meta = store.meta()
        meta.update(finished=ledger.now(), champion=champion, stop_reason=stop, holdout=holdout)
        store.write_meta(meta)
        return Summary(store.run_id, branch, base, champion, baseline, best, number, kept, stop, holdout)

    def _round(self, number: int, store: RunStore, worktree: Path, champion: str, champion_verdict: Verdict,
               champion_ws: Path, frozen: dict, best: Optional[float], rows: list) -> tuple[Row, Optional[tuple]]:
        """Play one round. Returns the ledger row and, on a win, (commit, verdict, judge workspace)."""
        round_dir = store.round_dir(number)
        gitops.reset_worktree(worktree, champion)
        workspace.link_assets(self.repo, worktree, self.assets)
        workspace.remove_matching(worktree, self.hidden)
        text = briefing.build(self.contract, best, champion_verdict, rows,
                              ledger.read_lessons(self.repo, self.contract.name))
        (round_dir / "prompt.md").write_text(text, encoding="utf-8")
        self.log(f"r{number}  {self.agent.name} is working...")
        control = gitops.control_files(self.repo)
        result = self.agent.run(self._sub(worktree), text, round_dir, self.contract.agent.timeout)
        tampered = gitops.restore_control_files(control, gitops.control_files(self.repo))
        if tampered:
            return Row(number, ledger.AGENT_FAIL, result.hypothesis, best=best, agent_seconds=result.seconds,
                       cost_usd=result.cost_usd, note="agent changed git config or hooks (restored): "
                       + ", ".join(tampered)), None
        if not result.ok:
            return Row(number, ledger.AGENT_FAIL, result.hypothesis, best=best, agent_seconds=result.seconds,
                       cost_usd=result.cost_usd, note=result.error[:300]), None
        allowed, ignored = self._changes(worktree)
        if not allowed:
            return Row(number, ledger.NO_CHANGE, result.hypothesis, best=best, ignored=ignored,
                       agent_seconds=result.seconds, cost_usd=result.cost_usd,
                       note="no edits inside the artifact paths" + (f"; ignored {len(ignored)} other edits" if ignored else "")), None
        (round_dir / "diff.patch").write_text(
            gitops.git(worktree, "diff", "--", *allowed) + "\n" + "\n".join(
                f"(new file) {p}" for p in allowed if not gitops.show(worktree, champion, p)), encoding="utf-8")
        overlay = {p: ((worktree / p).read_bytes() if (worktree / p).is_file() else None) for p in allowed}
        verdict, ws = self._evaluate(self.judge, champion, frozen, overlay, number)
        (round_dir / "verdict.json").write_text(
            json.dumps({"score": verdict.score, "gates": verdict.gates, "feedback": verdict.feedback,
                                      "metrics": verdict.metrics, "error": verdict.error}, indent=2,
                                     ensure_ascii=False, default=str), encoding="utf-8")
        common = dict(hypothesis=result.hypothesis, changed=allowed, ignored=ignored,
                      agent_seconds=round(result.seconds, 1), judge_seconds=round(verdict.seconds, 1),
                      cost_usd=result.cost_usd, gates=verdict.gates, feedback=verdict.feedback[:1500])
        if not verdict.ok:
            workspace.discard(ws)
            return Row(number, ledger.JUDGE_FAIL, best=best, note=verdict.error[:300], **common), None
        keep, reason = self.judge.prefers(self._sub(ws), self._sub(champion_ws), verdict, champion_verdict)
        if not keep:
            workspace.discard(ws)
            return Row(number, ledger.REVERT, score=verdict.score, best=best, note=reason[:300], **common), None
        before = "none" if best is None else f"{best:g}"
        message = f"rsi r{number}: {result.hypothesis or 'improvement'} ({before} -> {verdict.score:g})"
        commit = gitops.commit_paths(worktree, allowed, message[:200])
        row = Row(number, ledger.KEEP, score=verdict.score, best=verdict.score, commit=commit[:12], note=reason[:300],
                  **common)
        return row, (commit, verdict, ws)

    def _holdout(self, commit: str, frozen: dict, number: int) -> Optional[float]:
        verdict, ws = self._evaluate(self.holdout, commit, frozen, round_no=number)
        workspace.discard(ws)
        return verdict.score if verdict.ok else None

    def _learn(self, row: Row):
        score = "-" if row.score is None else f"{row.score:g}"
        what = row.hypothesis or "(no hypothesis given)"
        why = row.note or (row.feedback.splitlines()[0] if row.feedback else "")
        ledger.add_lesson(self.repo, self.contract.name, f"{row.status} score={score}: {what} -- {why}"[:500])

    @staticmethod
    def _line(row: Row) -> str:
        score = "" if row.score is None else f"score {row.score:g}  "
        detail = row.hypothesis[:90] if row.status == ledger.KEEP else (row.note or row.hypothesis)[:110]
        return f"r{row.round}  {row.status:<10} {score}{detail}"
