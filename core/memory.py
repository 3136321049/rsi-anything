from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path

HEADER = "round\ttimestamp\thypothesis\tscore\tbest_score\tstatus\tcommit_sha\tduration_ms\tnotes\n"

def init_ledger(track_dir: Path):
    track_dir = Path(track_dir)
    track_dir.mkdir(parents=True, exist_ok=True)
    if not (ledger := track_dir / "results.tsv").exists():
        ledger.write_text(HEADER, encoding="utf-8")
    (state := track_dir / ".rsi").mkdir(exist_ok=True)
    if not (lessons := state / "lessons.md").exists():
        lessons.write_text("# Ratchet lessons\n\n", encoding="utf-8")

def _clean(value) -> str:
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ")

def append_result(track_dir: Path, round_no: int, hypothesis: str, score: float,
                  best_score: float, status: str, commit_sha: str = "",
                  duration_ms: int = 0, notes: str = ""):
    init_ledger(track_dir)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    row = [round_no, stamp, hypothesis, f"{float(score):.2f}", f"{float(best_score):.2f}",
           status, commit_sha, int(duration_ms), notes]
    with (Path(track_dir) / "results.tsv").open("a", encoding="utf-8") as stream:
        stream.write("\t".join(_clean(item) for item in row) + "\n")

def append_lesson(track_dir: Path, lesson: str):
    init_ledger(track_dir)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with (Path(track_dir) / ".rsi" / "lessons.md").open("a", encoding="utf-8") as stream:
        stream.write(f"- {stamp} — {_clean(lesson)}\n")

def read_lessons(track_dir: Path, limit: int = 10) -> str:
    path = Path(track_dir) / ".rsi" / "lessons.md"
    if not path.exists() or limit <= 0:
        return ""
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("- ")]
    return "\n".join(lines[-limit:])
