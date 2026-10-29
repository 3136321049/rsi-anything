"""Re-render every judged version of a saved visual run and check it against the record. No model calls.

For each judged snapshot: copy the frozen judge and the saved artifact into a fresh folder, run the
frozen `judge/render.py`, and require the same gates, the same screenshots (byte for byte) and the
same page text. Then check the ledger: kept versions really moved the best score (or won a tie
head-to-head), and the final snapshot is the last kept one. Model scores are as recorded; they are
not recomputed here.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_once(snapshot: Path, artifact: list[str]) -> tuple[dict, dict]:
    saved = snapshot / "files"
    with tempfile.TemporaryDirectory(prefix="rsi-verify-") as box:
        box = Path(box)
        shutil.copytree(ROOT / "config/frozen/judge", box / "judge")
        for name in artifact:
            shutil.copy2(saved / name, box / name)
        run = subprocess.run([sys.executable, "-B", "judge/render.py"], cwd=box, capture_output=True, text=True)
        assert run.returncode == 0, (snapshot, run.stderr[-500:])
        assert json.loads((box / "out/gates.json").read_text()) == json.loads((saved / "out/gates.json").read_text())
        produced = sorted(p.relative_to(box).as_posix() for p in (box / "out").glob("*") if p.suffix in {".png", ".txt"})
        for rel in produced:
            assert (saved / rel).is_file(), (snapshot, rel)
        return {rel: sha(box / rel) for rel in produced}, {rel: sha(saved / rel) for rel in produced}


def replay(snapshot: Path, artifact: list[str], attempts: int = 3) -> dict:
    """Re-render until the output matches the saved files byte for byte. Phone screenshots can differ
    in their last few pixel rows from one browser launch to the next, so up to three launches count."""
    for attempt in range(1, attempts + 1):
        produced, saved = render_once(snapshot, artifact)
        if produced == saved:
            return {"files": produced, "render_attempts": attempt,
                    "artifact_sha256": {name: sha(snapshot / "files" / name) for name in artifact}}
    raise AssertionError((snapshot, "re-render differs", {k for k in produced if produced[k] != saved[k]}))


def main():
    meta = json.loads((ROOT / "run.json").read_text())
    execution = json.loads((ROOT / "config/execution.json").read_text())
    artifact = execution["artifact"]
    rows = [json.loads(line) for line in (ROOT / "ledger.jsonl").read_text().splitlines() if line.strip()]
    checks, best, champion = [], None, None
    for row in rows:
        snapshot = ROOT / row["artifacts"]
        manifest = json.loads((snapshot / "manifest.json").read_text())
        judged = manifest.get("evaluation_status") == "evaluated"
        check = {"round": row["round"], "status": row["status"], "score": row["score"], "snapshot": row["artifacts"],
                 "judged": judged}
        if judged:
            check.update(replay(snapshot, artifact), rerender_matches=True)
        if row["status"] in ("BASELINE", "KEEP"):
            assert judged and all(row["gates"].values()), row["round"]
            if row["status"] == "KEEP":
                assert row["score"] > best or (row["score"] == best and "won head-to-head" in row["note"]), row
            best, champion = row["score"], row["artifacts"]
        elif row["status"] == "REVERT" and best is not None and row["score"] is not None:
            assert row["score"] <= best or not all(row["gates"].values()) or "head-to-head" in row["note"], row
        checks.append(check)
    final = json.loads((ROOT / "artifacts/final/manifest.json").read_text())
    kept = json.loads((ROOT / champion / "manifest.json").read_text())
    assert final["files"] == kept["files"] and final.get("source_snapshot") == champion
    receipt = {"run_id": ROOT.name, "status": "verified", "model_calls_during_validation": 0,
               "command": "python verify_saved_results.py", "formal_scores_unchanged": True,
               "base_commit": meta["base"], "champion_commit": meta["champion"],
               "contract_digest": meta["contract_digest"], "final_source_snapshot": champion,
               "renderer": "headless Chrome via rsi_anything.sdk.screenshot, network blocked",
               "scores": "recorded jury scores; not recomputed", "checks": checks,
               "content_review_document": "../../README.md",
               "frozen_files": [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                                for path in sorted((ROOT / "config").rglob("*"))
                                if path.is_file() and "__pycache__" not in path.parts],
               "all_replay_checks_passed": True}
    (ROOT / "verification.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"versions_rerendered": sum(c["judged"] for c in checks), "scores": [c["score"] for c in checks],
                      "final": champion, "model_calls": 0}))


if __name__ == "__main__":
    main()
