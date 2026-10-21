#!/usr/bin/env python3
"""Frozen redline and PRISMA judge."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    ledger = json.loads((ROOT / "statutes.json").read_text(encoding="utf-8"))
    memo = (ROOT / "memo.md").read_text(encoding="utf-8") if (ROOT / "memo.md").exists() else ""
    statute_ids = re.findall(r"\[STATUTE-([A-Za-z0-9-]+)\]", memo)
    bad_statutes = [item for item in statute_ids if item not in ledger["statutes"]]
    pmids = re.findall(r"PMID[:\s]*([0-9]{4,8})", memo)
    bad_pmids = [item for item in pmids if item not in ledger["pmids"]]
    attacks = []
    if re.search(r"unlimited", memo, re.I):
        attacks.append("unlimited liability still present")
    if re.search(r"no cap", memo, re.I):
        attacks.append("penalty has no cap")
    if re.search(r"terminate at will", memo, re.I):
        attacks.append("one-sided termination")
    sections = ["Question", "Eligibility", "Search", "Bias", "Limitation"]
    missing = [name for name in sections if not re.search(rf"^#+\s+{name}\s*$", memo, re.M)]
    violations = []
    if bad_statutes:
        violations.append("unknown statutes: " + ", ".join(bad_statutes))
    if bad_pmids:
        violations.append("unknown PMIDs: " + ", ".join(bad_pmids))
    if attacks:
        violations.append("open attacks: " + "; ".join(attacks))
    if missing:
        violations.append("PRISMA sections missing: " + ", ".join(missing))
    redline = 50 - 10 * len(bad_statutes) - 8 * len(attacks)
    prisma = 50 - 8 * len(missing) - 10 * len(bad_pmids)
    score = round(max(0, redline) + max(0, prisma), 1)
    if violations:
        score = min(score, 70.0)
    print(json.dumps({
        "score": score,
        "passed_gates": not violations,
        "summary": f"{score}/100 attacks={len(attacks)} bad_ids={len(bad_statutes) + len(bad_pmids)}",
        "critique": {"violations": violations, "suggestions": ["Cite only ledger ids and close each one-sided clause."]},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
