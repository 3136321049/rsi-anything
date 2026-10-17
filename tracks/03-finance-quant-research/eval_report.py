#!/usr/bin/env python3
"""Frozen rubric auditor for the humanoid-component research report."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BANNED_HEADING = "## 看空逻辑与核心风险 (Bear Case)"


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _tables(md_text: str):
    lines, index, found = md_text.splitlines(), 0, []
    while index < len(lines):
        if lines[index].lstrip().startswith("|") and index + 1 < len(lines) and "---" in lines[index + 1]:
            header, index = _cells(lines[index]), index + 2
            rows = []
            while index < len(lines) and lines[index].lstrip().startswith("|"):
                rows.append(_cells(lines[index]))
                index += 1
            found.append((header, rows))
        else:
            index += 1
    return found


def _load():
    rubric = json.loads((ROOT / "rubric.yaml").read_text(encoding="utf-8"))
    catalog = json.loads((ROOT / "sources" / "verified_sources.json").read_text(encoding="utf-8"))
    known = {item["id"] for item in catalog["sources"]}
    return rubric, known


def _citations(md_text: str, known: set[str]):
    ordered = list(dict.fromkeys(re.findall(r"\[(SRC-\d+)\]", md_text)))
    verified = [item for item in ordered if item in known]
    unknown = [item for item in ordered if item not in known]
    return verified, unknown


def _bear_body(md_text: str, heading: str) -> str:
    start = md_text.find(heading)
    if start < 0:
        return ""
    rest = md_text[start + len(heading):]
    nxt = re.search(r"\n## ", rest)
    return rest[: nxt.start()] if nxt else rest


def _competitor(md_text: str, gates: dict) -> bool:
    needed = gates.get("competitor_headers", [])
    minimum = int(gates.get("competitor_min_rows", 1))
    for header, rows in _tables(md_text):
        blob = " ".join(header)
        if all(token in blob for token in needed) and len(rows) >= minimum:
            return True
    return False


def _share_ok(md_text: str, gates: dict) -> bool:
    tolerance = float(gates.get("share_tolerance", 1.0))
    checked = 0
    for header, rows in _tables(md_text):
        for col, name in enumerate(header):
            if not any(token in name for token in gates.get("share_headers", [])):
                continue
            nums = [float(match.group(1)) for row in rows if col < len(row)
                    and (match := re.search(r"(-?\d+(?:\.\d+)?)\s*%", row[col]))]
            if len(nums) >= 2:
                checked += 1
                if abs(sum(nums) - 100) > tolerance:
                    return False
    return checked > 0


def _fires(token: str, ctx: dict, signals: dict) -> bool:
    checks = {
        "always": True,
        "bear_heading": ctx["bear"],
        "bear_deep": ctx["bear_len"] >= int(signals["bear_min_chars"]),
        "triggers3": ctx["triggers"] >= int(signals["trigger_min"]),
        "verified3": ctx["verified"] >= 3,
        "verified12_clean": ctx["verified"] >= 12 and ctx["unknown"] == 0,
        "unknown": ctx["unknown"] >= 1,
        "bom_clean": ctx["bom"] and ctx["verified"] >= int(signals["bom_min_citations"]) and ctx["unknown"] == 0,
        "cites15_clean": ctx["verified"] >= int(signals["full_citations"]) and ctx["unknown"] == 0,
        "comp_table": ctx["comp"],
        "sensitivity": ctx["sens"],
        "scenarios": ctx["scenarios"],
        "channel_check": signals["channel_phrase"] in ctx["text"],
        "cross_foot": signals["cross_phrase"] in ctx["text"],
        "position_limit": signals["position_phrase"] in ctx["text"],
    }
    if token not in checks:
        raise KeyError(f"unknown rubric rule: {token}")
    return bool(checks[token])


def _fmt(value: float) -> str:
    text = f"{value:.1f}"
    return text[:-2] if text.endswith(".0") else text


def audit(md_text: str) -> dict:
    rubric, known = _load()
    gates, signals = rubric["hard_gates"], rubric["signals"]
    heading = gates.get("bear_heading", BANNED_HEADING)
    verified, unknown = _citations(md_text, known)
    fluff = [phrase for phrase in gates.get("banned_phrases", []) if phrase in md_text]
    ctx = {
        "text": md_text,
        "verified": len(verified),
        "unknown": len(unknown),
        "unknown_ids": unknown,
        "verified_ids": verified,
        "fluff": fluff,
        "bear": heading in md_text,
        "bear_len": len(_bear_body(md_text, heading).strip()),
        "triggers": md_text.count(signals["trigger_phrase"]),
        "comp": _competitor(md_text, gates),
        "arith": _share_ok(md_text, gates),
        "bom": signals["bom_phrase"] in md_text,
        "sens": signals["sensitivity_phrase"] in md_text,
        "scenarios": signals["optimistic"] in md_text and signals["pessimistic"] in md_text,
    }
    dimensions, suggestions = {}, []
    for dim in rubric["dimensions"]:
        tenths = 0
        for rule in dim["rules"]:
            fired = _fires(rule["when"], ctx, signals)
            if fired:
                tenths += int(round(float(rule["points"]) * 10))
                if rule["points"] < 0 and rule.get("suggestion"):
                    suggestions.append(rule["suggestion"])
            elif rule["points"] > 0 and rule.get("suggestion"):
                suggestions.append(rule["suggestion"])
        cap = int(round(float(dim["weight"]) * 10))
        dimensions[dim["id"]] = {"name": dim["name"], "weight": dim["weight"], "score": max(0, min(cap, tenths)) / 10}
    violations = []
    if ctx["verified"] < int(gates["min_verified_citations"]):
        violations.append(f"已核验引用 {ctx['verified']} 条，少于 {gates['min_verified_citations']} 条。")
    if unknown:
        violations.append("存在未登记引用: " + ", ".join(unknown))
    if len(fluff) > int(gates["max_banned_phrases"]):
        violations.append("出现空话: " + "、".join(fluff))
    if not ctx["bear"]:
        violations.append(f"缺少硬性章节 {heading}")
    if not ctx["comp"]:
        violations.append("缺少同时包含毛利率与产能的竞品对照表。")
    if not ctx["arith"]:
        violations.append("缺少可复核的份额表，或占比/份额列加总不等于100。")
    score = round(sum(item["score"] for item in dimensions.values()), 1)
    summary = f"{_fmt(score)}/100 gates={'PASS' if not violations else 'FAIL'} " + " ".join(
        f"{key}={_fmt(item['score'])}" for key, item in dimensions.items())
    return {
        "score": score,
        "passed_gates": not violations,
        "summary": summary,
        "critique": {
            "dimensions": dimensions,
            "violations": violations,
            "suggestions": list(dict.fromkeys(suggestions)),
            "verified_citations": verified,
            "unknown_citations": unknown,
            "banned_phrases": fluff,
            "bear_chars": ctx["bear_len"],
            "hypothesis": os.environ.get("RSI_HYPOTHESIS", ""),
        },
    }


def main():
    report = ROOT / "report.md"
    if not report.exists():
        result = {"score": 0.0, "passed_gates": False, "summary": "missing report.md", "critique": {"violations": ["missing report.md"]}}
    else:
        result = audit(report.read_text(encoding="utf-8"))
    out = ROOT / "critiques"
    out.mkdir(exist_ok=True)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    (out / "latest_critique.json").write_text(text, encoding="utf-8")
    number = int(os.environ.get("RSI_ROUND", "0")) + 1
    (out / f"critique_r{number}.json").write_text(text, encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
