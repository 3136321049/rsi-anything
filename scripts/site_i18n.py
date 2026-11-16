#!/usr/bin/env python3
"""Bilingual site: collect the experiment-record text the pages show, and apply the saved translations at build time."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "web/i18n"
LANGS = ("en", "zh")
CJK = re.compile(r"[\u3400-\u9fff\u3000-\u303f\uff00-\uffef]")
# Only these fields are translated; file contents, code, subtitles and paths stay as they are.
TEXT_KEYS = {"title", "description", "note", "metric", "unit", "category", "resource_exception_label",
             "exception_label", "goal", "reasons", "invalid_reason", "stop_reason", "hypothesis", "feedback", "preparation"}

# Templated notes (see build_showcase.human_note) are translated by rule, so not every number combination needs a table entry.
# Patterns run before the table lookup, also on mixed text such as English notes that list Chinese gate names.
PATTERNS = {
    "en": [
        (re.compile(r"^Failed required checks: (.*)$"),
         lambda m, tr: "Failed required checks: " + ", ".join(tr(gate.strip()) for gate in re.split(r"[,，、]", m[1]))),
    ],
    "zh": [
        (re.compile(r"^Score rose from ([\d.\-]+) to ([\d.\-]+)\.(?: Won (\d+/\d+) head-to-head comparisons\.)?$"),
         lambda m, tr: f"分数从 {m[1]} 提高到 {m[2]}。" + (f"两两比较获胜 {m[3]}。" if m[3] else "")),
        (re.compile(r"^Tied with the best version at ([\d.\-]+); won the head-to-head in both orders, (\d+/\d+)\.$"),
         lambda m, tr: f"与当前最好版本同分（{m[1]}），正反并排比较获胜 {m[2]}。"),
        (re.compile(r"^Tied with the best version at ([\d.\-]+); lost the head-to-head \((\d+/\d+)\)\.$"),
         lambda m, tr: f"与当前最好版本同分（{m[1]}），正反并排比较没有获胜（{m[2]}）。"),
        (re.compile(r"^Failed required checks: (.*)$"),
         lambda m, tr: "未通过必需检查：" + m[1]),
    ],
}


def needs(text, lang):
    """Whether a page in this language needs a translation: English pages translate text containing Chinese; Chinese pages translate pure-English text."""
    if not isinstance(text, str) or not text.strip():
        return False
    has_cjk = bool(CJK.search(text))
    return has_cjk if lang == "en" else (not has_cjk and bool(re.search(r"[A-Za-z]{3}", text)))


def walk(value, visit, key=None):
    if isinstance(value, dict):
        return {k: walk(v, visit, k) for k, v in value.items()}
    if isinstance(value, list):
        return [walk(v, visit, key) for v in value]
    if isinstance(value, str) and key in TEXT_KEYS:
        return visit(value)
    return value


def load(lang):
    path = I18N / f"records.{lang}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def translator(lang, table=None, missing=None):
    table = load(lang) if table is None else table

    def translate(text):
        if not isinstance(text, str) or not text.strip():
            return text
        for pattern, render in PATTERNS[lang]:
            match = pattern.match(text)
            if match:
                return render(match, translate)
        if not needs(text, lang):
            return text
        if text in table:
            return table[text]
        if missing is not None:
            missing.add(text)
        return text
    return translate


def localize(data, lang, missing=None):
    return walk(data, translator(lang, missing=missing))


def sources(root=ROOT):
    """The experiment data the site actually shows: the case catalog and the lab pages."""
    import sys
    sys.path.insert(0, str(root / "scripts"))
    import build_showcase
    data = build_showcase.collect(root)
    extra = [json.loads((root / "examples/video-cut/inputs/public-speech/source.json").read_text(encoding="utf-8"))]
    return [data, *extra]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--missing", choices=LANGS, help="list the text that has no translation for this language (JSON)")
    args = parser.parse_args()
    lang = args.missing or "en"
    missing = set()
    for item in sources():
        localize(item, lang, missing)
    print(json.dumps(sorted(missing), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
