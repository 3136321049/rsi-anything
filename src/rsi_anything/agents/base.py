from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AgentResult:
    ok: bool
    text: str = ""
    hypothesis: str = ""
    seconds: float = 0.0
    cost_usd: Optional[float] = None
    error: str = ""


class Agent:
    name = "agent"
    artifact: list[str] = []  # set by the engine; agents that write files themselves respect it

    def run(self, workdir: Path, prompt: str, round_dir: Path, timeout: int) -> AgentResult:
        raise NotImplementedError


def hypothesis_from(text: str) -> str:
    """The agent is asked to end with `HYPOTHESIS: ...`; fall back to its last non-empty line."""
    found = re.findall(r"HYPOTHESIS\s*[:：]\s*(.+)", text)
    if found:
        return found[-1].strip()[:300]
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    return (lines[-1] if lines else "")[:300]
