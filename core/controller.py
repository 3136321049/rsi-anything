from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path
from .guard import _safe_rel, parse_goal, save_frozen_hashes, snapshot_hashes, verify_guard
from .judge import run_evaluator
from .memory import append_lesson, append_result, init_ledger, read_lessons

_IGNORED = {".git", "__pycache__", ".pytest_cache", "worktrees", "locks"}
_BOOKKEEPING = {"results.tsv", ".rsi/lessons.md", ".rsi/frozen.sha256"}

def print_attribution_banner(track_name: str, credits: list[str]):
    lines = [f"RSI-Anything track: {track_name}", f"Upstream credit: {', '.join(credits) if credits else 'none declared'}"]
    width = max(len(line) for line in lines)
    print("╭" + "─" * (width + 2) + "╮\n" + "\n".join(f"│ {line.ljust(width)} │" for line in lines) + "\n╰" + "─" * (width + 2) + "╯")

def _iter_track_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and not (set(path.relative_to(root).parts) & _IGNORED):
            yield path.relative_to(root).as_posix(), path

def _capture_tree(root: Path) -> dict[str, bytes]:
    return {rel: path.read_bytes() for rel, path in _iter_track_files(root)}

def _restore_tree(root: Path, state: dict[str, bytes]):
    for rel, path in list(_iter_track_files(root)):
        if rel not in state:
            path.unlink(missing_ok=True)
    for rel, content in state.items():
        (_safe_rel(root, rel)).parent.mkdir(parents=True, exist_ok=True)
        (_safe_rel(root, rel)).write_bytes(content)

def _capture_paths(root: Path, rel_paths: list[str]) -> dict[str, bytes]:
    return {item.relative_to(root).as_posix(): item.read_bytes()
            for rel in rel_paths for item in (sorted(_safe_rel(root, rel).rglob("*")) if _safe_rel(root, rel).is_dir() else [_safe_rel(root, rel)]) if item.is_file()}

def _restore_paths(root: Path, rel_paths: list[str], state: dict[str, bytes]):
    for rel in rel_paths:
        path = _safe_rel(root, rel)
        shutil.rmtree(path) if path.is_dir() else path.unlink(missing_ok=True)
    for rel, content in state.items():
        (_safe_rel(root, rel)).parent.mkdir(parents=True, exist_ok=True)
        (_safe_rel(root, rel)).write_bytes(content)

def _sha(root: Path) -> str:
    run = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, text=True, capture_output=True)
    return run.stdout.strip() if run.returncode == 0 else ""

