"""Copy a run's evidence somewhere shareable, with local paths scrubbed.

Exported: run.json, ledger.jsonl, events.jsonl, report.md/html, the champion's full diff, and
per round the prompt the agent saw, its diff, the judge verdict and the agent's
final message. Raw agent logs are opt-in because they can be long and noisy.
"""
from __future__ import annotations

import re
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from . import gitops, report
from .ledger import RunStore

ROUND_FILES = ["prompt.md", "prompt-full.md", "diff.patch", "verdict.json", "agent-final.txt", "result.json",
               "agent-metadata.json", "agent-usage.jsonl", "judge-usage.jsonl"]


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
    if dest.resolve().is_relative_to(store.dir.resolve()):
        raise ValueError("export destination must be outside the saved run directory")
    report.write(store, repo)
    scrub = scrubber(repo)
    dest.mkdir(parents=True, exist_ok=True)
    written = []

    def put(source: Path, target: Path):
        if source.is_file() and not source.is_symlink():
            target.parent.mkdir(parents=True, exist_ok=True)
            data = source.read_bytes()
            # 视频、图片和训练产物保留原字节，文本才做本机路径替换。
            binary_suffixes = {".mp4", ".mov", ".mkv", ".webm", ".mp3", ".wav", ".png", ".jpg", ".jpeg",
                               ".gif", ".webp", ".pdf", ".zip", ".gz", ".npy", ".npz", ".pkl", ".joblib"}
            if source.suffix.lower() not in binary_suffixes and b"\0" not in data:
                try:
                    data = scrub(data.decode("utf-8")).encode("utf-8")
                except UnicodeDecodeError:
                    pass
            target.write_bytes(data)
            written.append(target)

    def tree(source: Path, target: Path):
        if not source.exists():
            return
        if target.is_symlink():
            target.unlink()
        elif target.exists():
            shutil.rmtree(target)
        for path in sorted(source.rglob("*")):
            if path.is_file():
                put(path, target / path.relative_to(source))

    for name in ("run.json", "ledger.jsonl", "events.jsonl", "report.md", "report.html"):
        put(store.dir / name, dest / name)
    tree(store.dir / "config", dest / "config")
    tree(store.dir / "artifacts", dest / "artifacts")
    rounds = store.dir / "rounds"
    for round_dir in sorted(rounds.iterdir()) if rounds.exists() else []:
        for name in ROUND_FILES + (["agent.log"] if with_logs else []):
            put(round_dir / name, dest / "rounds" / round_dir.name / name)
        tree(round_dir / "artifacts", dest / "rounds" / round_dir.name / "artifacts")
    meta = store.meta()
    if meta.get("champion") and meta.get("base") and meta["champion"] != meta["base"]:
        patch = gitops.git(repo, "diff", meta["base"], meta["champion"])
        (dest / "champion.patch").write_text(scrub(patch) + "\n", encoding="utf-8")
        written.append(dest / "champion.patch")
    # 导出文本经过路径替换后，以实际导出字节更新清单，并保留原始哈希。
    for path in dest.rglob("manifest.json"):
        if not (path.parent / "files").is_dir():
            continue
        manifest = json.loads(path.read_text(encoding="utf-8"))
        for item in manifest.get("files", []):
            file = path.parent / "files" / item["path"]
            digest = hashlib.sha256(file.read_bytes()).hexdigest()
            if item["sha256"] != digest:
                item["source_sha256"] = item["sha256"]
                item["sha256"] = digest
                item["bytes"] = file.stat().st_size
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return written
