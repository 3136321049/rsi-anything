"""Run events: one stream that the terminal, the run folder and a live view can all follow.

The engine emits plain dicts (`{"type": ..., "time": ..., ...}`); sinks decide
what to do with them. Every run writes `events.jsonl` next to its ledger, so a
viewer can follow a run as it happens instead of re-reading files afterwards.

Types: run_started, round_started, agent_finished, judged, round_finished,
run_finished, run_failed.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Protocol

from .domain import BASELINE, KEEP, now


class EventSink(Protocol):
    def emit(self, event: dict[str, Any]) -> None: ...


class Broadcast:
    def __init__(self, sinks: Iterable[EventSink] = ()):
        self.sinks = list(sinks)

    def emit(self, kind: str, **data: Any) -> None:
        event = {"type": kind, "time": now(), **data}
        for sink in self.sinks:
            sink.emit(event)


class JsonlSink:
    """Append each event as one JSON line, flushed at once so readers see it live."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def emit(self, event: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
            stream.flush()


class TerminalLog:
    """The human-readable progress lines `rsi run` prints."""

    def __init__(self, log: Callable[[str], None]):
        self.log = log

    def emit(self, event: dict[str, Any]) -> None:
        line = terminal_line(event)
        if line is not None:
            self.log(line)


def row_line(row: dict[str, Any]) -> str:
    score = "" if row.get("score") is None else f"score {row['score']:g}  "
    detail = (row.get("hypothesis") or "")[:90] if row["status"] == KEEP else (row.get("note") or row.get("hypothesis") or "")[:110]
    return f"r{row['round']}  {row['status']:<10} {score}{detail}"


def terminal_line(event: dict[str, Any]) -> Optional[str]:
    kind = event["type"]
    if kind == "run_started":
        return f"run {event['run_id']}  branch {event['branch']}  agent {event['agent']}"
    if kind == "round_started":
        return f"r{event['round']}  {event['agent']} is working..."
    if kind == "round_finished":
        row = event["row"]
        if row["status"] != BASELINE:
            return row_line(row)
        failed = [name for name, good in (row.get("gates") or {}).items() if not good]
        return f"r0  BASELINE  score {row['score']:g}" + (f"  failed gates: {', '.join(failed)}" if failed else "")
    return None


def read(path: Path) -> list[dict[str, Any]]:
    """Events recorded so far; a half-written last line (a run still writing) is skipped."""
    path = Path(path)
    if not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    return events
