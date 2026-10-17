from __future__ import annotations
import os
import re
import subprocess
from pathlib import Path

def _safe(task_id: str) -> str:
    if ".." in str(task_id):
        raise ValueError("invalid task id")
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(task_id)).strip("-")
    if not value:
        raise ValueError("empty task id")
    return value

def claim_task_lock(root: Path, task_id: str) -> bool:
    locks = Path(root) / ".rsi" / "locks"
    locks.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(locks / (_safe(task_id) + ".lock"), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    return True

def release_task_lock(root: Path, task_id: str):
    (Path(root) / ".rsi" / "locks" / (_safe(task_id) + ".lock")).unlink(missing_ok=True)

def _git(repo: Path, args: list[str], check: bool = True):
    return subprocess.run(["git", *args], cwd=repo, check=check, capture_output=True, text=True)

def create_worktree(repo_root: Path, task_id: str) -> Path:
    repo, task = Path(repo_root), _safe(task_id)
    target, branch = repo / ".rsi" / "worktrees" / task, f"rsi/{task}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return target
    exists = _git(repo, ["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], check=False).returncode == 0
    args = ["worktree", "add", str(target), branch] if exists else ["worktree", "add", "-b", branch, str(target), "HEAD"]
    _git(repo, args)
    return target

def remove_worktree(repo_root: Path, task_id: str):
    repo, task = Path(repo_root), _safe(task_id)
    target = repo / ".rsi" / "worktrees" / task
    if target.exists():
        _git(repo, ["worktree", "remove", "--force", str(target)])
    _git(repo, ["branch", "-D", f"rsi/{task}"], check=False)
