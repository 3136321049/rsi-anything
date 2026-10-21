"""Judge workspaces: a clean copy the candidate cannot reach.

The agent edits its own git worktree. The judge never runs there. For every
evaluation we build a fresh directory from the committed champion tree, copy in
only the candidate files that sit inside the artifact paths, then copy the
frozen judge files from the snapshot taken when the run started. Edits the agent
made to tests, rubrics or evaluator code therefore never reach the judge, and
bytecode caches are stripped so a planted `.pyc` cannot stand in for frozen code.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from . import gitops
from .paths import matches, normalize

_CACHE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def snapshot_frozen(repo: Path, commit: str, patterns: list[str]) -> dict[str, bytes]:
    """Read every committed file matching the frozen patterns at `commit`."""
    listed = gitops.git(repo, "ls-tree", "-r", "--name-only", commit)

    files = [path for path in listed.splitlines() if matches(path, patterns)]
    snapshot = {}
    for path in files:
        content = gitops.show(repo, commit, path)
        if content is not None:
            snapshot[path] = content
    return snapshot


def _strip_caches(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        for name in list(dirnames):
            if name in _CACHE_DIRS:
                shutil.rmtree(Path(dirpath) / name, ignore_errors=True)
                dirnames.remove(name)
        for name in filenames:
            if name.endswith((".pyc", ".pyo")):
                (Path(dirpath) / name).unlink(missing_ok=True)


def build(repo: Path, commit: str, frozen: dict[str, bytes], overlay: Optional[dict[str, Optional[bytes]]] = None,
          assets: Optional[list[str]] = None, parent: Optional[Path] = None) -> Path:
    """Materialize `commit` + candidate overlay + frozen judge files in a new temp dir."""
    dest = Path(tempfile.mkdtemp(prefix="rsi-judge-", dir=parent))
    gitops.export_tree(repo, commit, dest)
    for rel, content in (overlay or {}).items():
        target = dest / normalize(rel)
        if content is None:
            if target.is_file():
                target.unlink()
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    for rel, content in frozen.items():
        target = dest / normalize(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    for rel in assets or []:
        source = (Path(repo) / normalize(rel)).resolve()
        target = dest / normalize(rel)
        if source.exists() and not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(source, target_is_directory=source.is_dir())
    _strip_caches(dest)
    return dest


def link_assets(repo: Path, worktree: Path, assets: list[str]):
    """Give the agent read access to untracked assets (videos, datasets) by symlink."""
    for rel in assets:
        source = (Path(repo) / normalize(rel)).resolve()
        target = worktree / normalize(rel)
        if source.exists() and not target.exists() and not target.is_symlink():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(source, target_is_directory=source.is_dir())


def discard(path: Path):
    shutil.rmtree(path, ignore_errors=True)


def remove_matching(root: Path, patterns: list[str]):
    """Delete files under `root` that match `patterns` (used to hide hold-out data from the agent)."""
    if not patterns:
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            path = Path(dirpath) / name
            if matches(path.relative_to(root).as_posix(), patterns):
                path.unlink()
