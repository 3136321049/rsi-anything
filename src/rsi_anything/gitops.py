"""Thin wrappers around the git commands the ratchet needs."""
from __future__ import annotations

import io
import subprocess
import tarfile
from pathlib import Path
from typing import Optional


class GitError(RuntimeError):
    pass


def git(repo: Path, *args: str, check: bool = True, input: Optional[bytes] = None, strip: bool = True) -> str:
    run = subprocess.run(["git", *args], cwd=repo, input=input, capture_output=True)
    if check and run.returncode != 0:
        detail = run.stderr.decode("utf-8", "replace").strip() or run.stdout.decode("utf-8", "replace").strip()
        raise GitError(f"git {' '.join(args)} failed: {detail}")
    out = run.stdout.decode("utf-8", "replace")
    return out.strip() if strip else out


def toplevel(path: Path) -> Path:
    try:
        return Path(git(path, "rev-parse", "--show-toplevel"))
    except GitError as exc:
        raise GitError(f"{path} is not inside a git repository; run `git init` and commit first") from exc


def head(repo: Path, ref: str = "HEAD") -> str:
    return git(repo, "rev-parse", ref)


def dirty_paths(repo: Path) -> list[str]:
    """Tracked or untracked paths that differ from HEAD (ignored files excluded)."""
    out = git(repo, "status", "--porcelain", "-z", "--untracked-files=all", strip=False)
    paths, items = [], out.split("\0")
    i = 0
    while i < len(items):
        entry = items[i]
        if not entry:
            i += 1
            continue
        status, path = entry[:2], entry[3:]
        paths.append(path)
        if "R" in status or "C" in status:  # renames carry the old path as the next item
            i += 1
        i += 1
    return paths


def exclude_locally(repo: Path, pattern: str):
    """Add a pattern to .git/info/exclude so run state never shows up as a change."""
    exclude = Path(git(repo, "rev-parse", "--git-path", "info/exclude"))
    if not exclude.is_absolute():
        exclude = repo / exclude
    exclude.parent.mkdir(parents=True, exist_ok=True)
    lines = exclude.read_text(encoding="utf-8").splitlines() if exclude.exists() else []
    if pattern not in lines:
        exclude.write_text("\n".join([*lines, pattern]) + "\n", encoding="utf-8")


def branch_exists(repo: Path, branch: str) -> bool:
    return subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=repo).returncode == 0


def add_worktree(repo: Path, path: Path, branch: str, start: str):
    if path.exists():
        return
    if branch_exists(repo, branch):
        git(repo, "worktree", "add", "--force", str(path), branch)
    else:
        git(repo, "worktree", "add", "-b", branch, str(path), start)


def reset_worktree(worktree: Path, commit: str):
    """Put the worktree back to exactly `commit`, dropping every edit and stray file."""
    git(worktree, "reset", "--hard", commit)
    git(worktree, "clean", "-fdx")


def commit_paths(worktree: Path, paths: list[str], message: str) -> str:
    git(worktree, "add", "--all", "--", *paths)
    git(worktree, "commit", "--no-verify", "-m", message)
    return head(worktree)


def show(repo: Path, commit: str, path: str) -> Optional[bytes]:
    run = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=repo, capture_output=True)
    return run.stdout if run.returncode == 0 else None


def export_tree(repo: Path, commit: str, dest: Path):
    """Write the committed tree of `commit` into `dest` (no .git, no untracked files)."""
    data = subprocess.run(["git", "archive", "--format=tar", commit], cwd=repo, capture_output=True, check=True).stdout
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        for member in tar.getmembers():
            target = (dest / member.name).resolve()
            if not str(target).startswith(str(dest.resolve())):
                raise GitError(f"refusing to extract {member.name} outside {dest}")
        tar.extractall(dest)


def diff_stat(repo: Path, base: str, tip: str) -> str:
    return git(repo, "diff", "--stat", base, tip)