def _mutate(root: Path, step: dict | None, agent_cmd: str | None, round_no: int):
    env = dict(os.environ, RSI_ROUND=str(round_no), RSI_LESSONS=read_lessons(root))
    if step is None:
        if not agent_cmd:
            raise ValueError("iteration needs a scripted step or agent_cmd")
        subprocess.run(agent_cmd, cwd=root, shell=True, check=True, env=env)
        return
    if callable(step.get("apply")):
        step["apply"](root)
    for rel, content in step.get("files", {}).items():
        dest = _safe_rel(root, rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    for rel in step.get("delete", []):
        _safe_rel(root, rel).unlink(missing_ok=True)
    if step.get("command"):
        subprocess.run(step["command"], cwd=root, shell=True, check=True, env=env)

def run_ratchet_loop(track_dir: Path, steps: list[dict] | None = None,
                     agent_cmd: str | None = None, max_iterations: int | None = None) -> dict:
    root = Path(track_dir).resolve()
    goal = parse_goal(root / "GOAL.md")
    mutable, frozen = goal["mutable_paths"], goal["frozen_paths"]
    rounds = min(goal["max_iterations"] if max_iterations is None else max_iterations,
                 len(steps)) if steps is not None else (goal["max_iterations"] if max_iterations is None else max_iterations)
    for rel in _BOOKKEEPING:
        (root / rel).unlink(missing_ok=True)
    init_ledger(root)
    frozen_hashes = snapshot_hashes(root, frozen)
    save_frozen_hashes(root, frozen_hashes)
    pre_base = _capture_tree(root)
    champion = _capture_paths(root, mutable)
    print_attribution_banner(goal["name"], goal["upstream_credits"])
    os.environ.update(RSI_ROUND="0", RSI_HYPOTHESIS="BASELINE")
    baseline = run_evaluator(root, goal["eval_cmd"])
    after_base = _capture_tree(root)
    if snapshot_hashes(root, frozen) != frozen_hashes or any(after_base.get(b) != pre_base.get(b) for b in _BOOKKEEPING):
        _restore_tree(root, pre_base)
        raise RuntimeError("baseline evaluation tampered with frozen paths or ledger")
    best, higher = baseline.score, goal["direction"] == "maximize"
    append_result(root, 0, "BASELINE", best, best, "BASELINE", _sha(root), baseline.duration_ms, baseline.summary)
    append_lesson(root, f"Round 0 baseline {best:.2f}. Read the ledger before the next hypothesis.")
    history = [{"round": 0, "score": best, "status": "BASELINE"}]
    for number in range(1, rounds + 1):
        step = steps[number - 1] if steps is not None else None
        hypothesis, note = str((step or {}).get("hypothesis", f"agent iteration {number}")), str((step or {}).get("lesson", "")).strip()
        pre_round = _capture_tree(root)
        try:
            _mutate(root, step, agent_cmd, number)
        except Exception as exc:
            _restore_tree(root, pre_round)
            append_result(root, number, hypothesis, best, best, "REVERT_SCORE", notes=str(exc))
            append_lesson(root, f"Round {number} REVERT_SCORE: mutation failed ({exc}).")
            history.append({"round": number, "score": best, "status": "REVERT_SCORE"})
            continue
        post_round = _capture_tree(root)
        changed = sorted(rel for rel in set(pre_round) | set(post_round) if pre_round.get(rel) != post_round.get(rel))
        ok, reason = verify_guard(root, frozen_hashes, mutable, changed)
        if ok and snapshot_hashes(root, frozen) != frozen_hashes:
            ok, reason = False, "frozen path modified or added"
        if not ok:
            _restore_tree(root, pre_round)
            append_result(root, number, hypothesis, best, best, "REVERT_GUARD", notes=reason)
            append_lesson(root, f"Round {number} REVERT_GUARD: {reason}. {hypothesis}. {note}".strip())
            history.append({"round": number, "score": best, "status": "REVERT_GUARD"})
            continue
        os.environ.update(RSI_ROUND=str(number), RSI_HYPOTHESIS=hypothesis, RSI_LESSONS=read_lessons(root))
        result = run_evaluator(root, goal["eval_cmd"])
        after_eval = _capture_tree(root)
        if snapshot_hashes(root, frozen) != frozen_hashes or any(after_eval.get(b) != pre_round.get(b) for b in _BOOKKEEPING):
            _restore_tree(root, pre_round)
            reason = "frozen path or ledger modified during evaluation"
            append_result(root, number, hypothesis, best, best, "REVERT_GUARD", notes=reason)
            append_lesson(root, f"Round {number} REVERT_GUARD: {reason}. {hypothesis}. {note}".strip())
            history.append({"round": number, "score": best, "status": "REVERT_GUARD"})
            continue
        if (result.score > best if higher else result.score < best) and result.passed_gates:
            best, champion, status = result.score, _capture_paths(root, mutable), "KEEP"
            lesson = f"Round {number} KEEP {result.score:.2f}. {hypothesis}. {note}"
        else:
            _restore_paths(root, mutable, champion)
            status, lesson = "REVERT_SCORE", f"Round {number} REVERT_SCORE candidate {result.score:.2f} best {best:.2f} gates={result.passed_gates}. {hypothesis}. {note}"
        append_result(root, number, hypothesis, result.score, best, status, _sha(root), result.duration_ms, result.summary)
        append_lesson(root, lesson.strip())
        history.append({"round": number, "score": result.score, "status": status})
        target = float(goal["target_score"])
        if status == "KEEP" and ((higher and best >= target) or (not higher and best <= target)):
            break
    return {"best_score": best, "rounds": history, "target_reached": best >= float(goal["target_score"]) if higher else best <= float(goal["target_score"])}
