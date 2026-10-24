"""运行 `python example.py` 查看月度账单及三人分账。"""
import json
from pathlib import Path

from expense import amount_to_cents, monthly_totals, split_bill


def build_example():
    entries = json.loads(Path("judge/sample.json").read_text(encoding="utf-8"))
    return {"month": "2026-10", "totals_cents": monthly_totals(entries, "2026-10"),
            "dinner_split_cents": split_bill(amount_to_cents("100.00"), 3)}


if __name__ == "__main__":
    print(json.dumps(build_example(), ensure_ascii=False, indent=2))
