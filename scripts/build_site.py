#!/usr/bin/env python3
"""从已保存的实验构建可独立托管的中英文网站，不执行模型任务。"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_showcase
import site_i18n

SITE_URL = "https://www.riseai.top/darwin/"
CASES = {
    "code-speed": "2026-10-21-codex-3-rounds",
    "code-repair": "20261023-234857-expense-code-repair",
    "cpu-classifier": "20261024-001122-cpu-digits-classifier",
    "video-cut": "20261024-002228-talk-highlight",
}
# 英文为默认语言，中文放在 zh/ 下。
LANGS = {"en": "", "zh": "zh/"}
PAGES = {"": "home", "labs/code/": "code", "labs/experiments/": "experiments", "labs/video/": "video",
         "cases/": "cases", "start/": "start"}
# 公开站点只带这些说明文档（中英各一份）；内部交接、开发记录和发布审计不对外。
PUBLIC_DOCS = tuple(f"{name}{suffix}.md" for name in ("INSTALL", "EXTENDING", "OPEN-SOURCE", "PLAN") for suffix in (".zh-CN", ""))
EVIDENCE_KEYS = {"report.html": "report", "ledger.jsonl": "ledger", "verification.json": "verification",
                 "artifact-verification.json": "artifact_verification", "outcome-audit.json": "outcome_audit",
                 "source-receipts.json": "source_receipts", "rsi.yaml": "config", "execution.json": "execution",
                 "versions.json": "versions", "NOTES.md": "notes", "README.md": "readme"}
WHEEL = "rsi_anything-0.2.0.dev0-py3-none-any.whl"


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
        cues.append({"start": seconds(start), "end": seconds(end), "text": " ".join(lines[timing + 1:])})
    return cues


def case_data(root, case, domain):
    run = next(r for r in case["runs"] if r["id"] == CASES[case["template"]])
    folder = root / "examples" / case["template"] / "runs" / run["id"]
    rows = [json.loads(line) for line in (folder / "ledger.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    snapshots = []
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
            item["tests"] = read(files / "out/tests.json")
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
    return {"template": case["template"], "title": domain["title"],
            "description": domain["description"], "metric": domain["metric"], "unit": domain["unit"],
            "run_id": run["id"], "root": folder.relative_to(root).as_posix() + "/",
            "best_round": champion, "rounds": snapshots, "baseline": run["baseline"], "best": run["best"],
            "agent": run["agent"], "requested_model": run["requested_model"], "actual_model": run["actual_model"],
            "started": run["started"], "stop_reason": run["stop_reason"],
            "verified": run["eligible"], "reconstructed": run["reconstructed"],
            "source": read(root / "examples/video-cut/inputs/public-speech/source.json") if case["template"] == "video-cut" else None}


def public_file(item):
    """展示数据里的文件只留地址与类型，正文由页面按需读取。"""
    return {"name": item["name"], "url": "examples/" + item["url"], "kind": item["kind"], "bytes": item["bytes"]}


def english_doc(url, output):
    """说明文档的英文版：README.md → README.en.md，X.zh-CN.md → X.md；没有译文时沿用原文。"""
    folder, _, name = url.rpartition("/")
    english = name[:-len(".zh-CN.md")] + ".md" if name.endswith(".zh-CN.md") else name[:-3] + ".en.md"
    candidate = (folder + "/" if folder else "") + english
    return candidate if name.endswith(".md") and not name.endswith(".en.md") and (output / candidate).is_file() else url


def english_catalog_docs(catalog, output):
    """英文页的案例说明、模板说明和环境探测链接改指英文版。"""
    def swap(item):
        return item and {**item, "url": english_doc(item["url"], output)}
    for domain in catalog["domains"]:
        domain["probe"] = swap(domain["probe"])
        for case in domain["cases"]:
            case["readme"], case["template_readme"] = swap(case["readme"]), swap(case["template_readme"])
            for run in case["runs"]:
                run["evidence"] = [swap(item) if item["name"] == "README.md" else item for item in run["evidence"]]
    return catalog


def compact_catalog(data):
    domains = []
    for domain in data["domains"]:
        cases = []
        for case in domain["cases"]:
            runs = []
            for run in case["runs"]:
                versions = []
                for version in run["versions"]:
                    match = re.search(r"r(\d+)", version["snapshot"])
                    kind = "final" if version["status"] == "FINAL" else "baseline" if "baseline" in version["snapshot"] else "round"
                    number = int(match[1]) if kind == "round" and match else 0
                    versions.append({"kind": kind, "round": number, "status": version["status"], "note": version["note"],
                                     "quality_unknown": kind == "round" and number in run["quality_unknown_rounds"],
                                     "files": [public_file(f) for f in version["files"]]})
                inputs = []
                for item in run["inputs"]:
                    original = item["name"].startswith("原始输入 · ")
                    inputs.append({**public_file(item), "name": item["name"].removeprefix("原始输入 · "), "original": original})
                evidence = []
                for item in run["evidence"]:
                    name = item["url"].rsplit("/", 1)[-1]
                    key = "holdout" if name.startswith("holdout") else EVIDENCE_KEYS.get(name)
                    evidence.append({**public_file(item), "name": name, "key": key})
                runs.append({key: run[key] for key in ("id", "eligible", "finished", "invalid_reason", "reasons", "started",
                                                        "baseline", "best", "rounds", "kept", "goal", "holdout",
                                                        "quality_unknown_rounds", "agent", "requested_model", "actual_model",
                                                        "reasoning_effort", "jury", "task_model", "stop_reason")}
                            | {"rows": [{**{k: row[k] for k in ("round", "status", "score", "hypothesis", "note", "feedback")},
                                         "quality_unknown": row["round"] in run["quality_unknown_rounds"]} for row in run["rows"]],
                               "versions": versions, "inputs": inputs, "evidence": evidence})
            cases.append({"template": case["template"], "title": case["title"], "preferred_run": case["preferred_run"],
                          "readme": case["readme"] and {"url": "examples/" + case["readme"]["url"]},
                          "template_readme": case["template_readme"] and {"url": "examples/" + case["template_readme"]["url"]},
                          "runs": runs})
        domains.append({"id": domain["id"], "title": domain["title"], "category": domain["category"],
                        "description": domain["description"], "note": domain.get("note", ""),
                        "metric": domain["metric"], "unit": domain["unit"], "state": domain["state"],
                        "exception_label": domain.get("resource_exception_label") if domain["state"] == "resource_exception" else None,
                        "probe": domain["probe"] and {"url": "examples/" + domain["probe"]["url"]}, "cases": cases})
    return {"domains": domains}


def home_data(labs, strings, root):
    series = {}
    for template in ("code-speed", "cpu-classifier", "video-cut"):
        lab = labs[template]
        rounds = []
        for row in lab["rounds"]:
            if template == "video-cut":
                summary = strings["lab"]["video"]["summary"][str(row["round"])]
            else:
                summary = "" if row["status"] == "NO_CHANGE" else row["hypothesis"]
            rounds.append({"round": row["round"], "status": row["status"], "score": row["score"], "summary": summary})
        series[template] = {"metric": lab["metric"], "unit": lab["unit"], "best_round": lab["best_round"], "rounds": rounds}
    model = labs["cpu-classifier"]
    video = labs["video-cut"]
    total = len(read(root / "examples/video-cut/inputs/public-speech/sentences.json", []))
    return {"series": series,
            "matrices": {"baseline": model["rounds"][0]["metrics"]["confusion_matrix"],
                         "final": model["rounds"][model["best_round"]]["metrics"]["confusion_matrix"]},
            "segments": {"total": total, "selected": video["rounds"][video["best_round"]]["segments"]}}


def experiment_log(catalog, strings):
    rows = []
    for domain in catalog["domains"]:
        case = domain["cases"][0]
        run = case["runs"][case["preferred_run"]] if case["runs"] else None
        result = f"{_num(run['baseline'])} → {_num(run['best'])}{unit_text(domain['unit'])}" if run and run["best"] is not None else "—"
        if domain["state"] == "complete":
            label, tone = strings["log_state"]["complete"], "keep"
        else:
            label, tone = domain["exception_label"] or strings["log_state"]["resource_exception"], "warn"
        titles = " · ".join(c["title"] for c in domain["cases"])
        rows.append(f'<a class="log-row" role="row" href="__HOME__cases/#{domain["id"]}"><span class="mono" role="cell">{domain["id"]}</span>'
                    f'<span role="cell"><strong>{html.escape(domain["title"])}</strong><small>{html.escape(domain["category"])} · {html.escape(titles)}</small></span>'
                    f'<span class="mono" role="cell">{html.escape(result)}</span><span role="cell"><span class="pill {tone}">{html.escape(label)}</span></span></a>')
    return "\n".join(rows)


def unit_text(unit):
    """英文单位前留空格，符号与中文单位紧贴数字。"""
    return " " + unit if re.match(r"[A-Za-z]", unit or "") else unit or ""


def _num(value):
    return f"{value:g}" if isinstance(value, (int, float)) else "—"


def fill(text, strings):
    def lookup(match):
        node = strings
        for part in match[1].split("."):
            if not isinstance(node, dict) or part not in node:
                raise KeyError(f"缺少界面文字：{match[1]}")
            node = node[part]
        return node
    return re.sub(r"\{\{([\w.]+)\}\}", lookup, text)


def inline_json(value):
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def copy_public_tree(source, destination):
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if path.is_file() and not path.is_symlink() and not any(p.startswith(".") or p == "__pycache__" for p in relative.parts):
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def size(path):
    return f"{path.stat().st_size / 1024:.0f} KB" if path.is_file() else "—"


def build(root=ROOT, output=None):
    output = Path(output) if output else root / "build/site"
    if output.resolve() == root.resolve() or output.resolve() in (root / "src", root / "examples"):
        raise ValueError("网站输出必须使用独立目录。")
    if output.exists() and any(output.iterdir()):
        # 只清理此前生成的网站目录，避免误删其他内容。
        if not (output / "build-info.json").is_file():
            raise ValueError(f"输出目录不为空，也不是此前生成的网站：{output}")
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    data = build_showcase.collect(root)
    copy_public_tree(root / "examples", output / "examples")
    # 旧版集合页的地址可能已被分享，在网站中转到新的全部实验页。
    (output / "examples/index.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>DARWIN</title>'
        '<meta http-equiv="refresh" content="0;url=../cases/">'
        '<script>location.replace("../cases/" + location.hash)</script><a href="../cases/">All experiments</a>', encoding="utf-8")
    copy_public_tree(root / "src/rsi_anything/templates", output / "src/rsi_anything/templates")
    for name in PUBLIC_DOCS:
        (output / "docs").mkdir(exist_ok=True)
        shutil.copy2(root / "docs" / name, output / "docs" / name)
    for name in ("README.md", "README.zh-CN.md", "LICENSE"):
        shutil.copy2(root / name, output / name)
    (output / "dist").mkdir()
    # 源码包含内部开发文档，网站只提供 wheel。
    shutil.copy2(root / "dist" / WHEEL, output / "dist" / WHEEL)
    copy_public_tree(root / "web/assets", output / "assets")

    labs = {}
    (output / "downloads").mkdir()
    for domain in data["domains"]:
        for case in domain["cases"]:
            if case["template"] not in CASES:
                continue
            labs[case["template"]] = result = case_data(root, case, domain)
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
    catalog = compact_catalog(data)
    totals = {"__N_DOMAINS__": str(len(data["domains"])),
              "__N_COMPLETE__": str(sum(d["state"] == "complete" for d in data["domains"])),
              "__N_TEMPLATES__": str(sum(len(d["cases"]) for d in data["domains"]))}
    public_docs = ["README.md", "README.zh-CN.md", *("docs/" + n for n in PUBLIC_DOCS),
                   *(p.relative_to(output).as_posix() for p in output.glob("examples/**/*.md")),
                   *(p.relative_to(output).as_posix() for pattern in ("README*.md", "THIRD_PARTY*.md")
                     for p in output.glob("src/rsi_anything/templates/*/" + pattern))]
    template = (root / "web/page.html").read_text(encoding="utf-8")
    missing = set()
    sitemap = []
    for lang, prefix in LANGS.items():
        strings = json.loads((root / f"web/i18n/{lang}.json").read_text(encoding="utf-8"))
        lang_labs = {name: site_i18n.localize(value, lang, missing if lang == "en" else None) for name, value in labs.items()}
        lang_catalog = site_i18n.localize(catalog, lang, missing if lang == "en" else None)
        if lang == "en":
            lang_catalog = english_catalog_docs(lang_catalog, output)
        (output / "data" / lang).mkdir(parents=True)
        for name, value in lang_labs.items():
            (output / "data" / lang / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        (output / "data" / lang / "cases.json").write_text(json.dumps(lang_catalog, ensure_ascii=False), encoding="utf-8")
        script_strings = inline_json({**strings, "public_docs": public_docs})
        for route, kind in PAGES.items():
            alt_lang = "zh" if lang == "en" else "en"
            depth = len(Path(prefix + route).parts)
            base = "../" * depth or "./"
            home = "../" * len(Path(route).parts) or "./"
            alt = base + LANGS[alt_lang] + route
            content = (root / "web" / (kind + ".html")).read_text(encoding="utf-8")
            page = template.replace("__CONTENT__", content)
            page = fill(page, strings)
            replacements = {
                "__TITLE__": html.escape(strings["titles"][kind]), "__PAGE__": kind,
                "__CANONICAL__": SITE_URL + prefix + route, "__URL_EN__": SITE_URL + route, "__URL_ZH__": SITE_URL + "zh/" + route,
                "__SITE_URL__": SITE_URL, "__ALT__": alt, "__WHEEL__": WHEEL,
                "__WHEEL_URL__": SITE_URL + "dist/" + WHEEL, "__WHEEL_SIZE__": size(root / "dist" / WHEEL),
                "__EXPERIMENT_LOG__": experiment_log(lang_catalog, strings) if kind == "home" else "",
                "__HOME_DATA__": inline_json(home_data(lang_labs, strings, root)) if kind == "home" else "",
                "__JS_STRINGS__": script_strings, **totals}
            for key, value in replacements.items():
                page = page.replace(key, value)
            page = page.replace("__HOME__", home).replace("__BASE__", base)
            target = output / prefix / route
            target.mkdir(parents=True, exist_ok=True)
            (target / "index.html").write_text(page, encoding="utf-8")
            sitemap.append(SITE_URL + prefix + route)
    if missing:
        raise ValueError("以下实验记录缺少英文译文，请补充 web/i18n/records.en.json：\n" + "\n".join(sorted(missing)[:20]))
    (output / "404.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Page not found · DARWIN</title><link rel="stylesheet" href="/darwin/assets/site.css">'
        '<body class="not-found"><main class="wrap"><p class="eyebrow">404</p><h1>This page left no record.</h1>'
        '<p class="lede">这个页面没有留下记录。</p><p><a class="btn btn-primary" href="/darwin/">DARWIN →</a> '
        '<a class="btn btn-ghost" href="/darwin/zh/">中文首页 →</a></p></main></body></html>', encoding="utf-8")
    (output / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")
    (output / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                        + "".join(f"<url><loc>{u}</loc></url>\n" for u in sitemap) + "</urlset>\n", encoding="utf-8")
    (output / "build-info.json").write_text(json.dumps({"domains": int(totals["__N_DOMAINS__"]), "complete": int(totals["__N_COMPLETE__"]),
                                                        "cases": list(CASES), "languages": list(LANGS), "source": "已保存的正式运行",
                                                        "generated_at": data["generated_at"]}, ensure_ascii=False), encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    path = build(output=args.output)
    print(f"网站已生成：{path}")
