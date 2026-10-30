"""The ratchet: propose, judge in isolation, commit only proven gains.

One run lives on its own branch `rsi/<run-id>`. The champion is that branch's
tip. Each round resets a dedicated worktree to the champion, lets the agent edit
it, keeps only edits inside the artifact paths, judges them in a fresh copy with
the frozen judge files, and commits on a win. The user's own checkout is never
touched; they merge the branch when they like the result.

`Ratchet` owns the lifecycle (store, resume, baseline, budgets, final snapshot,
hold-out). What a round does is the strategy's call (`strategy.py`), whether a
candidate wins is the selector's (`selection.py`), and progress goes out as
events (`events.py`). `_Arena` gives the strategy one round's moves.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Optional

from . import artifacts, gitops, ledger, prompt as briefing, workspace
from .agents import Agent
from .contract import Contract
from .domain import Decision, Proposal
from .events import Broadcast, EventSink, JsonlSink, TerminalLog
from .judges import Judge, Verdict, make_judge
from .ledger import Row, RunStore
from .paths import matches, normalize
from .selection import JudgeSelector, Selector
from .strategy import Strategy, make_strategy

Log = Callable[[str], None]


@contextmanager
def _usage_log(path: Optional[Path]):
    before = os.environ.get("RSI_USAGE_LOG")
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        os.environ["RSI_USAGE_LOG"] = str(path)
    try:
        yield
    finally:
        if before is None:
            os.environ.pop("RSI_USAGE_LOG", None)
        else:
            os.environ["RSI_USAGE_LOG"] = before


class RunError(RuntimeError):
    pass


def _toolkit() -> dict:
    """Which rsi-anything ran this, and which rendering helpers judges imported (they are not frozen)."""
    try:
        version = importlib.metadata.version("rsi-anything")
    except importlib.metadata.PackageNotFoundError:
        version = None
    sdk = Path(__file__).with_name("sdk.py")
    return {"version": version, "sdk_sha256": hashlib.sha256(sdk.read_bytes()).hexdigest() if sdk.exists() else None}


@contextmanager
def task_model(contract: Contract):
    """`roles.task` reaches judge scripts as $RSI_TASK_MODEL, the variable task templates already read.
    The contract wins over the shell while a run or check is going on; the old value comes back after."""
    if not contract.task_model:
        yield
        return
    previous = os.environ.get("RSI_TASK_MODEL")
    os.environ["RSI_TASK_MODEL"] = contract.task_model
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("RSI_TASK_MODEL", None)
        else:
            os.environ["RSI_TASK_MODEL"] = previous


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
                 judge: Optional[Judge] = None, holdout: Optional[Judge] = None,
                 selector: Optional[Selector] = None, strategy: Optional[Strategy] = None,
                 events: tuple[EventSink, ...] = ()):
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
        self.selector = selector or JudgeSelector(self.judge)
        self.strategy = strategy or make_strategy(contract.strategy)
        self.sinks = [TerminalLog(log), *events]
        self.events = Broadcast(self.sinks)
        self.artifact = _prefix(self.rel_root, contract.artifact)
        self.frozen_patterns = _prefix(self.rel_root, contract.frozen_files)
        self.assets = _prefix(self.rel_root, contract.assets)
        self.saved_patterns = list(dict.fromkeys([*contract.artifact, *getattr(contract, "outputs", [])]))
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

    def _evaluate(self, judge: Judge, commit: str, frozen: dict, overlay=None, round_no: int = 0,
                  usage_log: Optional[Path] = None) -> tuple[Verdict, Path]:
        ws = workspace.build(self.repo, commit, frozen, overlay, self.assets)
        try:
            with _usage_log(usage_log):
                return judge.evaluate(self._sub(ws), round_no), ws
        except BaseException:
            workspace.discard(ws)
            raise

    def _configuration(self, store: RunStore, frozen: dict):
        config = store.dir / "config"
        if (config / "execution.json").exists():
            return
        for rel, content in frozen.items():
            target = config / "frozen" / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        (config / "rsi.yaml").write_bytes(frozen.get(_prefix(self.rel_root, ["rsi.yaml"])[0],
                                                       (self.project / "rsi.yaml").read_bytes()))
        execution = {"agent": {**asdict(self.contract.agent), "resolved_adapter": self.agent.name,
                               "requested_model": getattr(self.agent, "model", None) or self.contract.agent.model,
                               "actual_model": None,
                               "reasoning_effort": os.environ.get("RSI_CODEX_REASONING_EFFORT")
                                   if self.agent.name == "codex" else None},
                     "judge": asdict(self.contract.judge), "jury": getattr(self.judge, "models", []),
                     "holdout": asdict(self.contract.holdout) if self.contract.holdout else None,
                     "budget": asdict(self.contract.budget), "artifact": self.contract.artifact,
                     "outputs": getattr(self.contract, "outputs", []),
                     "task_model": os.environ.get("RSI_TASK_MODEL"), "roles": self._roles(), "rsi_anything": _toolkit()}
        artifacts.write_json(config / "execution.json", execution)

    def _roles(self) -> dict:
        """Who did what in this run, as resolved on this machine (`auto` expanded)."""
        model = getattr(self.agent, "model", None) or self.contract.agent.model
        return {"editor": f"{self.agent.name}:{model}" if model else self.agent.name,
                "judge": getattr(self.judge, "models", []) or self.contract.judge.type,
                "compare": getattr(self.judge, "compare_models", None) if self.contract.judge.pairwise else None,
                "task": os.environ.get("RSI_TASK_MODEL")}

    def _saved_evaluation(self, store: RunStore, commit: str, frozen: dict, snapshot: str):
        saved = store.dir / snapshot
        verdict = artifacts.verdict(saved)
        if verdict is not None and verdict.ok and (saved / "manifest.json").exists():
            ws = workspace.build(self.repo, commit, frozen, assets=self.assets)
            try:
                artifacts.restore(saved, self._sub(ws))
            except BaseException:
                workspace.discard(ws)
                raise
            return verdict, ws
        verdict, ws = self._evaluate(self.judge, commit, frozen, usage_log=saved / "judge-usage.jsonl")
        artifacts.save(self._sub(ws), saved, self.saved_patterns, verdict)
        return verdict, ws

    def _checkpoint(self, store: RunStore, **changes):
        meta = store.meta()
        meta.update(changes)
        meta["updated"] = ledger.now()
        store.write_meta(meta)

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
        with task_model(self.contract):
            return self._run(resume)

    def _run(self, resume: Optional[str] = None) -> Summary:
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
            store = RunStore(self.repo, ledger.new_run_id(self.contract.name, self.repo))
            base, branch = gitops.head(self.repo), f"rsi/{store.run_id}"
            champion = base
            store.write_meta({
                "schema": ledger.SCHEMA_VERSION, "strategy": self.strategy.name,
                "run_id": store.run_id, "contract": self.contract.name, "contract_digest": self.contract.digest,
                "goal": self.contract.goal, "base": base, "branch": branch, "project": self.rel_root or ".",
                "agent": self.agent.name, "judge": self.contract.judge.type,
                "jury": getattr(self.judge, "models", []), "started": ledger.now(),
            })
        self.events = Broadcast([*self.sinks, JsonlSink(store.dir / "events.jsonl")])
        frozen = workspace.snapshot_frozen(self.repo, base, self.frozen_patterns)
        self._configuration(store, frozen)
        store.recover_rounds()
        rows = store.rows()
        meta = store.meta()
        active = meta.get("active_round")
        if resume and active and not any(r["round"] == active for r in rows):
            expected = next((r["commit"] for r in reversed(rows) if r.get("commit")), base)
            if not champion.startswith(expected):
                raise RunError("run branch moved before its round was recorded; inspect the branch and round files before resuming")
            store.complete_round(Row(active, ledger.INTERRUPTED, best=rows[-1].get("best") if rows else None,
                                     artifacts=f"rounds/r{active:03d}/artifacts",
                                     note=f"interrupted during {meta.get('phase', 'round')}; retained files, continued from champion"))
            rows = store.rows()
        worktree = store.worktree
        gitops.add_worktree(self.repo, worktree, branch, champion)
        self.events.emit("run_started", run_id=store.run_id, branch=branch, agent=self.agent.name,
                         strategy=self.strategy.name, goal=self.contract.goal, resumed=bool(resume))
        started = time.monotonic()
        elapsed_before = float(meta.get("elapsed_seconds", 0))
        champion_ws = None
        number = rows[-1]["round"] if rows else 0
        champion_row = next((r for r in reversed(rows) if r["status"] in (ledger.KEEP, ledger.BASELINE)), {})
        champion_snapshot = champion_row.get("artifacts") or (
            f"rounds/r{champion_row['round']:03d}/artifacts" if champion_row.get("round") else "artifacts/baseline")
        stop = "round budget used"
        self._checkpoint(store, status="running", phase="baseline" if not rows else "resume", active_round=None,
                         finished=None, error=None, stop_reason=None)
        try:
            champion_verdict, champion_ws = self._saved_evaluation(store, champion, frozen, champion_snapshot)
            if not champion_verdict.ok:
                raise RunError(f"the judge cannot score the starting point: {champion_verdict.error}")
            if not rows:
                row = Row(0, ledger.BASELINE, score=champion_verdict.score, best=champion_verdict.score,
                          gates=champion_verdict.gates, feedback=champion_verdict.feedback, commit=champion[:12],
                          judge_seconds=champion_verdict.seconds, artifacts=champion_snapshot,
                          judge_cost_usd=champion_verdict.metrics.get("cost_usd"))
                if self.holdout:
                    row.holdout = self._holdout(champion, frozen, 0, store.dir / champion_snapshot / "holdout.json")
                store.complete_round(row)
                rows = store.rows()
                self.events.emit("round_finished", round=0, row=asdict(row))
            best, baseline = champion_verdict.score, rows[0]["score"]
            kept = sum(1 for r in rows if r["status"] == ledger.KEEP)
            stagnant = 0
            for row in reversed(rows):
                if row["status"] in (ledger.KEEP, ledger.BASELINE):
                    break
                stagnant += 1
            while True:
                if number >= budget.rounds:
                    stop = f"reached {budget.rounds} rounds"
                    break
                if (elapsed_before + time.monotonic() - started) / 60 >= budget.minutes:
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
                self._checkpoint(store, active_round=number, phase="agent", champion=champion,
                                 elapsed_seconds=elapsed_before + time.monotonic() - started)
                arena = _Arena(self, store, worktree, number, champion, champion_verdict, champion_ws, frozen,
                               best, store.rows())
                outcome = self.strategy.play(arena, number, best)
                row, win = outcome.row, outcome.win
                if win is not None:
                    # 已提交的胜出轮先落盘，账本追加前中断也能恢复。
                    artifacts.write_json(store.round_dir(number) / "result.json", asdict(row))
                    workspace.discard(champion_ws)
                    champion, champion_verdict, champion_ws = win
                    best = row.score
                    kept += 1
                    stagnant = 0
                else:
                    stagnant += 1
                store.complete_round(row)
                if row.status == ledger.KEEP:
                    champion_snapshot = row.artifacts
                self._checkpoint(store, active_round=None, phase="between_rounds", champion=champion,
                                 elapsed_seconds=elapsed_before + time.monotonic() - started)
                self._learn(row)
                self.events.emit("round_finished", round=row.round, row=asdict(row))
            final = store.dir / "artifacts" / "final"
            previous_final = store.meta().get("final_snapshot_champion")
            if previous_final != champion or not final.exists():
                if previous_final and final.exists():
                    # 已完成运行继续得到新版本时，保留上次最终验收和真实调用。
                    history = store.dir / "artifacts" / "final-history" / previous_final[:12]
                    history.parent.mkdir(parents=True, exist_ok=True)
                    final.rename(history)
                artifacts.copy_snapshot(store.dir / champion_snapshot, final, source_snapshot=champion_snapshot)
                self._checkpoint(store, final_snapshot_champion=champion, final_source_artifacts=champion_snapshot)
            self._checkpoint(store, phase="final_holdout", active_round=None)
            holdout = {}
            if self.holdout:
                holdout = {"baseline": rows[0].get("holdout"),
                           "final": self._holdout(champion, frozen, number, final / "holdout.json")}
            self._checkpoint(store, finished=ledger.now(), status="finished", phase="finished", champion=champion,
                             stop_reason=stop, holdout=holdout, final_artifacts="artifacts/final",
                             elapsed_seconds=elapsed_before + time.monotonic() - started)
            self.events.emit("run_finished", run_id=store.run_id, stop_reason=stop, baseline=baseline, best=best,
                             rounds=number, kept=kept, holdout=holdout)
            return Summary(store.run_id, branch, base, champion, baseline, best, number, kept, stop, holdout)
        except BaseException as exc:
            active = store.meta().get("active_round")
            if active and worktree.exists() and not (store.round_dir(active) / "artifacts" / "manifest.json").exists():
                artifacts.save(self._sub(worktree), store.round_dir(active) / "artifacts", self.saved_patterns)
            if active and not any(row["round"] == active for row in store.rows()):
                artifacts.mark_incomplete(store.round_dir(active) / "artifacts")
            status = "interrupted" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "failed"
            self._checkpoint(store, status=status, error=f"{type(exc).__name__}: {exc}", champion=champion,
                             elapsed_seconds=elapsed_before + time.monotonic() - started)
            self.events.emit("run_failed", run_id=store.run_id, status=status, error=f"{type(exc).__name__}: {exc}")
            raise
        finally:
            if champion_ws is not None:
                workspace.discard(champion_ws)
            gitops.reset_worktree(worktree, champion)
            gitops.git(self.repo, "worktree", "remove", "--force", str(worktree), check=False)

    def _holdout(self, commit: str, frozen: dict, number: int, receipt: Optional[Path] = None) -> Optional[float]:
        if receipt is not None and receipt.exists():
            verdict = Verdict(**json.loads(receipt.read_text(encoding="utf-8")))
            return verdict.score if verdict.ok else None
        verdict, ws = self._evaluate(self.holdout, commit, frozen, round_no=number,
                                    usage_log=receipt.parent / "holdout-usage.jsonl" if receipt else None)
        try:
            if receipt is not None:
                artifacts.save(self._sub(ws), receipt.parent / "holdout-artifacts", self.saved_patterns, verdict)
        finally:
            workspace.discard(ws)
        if receipt is not None:
            artifacts.write_json(receipt, asdict(verdict))
        return verdict.score if verdict.ok else None

    def _learn(self, row: Row):
        score = "-" if row.score is None else f"{row.score:g}"
        what = row.hypothesis or "(no hypothesis given)"
        why = row.note or (row.feedback.splitlines()[0] if row.feedback else "")
        ledger.add_lesson(self.repo, self.contract.name, f"{row.status} score={score}: {what} -- {why}"[:500])


class _Arena:
    """One round's moves, handed to the strategy (see `strategy.Arena`)."""

    def __init__(self, ratchet: Ratchet, store: RunStore, worktree: Path, number: int, champion: str,
                 champion_verdict: Verdict, champion_ws: Path, frozen: dict, best: Optional[float], rows: list):
        self.r, self.store, self.worktree, self.number = ratchet, store, worktree, number
        self.champion, self.champion_verdict, self.champion_ws = champion, champion_verdict, champion_ws
        self.frozen, self.best, self.rows = frozen, best, rows
        self.round_dir = store.round_dir(number)

    def propose(self, number: int) -> Proposal:
        r, worktree = self.r, self.worktree
        gitops.reset_worktree(worktree, self.champion)
        workspace.link_assets(r.repo, worktree, r.assets)
        workspace.remove_matching(worktree, r.hidden)
        text = briefing.build(r.contract, self.best, self.champion_verdict, self.rows,
                              ledger.read_lessons(r.repo, r.contract.name))
        (self.round_dir / "prompt.md").write_text(text, encoding="utf-8")
        r.events.emit("round_started", round=number, agent=r.agent.name)
        control = gitops.control_files(r.repo)
        try:
            with _usage_log(self.round_dir / "agent-usage.jsonl"):
                result = r.agent.run(r._sub(worktree), text, self.round_dir, r.contract.agent.timeout)
        finally:
            tampered = gitops.restore_control_files(control, gitops.control_files(r.repo))
        (self.round_dir / "agent-final.txt").write_text(result.text, encoding="utf-8")
        snapshot = f"rounds/r{number:03d}/artifacts"
        artifacts.save(r._sub(worktree), self.store.dir / snapshot, r.saved_patterns)
        proposal = Proposal(number, result.hypothesis, agent_seconds=result.seconds, cost_usd=result.cost_usd,
                            snapshot=snapshot)
        if tampered:
            proposal.failure = ledger.AGENT_FAIL
            proposal.note = "agent changed git config or hooks (restored): " + ", ".join(tampered)
        elif not result.ok:
            proposal.failure, proposal.note = ledger.AGENT_FAIL, result.error[:300]
        else:
            proposal.changed, proposal.ignored = r._changes(worktree)
            if not proposal.changed:
                proposal.failure = ledger.NO_CHANGE
                proposal.note = "no edits inside the artifact paths" + (
                    f"; ignored {len(proposal.ignored)} other edits" if proposal.ignored else "")
            else:
                allowed = proposal.changed
                (self.round_dir / "diff.patch").write_text(
                    gitops.git(worktree, "diff", "--", *allowed) + "\n" + "\n".join(
                        f"(new file) {p}" for p in allowed if not gitops.show(worktree, self.champion, p)),
                    encoding="utf-8")
                proposal.overlay = {p: ((worktree / p).read_bytes() if (worktree / p).is_file() else None)
                                    for p in allowed}
        r.events.emit("agent_finished", round=number, failure=proposal.failure, hypothesis=proposal.hypothesis,
                      changed=proposal.changed, seconds=round(result.seconds, 1))
        return proposal

    def evaluate(self, proposal: Proposal) -> tuple[Verdict, Path]:
        r = self.r
        r._checkpoint(self.store, phase="judge")
        verdict, ws = r._evaluate(r.judge, self.champion, self.frozen, proposal.overlay, proposal.round,
                                  self.round_dir / "judge-usage.jsonl")
        artifacts.save(r._sub(ws), self.store.dir / proposal.snapshot, r.saved_patterns, verdict)
        (self.round_dir / "verdict.json").write_text(
            json.dumps({"score": verdict.score, "gates": verdict.gates, "feedback": verdict.feedback,
                        "metrics": verdict.metrics, "error": verdict.error}, indent=2,
                       ensure_ascii=False, default=str), encoding="utf-8")
        r.events.emit("judged", round=proposal.round, ok=verdict.ok, score=verdict.score, gates=verdict.gates,
                      seconds=round(verdict.seconds, 1))
        return verdict, ws

    def decide(self, ws: Path, verdict: Verdict) -> Decision:
        with _usage_log(self.round_dir / "judge-usage.jsonl"):
            return self.r.selector.decide(self.r._sub(ws), self.r._sub(self.champion_ws), verdict,
                                          self.champion_verdict)

    def commit(self, proposal: Proposal, verdict: Verdict) -> str:
        before = "none" if self.best is None else f"{self.best:g}"
        message = f"rsi r{proposal.round}: {proposal.hypothesis or 'improvement'} ({before} -> {verdict.score:g})"
        self.r._checkpoint(self.store, phase="commit")
        # 助手可能暂存了范围外文件；提交前重建暂存区，只纳入已评审的文件。
        gitops.git(self.worktree, "reset")
        return gitops.commit_paths(self.worktree, proposal.changed, message[:200])

    def discard(self, ws: Path) -> None:
        workspace.discard(ws)
