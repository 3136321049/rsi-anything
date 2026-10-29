"""Watch a run as it evolves (`rsi watch`, `rsi run --live`) or save it as one shareable page (`rsi share`).

Both read run folders only: `run.json`, `ledger.jsonl`, `events.jsonl` and the
saved snapshots. The watcher serves them on 127.0.0.1 and the page polls; the
shared page carries the same state inline, with images embedded, so it opens
anywhere without a server.

A run that starts from exactly the artifact an earlier run ended with continues
that run's story (say, after the owner changed a rule in rsi.yaml). Such runs are
shown as one timeline, with the contract change marked where the new run begins.
"""
from __future__ import annotations

import base64
import difflib
import json
import mimetypes
import os
import threading
import urllib.parse
import webbrowser
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Optional

from . import events as run_events
from .ledger import STATE_DIR, list_runs

PAGE = Path(__file__).with_name("live.html")
MEDIA = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
TEXT_LIMIT = 8000


def _json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _rows(run: Path) -> list[dict[str, Any]]:
    path = run / "ledger.jsonl"
    rows = []
    for line in (path.read_text(encoding="utf-8").splitlines() if path.exists() else []):
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue  # a row still being written
    return rows


def _snapshot(run: Path, rel: str, artifact: list[str], link: Callable[[Path], str]) -> dict[str, Any]:
    """Images and artifact text saved for one version."""
    folder = run / rel
    files = [item["path"] for item in _json(folder / "manifest.json", {}).get("files", [])]
    images = [f for f in files if Path(f).suffix.lower() in MEDIA]
    rendered = [f for f in images if Path(f).suffix.lower() != ".svg"]  # prefer what the judge saw
    shown = rendered or images
    text = {}
    for name in artifact:
        path = folder / "files" / name
        if path.is_file() and path.suffix.lower() not in MEDIA:
            text[name] = path.read_text(encoding="utf-8", errors="replace")[:TEXT_LIMIT]
    return {"images": [{"name": f, "src": link(folder / "files" / f)} for f in shown], "text": text}


def _artifact_digest(run: Path, snapshot: str, artifact: list[str]) -> dict[str, str]:
    files = _json(run / snapshot / "manifest.json", {}).get("files", [])
    return {f["path"]: f["sha256"] for f in files if f["path"] in artifact}


def lineage(run: Path) -> list[Path]:
    """Earlier runs this one continues (oldest first), ending with `run` itself."""
    run = Path(run)
    artifact = (_json(run / "config" / "execution.json", {}).get("artifact")) or []
    chain = [run]
    while True:
        rows = _rows(chain[0])
        start = _artifact_digest(chain[0], rows[0].get("artifacts", ""), artifact) if rows else {}
        earlier = [other for other in sorted(run.parent.iterdir()) if other.name < chain[0].name and other not in chain
                   and start and _artifact_digest(other, "artifacts/final", artifact) == start]
        if not earlier:
            return chain
        chain.insert(0, earlier[-1])


def _contract_change(before: Path, after: Path) -> list[str]:
    old = (before / "config" / "rsi.yaml").read_text(encoding="utf-8").splitlines() if (before / "config" / "rsi.yaml").exists() else []
    new = (after / "config" / "rsi.yaml").read_text(encoding="utf-8").splitlines() if (after / "config" / "rsi.yaml").exists() else []
    return [line for line in difflib.unified_diff(old, new, lineterm="", n=0)
            if line[:1] in "+-" and not line.startswith(("+++", "---"))][:12]


