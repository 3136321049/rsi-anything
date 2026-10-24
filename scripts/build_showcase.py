#!/usr/bin/env python3
"""读取领域目录和原始实验，生成本地展示页；不改实验记录，不联网。"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shlex
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"BASELINE": "初始", "KEEP": "保留", "REVERT": "拒绝", "NO_CHANGE": "无修改",
            "AGENT_FAIL": "执行失败", "JUDGE_FAIL": "评审失败", "INTERRUPTED": "中断", "FINAL": "最终"}
TEXT_EXTENSIONS = {".md", ".txt", ".py", ".json", ".yaml", ".yml", ".csv", ".mmd"}


def human_note(text):
    """界面显示中文说明；精确英文记录仍在原账本。"""
    if text.startswith("no edits inside the artifact paths"):
        return "允许修改的作品文件没有变化，未进入正式评审。"
    if text.startswith("score ") and " -> " in text:
        match = re.search(r"score ([\d.\-]+) -> ([\d.\-]+)", text)
        if match:
            suffix = re.search(r"head-to-head (\d+/\d+)", text)
            return f"分数从 {match[1]} 提高到 {match[2]}。" + (f"两两比较获胜 {suffix[1]}。" if suffix else "")
    if text.startswith("score ") and "not better" in text:
        return "正式分数未超过当前最好版本所需的进步幅度。"
    if "lost head-to-head" in text:
        return "分数更高，但新旧作品正反顺序比较没有获胜。"
    if text.startswith("passes gates"):
        return "修复了当前最好版本尚未满足的硬条件。"
    if text.startswith("failed gates:"):
        return "未通过必需检查：" + text.partition(":")[2].strip()
    return text


def read_json(path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {} if default is None else default


def independently_verified(run):
    verification = read_json(run / "verification.json")
    if "final_verified" in verification:
        return verification["final_verified"] is True and verification.get("all_formally_judged_snapshots_passed", True) is True
    if any(verification.get(key) is True for key in ("all_passed", "all_file_checks_passed")):
        return True
    if verification.get("status") == "verified":
        return True
    history = read_json(run / "artifact-verification.json")
    versions = history.get("versions") or []
    return bool(versions) and any(item.get("version") == "final" for item in versions) and all(
        bool(item.get("verification", {}).get("gates")) and all(item["verification"]["gates"].values()) for item in versions)


def safe_file(root, path):
    path = path.resolve()
    return path if path.is_file() and path.is_relative_to(root.resolve()) else None


def file_item(root, path, primary=()):
    path = safe_file(root, path)
    if path is None:
        return None
    examples = root / "examples"
    import os
    url = quote(os.path.relpath(path, examples).replace(os.sep, "/"), safe="/")
    suffix = path.suffix.lower()
    kind = "video" if suffix in {".mp4", ".webm", ".mov"} else "image" if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"} else "html" if suffix == ".html" else "text" if suffix in TEXT_EXTENSIONS else "file"
    name = path.name
    item = {"name": name, "url": url, "kind": kind, "bytes": path.stat().st_size}
    if kind == "html":
        content = path.read_text(encoding="utf-8", errors="replace")[:150000]
        content = re.sub(r"<script\b[^>]*>.*?</script\s*>", "", content, flags=re.I | re.S)
        content = re.sub(r"<base\b[^>]*>", "", content, flags=re.I)
        content = re.sub(r'<pre class="mermaid">(.*?)</pre>',
                         r'<details><summary>图表定义（Mermaid）</summary><pre>\1</pre></details>', content, flags=re.S)
        item["html"] = content
    elif kind == "text" and (suffix in {".md", ".txt", ".py"} or path.name in {Path(p).name for p in primary}):
        content = path.read_text(encoding="utf-8", errors="replace")
        item["text"] = content[:50000]
        item["truncated"] = len(content) > 50000
    return item


def snapshot(root, run, relative, label, status, primary):
    directory = run / relative
    files_root = directory / "files"
    if not files_root.is_dir() or not directory.resolve().is_relative_to(run.resolve()):
        return None
    manifest = read_json(directory / "manifest.json")
    names = [item["path"] for item in manifest.get("files", []) if isinstance(item, dict) and isinstance(item.get("path"), str)]
    if not names:
        names = [path.relative_to(files_root).as_posix() for path in files_root.rglob("*") if path.is_file()]
    order = {name: index for index, name in enumerate(primary)}
    names.sort(key=lambda name: (order.get(name, 999), name))
    files = []
    hidden_internal_outputs = False
    for name in names:
        if name.startswith("out/") and status in {"NO_CHANGE", "AGENT_FAIL", "INTERRUPTED"}:
            hidden_internal_outputs = True
            continue
        path = files_root / name
        if not path.resolve().is_relative_to(files_root.resolve()):
            continue
        item = file_item(root, path, primary)
        if item:
            item["name"] = name
            files.append(item)
    return {"label": label, "status": status, "files": files, "snapshot": relative,
            "note": "此轮没有正式评审；助手内部生成的 out 未用于作品比较，原记录仍保留。" if hidden_internal_outputs else ""}


def run_data(root, domain, case, run):
    meta = read_json(run / "run.json")
    if not meta:
        return None
    rows = []
    raw_ledger = b""
    if (run / "ledger.jsonl").is_file():
        raw_ledger = (run / "ledger.jsonl").read_bytes()
        for line in raw_ledger.decode("utf-8").splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    outcome_audit = read_json(run / "outcome-audit.json")
    audit_valid = bool(outcome_audit) and outcome_audit.get("raw_ledger_sha256") == hashlib.sha256(raw_ledger).hexdigest()
    audited = {item.get("round"): item for item in outcome_audit.get("rounds", [])} if audit_valid else {}
    unknown_rounds = []
    for row in rows:
        number = row.get("round", 0)
        relative = row.get("artifacts") or ("artifacts/baseline" if number == 0 else f"rounds/r{number:03d}/artifacts")
        error = read_json(run / relative / "files/out/error.json")
        derived = audited.get(number, {})
        if error.get("quality_result") == "unknown" or derived.get("quality_result") == "unknown":
            row["raw_status"], row["raw_score"] = row.get("status"), row.get("score")
            row.update(status="JUDGE_FAIL", score=None, quality_result="unknown",
                       note=derived.get("reason") or "服务或环境未完成，未获得可评价的作品，质量未知。原始记录保持不变。")
            unknown_rounds.append(number)
    invalid = case.get("invalid_runs", {}).get(run.name, "")
    versions = []
    for row in rows:
        number = row.get("round", 0)
        rel = row.get("artifacts") or ("artifacts/baseline" if number == 0 else f"rounds/r{number:03d}/artifacts")
        label = "初始作品" if number == 0 else f"第 {number} 轮 · {STATUSES.get(row.get('status'), row.get('status', '未知'))}"
        version = snapshot(root, run, rel, label, row.get("status"), case["primary"])
        if version:
            if row.get("quality_result") == "unknown":
                version["label"] = f"第 {number} 轮 · 质量未知"
                version["note"] = "生成或执行未完成，这里只保留输入与错误凭证，没有可评价的新作品。"
            versions.append(version)
    final = snapshot(root, run, meta.get("final_artifacts") or "artifacts/final", "最终保留作品", "FINAL", case["primary"])
    if final:
        versions.append(final)
    attempts = [row for row in rows if row.get("round", 0) > 0]
    actual_attempts = [row for row in attempts if row.get("status") in {"KEEP", "REVERT", "NO_CHANGE"}]
    reasons = []
    if invalid:
        reasons.append(invalid)
    if not meta.get("finished") or meta.get("status") in {"failed", "interrupted", "running"}:
        reasons.append("运行尚无正常结束记录。")
    if len(actual_attempts) < 2:
        reasons.append("尚无至少两轮已完成的真实尝试。")
    if audit_valid and outcome_audit.get("complete_multiround") is False:
        reasons.append("派生核验确认只有部分实测，服务失败轮次不能作为作品质量结果。")
    if not final or not final["files"]:
        reasons.append("最终作品未保存。")
    if not independently_verified(run):
        reasons.append("独立验证记录尚未完成或未通过。")
    if domain.get("require_holdout") and meta.get("holdout", {}).get("final") is None:
        reasons.append("最终留出集结果缺失。")
    if domain.get("require_video") and not any(item["kind"] == "video" for item in (final or {}).get("files", [])):
        reasons.append("最终可播放视频缺失。")
    if domain.get("require_gpu"):
        measurements = read_json(run / (meta.get("final_artifacts") or "artifacts/final") / "files/out/metrics.json")
        if measurements.get("status") != "measured" or not measurements.get("metrics", {}).get("module"):
            reasons.append("尚无真实 GPU 与模块对照结果。")
    execution = read_json(run / "config/execution.json")
    model = execution.get("agent", {})
    baseline = rows[0].get("score") if rows else None
    best = rows[-1].get("best") if rows else None
    if best is None and final:
        best = read_json(run / final["snapshot"] / "verdict.json").get("score")
    def finite(value):
        return value if isinstance(value, (int, float)) and math.isfinite(value) else None
    mapped_rows = [{"round": row.get("round"), "status": row.get("status"),
                    "label": "生成未完成 · 质量未知" if row.get("quality_result") == "unknown" else STATUSES.get(row.get("status"), "未知"),
                    "score": None if invalid else finite(row.get("score")), "hypothesis": row.get("hypothesis", ""),
                    "note": human_note(row.get("note", "")), "feedback": row.get("feedback", "")} for row in rows]
    inputs = []
    for pattern in case.get("inputs", []):
        files = sorted((run / "config/frozen").glob(pattern))
        for file in files:
            candidates = sorted(file.rglob("*")) if file.is_dir() else [file]
            for candidate in candidates:
                item = file_item(root, candidate, case["inputs"])
                if item:
                    item["name"] = candidate.relative_to(run / "config/frozen").as_posix()
                    inputs.append(item)
    extras = []
    for path in domain.get("extra_inputs", []):
        item = file_item(root, root / "examples" / path)
        if item:
            item["name"] = "原始输入 · " + item["name"]
            inputs.insert(0, item)
    for name in ("report.html", "ledger.jsonl", "verification.json", "artifact-verification.json", "outcome-audit.json", "source-receipts.json", "config/rsi.yaml",
                 "config/execution.json", "versions.json", "NOTES.md", "README.md"):
        item = file_item(root, run / name)
        if item:
            item["name"] = {"report.html": "原始实验报告", "ledger.jsonl": "完整轮次账本", "verification.json": "独立验证",
                            "artifact-verification.json": "历史产物独立验证", "config/rsi.yaml": "冻结任务配置",
                            "outcome-audit.json": "派生结果核验（原账本不改）", "source-receipts.json": "服务原始来源凭证",
                            "config/execution.json": "模型与运行参数", "versions.json": "版本重建来源",
                            "NOTES.md": "历史实验说明", "README.md": "运行说明"}[name]
            extras.append(item)
    reconstructed = read_json(run / "versions.json").get("source") == "reconstructed_from_original_patches"
    holdout_files = []
    for path in sorted((run / "artifacts/final").glob("holdout*")):
        if path.is_file():
            item = file_item(root, path)
            if item:
                holdout_files.append(item)
    budget = execution.get("budget", {})
    command = ["python", "scripts/run_demo.py", case["template"], "--model", model.get("requested_model") or model.get("model") or "<你的模型型号>",
               "--rounds", str(budget.get("rounds") or len(attempts) or 3), "--minutes", str(budget.get("minutes") or 25),
               "--codex-isolated", "--continue-after-target"]
    if meta.get("jury"):
        command += ["--jury", *meta["jury"]]
    if execution.get("task_model"):
        command += ["--task-model", execution["task_model"]]
    return {"id": run.name, "finished": bool(meta.get("finished")), "eligible": not reasons, "reasons": reasons,
            "started": meta.get("started", ""), "baseline": None if invalid else finite(baseline),
            "best": None if invalid else finite(best), "rounds": len(attempts), "kept": sum(row.get("status") == "KEEP" for row in attempts),
            "goal": meta.get("goal", ""), "rows": mapped_rows, "versions": versions, "inputs": inputs,
            "evidence": extras + holdout_files, "holdout": meta.get("holdout") or {}, "invalid_reason": invalid,
            "reconstructed": reconstructed, "quality_unknown_rounds": unknown_rounds,
            "requested_model": model.get("requested_model") or model.get("model"),
            "actual_model": model.get("actual_model"), "reasoning_effort": model.get("reasoning_effort"),
            "agent": meta.get("agent", "未知"), "jury": meta.get("jury", []), "task_model": execution.get("task_model"),
            "stop_reason": meta.get("stop_reason", "未提供"), "elapsed_seconds": meta.get("elapsed_seconds"),
            "command": shlex.join(command)}


def collect(root=ROOT, catalog=None):
    catalog = catalog or read_json(root / "examples/catalog.json")
    domains = []
    for specification in catalog["domains"]:
        domain = dict(specification)
        cases = []
        for case in specification["cases"]:
            item = dict(case)
            item["runs"] = []
            for path in sorted((root / "examples" / case["template"] / "runs").glob("*"), reverse=True):
                result = run_data(root, specification, case, path)
                if result:
                    item["runs"].append(result)
            item["preferred_run"] = next((index for index, run in enumerate(item["runs"]) if run["eligible"]), 0)
            item["complete"] = any(run["eligible"] for run in item["runs"])
            item["readme"] = file_item(root, root / "examples" / case["template"] / "README.md")
            item["template_readme"] = file_item(root, root / "src/rsi_anything/templates" / case["template"] / "README.md")
            if item["readme"]:
                item["readme"]["name"] = "领域结果说明"
            if item["template_readme"]:
                item["template_readme"]["name"] = "模板用法与来源"
            cases.append(item)
        domain["cases"] = cases
        domain["state"] = ("complete" if all(case["complete"] for case in cases)
                           else "resource_exception" if specification.get("resource_exception")
                           else "partial" if any(case["runs"] for case in cases) else specification["pending"])
        domain["probe"] = file_item(root, root / "examples" / specification["probe"] / "README.md") if specification.get("probe") else None
        if domain["probe"]:
            domain["probe"]["name"] = "本机环境探测记录"
        domains.append(domain)
    return {"title": catalog["title"], "description": catalog["description"], "domains": domains,
            "generated_at": datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M（北京时间）")}


def build(root=ROOT, output=None):
    data = collect(root)
    encoded = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    output = output or root / "examples/index.html"
    if output.resolve().parent != (root / "examples").resolve():
        raise ValueError("展示页需放在 examples 目录，才能保留原始产物的相对链接。")
    output.write_text(PAGE.replace("__CATALOG_DATA__", encoded), encoding="utf-8")
    return data


PAGE = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Open RSI · 实验与作品</title>
<style>
:root{--ink:#203038;--muted:#64737b;--line:#dce4e3;--paper:#f3f5f2;--card:#fff;--green:#176d54;--pale:#e7f2eb;--amber:#92630c;--soft:#f7ecd6;--red:#9a4c40}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif}button,select{font:inherit}button{cursor:pointer}a{color:var(--green);text-underline-offset:3px}header{background:#142b26;color:#fff;padding:34px max(24px,calc((100vw - 1420px)/2)) 38px}header .brand{letter-spacing:.2em;font-size:12px;color:#9dc8b5}h1{font-size:clamp(30px,4vw,48px);letter-spacing:-.04em;line-height:1.2;margin:16px 0}header p{color:#c3d6ce;max-width:740px;margin:0}.headline{display:flex;justify-content:space-between;align-items:end;gap:32px}.totals{display:flex;gap:28px;white-space:nowrap}.totals b{font-size:32px;display:block;line-height:1.1}.totals span{font-size:12px;color:#bed1c8}.shell{max-width:1468px;margin:auto;padding:24px}.toolbar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}.filter,.case-tab{border:1px solid var(--line);background:white;color:var(--ink);border-radius:22px;padding:7px 15px}.filter.active,.case-tab.active{color:#fff;background:var(--green);border-color:var(--green)}.workspace{display:grid;grid-template-columns:300px minmax(0,1fr);gap:24px;align-items:start}.catalog{display:grid;gap:10px;max-height:calc(100vh - 35px);overflow:auto;position:sticky;top:16px;padding-right:4px}.domain-card{display:block;width:100%;text-align:left;border:1px solid var(--line);background:var(--card);padding:15px 17px;border-radius:12px;color:var(--ink);transition:.15s}.domain-card:hover{border-color:#75a18f;transform:translateY(-1px)}.domain-card.active{border-color:var(--green);box-shadow:inset 4px 0 var(--green);background:#f9fdf9}.card-top{display:flex;justify-content:space-between;gap:8px;font-size:11px;color:var(--muted)}.domain-card h3{font-size:16px;margin:8px 0 4px}.domain-card p{margin:0;color:var(--muted);font-size:12px;line-height:1.5}.badge{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:650;background:#e9edee;color:#66747c}.badge.complete,.badge.keep{background:var(--pale);color:var(--green)}.badge.partial,.badge.waiting,.badge.revert{background:var(--soft);color:var(--amber)}.badge.fail{background:#f9e9e3;color:var(--red)}.panel{background:white;border:1px solid var(--line);border-radius:16px;overflow:hidden;min-width:0}.panel-head{padding:28px 30px 24px;border-bottom:1px solid var(--line)}.eyebrow{font-size:12px;color:var(--muted)}h2{font-size:28px;margin:8px 0 10px;line-height:1.3}.description{color:var(--muted);margin:0}.note{font-size:13px;background:#f6f7f2;border-left:3px solid #b1bfae;padding:10px 14px;margin-top:16px;white-space:pre-wrap}.note.warning{border-color:#c89942;background:#fbf4e8}.case-tabs{display:flex;gap:8px;margin-top:20px}.panel-body{padding:24px 30px 32px}.run-picker{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.run-picker label{font-size:12px;color:var(--muted)}select{max-width:100%;border:1px solid var(--line);padding:8px 11px;border-radius:7px;background:#fff;color:var(--ink);min-width:0}.run-picker select{flex:1;font-size:12px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}.stat{padding:16px;background:#f4f7f4;border-radius:10px}.stat .label{font-size:11px;color:var(--muted)}.stat b{display:block;font-size:26px;font-weight:650;margin-top:5px;line-height:1.2}.stat small{color:var(--muted);font-size:11px}.section-label{font-size:16px;font-weight:650;margin:26px 0 12px}.compare-toolbar{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}.compare-toolbar .section-label{margin:12px 0}.mode{display:flex;gap:6px}.mode button{font-size:12px;background:white;border:1px solid var(--line);padding:5px 10px;border-radius:6px}.mode button.active{background:#edf5f0;border-color:var(--green);color:var(--green)}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:14px}.version{border:1px solid var(--line);border-radius:10px;min-width:0;overflow:hidden;background:#fff}.version-controls{padding:12px;background:#f7f9f7;display:grid;gap:8px;border-bottom:1px solid var(--line)}.version-controls select{width:100%;font-size:12px}.version-body{height:520px;overflow:auto;position:relative}.version-body.image{height:auto;min-height:250px}.version-body img{width:100%;height:auto;display:block;max-height:600px;object-fit:contain}.version-body video{width:100%;height:auto;max-height:560px;background:#101e1b;display:block}.version-body iframe{width:100%;height:520px;border:0;background:white}.version-body pre{margin:0;padding:18px;font:12px/1.8 ui-monospace,SFMono-Regular,Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere}.version-body .prose{font:14px/1.9 system-ui}.file-foot{padding:8px 12px;font-size:11px;border-top:1px solid var(--line);display:flex;justify-content:space-between;gap:8px}.empty{padding:50px 24px;text-align:center;color:var(--muted);background:#f8faf7;border-radius:10px}.empty b{display:block;color:var(--ink);font-size:20px;margin-bottom:8px}.diff-added{background:#e9f6e9;color:#1c6637}.diff-removed{background:#fbe9e4;color:#9a4c40}.diff-line{display:block;white-space:pre-wrap;padding:0 10px;border-bottom:1px solid #f1f3f1}.diff{max-height:520px;overflow:auto;font:12px/1.8 ui-monospace,monospace;border:1px solid var(--line);border-radius:9px;padding:12px 0}.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:9px}table{width:100%;border-collapse:collapse;font-size:12px}th,td{text-align:left;padding:12px;border-bottom:1px solid var(--line);vertical-align:top}th{background:#f7f9f7;color:var(--muted);font-weight:500}tr:last-child td{border-bottom:0}.score{white-space:nowrap;font-weight:650}.row-note{display:block;color:var(--muted);margin-top:4px;max-width:550px}.details{border-top:1px solid var(--line);margin-top:22px;padding-top:12px}.details summary{cursor:pointer;font-weight:650;padding:6px 0}.detail-content{padding:10px 0;color:var(--muted);font-size:13px}.links{display:flex;gap:8px;flex-wrap:wrap}.links a{background:#f1f5f1;padding:5px 9px;border-radius:5px;font-size:12px;overflow-wrap:anywhere}.input-preview{max-height:280px;overflow:auto;margin-top:12px}.input-preview video{width:100%;max-height:300px;background:#15221d}.command{padding:14px;background:#172d27;color:#e1f1e6;border-radius:8px;white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.7 ui-monospace,monospace}.footer{color:var(--muted);font-size:12px;padding:28px 0 10px}.status-message{font-size:13px;color:var(--muted);margin:12px 0}.hidden{display:none!important}@media(max-width:1100px){.workspace{grid-template-columns:250px minmax(0,1fr);gap:16px}.shell{padding:16px}.panel-head,.panel-body{padding:20px}.stats{gap:8px}.stat{padding:12px}.stat b{font-size:22px}.headline{align-items:start}.totals{gap:15px}}@media(max-width:760px){header{padding:24px 20px}.headline{display:block}.totals{margin-top:24px}.workspace{display:block}.catalog{display:flex;position:static;max-height:none;overflow-x:auto;gap:8px;margin-bottom:16px;padding-bottom:10px}.domain-card{min-width:220px;width:220px}.comparison{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.version-body{height:400px}.version-body iframe{height:400px}.panel-head,.panel-body{padding:18px}.run-picker{display:block}.run-picker select{width:100%}.toolbar{gap:5px}.filter{padding:6px 11px;font-size:12px}h2{font-size:24px}.version-body.image{min-height:160px}}
</style></head><body>
<header><div class="brand">OPEN RSI / 实验与作品</div><div class="headline"><div><h1>看看 AI 实际改了什么</h1><p>从初稿到最后保留的作品。每一次尝试、接受、拒绝和停滞，都有原始记录可查。</p></div><div class="totals" id="totals"></div></div></header>
<main class="shell"><nav class="toolbar" aria-label="领域过滤" id="filters"></nav><div class="workspace"><aside class="catalog" id="catalog" aria-label="15 个领域"></aside><article class="panel" id="detail" aria-live="polite"></article></div><footer class="footer" id="footer"></footer></main>
<script id="catalog-data" type="application/json">__CATALOG_DATA__</script>
<script>
'use strict';
const DATA=JSON.parse(document.getElementById('catalog-data').textContent);
const stateLabels={complete:'已验收',partial:'部分完成',developing:'开发中',waiting:'等待外部条件',resource_exception:'资源例外'};
const statusLabels={BASELINE:'初始',KEEP:'保留',REVERT:'拒绝',NO_CHANGE:'无修改',AGENT_FAIL:'执行失败',JUDGE_FAIL:'评审失败',INTERRUPTED:'中断',FINAL:'最终'};
let selected='D04',caseIndex=0,runIndex=0,filter='全部',mode='compare';
const esc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const number=value=>value===null||value===undefined?'—':Number(value).toLocaleString('zh-CN',{maximumFractionDigits:3});
const badge=(label,state)=>`<span class="badge ${esc(state)}">${esc(label)}</span>`;
const link=item=>`<a href="${esc(item.url)}" target="_blank" rel="noopener">${esc(item.name)}</a>`;
function chosen(){const domain=DATA.domains.find(d=>d.id===selected);const example=domain.cases[caseIndex]||domain.cases[0];return {domain,example,run:example.runs[runIndex]};}
function renderNavigation(){const counts={};for(const d of DATA.domains)counts[d.state]=(counts[d.state]||0)+1;
 document.getElementById('totals').innerHTML=`<div><b>${DATA.domains.length}</b><span>领域案例</span></div><div><b>${counts.complete||0}</b><span>有完整多轮与作品</span></div><div><b>${DATA.domains.length-(counts.complete||0)-(counts.resource_exception||0)} / ${counts.resource_exception||0}</b><span>待完成 / 资源例外</span></div>`;
 document.getElementById('filters').innerHTML=['全部','已验收','仍在推进','资源例外','工程','模型','创作','研究','生活'].map(x=>`<button class="filter ${filter===x?'active':''}" data-filter="${x}">${x}</button>`).join('');
 document.getElementById('catalog').innerHTML=DATA.domains.filter(d=>filter==='全部'||filter==='已验收'&&d.state==='complete'||filter==='仍在推进'&&!['complete','resource_exception'].includes(d.state)||filter==='资源例外'&&d.state==='resource_exception'||d.category===filter).map(d=>`<button class="domain-card ${d.id===selected?'active':''}" data-domain="${d.id}"><div class="card-top"><span>${d.id} · ${d.category}</span>${badge((d.resource_exception_label&&d.state==='resource_exception'?d.resource_exception_label:stateLabels[d.state]),d.state)}</div><h3>${esc(d.title)}</h3><p>${esc(d.description)}</p></button>`).join('');
 document.querySelectorAll('[data-filter]').forEach(b=>b.onclick=()=>{filter=b.dataset.filter;renderNavigation();});
 document.querySelectorAll('[data-domain]').forEach(b=>b.onclick=()=>selectDomain(b.dataset.domain));}
function selectDomain(id){selected=id;caseIndex=0;runIndex=DATA.domains.find(d=>d.id===id).cases[0].preferred_run;mode='compare';history.replaceState(null,'','#'+id);renderNavigation();renderDetail();}
function modelText(run){return `执行助手：${run.agent}；请求型号：${run.requested_model||'历史记录未固定'}；服务端确认型号：${run.actual_model||'未返回'}；思考强度：${run.reasoning_effort||'未记录'}。${run.jury.length?'评委：'+run.jury.join('、')+'。':'采用程序评价，无模型评委。'}${run.task_model?'任务模型：'+run.task_model+'。':''}`;}
function renderDetail(){const {domain,example,run}=chosen();const container=document.getElementById('detail');
 let body=`<div class="panel-head"><div class="eyebrow">${domain.id} / ${domain.category} ${badge((domain.resource_exception_label&&domain.state==='resource_exception'?domain.resource_exception_label:stateLabels[domain.state]),domain.state)}</div><h2>${esc(domain.title)}</h2><p class="description">${esc(domain.description)}</p>${domain.note?`<div class="note">${esc(domain.note)}</div>`:''}<div class="case-tabs">${domain.cases.map((c,i)=>`<button class="case-tab ${i===caseIndex?'active':''}" data-case="${i}">${esc(c.title)} ${c.complete?'✓':''}</button>`).join('')}</div></div><div class="panel-body">`;
 if(!run){body+=`<div class="empty"><b>${(domain.resource_exception_label&&domain.state==='resource_exception'?domain.resource_exception_label:stateLabels[domain.state])}</b>当前没有可展示的完整多轮记录。<br>分数与加速倍数留空，模板和探测结果不计作实验完成。</div><div class="links" style="margin-top:20px">${[example.template_readme,example.readme,domain.probe].filter(Boolean).map(link).join('')}</div></div>`;container.innerHTML=body;bindCases();return;}
 body+=`<div class="run-picker"><label for="run-select">原始运行</label><select id="run-select">${example.runs.map((r,i)=>`<option value="${i}" ${i===runIndex?'selected':''}>${esc(r.id)} · ${r.eligible?'完整多轮':r.invalid_reason?'评分异常':r.finished?'部分完成':'尚未结束'}</option>`).join('')}</select></div>`;
 if(run.reasons.length)body+=`<div class="note warning">${run.reasons.map(esc).join('\n')}</div>`;
 body+=`<div class="stats"><div class="stat"><span class="label">初始 · ${esc(domain.metric)}</span><b>${number(run.baseline)}<small> ${run.baseline!==null?esc(domain.unit):''}</small></b></div><div class="stat"><span class="label">最终保留</span><b>${number(run.best)}<small> ${run.best!==null?esc(domain.unit):''}</small></b></div><div class="stat"><span class="label">真实尝试</span><b>${run.rounds}<small> 轮</small></b></div><div class="stat"><span class="label">保留 / 尝试</span><b>${run.kept}<small> / ${run.rounds}</small></b></div></div>`;
 if(run.quality_unknown_rounds.length)body+=`<div class="note warning">第 ${run.quality_unknown_rounds.join('、')} 轮没有获得作品，正式质量分留空；原始失败和派生核验都可在下方打开。</div>`;
 if(Object.keys(run.holdout).length)body+=`<div class="status-message">留出集：${number(run.holdout.baseline)} → ${number(run.holdout.final)}。留出结果单列，不与开发分混算。</div>`;
 body+=`<div class="compare-toolbar"><div class="section-label">作品版本</div><div class="mode"><button id="compare-mode" class="active">并排查看</button><button id="diff-mode">文字差异</button></div></div><div id="version-area"></div><div class="section-label">完整轮次</div><div class="table-wrap"><table><thead><tr><th>轮次</th><th>决定</th><th>正式分数</th><th>改了什么 / 为什么保留或拒绝</th></tr></thead><tbody>${run.rows.map(r=>`<tr><td>${r.round===0?'初始':r.round}</td><td>${badge(r.label,r.status==='KEEP'?'keep':r.status==='REVERT'?'revert':r.status.endsWith('FAIL')?'fail':'')}</td><td class="score">${number(r.score)}</td><td>${esc(r.hypothesis||(r.round===0?'冻结输入与评价，建立初始结果。':'没有留下新的正式候选。'))}<span class="row-note">${esc(r.note)}</span></td></tr>`).join('')}</tbody></table></div>`;
 body+=`<details class="details"><summary>任务与原始输入</summary><div class="detail-content"><p style="white-space:pre-wrap">${esc(run.goal)}</p><div class="links">${run.inputs.map(link).join('')||'这次运行未保存输入入口，请查看原始说明。'}</div>${run.inputs.filter(i=>i.kind==='video').map(i=>`<div class="input-preview"><video controls preload="none" src="${esc(i.url)}"></video></div>`).join('')}</div></details><details class="details"><summary>模型、来源与复现</summary><div class="detail-content"><p>${esc(modelText(run))}</p><p>调用费用仅以原记录为准；未返回费用不表示免费。${run.reconstructed?'历史作品从原始补丁重建，未重新生成或改写原评分。':''}</p><p>开始：${esc(run.started)}<br>停止原因：${esc(run.stop_reason)}</p><pre class="command">${esc(run.command)}</pre><p>启动前按领域说明安装依赖并准备个人账号；运行环境和评价配置必须保持一致。</p><div class="links">${[example.readme,example.template_readme].filter(Boolean).map(link).join('')}</div></div></details><details class="details"><summary>原始记录与验证凭证</summary><div class="detail-content"><div class="links">${run.evidence.map(link).join('')}</div><p>原始报告、账本和作品不会被展示页覆盖；无修改或失败轮次不补造正式分数。</p></div></details></div>`;
 container.innerHTML=body;bindCases();document.getElementById('run-select').onchange=e=>{runIndex=Number(e.target.value);mode='compare';renderDetail();};renderVersions();document.getElementById('compare-mode').onclick=()=>{mode='compare';updateMode();};document.getElementById('diff-mode').onclick=()=>{mode='diff';updateMode();};}
function bindCases(){document.querySelectorAll('[data-case]').forEach(b=>b.onclick=()=>{caseIndex=Number(b.dataset.case);runIndex=chosen().example.preferred_run;mode='compare';renderDetail();});}
let versionSelection=[0,0],fileSelection=[0,0];
function renderVersions(){const {run}=chosen();if(!run.versions.length){document.getElementById('version-area').innerHTML='<div class="empty">没有保存可比较的作品。</div>';return;}versionSelection=[0,run.versions.length-1];fileSelection=[0,0];updateMode();}
function currentFile(side){const {run}=chosen();return run.versions[versionSelection[side]]?.files[fileSelection[side]];}
function updateMode(){const {run}=chosen();document.getElementById('compare-mode').classList.toggle('active',mode==='compare');document.getElementById('diff-mode').classList.toggle('active',mode==='diff');
 const area=document.getElementById('version-area');area.innerHTML=`<div class="comparison">${[0,1].map(side=>{const v=run.versions[versionSelection[side]];return `<section class="version"><div class="version-controls"><select aria-label="${side?'右':'左'}侧版本" data-version="${side}">${run.versions.map((x,i)=>`<option value="${i}" ${i===versionSelection[side]?'selected':''}>${esc(x.label)}</option>`).join('')}</select><select aria-label="${side?'右':'左'}侧文件" data-file="${side}">${v.files.map((f,i)=>`<option value="${i}" ${i===fileSelection[side]?'selected':''}>${esc(f.name)}</option>`).join('')}</select></div>${v.note?`<div class="note warning">${esc(v.note)}</div>`:''}<div class="version-body" id="viewer-${side}"></div><div class="file-foot" id="file-foot-${side}"></div></section>`;}).join('')}</div><div id="text-diff"></div>`;
 document.querySelectorAll('[data-version]').forEach(s=>s.onchange=e=>{const side=Number(s.dataset.version);versionSelection[side]=Number(e.target.value);fileSelection[side]=0;updateMode();});document.querySelectorAll('[data-file]').forEach(s=>s.onchange=e=>{fileSelection[Number(s.dataset.file)]=Number(e.target.value);updateMode();});
 for(const side of [0,1])renderFile(side,currentFile(side));
 if(mode==='diff'){const a=currentFile(0),b=currentFile(1);if(a?.text!==undefined&&b?.text!==undefined){document.querySelectorAll('.version-body').forEach(el=>el.classList.add('hidden'));document.getElementById('text-diff').innerHTML=lineDiff(a.text,b.text);}else document.getElementById('text-diff').innerHTML='<p class="status-message">请选择两侧的文本或代码文件，再查看逐行差异。</p>';}}
function renderFile(side,file){const view=document.getElementById('viewer-'+side),foot=document.getElementById('file-foot-'+side);if(!file){view.innerHTML='<div class="empty">此版本没有保存的文件。</div>';return;}foot.innerHTML=link({...file,name:'打开完整文件'})+`<span>${(file.bytes/1024).toFixed(1)} KB</span>`;
 if(file.kind==='image'){view.classList.add('image');view.innerHTML=`<img src="${esc(file.url)}" alt="${esc(file.name)}" loading="lazy">`;}
 else if(file.kind==='video'){view.classList.add('image');view.innerHTML=`<video controls preload="metadata" src="${esc(file.url)}"></video>`;}
 else if(file.kind==='html'){const frame=document.createElement('iframe');frame.title=file.name;frame.sandbox='';const policy="default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:; base-uri 'self';";frame.srcdoc=`<meta http-equiv="Content-Security-Policy" content="${policy}"><base href="${esc(new URL(file.url,location.href).href)}">`+file.html;view.append(frame);}
 else if(file.text!==undefined)view.innerHTML=`<pre class="${file.name.endsWith('.md')?'prose':''}">${esc(file.text)}${file.truncated?'\n\n……其余内容见完整文件。':''}</pre>`;
 else view.innerHTML=`<div class="empty">${link({...file,name:'打开原文件'})}</div>`;}
function lineDiff(a,b){const left=a.split('\n'),right=b.split('\n');if(left.length*right.length>1000000)return '<p class="status-message">文本较长，请使用并排查看与完整文件。</p>';
 const table=Array.from({length:left.length+1},()=>new Uint32Array(right.length+1));for(let i=left.length-1;i>=0;i--)for(let j=right.length-1;j>=0;j--)table[i][j]=left[i]===right[j]?table[i+1][j+1]+1:Math.max(table[i+1][j],table[i][j+1]);let i=0,j=0,html='';while(i<left.length||j<right.length){if(i<left.length&&j<right.length&&left[i]===right[j]){html+=`<span class="diff-line">  ${esc(left[i])}</span>`;i++;j++;}else if(j<right.length&&(i===left.length||table[i][j+1]>=table[i+1][j])){html+=`<span class="diff-line diff-added">+ ${esc(right[j++])}</span>`;}else html+=`<span class="diff-line diff-removed">− ${esc(left[i++])}</span>`;}return '<div class="diff" aria-label="逐行文字差异">'+html+'</div>';}
document.getElementById('footer').textContent='本地生成：'+DATA.generated_at+' · 完成状态依据领域要求与原始运行证据；整组首发仍以全部必需领域的验收为准。';
const hash=location.hash.slice(1);if(DATA.domains.some(d=>d.id===hash))selected=hash;selectDomain(selected);
</script></body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = build(args.root.resolve(), args.output)
    complete = sum(domain["state"] == "complete" for domain in data["domains"])
    print(f"已生成本地展示：{complete}/{len(data['domains'])} 个领域具备完整多轮与最终作品；其他状态明确保留。")


if __name__ == "__main__":
    main()
