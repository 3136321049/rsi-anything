"""Copy a run's evidence somewhere shareable, with local paths scrubbed.

Exported: run.json, ledger.jsonl, report.md/html, the champion's full diff, and
per round the prompt the agent saw, its diff, the judge verdict and the agent's
final message. Raw agent logs are opt-in because they can be long and noisy.
"""
from __future__ import annotations

import re
import tempfile
from pathlib import Path

from . import gitops, report
from .ledger import RunStore

ROUND_FILES = ["prompt.md", "diff.patch", "verdict.json", "agent-final.txt"]


def scrubber(repo: Path):
    replacements = [(str(Path(repo).resolve()), "<project>"), (str(Path(repo)), "<project>"),
                    (str(Path(tempfile.gettempdir()).resolve()), "<tmp>"), (str(Path.home()), "~")]
    patterns = [re.compile(r"/(?:private/)?(?:var/folders|tmp)/[^\s\"'`)]+"), re.compile(r"/(?:Users|home)/[^/\s\"'`]+")]

    def scrub(text: str) -> str:
        for old, new in replacements:
            text = text.replace(old, new)
        text = patterns[0].sub("<tmp>", text)
        return patterns[1].sub("~", text)

    return scrub


def export_run(store: RunStore, repo: Path, dest: Path, with_logs: bool = False) -> list[Path]:
    report.write(store, repo)
    scrub = scrubber(repo)
    dest.mkdir(parents=True, exist_ok=True)
    written = []

    def put(source: Path, target: Path):
        if source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(scrub(source.read_text(encoding="utf-8", errors="replace")), encoding="utf-8")
            written.append(target)

    for name in ("run.json", "ledger.jsonl", "report.md", "report.html"):
        put(store.dir / name, dest / name)
    rounds = store.dir / "rounds"
    for round_dir in sorted(rounds.iterdir()) if rounds.exists() else []:
        for name in ROUND_FILES + (["agent.log"] if with_logs else []):
            put(round_dir / name, dest / "rounds" / round_dir.name / name)
    meta = store.meta()
    if meta.get("champion") and meta.get("base") and meta["champion"] != meta["base"]:
        patch = gitops.git(repo, "diff", meta["base"], meta["champion"])
        (dest / "champion.patch").write_text(scrub(patch) + "\n", encoding="utf-8")
        written.append(dest / "champion.patch")
    return written
