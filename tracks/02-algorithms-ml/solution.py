"""Weak keyword baseline. The ratchet may replace this file only."""


def predict(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ("null", "error", "exception", "bug")):
        return "defect"
    return "config"
