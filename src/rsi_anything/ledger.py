"""Run state on disk: an append-only ledger per run and lessons that outlive runs.

Layout inside the project (excluded from git automatically):

    .rsi/
      lessons/<contract-name>.md      lessons carried into every future run
      runs/<run-id>/run.json          what was frozen, base commit, branch, agent
      runs/<run-id>/ledger.jsonl      one row per round, never rewritten
      runs/<run-id>/rounds/rNNN/      prompt, agent transcript, judge output, diff
      worktrees/<run-id>/             the agent's sandbox checkout
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

STATE_DIR = ".rsi"

# Round outcomes. Only KEEP moves the champion.
BASELINE = "BASELINE"
KEEP = "KEEP"
REVERT = "REVERT"            # judged, not better (or a gate failed)
NO_CHANGE = "NO_CHANGE"      # the agent changed nothing inside the artifact paths
AGENT_FAIL = "AGENT_FAIL"    # the agent crashed or timed out
JUDGE_FAIL = "JUDGE_FAIL"    # the judge could not produce a verdict


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_run_id(name: str) -> str:
    slug = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")[:32] or "run"
    return f"{time.strftime('%Y%m%d-%H%M%S')}-{slug}"


@dataclass
class Row:
    round: int
    status: str
    hypothesis: str = ""
    score: Optional[float] = None
    best: Optional[float] = None
    gates: dict[str, bool] = field(default_factory=dict)
    feedback: str = ""
    commit: str = ""
    changed: list[str] = field(default_factory=list)
    ignored: list[str] = field(default_factory=list)
    agent_seconds: float = 0.0
    judge_seconds: float = 0.0
    cost_usd: Optional[float] = None
    holdout: Optional[float] = None
    note: str = ""
    time: str = field(default_factory=now)


class RunStore:
    def __init__(self, repo: Path, run_id: str):
        self.repo = Path(repo)
        self.run_id = run_id
        self.dir = self.repo / STATE_DIR / "runs" / run_id
        self.dir.mkdir(parents=True, exist_ok=True)

    @property
    def worktree(self) -> Path:
        return self.repo / STATE_DIR / "worktrees" / self.run_id

    @property
    def ledger_path(self) -> Path:
        return self.dir / "ledger.jsonl"

    def round_dir(self, number: int) -> Path:
        path = self.dir / "rounds" / f"r{number:03d}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_meta(self, meta: dict[str, Any]):
        (self.dir / "run.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def meta(self) -> dict[str, Any]:
        path = self.dir / "run.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def append(self, row: Row):
        with self.ledger_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")

    def rows(self) -> list[dict[str, Any]]:
        if not self.ledger_path.exists():
            return []
        return [json.loads(line) for line in self.ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def lessons_path(repo: Path, contract_name: str) -> Path:
    slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in contract_name) or "default"
    return Path(repo) / STATE_DIR / "lessons" / f"{slug}.md"


def read_lessons(repo: Path, contract_name: str, limit: int = 12) -> list[str]:
    path = lessons_path(repo, contract_name)
    if not path.exists():
        return []
    lines = [line[2:] for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("- ")]
    return lines[-limit:]


def add_lesson(repo: Path, contract_name: str, text: str):
    path = lessons_path(repo, contract_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(f"# Lessons for {contract_name}\n\n", encoding="utf-8")
    clean = " ".join(text.split())
    with path.open("a", encoding="utf-8") as stream:
        stream.write(f"- {clean}\n")


def list_runs(repo: Path) -> list[str]:
    runs = Path(repo) / STATE_DIR / "runs"
    return sorted(p.name for p in runs.iterdir() if p.is_dir()) if runs.exists() else []
