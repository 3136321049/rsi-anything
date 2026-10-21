#!/usr/bin/env python3
"""Frozen Feynman and ATS judge."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    rubric = json.loads((ROOT / "rubric.yaml").read_text(encoding="utf-8"))
    packet = (ROOT / "packet.md").read_text(encoding="utf-8") if (ROOT / "packet.md").exists() else ""
    job = (ROOT / "job.txt").read_text(encoding="utf-8").lower()
    keywords = re.findall(r"[a-z][a-z0-9+.#]{2,}", job)
    required = rubric["profiles"]["feynman"]["required"]
    missing = [name for name in required if name.lower() not in packet.lower()]
    fluff = [word for word in rubric["profiles"]["feynman"]["banned"] if word.lower() in packet.lower()]
    overlap = sorted({word for word in keywords if word in packet.lower()})
    quantified = len(re.findall(r"\d", packet))
    violations = []
    if missing:
        violations.append("Feynman gaps: " + ", ".join(missing))
    if fluff:
        violations.append("jargon smugness: " + ", ".join(fluff))
    if "objective:" in packet.lower():
        violations.append("resume still has an objective statement")
    if "backend" not in packet.lower():
        violations.append("target role not named")
    feynman = max(0, 50 - 10 * len(missing) - 8 * len(fluff))
    ats = min(20, 4 * len(overlap)) + min(15, quantified) + (15 if "backend" in packet.lower() else 0)
    score = round(feynman + min(50, ats), 1)
    if violations:
        score = min(score, 70.0)
    print(json.dumps({
        "score": score,
        "passed_gates": not violations and score >= 90,
        "summary": f"{score}/100 overlap={len(overlap)} feynman_gaps={len(missing)}",
        "critique": {"violations": violations, "keyword_hits": overlap,
                     "suggestions": ["Restate the idea without 'obviously', then quantify one resume bullet per keyword."]},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
