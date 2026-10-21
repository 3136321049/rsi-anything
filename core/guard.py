from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any

def _scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value[:1] == "[" and value[-1:] == "]":
        inner = value[1:-1].strip()
        return [] if not inner else [_scalar(part) for part in inner.split(",")]
    try:
        return float(value) if any(ch in value for ch in ".eE") else int(value)
    except ValueError:
        return value

def _safe_rel(root: Path, rel: str) -> Path:
    raw = str(rel).strip()
    raw = raw[2:] if raw.startswith("./") else raw
    p, base = Path(raw), Path(root).resolve()
    if not raw or p.is_absolute() or ".." in p.parts or not (base / p).resolve().is_relative_to(base):
        raise ValueError(f"unsafe path: {rel}")
    return Path(root) / p

def parse_goal(goal_path: Path) -> dict:
    """Parse YAML frontmatter and the markdown body. Unknown keys are kept."""
    goal_file = Path(goal_path).resolve()
    text = goal_file.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if not text.startswith("---") or len(parts) != 3:
        raise ValueError("GOAL.md requires closed YAML frontmatter")
    data: dict[str, Any] = {}
    active = None
    for raw in parts[1].splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            if active is None:
                raise ValueError("list item without a key")
            data[active] = [*data[active], _scalar(line[2:])] if isinstance(data.get(active), list) else [_scalar(line[2:])]
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {raw}")
        active, raw_value = line.split(":", 1)
        active, data[active.strip()] = active.strip(), _scalar(raw_value)
    goal: dict[str, Any] = {
        "name": "", "track": "", "direction": "maximize", "target_score": 0.0,
        "max_iterations": 1, "eval_cmd": "", "mutable_paths": [], "frozen_paths": [],
        "upstream_credits": [],
    }
    goal.update(data)
    if goal["direction"] not in {"maximize", "minimize"}:
        raise ValueError("direction must be maximize or minimize")
    goal["target_score"], goal["max_iterations"] = float(goal["target_score"]), int(goal["max_iterations"])
    for key in ("mutable_paths", "frozen_paths", "upstream_credits"):
        goal[key] = [str(x) for x in (goal[key] if isinstance(goal[key], list) else [goal[key]]) if str(x).strip()]
    for rel in [*goal["mutable_paths"], *goal["frozen_paths"]]:
        _safe_rel(goal_file.parent, rel)
    goal["body"] = parts[2].lstrip("\n")
    return goal

def _paths(root: Path, rel_paths: list[str]):
    for rel in rel_paths:
        path = _safe_rel(root, rel)
        yield from ([item for item in sorted(path.rglob("*")) if item.is_file()] if path.is_dir() else [path])

def snapshot_hashes(root: Path, rel_paths: list[str]) -> dict[str, str]:
    """SHA-256 of every listed file. A missing file is recorded as '<missing>'."""
    root = Path(root)
    return {path.relative_to(root).as_posix(): (hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "<missing>")
            for path in _paths(root, rel_paths)}

def save_frozen_hashes(root: Path, hashes: dict[str, str]):
    state = Path(root) / ".rsi"
    state.mkdir(parents=True, exist_ok=True)
    (state / "frozen.sha256").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def load_frozen_hashes(root: Path) -> dict[str, str]:
    manifest = Path(root) / ".rsi" / "frozen.sha256"
    if not manifest.is_file():
        raise ValueError("missing .rsi/frozen.sha256 manifest")
    return json.loads(manifest.read_text(encoding="utf-8"))

def verify_guard(root: Path, frozen_hashes: dict[str, str], mutable_paths: list[str],
                 changed_files: list[str] | None = None) -> tuple[bool, str]:
    """Fail when a frozen file changes, or an edit lands outside mutable_paths."""
    root = Path(root)
    for rel, expected in frozen_hashes.items():
        try:
            path = _safe_rel(root, rel)
        except ValueError as exc:
            return False, str(exc)
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "<missing>"
        if actual != expected:
            return False, f"frozen path modified or deleted: {rel}"
    if changed_files is not None:
        cleaned = [Path(m[2:] if m.startswith("./") else m).as_posix().rstrip("/") for m in mutable_paths]
        def allowed(rel: str) -> bool:
            raw = rel[2:] if rel.startswith("./") else rel
            p = Path(raw)
            if not raw or p.is_absolute() or ".." in p.parts:
                return False
            norm = p.as_posix().rstrip("/")
            return any(norm == item or norm.startswith(item + "/") for item in cleaned if item)
        if illegal := sorted(rel for rel in changed_files if not allowed(rel)):
            return False, "change outside mutable_paths: " + ", ".join(illegal)
    return True, "guard passed"
