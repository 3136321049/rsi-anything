#!/usr/bin/env python3
"""Read the domain catalog and raw experiments and build the local showcase page; never changes experiment records or goes online."""
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
STATUSES = {"BASELINE": "Baseline", "KEEP": "Kept", "REVERT": "Rejected", "NO_CHANGE": "No change",
            "AGENT_FAIL": "Agent failed", "JUDGE_FAIL": "Judge failed", "INTERRUPTED": "Interrupted", "FINAL": "Final"}
ORIGINAL_INPUT = "Original input · "
TEXT_EXTENSIONS = {".md", ".txt", ".py", ".json", ".yaml", ".yml", ".csv", ".mmd"}


def human_note(text):
    """Readable note for the pages; the exact original note stays in the ledger."""
    if text.startswith("no edits inside the artifact paths"):
        return "The editable artifact files did not change, so the round did not go to formal review."
    if "tie not broken" in text:
        return "Tied with the best version, but the side-by-side comparison didn't finish, so the best version stays."
    if text.startswith("score ") and " -> " in text:
        match = re.search(r"score ([\d.\-]+) -> ([\d.\-]+)", text)
        if match:
            suffix = re.search(r"head-to-head (\d+/\d+)", text)
            return f"Score rose from {match[1]} to {match[2]}." + (f" Won {suffix[1]} head-to-head comparisons." if suffix else "")
    if text.startswith("score ") and "not better" in text:
        return "The formal score did not clear the margin needed to beat the current best."
    tie = re.match(r"tied at ([\d.\-]+)(?:; won head-to-head (\d+/\d+)| and lost head-to-head \((\d+/\d+) votes\))", text)
    if tie:
        return (f"Tied with the best version at {tie[1]}; won the head-to-head in both orders, {tie[2]}." if tie[2]
                else f"Tied with the best version at {tie[1]}; lost the head-to-head ({tie[3]}).")
    if "lost head-to-head" in text:
        return "Higher score, but it did not win the head-to-head comparison with the current best (both orders)."
    if text.startswith("passes gates"):
        return "Fixes required checks that the current best did not yet pass."
    if text.startswith("failed gates:"):
        return "Failed required checks: " + text.partition(":")[2].strip()
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
                         r'<details><summary>Chart definition (Mermaid)</summary><pre>\1</pre></details>', content, flags=re.S)
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
            "note": "This round had no formal review; the out files the agent generated internally were not used to compare artifacts, and the original record is still kept." if hidden_internal_outputs else ""}


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
                       note=derived.get("reason") or "The service or environment didn't finish, so there was no artifact to judge and its quality is unknown. The raw record is kept unchanged.")
            unknown_rounds.append(number)
    invalid = case.get("invalid_runs", {}).get(run.name, "")
    versions = []
    for row in rows:
        number = row.get("round", 0)
        rel = row.get("artifacts") or ("artifacts/baseline" if number == 0 else f"rounds/r{number:03d}/artifacts")
        label = "Starting artifact" if number == 0 else f"Round {number} · {STATUSES.get(row.get('status'), row.get('status', 'Unknown'))}"
        version = snapshot(root, run, rel, label, row.get("status"), case["primary"])
        if version:
            if row.get("quality_result") == "unknown":
                version["label"] = f"Round {number} · quality unknown"
                version["note"] = "Generation or execution did not finish; only the inputs and error evidence are kept here, and there is no new artifact to evaluate."
            versions.append(version)
    final = snapshot(root, run, meta.get("final_artifacts") or "artifacts/final", "Final kept artifact", "FINAL", case["primary"])
    if final:
        versions.append(final)
    attempts = [row for row in rows if row.get("round", 0) > 0]
    actual_attempts = [row for row in attempts if row.get("status") in {"KEEP", "REVERT", "NO_CHANGE"}]
    reasons = []
    if invalid:
        reasons.append(invalid)
    if not meta.get("finished") or meta.get("status") in {"failed", "interrupted", "running"}:
        reasons.append("The run has no record of finishing normally yet.")
    if len(actual_attempts) < 2:
        reasons.append("There are not yet at least two completed real attempts.")
    if audit_valid and outcome_audit.get("complete_multiround") is False:
        reasons.append("Derived verification confirms only partial measurement; rounds where the service failed cannot count as artifact-quality results.")
    if not final or not final["files"]:
        reasons.append("The final artifact was not saved.")
    if not independently_verified(run):
        reasons.append("The independent verification record is not yet complete or did not pass.")
    if domain.get("require_holdout") and meta.get("holdout", {}).get("final") is None:
        reasons.append("The final held-out result is missing.")
    if domain.get("require_video") and not any(item["kind"] == "video" for item in (final or {}).get("files", [])):
        reasons.append("The final playable video is missing.")
    if domain.get("require_gpu"):
        measurements = read_json(run / (meta.get("final_artifacts") or "artifacts/final") / "files/out/metrics.json")
        if measurements.get("status") != "measured" or not measurements.get("metrics", {}).get("module"):
            reasons.append("There are no real GPU and module comparison results yet.")
    execution = read_json(run / "config/execution.json")
    model = execution.get("agent", {})
    baseline = rows[0].get("score") if rows else None
    best = rows[-1].get("best") if rows else None
    if best is None and final:
        best = read_json(run / final["snapshot"] / "verdict.json").get("score")
    def finite(value):
        return value if isinstance(value, (int, float)) and math.isfinite(value) else None
    mapped_rows = [{"round": row.get("round"), "status": row.get("status"),
                    "label": "Generation unfinished · quality unknown" if row.get("quality_result") == "unknown" else STATUSES.get(row.get("status"), "Unknown"),
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
            item["name"] = ORIGINAL_INPUT + item["name"]
            inputs.insert(0, item)
    for name in ("report.html", "ledger.jsonl", "verification.json", "artifact-verification.json", "outcome-audit.json", "source-receipts.json", "config/rsi.yaml",
                 "config/execution.json", "versions.json", "NOTES.md", "README.md"):
        item = file_item(root, run / name)
        if item:
            item["name"] = {"report.html": "Original run report", "ledger.jsonl": "Full round ledger", "verification.json": "Independent verification",
                            "artifact-verification.json": "Independent verification of historical artifacts", "config/rsi.yaml": "Frozen task config",
                            "outcome-audit.json": "Derived outcome audit (original ledger unchanged)", "source-receipts.json": "Original service receipts",
                            "config/execution.json": "Model and run parameters", "versions.json": "Version reconstruction source",
                            "NOTES.md": "Historical run notes", "README.md": "Run notes"}[name]
            extras.append(item)
    reconstructed = read_json(run / "versions.json").get("source") == "reconstructed_from_original_patches"
    holdout_files = []
    for path in sorted((run / "artifacts/final").glob("holdout*")):
        if path.is_file():
            item = file_item(root, path)
            if item:
                holdout_files.append(item)
    budget = execution.get("budget", {})
    command = ["python", "scripts/run_demo.py", case["template"], "--model", model.get("requested_model") or model.get("model") or "<your-model>",
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
            "agent": meta.get("agent", "unknown"), "jury": meta.get("jury", []), "task_model": execution.get("task_model"),
            "stop_reason": meta.get("stop_reason", "Not provided"), "elapsed_seconds": meta.get("elapsed_seconds"),
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
                item["readme"]["name"] = "Domain results"
            if item["template_readme"]:
                item["template_readme"]["name"] = "Template usage and sources"
            cases.append(item)
        domain["cases"] = cases
        domain["state"] = ("complete" if all(case["complete"] for case in cases)
                           else "resource_exception" if specification.get("resource_exception")
                           else "partial" if any(case["runs"] for case in cases) else specification["pending"])
        domain["probe"] = file_item(root, root / "examples" / specification["probe"] / "README.md") if specification.get("probe") else None
        if domain["probe"]:
            domain["probe"]["name"] = "Local environment probe record"
        domains.append(domain)
    return {"title": catalog["title"], "description": catalog["description"], "domains": domains,
            "generated_at": datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M (Beijing time)")}


def build(root=ROOT, output=None):
    data = collect(root)
    encoded = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    output = output or root / "examples/index.html"
    if output.resolve().parent != (root / "examples").resolve():
        raise ValueError("The showcase page must live in the examples directory so its relative links to the original artifacts keep working.")
    output.write_text(PAGE.replace("__CATALOG_DATA__", encoded), encoding="utf-8")
    return data


PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Open RSI · Experiments and artifacts</title>
<style>
:root{--ink:#203038;--muted:#64737b;--line:#dce4e3;--paper:#f3f5f2;--card:#fff;--green:#176d54;--pale:#e7f2eb;--amber:#92630c;--soft:#f7ecd6;--red:#9a4c40}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif}button,select{font:inherit}button{cursor:pointer}a{color:var(--green);text-underline-offset:3px}header{background:#142b26;color:#fff;padding:34px max(24px,calc((100vw - 1420px)/2)) 38px}header .brand{letter-spacing:.2em;font-size:12px;color:#9dc8b5}h1{font-size:clamp(30px,4vw,48px);letter-spacing:-.04em;line-height:1.2;margin:16px 0}header p{color:#c3d6ce;max-width:740px;margin:0}.headline{display:flex;justify-content:space-between;align-items:end;gap:32px}.totals{display:flex;gap:28px;white-space:nowrap}.totals b{font-size:32px;display:block;line-height:1.1}.totals span{font-size:12px;color:#bed1c8}.shell{max-width:1468px;margin:auto;padding:24px}.toolbar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}.filter,.case-tab{border:1px solid var(--line);background:white;color:var(--ink);border-radius:22px;padding:7px 15px}.filter.active,.case-tab.active{color:#fff;background:var(--green);border-color:var(--green)}.workspace{display:grid;grid-template-columns:300px minmax(0,1fr);gap:24px;align-items:start}.catalog{display:grid;gap:10px;max-height:calc(100vh - 35px);overflow:auto;position:sticky;top:16px;padding-right:4px}.domain-card{display:block;width:100%;text-align:left;border:1px solid var(--line);background:var(--card);padding:15px 17px;border-radius:12px;color:var(--ink);transition:.15s}.domain-card:hover{border-color:#75a18f;transform:translateY(-1px)}.domain-card.active{border-color:var(--green);box-shadow:inset 4px 0 var(--green);background:#f9fdf9}.card-top{display:flex;justify-content:space-between;gap:8px;font-size:11px;color:var(--muted)}.domain-card h3{font-size:16px;margin:8px 0 4px}.domain-card p{margin:0;color:var(--muted);font-size:12px;line-height:1.5}.badge{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:650;background:#e9edee;color:#66747c}.badge.complete,.badge.keep{background:var(--pale);color:var(--green)}.badge.partial,.badge.waiting,.badge.revert{background:var(--soft);color:var(--amber)}.badge.fail{background:#f9e9e3;color:var(--red)}.panel{background:white;border:1px solid var(--line);border-radius:16px;overflow:hidden;min-width:0}.panel-head{padding:28px 30px 24px;border-bottom:1px solid var(--line)}.eyebrow{font-size:12px;color:var(--muted)}h2{font-size:28px;margin:8px 0 10px;line-height:1.3}.description{color:var(--muted);margin:0}.note{font-size:13px;background:#f6f7f2;border-left:3px solid #b1bfae;padding:10px 14px;margin-top:16px;white-space:pre-wrap}.note.warning{border-color:#c89942;background:#fbf4e8}.case-tabs{display:flex;gap:8px;margin-top:20px}.panel-body{padding:24px 30px 32px}.run-picker{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.run-picker label{font-size:12px;color:var(--muted)}select{max-width:100%;border:1px solid var(--line);padding:8px 11px;border-radius:7px;background:#fff;color:var(--ink);min-width:0}.run-picker select{flex:1;font-size:12px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}.stat{padding:16px;background:#f4f7f4;border-radius:10px}.stat .label{font-size:11px;color:var(--muted)}.stat b{display:block;font-size:26px;font-weight:650;margin-top:5px;line-height:1.2}.stat small{color:var(--muted);font-size:11px}.section-label{font-size:16px;font-weight:650;margin:26px 0 12px}.compare-toolbar{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}.compare-toolbar .section-label{margin:12px 0}.mode{display:flex;gap:6px}.mode button{font-size:12px;background:white;border:1px solid var(--line);padding:5px 10px;border-radius:6px}.mode button.active{background:#edf5f0;border-color:var(--green);color:var(--green)}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:14px}.version{border:1px solid var(--line);border-radius:10px;min-width:0;overflow:hidden;background:#fff}.version-controls{padding:12px;background:#f7f9f7;display:grid;gap:8px;border-bottom:1px solid var(--line)}.version-controls select{width:100%;font-size:12px}.version-body{height:520px;overflow:auto;position:relative}.version-body.image{height:auto;min-height:250px}.version-body img{width:100%;height:auto;display:block;max-height:600px;object-fit:contain}.version-body video{width:100%;height:auto;max-height:560px;background:#101e1b;display:block}.version-body iframe{width:100%;height:520px;border:0;background:white}.version-body pre{margin:0;padding:18px;font:12px/1.8 ui-monospace,SFMono-Regular,Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere}.version-body .prose{font:14px/1.9 system-ui}.file-foot{padding:8px 12px;font-size:11px;border-top:1px solid var(--line);display:flex;justify-content:space-between;gap:8px}.empty{padding:50px 24px;text-align:center;color:var(--muted);background:#f8faf7;border-radius:10px}.empty b{display:block;color:var(--ink);font-size:20px;margin-bottom:8px}.diff-added{background:#e9f6e9;color:#1c6637}.diff-removed{background:#fbe9e4;color:#9a4c40}.diff-line{display:block;white-space:pre-wrap;padding:0 10px;border-bottom:1px solid #f1f3f1}.diff{max-height:520px;overflow:auto;font:12px/1.8 ui-monospace,monospace;border:1px solid var(--line);border-radius:9px;padding:12px 0}.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:9px}table{width:100%;border-collapse:collapse;font-size:12px}th,td{text-align:left;padding:12px;border-bottom:1px solid var(--line);vertical-align:top}th{background:#f7f9f7;color:var(--muted);font-weight:500}tr:last-child td{border-bottom:0}.score{white-space:nowrap;font-weight:650}.row-note{display:block;color:var(--muted);margin-top:4px;max-width:550px}.details{border-top:1px solid var(--line);margin-top:22px;padding-top:12px}.details summary{cursor:pointer;font-weight:650;padding:6px 0}.detail-content{padding:10px 0;color:var(--muted);font-size:13px}.links{display:flex;gap:8px;flex-wrap:wrap}.links a{background:#f1f5f1;padding:5px 9px;border-radius:5px;font-size:12px;overflow-wrap:anywhere}.input-preview{max-height:280px;overflow:auto;margin-top:12px}.input-preview video{width:100%;max-height:300px;background:#15221d}.command{padding:14px;background:#172d27;color:#e1f1e6;border-radius:8px;white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.7 ui-monospace,monospace}.footer{color:var(--muted);font-size:12px;padding:28px 0 10px}.status-message{font-size:13px;color:var(--muted);margin:12px 0}.hidden{display:none!important}@media(max-width:1100px){.workspace{grid-template-columns:250px minmax(0,1fr);gap:16px}.shell{padding:16px}.panel-head,.panel-body{padding:20px}.stats{gap:8px}.stat{padding:12px}.stat b{font-size:22px}.headline{align-items:start}.totals{gap:15px}}@media(max-width:760px){header{padding:24px 20px}.headline{display:block}.totals{margin-top:24px}.workspace{display:block}.catalog{display:flex;position:static;max-height:none;overflow-x:auto;gap:8px;margin-bottom:16px;padding-bottom:10px}.domain-card{min-width:220px;width:220px}.comparison{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.version-body{height:400px}.version-body iframe{height:400px}.panel-head,.panel-body{padding:18px}.run-picker{display:block}.run-picker select{width:100%}.toolbar{gap:5px}.filter{padding:6px 11px;font-size:12px}h2{font-size:24px}.version-body.image{min-height:160px}}
</style></head><body>
<header><div class="brand">OPEN RSI / EXPERIMENTS AND ARTIFACTS</div><div class="headline"><div><h1>See what the AI actually changed</h1><p>From the first draft to the artifact that was finally kept. Every attempt, acceptance, rejection and stall has a raw record you can check.</p></div><div class="totals" id="totals"></div></div></header>
<main class="shell"><nav class="toolbar" aria-label="Domain filter" id="filters"></nav><div class="workspace"><aside class="catalog" id="catalog" aria-label="15 domains"></aside><article class="panel" id="detail" aria-live="polite"></article></div><footer class="footer" id="footer"></footer></main>
<script id="catalog-data" type="application/json">__CATALOG_DATA__</script>
<script>
'use strict';
const DATA=JSON.parse(document.getElementById('catalog-data').textContent);
const stateLabels={complete:'Accepted',partial:'Partly done',developing:'In development',waiting:'Waiting on outside conditions',resource_exception:'Resource exception'};
const statusLabels={BASELINE:'Baseline',KEEP:'Kept',REVERT:'Rejected',NO_CHANGE:'No change',AGENT_FAIL:'Agent failed',JUDGE_FAIL:'Judge failed',INTERRUPTED:'Interrupted',FINAL:'Final'};
let selected='D04',caseIndex=0,runIndex=0,filter='All',mode='compare';
const esc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const number=value=>value===null||value===undefined?'—':Number(value).toLocaleString('en-US',{maximumFractionDigits:3});
const badge=(label,state)=>`<span class="badge ${esc(state)}">${esc(label)}</span>`;
const link=item=>`<a href="${esc(item.url)}" target="_blank" rel="noopener">${esc(item.name)}</a>`;
function chosen(){const domain=DATA.domains.find(d=>d.id===selected);const example=domain.cases[caseIndex]||domain.cases[0];return {domain,example,run:example.runs[runIndex]};}
function renderNavigation(){const counts={};for(const d of DATA.domains)counts[d.state]=(counts[d.state]||0)+1;
 document.getElementById('totals').innerHTML=`<div><b>${DATA.domains.length}</b><span>domains</span></div><div><b>${counts.complete||0}</b><span>with complete multi-round runs and artifacts</span></div><div><b>${DATA.domains.length-(counts.complete||0)-(counts.resource_exception||0)} / ${counts.resource_exception||0}</b><span>to do / resource exceptions</span></div>`;
 document.getElementById('filters').innerHTML=['All','Accepted','In progress','Resource exception','Engineering','Models','Creative','Research','Everyday'].map(x=>`<button class="filter ${filter===x?'active':''}" data-filter="${x}">${x}</button>`).join('');
 document.getElementById('catalog').innerHTML=DATA.domains.filter(d=>filter==='All'||filter==='Accepted'&&d.state==='complete'||filter==='In progress'&&!['complete','resource_exception'].includes(d.state)||filter==='Resource exception'&&d.state==='resource_exception'||d.category===filter).map(d=>`<button class="domain-card ${d.id===selected?'active':''}" data-domain="${d.id}"><div class="card-top"><span>${d.id} · ${d.category}</span>${badge((d.resource_exception_label&&d.state==='resource_exception'?d.resource_exception_label:stateLabels[d.state]),d.state)}</div><h3>${esc(d.title)}</h3><p>${esc(d.description)}</p></button>`).join('');
 document.querySelectorAll('[data-filter]').forEach(b=>b.onclick=()=>{filter=b.dataset.filter;renderNavigation();});
 document.querySelectorAll('[data-domain]').forEach(b=>b.onclick=()=>selectDomain(b.dataset.domain));}
function selectDomain(id){selected=id;caseIndex=0;runIndex=DATA.domains.find(d=>d.id===id).cases[0].preferred_run;mode='compare';history.replaceState(null,'','#'+id);renderNavigation();renderDetail();}
function modelText(run){return `Agent: ${run.agent}; requested model: ${run.requested_model||'not pinned in the historical record'}; model confirmed by the service: ${run.actual_model||'not returned'}; reasoning effort: ${run.reasoning_effort||'not recorded'}. ${run.jury.length?'Jury: '+run.jury.join(', ')+'.':'Scored by a program, with no model jury.'}${run.task_model?' Task model: '+run.task_model+'.':''}`;}
function renderDetail(){const {domain,example,run}=chosen();const container=document.getElementById('detail');
 let body=`<div class="panel-head"><div class="eyebrow">${domain.id} / ${domain.category} ${badge((domain.resource_exception_label&&domain.state==='resource_exception'?domain.resource_exception_label:stateLabels[domain.state]),domain.state)}</div><h2>${esc(domain.title)}</h2><p class="description">${esc(domain.description)}</p>${domain.note?`<div class="note">${esc(domain.note)}</div>`:''}<div class="case-tabs">${domain.cases.map((c,i)=>`<button class="case-tab ${i===caseIndex?'active':''}" data-case="${i}">${esc(c.title)} ${c.complete?'✓':''}</button>`).join('')}</div></div><div class="panel-body">`;
 if(!run){body+=`<div class="empty"><b>${(domain.resource_exception_label&&domain.state==='resource_exception'?domain.resource_exception_label:stateLabels[domain.state])}</b>There is no complete multi-round record to show yet.<br>Scores and speedups are left blank; templates and probe results do not count as finished experiments.</div><div class="links" style="margin-top:20px">${[example.template_readme,example.readme,domain.probe].filter(Boolean).map(link).join('')}</div></div>`;container.innerHTML=body;bindCases();return;}
 body+=`<div class="run-picker"><label for="run-select">Raw run</label><select id="run-select">${example.runs.map((r,i)=>`<option value="${i}" ${i===runIndex?'selected':''}>${esc(r.id)} · ${r.eligible?'Complete multi-round':r.invalid_reason?'Scoring problem':r.finished?'Partly done':'Not finished'}</option>`).join('')}</select></div>`;
 if(run.reasons.length)body+=`<div class="note warning">${run.reasons.map(esc).join('\n')}</div>`;
 body+=`<div class="stats"><div class="stat"><span class="label">Baseline · ${esc(domain.metric)}</span><b>${number(run.baseline)}<small> ${run.baseline!==null?esc(domain.unit):''}</small></b></div><div class="stat"><span class="label">Finally kept</span><b>${number(run.best)}<small> ${run.best!==null?esc(domain.unit):''}</small></b></div><div class="stat"><span class="label">Real attempts</span><b>${run.rounds}<small> rounds</small></b></div><div class="stat"><span class="label">Kept / attempts</span><b>${run.kept}<small> / ${run.rounds}</small></b></div></div>`;
 if(run.quality_unknown_rounds.length)body+=`<div class="note warning">Round ${run.quality_unknown_rounds.join(', ')} produced no artifact, so the formal quality score is left blank; the raw failure and the derived audit can both be opened below.</div>`;
 if(Object.keys(run.holdout).length)body+=`<div class="status-message">Held-out set: ${number(run.holdout.baseline)} → ${number(run.holdout.final)}. The held-out result is listed separately and never mixed with the development score.</div>`;
 body+=`<div class="compare-toolbar"><div class="section-label">Artifact versions</div><div class="mode"><button id="compare-mode" class="active">Side by side</button><button id="diff-mode">Text diff</button></div></div><div id="version-area"></div><div class="section-label">All rounds</div><div class="table-wrap"><table><thead><tr><th>Round</th><th>Decision</th><th>Formal score</th><th>What changed / why it was kept or rejected</th></tr></thead><tbody>${run.rows.map(r=>`<tr><td>${r.round===0?'Baseline':r.round}</td><td>${badge(r.label,r.status==='KEEP'?'keep':r.status==='REVERT'?'revert':r.status.endsWith('FAIL')?'fail':'')}</td><td class="score">${number(r.score)}</td><td>${esc(r.hypothesis||(r.round===0?'Froze the inputs and evaluation and recorded the starting result.':'No new formal candidate was left.'))}<span class="row-note">${esc(r.note)}</span></td></tr>`).join('')}</tbody></table></div>`;
 body+=`<details class="details"><summary>Task and raw inputs</summary><div class="detail-content"><p style="white-space:pre-wrap">${esc(run.goal)}</p><div class="links">${run.inputs.map(link).join('')||'This run saved no input links; see the original notes.'}</div>${run.inputs.filter(i=>i.kind==='video').map(i=>`<div class="input-preview"><video controls preload="none" src="${esc(i.url)}"></video></div>`).join('')}</div></details><details class="details"><summary>Models, sources and reproduction</summary><div class="detail-content"><p>${esc(modelText(run))}</p><p>Call costs come only from the original records; a missing cost does not mean it was free.${run.reconstructed?' Historical artifacts were rebuilt from the original patches; nothing was regenerated and the original scores were not rewritten.':''}</p><p>Started: ${esc(run.started)}<br>Stop reason: ${esc(run.stop_reason)}</p><pre class="command">${esc(run.command)}</pre><p>Before starting, install the dependencies and prepare a personal account as the domain notes describe; the runtime environment and evaluation config must stay the same.</p><div class="links">${[example.readme,example.template_readme].filter(Boolean).map(link).join('')}</div></div></details><details class="details"><summary>Raw records and verification evidence</summary><div class="detail-content"><div class="links">${run.evidence.map(link).join('')}</div><p>The showcase never overwrites the original reports, ledgers or artifacts, and no formal score is invented for unchanged or failed rounds.</p></div></details></div>`;
 container.innerHTML=body;bindCases();document.getElementById('run-select').onchange=e=>{runIndex=Number(e.target.value);mode='compare';renderDetail();};renderVersions();document.getElementById('compare-mode').onclick=()=>{mode='compare';updateMode();};document.getElementById('diff-mode').onclick=()=>{mode='diff';updateMode();};}
function bindCases(){document.querySelectorAll('[data-case]').forEach(b=>b.onclick=()=>{caseIndex=Number(b.dataset.case);runIndex=chosen().example.preferred_run;mode='compare';renderDetail();});}
let versionSelection=[0,0],fileSelection=[0,0];
function renderVersions(){const {run}=chosen();if(!run.versions.length){document.getElementById('version-area').innerHTML='<div class="empty">No artifacts were saved to compare.</div>';return;}versionSelection=[0,run.versions.length-1];fileSelection=[0,0];updateMode();}
function currentFile(side){const {run}=chosen();return run.versions[versionSelection[side]]?.files[fileSelection[side]];}
function updateMode(){const {run}=chosen();document.getElementById('compare-mode').classList.toggle('active',mode==='compare');document.getElementById('diff-mode').classList.toggle('active',mode==='diff');
 const area=document.getElementById('version-area');area.innerHTML=`<div class="comparison">${[0,1].map(side=>{const v=run.versions[versionSelection[side]];return `<section class="version"><div class="version-controls"><select aria-label="${side?'Right':'Left'} version" data-version="${side}">${run.versions.map((x,i)=>`<option value="${i}" ${i===versionSelection[side]?'selected':''}>${esc(x.label)}</option>`).join('')}</select><select aria-label="${side?'Right':'Left'} file" data-file="${side}">${v.files.map((f,i)=>`<option value="${i}" ${i===fileSelection[side]?'selected':''}>${esc(f.name)}</option>`).join('')}</select></div>${v.note?`<div class="note warning">${esc(v.note)}</div>`:''}<div class="version-body" id="viewer-${side}"></div><div class="file-foot" id="file-foot-${side}"></div></section>`;}).join('')}</div><div id="text-diff"></div>`;
 document.querySelectorAll('[data-version]').forEach(s=>s.onchange=e=>{const side=Number(s.dataset.version);versionSelection[side]=Number(e.target.value);fileSelection[side]=0;updateMode();});document.querySelectorAll('[data-file]').forEach(s=>s.onchange=e=>{fileSelection[Number(s.dataset.file)]=Number(e.target.value);updateMode();});
 for(const side of [0,1])renderFile(side,currentFile(side));
 if(mode==='diff'){const a=currentFile(0),b=currentFile(1);if(a?.text!==undefined&&b?.text!==undefined){document.querySelectorAll('.version-body').forEach(el=>el.classList.add('hidden'));document.getElementById('text-diff').innerHTML=lineDiff(a.text,b.text);}else document.getElementById('text-diff').innerHTML='<p class="status-message">Pick a text or code file on both sides to see the line-by-line diff.</p>';}}
function renderFile(side,file){const view=document.getElementById('viewer-'+side),foot=document.getElementById('file-foot-'+side);if(!file){view.innerHTML='<div class="empty">This version has no saved files.</div>';return;}foot.innerHTML=link({...file,name:'Open the full file'})+`<span>${(file.bytes/1024).toFixed(1)} KB</span>`;
 if(file.kind==='image'){view.classList.add('image');view.innerHTML=`<img src="${esc(file.url)}" alt="${esc(file.name)}" loading="lazy">`;}
 else if(file.kind==='video'){view.classList.add('image');view.innerHTML=`<video controls preload="metadata" src="${esc(file.url)}"></video>`;}
 else if(file.kind==='html'){const frame=document.createElement('iframe');frame.title=file.name;frame.sandbox='';const policy="default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:; base-uri 'self';";frame.srcdoc=`<meta http-equiv="Content-Security-Policy" content="${policy}"><base href="${esc(new URL(file.url,location.href).href)}">`+file.html;view.append(frame);}
 else if(file.text!==undefined)view.innerHTML=`<pre class="${file.name.endsWith('.md')?'prose':''}">${esc(file.text)}${file.truncated?'\n\n… the rest is in the full file.':''}</pre>`;
 else view.innerHTML=`<div class="empty">${link({...file,name:'Open the original file'})}</div>`;}
function lineDiff(a,b){const left=a.split('\n'),right=b.split('\n');if(left.length*right.length>1000000)return '<p class="status-message">The text is long; use the side-by-side view and the full file.</p>';
 const table=Array.from({length:left.length+1},()=>new Uint32Array(right.length+1));for(let i=left.length-1;i>=0;i--)for(let j=right.length-1;j>=0;j--)table[i][j]=left[i]===right[j]?table[i+1][j+1]+1:Math.max(table[i+1][j],table[i][j+1]);let i=0,j=0,html='';while(i<left.length||j<right.length){if(i<left.length&&j<right.length&&left[i]===right[j]){html+=`<span class="diff-line">  ${esc(left[i])}</span>`;i++;j++;}else if(j<right.length&&(i===left.length||table[i][j+1]>=table[i+1][j])){html+=`<span class="diff-line diff-added">+ ${esc(right[j++])}</span>`;}else html+=`<span class="diff-line diff-removed">− ${esc(left[i++])}</span>`;}return '<div class="diff" aria-label="Line-by-line text diff">'+html+'</div>';}
document.getElementById('footer').textContent='Generated locally: '+DATA.generated_at+' · Completion status follows the domain requirements and the raw run evidence; the first full release still depends on every required domain being accepted.';
const hash=location.hash.slice(1);if(DATA.domains.some(d=>d.id===hash))selected=hash;selectDomain(selected);
</script></body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = build(args.root.resolve(), args.output)
    complete = sum(domain["state"] == "complete" for domain in data["domains"])
    print(f"Built the local showcase: {complete}/{len(data['domains'])} domains have complete multi-round runs and final artifacts; other states are shown as they are.")


if __name__ == "__main__":
    main()
