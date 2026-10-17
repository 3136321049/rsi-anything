#!/usr/bin/env python3
"""Frozen accuracy judge for solution.predict. Stdlib only."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _predict():
    spec = importlib.util.spec_from_file_location("solution", ROOT / "solution.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.predict


def main():
    predict = _predict()
    rows = [json.loads(line) for line in (ROOT / "data" / "dev.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    correct, misses = 0, []
    for row in rows:
        guess = predict(row["text"])
        if guess == row["label"]:
            correct += 1
        else:
            misses.append({"text": row["text"], "expected": row["label"], "got": guess})
    score = round(correct / len(rows), 4) if rows else 0.0
    print(json.dumps({
        "score": score,
        "passed_gates": score >= 0.9 and not any(not isinstance(predict(row["text"]), str) for row in rows),
        "summary": f"accuracy {score:.3f} ({correct}/{len(rows)})",
        "critique": {"misses": misses, "suggestions": ["Separate defect words from metric words such as 'error bars'."]},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
