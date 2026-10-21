"""Cheap, deterministic checks that catch degenerate text before any model sees it.

Optimizers that are scored by LLMs drift toward padding, keyword stuffing,
placeholders and lines addressed to the evaluator. These rules (repetition
thresholds adapted from the Gopher data-cleaning heuristics) reject that
without spending a model call. Thresholds are deliberately loose: normal
prose should never trip them.

Usable from your own command judges:

    from rsi_anything.degenerate import check
    gates, problems = check(text)
"""
from __future__ import annotations

import re
import zlib
from collections import Counter

_CJK = re.compile(r"[一-鿿]")
_PLACEHOLDER = re.compile(r"lorem ipsum|\bTODO\b|\bTBD\b|待补充|此处填写|\bx{3,}\b|\[placeholder\]", re.I)
_EVALUATOR = re.compile(
    r"ignore (?:all |the )?(?:previous|above|prior) (?:instructions|rules|criteria)"
    r"|note to the (?:evaluator|judge|grader)|as an ai (?:evaluator|judge)|you are (?:the|an) (?:evaluator|judge|grader)"
    r"|(?:score|rating|grade)\s*[:=]?\s*(?:10\s*/\s*10|100\s*/\s*100|maximum|full marks)"
    r"|忽略(?:以上|上述|之前|前面)|给(?:评审|评委|裁判)|你是(?:评审|评委|裁判)|(?:评分|打分|得分)\s*[:：]?\s*(?:10\s*/\s*10|满分|100\s*分)"
    r"|</?(?:system|ARTIFACT_|A_|B_)",
    re.I,
)
_OPENER_ONLY = re.compile(r"^\s*(?:thought process|let'?s (?:solve|think)[^\n]*|思考过程|让我们一步步)\s*[:：.。]?\s*$", re.I)


def _units(text: str) -> list[str]:
    """Words for alphabetic text, single characters for CJK text."""
    if len(_CJK.findall(text)) > len(text) * 0.2:
        return [c for c in text if not c.isspace()]
    return re.findall(r"\w+", text.lower())


def _top_ngram_share(units: list[str], n: int) -> float:
    if len(units) < n * 4:
        return 0.0
    grams = Counter(tuple(units[i:i + n]) for i in range(len(units) - n + 1))
    gram, count = grams.most_common(1)[0]
    if count < 3:
        return 0.0
    return min(1.0, count * sum(len(u) for u in gram) / max(1, sum(len(u) for u in units)))


def check(text: str, min_chars: int = 20) -> tuple[dict[str, bool], list[str]]:
    problems: list[str] = []
    body = text.strip()
    lines = [line.strip() for line in body.splitlines() if line.strip()]

    substance = len(re.sub(r"[#>*\-\s|`_]+", "", body)) >= min_chars and not _OPENER_ONLY.match(body)
    if not substance:
        problems.append("too little actual content")

    repetitive = False
    if len(lines) >= 4:
        counts = Counter(lines)
        dup_lines = sum(c for c in counts.values() if c > 1)
        dup_chars = sum(len(line) * c for line, c in counts.items() if c > 1)
        if dup_lines / len(lines) > 0.30 or dup_chars / max(1, sum(len(l) for l in lines)) > 0.20:
            repetitive = True
            problems.append("many repeated lines")
    units = _units(body)
    cjk = len(_CJK.findall(body)) > len(body) * 0.2
    for n, limit in ((2, 0.20), (3, 0.18), (4, 0.16)) if not cjk else ((4, 0.20), (6, 0.18), (8, 0.16)):
        share = _top_ngram_share(units, n)
        if share > limit:
            repetitive = True
            problems.append(f"one phrase fills {share:.0%} of the text")
            break
    raw = body.encode("utf-8")
    if len(raw) > 400 and len(zlib.compress(raw, 9)) / len(raw) < 0.18:
        repetitive = True
        problems.append("text compresses like padding")

    placeholder = _PLACEHOLDER.search(body)
    if placeholder:
        problems.append(f"placeholder text: {placeholder.group(0)!r}")
    address = _EVALUATOR.search(body)
    if address:
        problems.append(f"addresses the evaluator: {address.group(0)!r}")

    gates = {
        "substance": substance,
        "not_repetitive": not repetitive,
        "no_placeholder": placeholder is None,
        "no_evaluator_address": address is None,
    }
    return gates, problems
