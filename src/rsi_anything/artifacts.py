"""保存评审后的作品和生成文件，临时评审目录清理后仍能查看。"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from .domain import Verdict
from .paths import matches, normalize


def write_json(path: Path, data):
    """先写同目录临时文件，避免中断时留下半份状态。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False, default=str)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def save(source: Path, dest: Path, patterns: list[str], verdict: Optional[Verdict] = None) -> dict:
    """保存相对项目目录的普通文件；外部素材链接不会被意外打包。"""
    source = source.resolve()
    target_root = dest / "files"
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)
    files, skipped = [], []
    for directory, directories, names in os.walk(source):
        directories[:] = [name for name in directories if name not in {".git", ".rsi", "__pycache__"}]
        for name in sorted(names):
            path = Path(directory) / name
            rel = path.relative_to(source).as_posix()
            if not matches(rel, patterns):
                continue
            if not path.is_file() or not path.resolve().is_relative_to(source):
                skipped.append(rel)
                continue
            data = path.read_bytes()
            target = target_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            shutil.copymode(path, target)
            files.append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    files.sort(key=lambda item: item["path"])
    manifest = {"files": files, "missing_patterns": [p for p in patterns if not any(matches(f["path"], [p]) for f in files)],
                "skipped": sorted(skipped),
                "source": "judge_workspace" if verdict is not None else "agent_workspace",
                "evaluation_status": ("evaluated" if verdict.ok else "judge_failed") if verdict is not None else "unreviewed"}
    write_json(dest / "manifest.json", manifest)
    if verdict is not None:
        write_json(dest / "verdict.json", asdict(verdict))
    return manifest


def mark_incomplete(snapshot: Path):
    """保留真实目录来源，标记这一轮尚无完整正式结论。"""
    path = snapshot / "manifest.json"
    if path.exists():
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["evaluation_status"] = "round_incomplete"
        write_json(path, manifest)


def restore(snapshot: Path, dest: Path):
    """恢复已保存的生成文件，续跑时无需再次渲染当前最好版本。"""
    manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        rel = normalize(item["path"])
        data = (snapshot / "files" / rel).read_bytes()
        if hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError(f"saved artifact checksum mismatch: {rel}")
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def verdict(snapshot: Path) -> Optional[Verdict]:
    path = snapshot / "verdict.json"
    return Verdict(**json.loads(path.read_text(encoding="utf-8"))) if path.exists() else None


def copy_snapshot(source: Path, dest: Path, *, source_snapshot: str = ""):
    """复用作品和评分结论，调用记录留在真正执行它们的阶段。"""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    shutil.copytree(source / "files", dest / "files")
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if source_snapshot:
        manifest["source_snapshot"] = source_snapshot
    write_json(dest / "manifest.json", manifest)
    if (source / "verdict.json").exists():
        shutil.copy2(source / "verdict.json", dest / "verdict.json")
