from __future__ import annotations
import json
import re
from pathlib import Path

_BANNED = ["众所周知", "未来可期", "不言而喻", "毫无疑问", "前景广阔",
           "obviously", "game-changing", "revolutionary", "unprecedented"]

def induce_rubric(domain: str, topic: str, output_path: Path | None = None) -> dict:
    rubric = {
        "domain": domain, "topic": topic,
        "hard_gates": {
            "citation_tag": "[SRC-", "min_citations": 3,
            "required_sections": ["Executive Summary", "Bear Case", "Sources"],
            "require_table": True, "share_headers": ["占比", "份额", "share"],
            "share_tolerance": 1.0, "banned_fluff": list(_BANNED),
        },
        "weights": {"evidence": 30, "analysis": 25, "bear_case": 20, "structure": 15, "clarity": 10},
    }
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(rubric, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rubric

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

def _share_violation(md_text: str, gates: dict) -> str:
    tolerance = float(gates.get("share_tolerance", 1.0))
    for header, rows in _tables(md_text):
        for col, name in enumerate(header):
            if not any(token.lower() in name.lower() for token in gates.get("share_headers") or []):
                continue
            nums = [float(match.group(1)) for row in rows if col < len(row)
                    and (match := re.search(r"(-?\d+(?:\.\d+)?)\s*%", row[col]))]
            if len(nums) >= 2 and abs(sum(nums) - 100) > tolerance:
                return f"share column '{name}' sums to {sum(nums):.1f}, not 100"
    return ""

def evaluate_markdown_with_rubric(md_text: str, rubric: dict) -> dict:
    gates, violations, suggestions = rubric.get("hard_gates", {}), [], []
    minimum = int(gates.get("min_citations", 1))
    citations = len(re.findall(r"\[SRC-[^\]]+\]", md_text))
    sections = gates.get("required_sections", ["Bear Case"])
    missing = [name for name in sections if not re.search(rf"^#+\s+{re.escape(name)}\s*$", md_text, re.I | re.M)]
    fluff = [word for word in gates.get("banned_fluff", []) if word.lower() in md_text.lower()]
    tables = _tables(md_text)
    if citations < minimum:
        violations.append(f"need at least {minimum} [SRC- citations, found {citations}")
        suggestions.append("Attach a verifiable [SRC-] tag to every material claim.")
    if missing:
        violations.append("missing sections: " + ", ".join(missing))
        suggestions.append("Add every required section, including a Bear Case.")
    if gates.get("require_table", True) and not tables:
        violations.append("missing markdown table")
        suggestions.append("Add a comparison table with sources and figures.")
    if fluff:
        violations.append("banned fluff: " + ", ".join(fluff))
        suggestions.append("Replace promotional wording with a measured, falsifiable claim.")
    if share := _share_violation(md_text, gates):
        violations.append(share)
        suggestions.append("Make share/占比 columns sum to 100 before citing them.")
    words = len(md_text.split())
    earned = {
        "evidence": min(1, citations / max(1, minimum)),
        "analysis": min(1, words / 350),
        "bear_case": 0 if any("bear case" in name.lower() for name in missing) else 1,
        "structure": max(0, 1 - len(missing) / max(1, len(sections))),
        "clarity": 1 if words >= 80 and not fluff else 0.5,
    }
    weights = rubric.get("weights", {})
    breakdown = {key: round(float(weights.get(key, 0)) * value, 1) for key, value in earned.items()}
    score = round(sum(breakdown.values()), 1)
    if violations:
        score = min(score, 69.0)
    return {"score": score, "passed_gates": not violations, "violations": violations,
            "suggestions": suggestions, "breakdown": breakdown}
