#!/usr/bin/env python3
"""网站双语：收集实验记录中要显示的文字，并在构建时套用保存的译文。"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "web/i18n"
LANGS = ("en", "zh")
CJK = re.compile(r"[\u3400-\u9fff\u3000-\u303f\uff00-\uffef]")
# 只翻译这些字段；文件内容、代码、字幕和路径保持原样。
TEXT_KEYS = {"title", "description", "note", "metric", "unit", "category", "resource_exception_label",
             "exception_label", "goal", "reasons", "invalid_reason", "stop_reason", "hypothesis", "feedback", "preparation"}

# 模板化说明直接按规则翻译，避免每个数字组合都进译文表。
PATTERNS = {
    "en": [
        (re.compile(r"^分数从 ([\d.\-]+) 提高到 ([\d.\-]+)。(?:两两比较获胜 (\d+/\d+)。)?$"),
         lambda m, tr: f"Score rose from {m[1]} to {m[2]}." + (f" Won {m[3]} head-to-head comparisons." if m[3] else "")),
        (re.compile(r"^未通过必需检查：(.*)$"),
         lambda m, tr: "Failed required checks: " + ", ".join(tr(gate.strip()) for gate in re.split(r"[,，、]", m[1]))),
    ],
    "zh": [],
}


def needs(text, lang):
    """该语言页面是否需要译文：英文页翻译含中文的文字，中文页翻译纯英文说明。"""
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
        if not needs(text, lang):
            return text
        for pattern, render in PATTERNS[lang]:
            match = pattern.match(text)
            if match:
                return render(match, translate)
        if text in table:
            return table[text]
        if missing is not None:
            missing.add(text)
        return text
    return translate


def localize(data, lang, missing=None):
    return walk(data, translator(lang, missing=missing))


def sources(root=ROOT):
    """网站实际展示的实验数据：案例集合和三个实验室页。"""
    import sys
    sys.path.insert(0, str(root / "scripts"))
    import build_showcase
    data = build_showcase.collect(root)
    extra = [json.loads((root / "examples/video-cut/inputs/public-speech/source.json").read_text(encoding="utf-8"))]
    return [data, *extra]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--missing", choices=LANGS, help="列出该语言缺少译文的文字（JSON）")
    args = parser.parse_args()
    lang = args.missing or "en"
    missing = set()
    for item in sources():
        localize(item, lang, missing)
    print(json.dumps(sorted(missing), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
