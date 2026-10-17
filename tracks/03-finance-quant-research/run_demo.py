#!/usr/bin/env python3
"""Replay the finance research ratchet and write the ledger artifacts."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

for candidate in [
    Path(os.environ["RSI_ENGINE"]) if os.environ.get("RSI_ENGINE") else None,
    Path("/tmp/rsi-candidates/grok47"),
    ROOT.parents[2],
]:
    if candidate and (candidate / "core" / "controller.py").exists():
        sys.path.insert(0, str(candidate))
        break
else:
    raise SystemExit("ratchet engine not found; set RSI_ENGINE to the core checkout")

from core.controller import run_ratchet_loop  # noqa: E402
from demo_steps import steps  # noqa: E402
from eval_report import audit  # noqa: E402

EXPECTED = {
    "v1_baseline.md": (58.0, False),
    "v2_competitor_table.md": (72.5, True),
    "v3_hallucinated_source.md": (64.5, False),
    "v4_bear_case_bom.md": (84.0, True),
    "v6_champion.md": (94.5, True),
}
STATUSES = ["BASELINE", "KEEP", "REVERT_SCORE", "KEEP", "REVERT_GUARD", "KEEP"]


def _reset():
    (ROOT / "report.md").write_text((ROOT / "drafts" / "v1_baseline.md").read_text(encoding="utf-8"), encoding="utf-8")
    for rel in ("results.tsv", ".rsi/lessons.md"):
        path = ROOT / rel
        if path.exists():
            path.unlink()
    critiques = ROOT / "critiques"
    critiques.mkdir(exist_ok=True)
    for child in critiques.glob("*.json"):
        child.unlink()


def _check_drafts():
    for name, (score, passed) in EXPECTED.items():
        result = audit((ROOT / "drafts" / name).read_text(encoding="utf-8"))
        if result["score"] != score or result["passed_gates"] is not passed:
            raise SystemExit(f"{name} scored {result['score']} gates={result['passed_gates']}, expected {score}/{passed}")


def _summary(result: dict):
    lines = ["# Ratchet summary — 人形机器人核心零部件深度研报", ""]
    lines.append(f"**Best score: {result['best_score']} / target 92.0 / reached: {result['target_reached']}**")
    lines.append("")
    lines.append("| Round | Status | Score | Best |")
    lines.append("|---:|---|---:|---:|")
    rows = (ROOT / "results.tsv").read_text(encoding="utf-8").splitlines()[1:]
    chart = ["```text"]
    for row in rows:
        cols = row.split("\t")
        score, best, status = float(cols[3]), float(cols[4]), cols[5]
        lines.append(f"| {cols[0]} | {status} | {score:.1f} | {best:.1f} |")
        filled = max(1, round(score / 100 * 32))
        chart.append(f"R{cols[0]:>2} {status:<12} {score:6.1f} {'█' * filled}")
    chart.append("```")
    lines.extend(["", *chart, "", "Round 0 is the 58-point draft. Round 2 is the fake-source revert.",
                  "Round 4 never reaches the judge: the frozen rubric hash changed, so both the rubric and the candidate report are restored.",
                  "", "---",
                  "Upstream inspiration: karpathy/autoresearch · stanford-oval/storm · assafelovic/gpt-researcher · Future-House/paper-qa"])
    (ROOT / "ratchet_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    _check_drafts()
    rubric_hash = hashlib.sha256((ROOT / "rubric.yaml").read_bytes()).hexdigest()
    _reset()
    result = run_ratchet_loop(ROOT, steps=steps())
    guard = {
        "score": None,
        "passed_gates": False,
        "summary": "REVERT_GUARD before evaluation: frozen rubric.yaml was modified",
        "critique": {
            "status": "REVERT_GUARD",
            "violations": ["frozen path modified: rubric.yaml"],
            "suggestions": ["不要修改 eval_report.py、rubric.yaml 或 sources/verified_sources.json。"],
        },
    }
    (ROOT / "critiques" / "critique_r5.json").write_text(
        json.dumps(guard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _summary(result)
    statuses = [row.split("\t")[5] for row in (ROOT / "results.tsv").read_text(encoding="utf-8").splitlines()[1:]]
    champion = (ROOT / "drafts" / "v6_champion.md").read_text(encoding="utf-8")
    if statuses != STATUSES:
        raise SystemExit(f"unexpected statuses: {statuses}")
    if result["best_score"] != 94.5 or not result["target_reached"]:
        raise SystemExit(f"ratchet stopped at {result['best_score']}")
    if (ROOT / "report.md").read_text(encoding="utf-8") != champion:
        raise SystemExit("champion report was not kept")
    if hashlib.sha256((ROOT / "rubric.yaml").read_bytes()).hexdigest() != rubric_hash:
        raise SystemExit("frozen rubric was not restored")
    missing = [f"critique_r{n}.json" for n in range(1, 7) if not (ROOT / "critiques" / f"critique_r{n}.json").exists()]
    if missing:
        raise SystemExit("missing critiques: " + ", ".join(missing))
    print(f"best={result['best_score']} target_reached={result['target_reached']}")
    print((ROOT / "ratchet_summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
