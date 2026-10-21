"""Path patterns used by contracts: `src/*.py`, `docs/**`, `post.md`."""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import PurePosixPath
from typing import Iterable


def normalize(path: str) -> str:
    """Repo-relative POSIX path without a leading `./`; rejects escapes."""
    raw = str(path).strip().replace("\\", "/")
    while raw.startswith("./"):
        raw = raw[2:]
    pure = PurePosixPath(raw)
    if not raw or pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"path must stay inside the project: {path!r}")
    return pure.as_posix()


@lru_cache(maxsize=256)
def _compile(pattern: str) -> re.Pattern:
    pattern = normalize(pattern).rstrip("/")
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    # A bare directory pattern (`judge`) also covers everything below it.
    return re.compile("^" + "".join(out) + "(?:/.*)?$")


def matches(path: str, patterns: Iterable[str]) -> bool:
    try:
        rel = normalize(path)
    except ValueError:
        return False
    return any(_compile(p).match(rel) for p in patterns)


def overlap(a: Iterable[str], b: Iterable[str]) -> list[str]:
    """Patterns from `a` that literally sit inside or contain a pattern from `b`."""
    clashes = []
    for left in a:
        for right in b:
            l, r = normalize(left).rstrip("/"), normalize(right).rstrip("/")
            if matches(l, [r]) or matches(r, [l]):
                clashes.append(f"{left} <-> {right}")
    return clashes
