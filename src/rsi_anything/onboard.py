"""`rsi setup`: check this machine, suggest who edits and who judges, and install the /rsi skill.

Nothing here logs in, reads credentials or changes an agent's settings. The only files it writes are
the skill's SKILL.md in the agents' user skill folders, and only when asked.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import llm, sdk
from .agents import detect

SKILL = Path(__file__).parent / "skill" / "SKILL.md"
# Where each agent looks for user-level skills (agents without a skills folder get printed instructions).
SKILL_DIRS = {
    "claude": "~/.claude/skills/rsi",
    "codex": "~/.codex/skills/rsi",
    "cursor": "~/.cursor/skills/rsi",
    "codebuddy": "~/.codebuddy/skills/rsi",
}
# Judges from a different vendor than the editor, so no model grades its own work.
PARTNER = {"codex": "claude", "claude": "codex", "gemini": "claude", "qwen": "claude", "opencode": "claude"}


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    fix: str = ""
    needed: bool = True      # False: only some templates need it


def skill_path(agent: str) -> Optional[Path]:
    return Path(os.path.expanduser(SKILL_DIRS[agent])) / "SKILL.md" if agent in SKILL_DIRS else None


def skill_current(agent: str) -> bool:
    path = skill_path(agent)
    return bool(path and path.is_file() and path.read_bytes() == SKILL.read_bytes())


def install_skill(agents: list[str]) -> list[str]:
    """Copy SKILL.md into each agent's skills folder; returns one line per agent."""
    lines = []
    for name in agents:
        path = skill_path(name)
        if path is None:
            lines.append(f"{name}: no skills folder; add the text of `rsi skill show` to its instructions file")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SKILL, path)
        lines.append(f"{name}: installed {path}")
    return lines


def _git_identity() -> bool:
    if all(os.environ.get(f"GIT_{who}_{what}") for who in ("AUTHOR", "COMMITTER") for what in ("NAME", "EMAIL")):
        return True
    return all(subprocess.run(["git", "config", "--get", key], capture_output=True, text=True).stdout.strip()
               for key in ("user.name", "user.email"))


def pairing(ready: list[str]) -> tuple[Optional[str], Optional[str]]:
    """Editor and judge to suggest: Codex edits if it can, and a different vendor judges when one is ready."""
    if not ready:
        return None, None
    editor = "codex" if "codex" in ready else ready[0]
    partner = PARTNER.get(editor)
    judge = partner if partner in ready else next((name for name in ready if name != editor), editor)
    return editor, judge


def checks() -> tuple[list[Check], list[str]]:
    """Everything `rsi setup` reports, plus the coding agents that answered."""
    ready = [spec.name for spec in detect()]
    installed = [spec.name for spec in detect(check=False)]
    keys = [provider for provider, (_, _, env) in llm.PROVIDERS.items() if env and os.environ.get(env)]
    found = [
        Check("python", sys.version_info >= (3, 9), sys.version.split()[0], "install Python 3.9 or newer (3.11 recommended)"),
        Check("git", bool(shutil.which("git")), shutil.which("git") or "not found", "install git"),
    ]
    if shutil.which("git"):
        found.append(Check("git identity", _git_identity(), "name and email set" if _git_identity() else "missing",
                           'git config --global user.name "Your Name" && git config --global user.email you@example.com'))
    silent = [name for name in installed if name not in ready]
    found.append(Check("coding agent", bool(ready) or bool(keys),
                       ", ".join(ready) + (f" (installed but not answering: {', '.join(silent)})" if silent else "")
                       if ready else (f"none answering; API keys for {', '.join(keys)}" if keys else "none found"),
                       "install and sign in to one, e.g. Codex or Claude Code (`rsi agents` lists all)"))
    browser = sdk.find_browser()
    found.append(Check("browser", bool(browser), browser or "not found",
                       "install Google Chrome or Chromium, or set RSI_BROWSER (for screenshot judges)", needed=False))
    ffmpeg = shutil.which("ffmpeg") and shutil.which("ffprobe")
    found.append(Check("ffmpeg", bool(ffmpeg), "ffmpeg and ffprobe" if ffmpeg else "not found",
                       "install FFmpeg (for the video templates)", needed=False))
    for name in ready:
        if name in SKILL_DIRS:
            found.append(Check(f"/rsi skill · {name}", skill_current(name),
                               "up to date" if skill_current(name) else "not installed" if not skill_path(name).is_file()
                               else "older version", "rsi setup --yes", needed=False))
    return found, ready
