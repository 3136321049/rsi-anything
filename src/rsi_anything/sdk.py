"""Helpers for judge scripts: report a score, record gates, say "unknown", render pages.

Judge commands run with the interpreter that runs rsi (`{python}` in rsi.yaml),
so a judge can `from rsi_anything import sdk`. The conventions it writes are the
ones the engine reads:

    $RSI_RESULT         score, gates, feedback (command judges)      -> report()
    out/gates.json      gates from a `prepare` step                  -> write_gates()
    out/notes.txt       notes the judge passes on to the agent       -> write_gates(notes=...)
    out/error.json      no artifact because a tool or service failed -> unavailable()
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from typing import NoReturn, Optional

from .result import report_result as report

__all__ = ["report", "write_gates", "unavailable", "find_browser", "screenshot", "visible_text"]

OUT = Path("out")


def write_gates(gates: dict[str, bool], notes: str = "", out: Path = OUT) -> bool:
    """For `prepare` steps: record pass/fail gates (and notes for the agent). Returns whether all passed."""
    out.mkdir(parents=True, exist_ok=True)
    (out / "gates.json").write_text(json.dumps({k: bool(v) for k, v in gates.items()}, ensure_ascii=False, indent=2),
                                    encoding="utf-8")
    if notes.strip():
        (out / "notes.txt").write_text(notes.strip() + "\n", encoding="utf-8")
    return all(gates.values())


def unavailable(error: str, stage: str, out: Path = OUT, code: int = 3) -> NoReturn:
    """A tool or service failed and left nothing to judge: quality is unknown, not zero. Exits."""
    out.mkdir(parents=True, exist_ok=True)
    (out / "error.json").write_text(json.dumps({"quality_result": "unknown", "stage": stage, "error": error},
                                               ensure_ascii=False, indent=2), encoding="utf-8")
    print(error, file=sys.stderr)
    raise SystemExit(code)


# ---------------------------------------------------------------- rendering with a local browser

_BROWSER_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "microsoft-edge")
_BROWSER_PATHS = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  "/Applications/Chromium.app/Contents/MacOS/Chromium",
                  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")
_PLAYWRIGHT = ("~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium",
               "~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
               "~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome")


def find_browser() -> Optional[str]:
    """A Chrome-family browser for headless rendering: $RSI_BROWSER, PATH, the usual app folders, Playwright's copy."""
    if os.environ.get("RSI_BROWSER"):
        return os.environ["RSI_BROWSER"]
    for name in _BROWSER_NAMES:
        if shutil.which(name):
            return shutil.which(name)
    for path in _BROWSER_PATHS:
        if Path(path).is_file():
            return path
    for pattern in _PLAYWRIGHT:
        found = sorted(glob.glob(os.path.expanduser(pattern)))
        if found:
            return found[-1]
    return None


MIN_WINDOW = 500  # headless Chrome never lays out narrower than this


def screenshot(page: Path, png: Path, width: int, height: int, timeout: int = 90) -> Path:
    """Render a local HTML or SVG file to PNG with headless Chrome. All network access is blocked,
    so the page has to be self-contained. A missing browser or a crash is reported as `unavailable`.

    Chrome will not lay a page out narrower than 500px, so a phone width such as 390 is rendered in an
    iframe of exactly that width, zoomed to fill the window: the image is 500px wide and shows the
    390px layout, with media queries seeing the phone width. (CSS `zoom`, not `transform: scale`:
    Chrome paints a scaled iframe only down to its unscaled height, leaving the bottom blank.)"""
    browser = find_browser()
    if not browser:
        unavailable("no Chrome or Chromium found for rendering; install one or set RSI_BROWSER", "render")
    if not (Path(browser).is_file() or shutil.which(browser)):
        unavailable(f"the browser at {browser} does not exist; fix RSI_BROWSER", "render")
    png = Path(png).resolve()
    png.parent.mkdir(parents=True, exist_ok=True)
    png.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="rsi-browser-") as profile:
        target, window = Path(page).resolve().as_uri(), (width, height)
        if width < MIN_WINDOW:
            scale = MIN_WINDOW / width
            window = (MIN_WINDOW, round(height * scale))
            frame = Path(profile) / "phone.html"
            frame.write_text('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;overflow:hidden;background:#fff}'
                             f'iframe{{display:block;border:0;width:{width}px;height:{height}px;zoom:{scale:.6f}}}</style>'
                             f'<iframe src="{target}"></iframe>', encoding="utf-8")
            target = frame.as_uri()
        command = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                   "--no-default-browser-check", "--disable-extensions", f"--user-data-dir={profile}",
                   "--proxy-server=http://127.0.0.1:9", "--proxy-bypass-list=<-loopback>",
                   "--allow-file-access-from-files", "--virtual-time-budget=3000", "--force-device-scale-factor=1",
                   f"--window-size={window[0]},{window[1]}", f"--screenshot={png}", target]
        try:
            run = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            unavailable(f"browser timed out after {timeout}s rendering {Path(page).name}", "render")
        except OSError as exc:
            unavailable(f"browser could not start: {exc}", "render")
    if run.returncode != 0 or not png.is_file() or png.stat().st_size == 0:
        unavailable(f"browser could not render {Path(page).name}: {(run.stderr or run.stdout)[-400:]}", "render")
    return png


class _Text(HTMLParser):
    SKIP = {"head", "title", "script", "style", "template", "noscript", "svg"}

    def __init__(self):
        super().__init__()
        self.parts, self.depth = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.depth += 1
        elif tag in {"p", "div", "section", "li", "h1", "h2", "h3", "h4", "br", "tr", "header", "footer", "article"}:
            self.parts.append("\n")
        alt = dict(attrs).get("alt") if tag == "img" else None
        if alt and not self.depth:
            self.parts.append(f" [image: {alt}] ")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if not self.depth:
            self.parts.append(data)


def visible_text(html: str) -> str:
    """The words a visitor reads (scripts and styles dropped), for fact checks and text judges."""
    parser = _Text()
    parser.feed(html)
    text = re.sub(r"[ \t\r\f\v]+", " ", "".join(parser.parts))
    return re.sub(r"\n\s*\n+", "\n", text).strip()
