#!/usr/bin/env python3
"""从已有补丁重建历史作品；保留原始账本和分数，不运行新优化。"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rsi_anything import artifacts


def restore(domain, run, filename, baseline):
    folder = ROOT / "examples" / domain / "runs" / run
    rows = [json.loads(line) for line in (folder / "ledger.jsonl").read_text().splitlines() if line.strip()]
    current = baseline.read_bytes()
    versions = []
    with tempfile.TemporaryDirectory(prefix="rsi-restore-") as tmp:
        work = Path(tmp)
        (work / filename).write_bytes(current)
        artifacts.save(work, folder / "artifacts" / "baseline", [filename])
        versions.append({"round": 0, "status": "BASELINE", "path": f"artifacts/baseline/files/{filename}"})
        for row in rows[1:]:
            (work / filename).write_bytes(current)
            patch = folder / "rounds" / f"r{row['round']:03d}" / "diff.patch"
            if not patch.exists():
                continue
            subprocess.run(["git", "apply", "--check", str(patch)], cwd=work, check=True, capture_output=True)
            subprocess.run(["git", "apply", str(patch)], cwd=work, check=True, capture_output=True)
            relative = f"rounds/r{row['round']:03d}/artifacts"
            artifacts.save(work, folder / relative, [filename])
            versions.append({"round": row["round"], "status": row["status"], "path": f"{relative}/files/{filename}"})
            if row["status"] == "KEEP":
                current = (work / filename).read_bytes()
        (work / filename).write_bytes(current)
        artifacts.save(work, folder / "artifacts" / "final", [filename])
        expected = folder / "final-post.md"
        if expected.exists():
            assert current == expected.read_bytes(), "重建稿与原始最终稿不一致"
    versions.append({"round": "final", "status": "FINAL", "path": f"artifacts/final/files/{filename}"})
    (folder / "versions.json").write_text(json.dumps({"source": "reconstructed_from_original_patches", "versions": versions},
                                                   ensure_ascii=False, indent=2) + "\n")
    print(domain, len(versions), "个版本已从原补丁重建")


if __name__ == "__main__":
    restore("code-speed", "2026-10-21-codex-3-rounds", "search.py",
            ROOT / "src/rsi_anything/templates/code-speed/search.py")
    restore("copywriting", "2026-10-21-codex-5-rounds", "post.md",
            ROOT / "examples/copywriting/runs/2026-10-21-codex-5-rounds/first-draft.md")
