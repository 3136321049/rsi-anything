#!/usr/bin/env python3
"""Frozen literature-review judge. Reads rubric.yaml with json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    rubric = json.loads((ROOT / "rubric.yaml").read_text(encoding="utf-8"))
    essay = (ROOT / "essay.md").read_text(encoding="utf-8") if (ROOT / "essay.md").exists() else ""
    gates = rubric["hard_gates"]
    missing = [name for name in gates["required_sections"]
               if not re.search(rf"^#+\s+{re.escape(name)}\s*$", essay, re.M)]
    cites = len(set(re.findall(r"\[SRC-[^\]]+\]", essay)))
    fluff = [phrase for phrase in gates["banned_phrases"] if phrase.lower() in essay.lower()]
    violations = []
    if missing:
        violations.append("missing sections: " + ", ".join(missing))
    if cites < gates["min_citations"]:
        violations.append(f"citations {cites} < {gates['min_citations']}")
    if fluff:
        violations.append("banned fluff: " + ", ".join(fluff))
    earned = {
        "question": 25 if "Research Question" not in missing and "?" in essay else 8,
        "map": 25 if "Literature Map" not in missing and cites >= 4 else 6,
        "counter": 20 if "Counterargument" not in missing else 0,
        "evidence": min(15, cites * 2),
        "increment": 15 if "this review" in essay.lower() or "本文" in essay else 4,
    }
    score = round(sum(min(dim["weight"], earned[dim["id"]]) for dim in rubric["dimensions"]), 1)
    if violations:
        score = min(score, 69.0)
    print(json.dumps({
        "score": score,
        "passed_gates": not violations,
        "summary": f"{score}/100 sections_missing={len(missing)} cites={cites}",
        "critique": {"violations": violations, "suggestions": ["Add the four required headings and six [SRC-] tags."]},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
