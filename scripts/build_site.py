#!/usr/bin/env python3
"""从已保存的实验构建可独立托管的网站，不执行模型任务。"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_showcase

CASES = {
    "code-speed": ("D01", "代码优化", "code"),
    "code-repair": ("D02", "代码修复", "code"),
    "cpu-classifier": ("D04", "模型实验", "experiments"),
    "video-cut": ("D06", "视频创作", "video"),
}


def read(path, fallback=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {} if fallback is None else fallback


def cues_from_srt(text):
    cues = []
    for block in re.split(r"\n\s*\n", text.replace("\r", "").strip()):
        lines = block.splitlines()
        timing = next((i for i, line in enumerate(lines) if " --> " in line), None)
        if timing is None:
            continue
        start, end = lines[timing].split(" --> ")
        def seconds(value):
            h, m, s = value.replace(",", ".").split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
        cues.append({"start": seconds(start), "end": seconds(end),
                     "text": " ".join(lines[timing + 1:])})
    return cues


def case_data(root, case, domain):
    selected_runs = {"code-speed":"2026-10-21-codex-3-rounds", "code-repair":"20261023-234857-expense-code-repair", "cpu-classifier":"20261024-001122-cpu-digits-classifier", "video-cut":"20261024-002228-talk-highlight"}
    run = next(r for r in case["runs"] if r["id"] == selected_runs[case["template"]])
    folder = root / "examples" / case["template"] / "runs" / run["id"]
    rows = [json.loads(line) for line in (folder / "ledger.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    snapshots = []
    previous = ""
    champion = 0
    for row in rows:
        number = row["round"]
        relative = row.get("artifacts") or ("artifacts/baseline" if number == 0 else f"rounds/r{number:03d}/artifacts")
        files = folder / relative / "files"
        formal = row["status"] in {"BASELINE", "KEEP", "REVERT"}
        item = {"round": number, "status": row["status"], "score": row.get("score"),
                "best": row.get("best"), "hypothesis": row.get("hypothesis", ""),
                "note": build_showcase.human_note(row.get("note", "")),
                "feedback": row.get("feedback", ""), "gates": row.get("gates", {}),
                "previous_best": champion, "formal": formal,
                "files_base": files.relative_to(root).as_posix() + "/"}
        if case["template"] in {"code-speed", "code-repair"}:
            name = "search.py" if case["template"] == "code-speed" else "expense.py"
            item["code"] = (files / name).read_text(encoding="utf-8") if (files / name).exists() else ""
            item["filename"] = name
            item["diff"] = "\n".join(difflib.unified_diff(previous.splitlines(), item["code"].splitlines(),
                                                        fromfile="上一保留版本", tofile="本轮候选", lineterm=""))
            item["tests"] = read(files / "out/tests.json")
            if number == 0 or row["status"] == "KEEP":
                previous = item["code"]
        if case["template"] == "cpu-classifier":
            item["configuration"] = read(files / "training.json")
            if formal:
                item["metrics"] = read(files / "out/metrics.json").get("metrics", {})
                item["predictions"] = read(files / "out/predictions.json", [])
                item["mistakes"] = read(files / "out/mistakes.json", [])
        if case["template"] == "video-cut":
            item["segments"] = read(files / "edit.json").get("segments", [])
            item["media"] = read(files / "out/media.json")
            subtitle = files / "out/cut.srt"
            item["cues"] = cues_from_srt(subtitle.read_text(encoding="utf-8")) if subtitle.exists() else []
            item["duration"] = float(item["media"].get("format", {}).get("duration", 0))
        snapshots.append(item)
        if number == 0 or row["status"] == "KEEP":
            champion = number
    result = {"template": case["template"], "title": domain["title"],
              "description": domain["description"], "metric": domain["metric"], "unit": domain["unit"],
              "run_id": run["id"], "root": folder.relative_to(root).as_posix() + "/",
              "best_round": champion, "rounds": snapshots, "baseline": run["baseline"], "best": run["best"],
              "agent": run["agent"], "requested_model": run["requested_model"], "actual_model": run["actual_model"],
              "started": run["started"], "stop_reason": run["stop_reason"],
              "verified": run["eligible"], "reconstructed": run["reconstructed"],
              "source": read(root / "examples/video-cut/inputs/public-speech/source.json") if case["template"] == "video-cut" else None}
    return result


def copy_public_tree(source, destination):
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if path.is_file() and not path.is_symlink() and not any(p.startswith(".") or p == "__pycache__" for p in relative.parts):
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def build(root=ROOT, output=None):
    output = Path(output) if output else root / "build/site"
    if output.resolve() == root.resolve() or output.resolve() in (root / "src", root / "examples"):
        raise ValueError("网站输出必须使用独立目录。")
    output.mkdir(parents=True, exist_ok=True)
    data = build_showcase.collect(root)
    for name in ("examples", "docs", "release"):
        copy_public_tree(root / name, output / name)
    copy_public_tree(root / "src/rsi_anything/templates", output / "src/rsi_anything/templates")
    for name in ("README.md", "README.zh-CN.md", "LICENSE", "AGENTS.md", "CLAUDE.md"):
        shutil.copy2(root / name, output / name)
    (output / "dist").mkdir(exist_ok=True)
    for package in ("rsi_anything-0.2.0.dev0-py3-none-any.whl", "rsi_anything-0.2.0.dev0.tar.gz"):
        if (root / "dist" / package).is_file():
            shutil.copy2(root / "dist" / package, output / "dist" / package)
    copy_public_tree(root / "web/assets", output / "assets")
    (output / "web").mkdir(exist_ok=True)
    shutil.copy2(root / "web/README.md", output / "web/README.md")
    (output / "data").mkdir(exist_ok=True)
    (output / "downloads").mkdir(exist_ok=True)
    for domain in data["domains"]:
        for case in domain["cases"]:
            if case["template"] not in CASES:
                continue
            result = case_data(root, case, domain)
            (output / "data" / (case["template"] + ".json")).write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
            folder = root / result["root"]
            with zipfile.ZipFile(output / "downloads" / (case["template"] + ".zip"), "w", zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(folder.rglob("*")):
                    if path.is_file() and not path.is_symlink():
                        archive.write(path, path.relative_to(folder.parent))
            if case["template"] == "video-cut":
                for snapshot in result["rounds"]:
                    srt = root / snapshot["files_base"] / "out/cut.srt"
                    if srt.exists():
                        dest = output / snapshot["files_base"] / "out/cut.vtt"
                        dest.write_text("WEBVTT\n\n" + re.sub(r"(\d{2}:\d{2}:\d{2}),(\d{3})", r"\1.\2", srt.read_text(encoding="utf-8")), encoding="utf-8")
    home = {"domains": len(data["domains"]), "templates": sum(len(d["cases"]) for d in data["domains"]),
            "complete": sum(d["state"] == "complete" for d in data["domains"]),
            "catalog": [{"id":d["id"], "title":d["title"], "category":d["category"], "state":d["state"]} for d in data["domains"]]}
    (output / "data/home.json").write_text(json.dumps(home, ensure_ascii=False), encoding="utf-8")
    template = (root / "web/page.html").read_text(encoding="utf-8")
    pages = {"":("home","DARWIN · 用真实反馈，持续改进作品"),
             "labs/code":("code","代码优化 · DARWIN"),
             "labs/experiments":("experiments","模型实验 · DARWIN"),
             "labs/video":("video","视频创作 · DARWIN"),
             "start":("start","开始使用 · DARWIN")}
    for route,(kind,title) in pages.items():
        target = output / route
        target.mkdir(parents=True, exist_ok=True)
        prefix = "../" * len(Path(route).parts) if route else "./"
        content = (root / "web" / (kind + ".html")).read_text(encoding="utf-8")
        text = template.replace("__CONTENT__",content).replace("__BASE__",prefix).replace("__PAGE__",kind).replace("__TITLE__",title).replace("__ROUTE__",route + "/" if route else "")
        (target / "index.html").write_text(text,encoding="utf-8")
    (output / "404.html").write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>页面未找到 · DARWIN</title><body style="font:18px system-ui;background:#f5f4ed;padding:10vw"><h1>这个页面还没有留下记录。</h1><p>请检查地址，或回到首页选择一个领域。</p><a href="./">回到 DARWIN</a></body></html>',encoding="utf-8")
    (output / "build-info.json").write_text(json.dumps({"domains":home["domains"],"complete":home["complete"],"cases":list(CASES),"source":"已保存的正式运行","generated_at":data["generated_at"]},ensure_ascii=False),encoding="utf-8")
    return output


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    path=build(output=args.output)
    print(f"网站已生成：{path}")
