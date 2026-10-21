"""Helper for command judges written in Python."""
from __future__ import annotations

import json
import os
from typing import Any, Optional


def report_result(score: float, gates: Optional[dict[str, bool]] = None, feedback: str = "",
                  metrics: Optional[dict[str, Any]] = None):
    """Write the verdict where the ratchet expects it (`$RSI_RESULT`); print it when run by hand."""
    payload = {"score": float(score), "gates": gates or {}, "feedback": feedback, "metrics": metrics or {}}
    target = os.environ.get("RSI_RESULT")
    if target:
        with open(target, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False)
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