def state(run: Path, link: Optional[Callable[[Path], str]] = None, follow: bool = True) -> dict[str, Any]:
    """Everything the page shows about a run (and the runs it continues), read from their folders."""
    run = Path(run)
    root = run.parent
    link = link or (lambda path: "files/" + path.relative_to(root).as_posix())
    meta = _json(run / "run.json", {})
    execution = _json(run / "config" / "execution.json", {})
    artifact = execution.get("artifact") or []
    chain = lineage(run) if follow else [run]
    rows, runs = [], []
    for number, folder in enumerate(chain, 1):
        folder_meta = _json(folder / "run.json", {})
        runs.append({"run": number, "run_id": folder_meta.get("run_id", folder.name),
                     "stop_reason": folder_meta.get("stop_reason"),
                     "change": _contract_change(chain[number - 2], folder) if number > 1 else []})
        for row in _rows(folder):
            row["run"] = number
            row["snapshot"] = _snapshot(folder, row.get("artifacts") or "", artifact, link) if row.get("artifacts") else None
            rows.append(row)
    stream = run_events.read(run / "events.jsonl")
    finished = {row["round"] for row in rows if row["run"] == len(chain)}
    active = None
    for event in stream:
        if event["type"] == "round_started" and event["round"] not in finished:
            active = {"round": event["round"], "phase": "agent", "agent": event.get("agent")}
        elif active and event.get("round") == active["round"] and event["type"] in ("agent_finished", "judged"):
            active["phase"] = "judging" if event["type"] == "agent_finished" else "deciding"
    if meta.get("status") in ("finished", "failed", "interrupted"):
        active = None
    return {"run_id": meta.get("run_id", run.name), "contract": meta.get("contract"), "goal": meta.get("goal"),
            "status": meta.get("status"), "stop_reason": meta.get("stop_reason"), "error": meta.get("error"),
            "started": meta.get("started"), "finished": meta.get("finished"), "strategy": meta.get("strategy", "greedy"),
            "agent": (execution.get("agent") or {}).get("resolved_adapter") or meta.get("agent"),
            "model": (execution.get("agent") or {}).get("requested_model"), "jury": execution.get("jury") or meta.get("jury"),
            "direction": (execution.get("judge") or {}).get("direction", "maximize"),
            "budget": execution.get("budget"), "runs": runs, "rows": rows, "active": active, "events": len(stream)}


def latest(repo: Path) -> Optional[Path]:
    runs = list_runs(repo)
    return Path(repo) / STATE_DIR / "runs" / runs[-1] if runs else None


class _Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, resolve: Callable[[], Optional[Path]], **kwargs):
        self.resolve = resolve
        super().__init__(*args, **kwargs)

    def log_message(self, *args):  # keep the terminal for the run's own progress lines
        pass

    def _send(self, status: int, body: bytes, kind: str):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        run = self.resolve()
        if path in ("/", "/index.html"):
            return self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        if path == "/api/state":
            body = state(run) if run else {"status": "waiting", "rows": []}
            return self._send(200, json.dumps(body, ensure_ascii=False, default=str).encode("utf-8"),
                              "application/json; charset=utf-8")
        if path.startswith("/files/") and run:
            runs = run.parent.resolve()  # the run and the earlier runs it continues
            target = (runs / urllib.parse.unquote(path[len("/files/"):])).resolve()
            if target.is_file() and target.is_relative_to(runs):
                kind = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
                return self._send(200, target.read_bytes(), kind)
        self._send(404, b"not found", "text/plain")


def serve(resolve: Callable[[], Optional[Path]], port: int = 8765, open_browser: bool = True) -> ThreadingHTTPServer:
    """Start the watcher on 127.0.0.1 in a background thread; returns the server (call `.shutdown()` to stop)."""
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(_Handler, resolve=resolve))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    if open_browser:
        webbrowser.open(url)
    return server


def _scrubbed(value: Any, scrub: Callable[[str], str]) -> Any:
    if isinstance(value, dict):
        return {k: _scrubbed(v, scrub) for k, v in value.items()}
    if isinstance(value, list):
        return [_scrubbed(v, scrub) for v in value]
    if isinstance(value, str) and not value.startswith("data:"):
        return scrub(value)
    return value


def share(run: Path, dest: Path, scrub: Optional[Callable[[str], str]] = None, max_bytes: int = 15_000_000,
          embed: bool = True) -> Path:
    """One HTML file: the same page with the run's state inline. Images are embedded (`embed=True`, a
    self-contained file) or linked relative to `dest` (for a page kept next to the exported runs).
    Text goes through `scrub` (local paths removed) when given; image bytes are never altered."""
    dest = Path(dest)
    budget = [max_bytes]

    def inline(path: Path) -> str:
        data = path.read_bytes() if path.is_file() else b""
        if not data or len(data) > budget[0]:
            return ""
        budget[0] -= len(data)
        kind = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return f"data:{kind};base64," + base64.b64encode(data).decode("ascii")

    def relative(path: Path) -> str:
        return Path(os.path.relpath(path.resolve(), dest.resolve().parent)).as_posix()

    snapshot = state(run, link=inline if embed else relative)
    if scrub is not None:
        snapshot = _scrubbed(snapshot, scrub)
    data = json.dumps(snapshot, ensure_ascii=False, default=str).replace("</", "<\\/")
    html = PAGE.read_text(encoding="utf-8").replace("<!--STATE-->", f'<script id="state" type="application/json">{data}</script>')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")
    return dest
