"""A minimal agent for people with an API key but no coding-agent CLI.

It shows the model the current artifact files and asks for full replacement
contents as JSON. That is enough for text artifacts (posts, scripts, prompts,
reports, configs, small modules) and works with any model `llm.ask` supports,
including DeepSeek, Qwen, Kimi, GLM and Doubao.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from .. import llm
from ..paths import matches, normalize
from .base import Agent, AgentResult

MAX_CHARS = 200_000

_FORMAT = """
## How to answer

Reply with a single JSON object and nothing else:

{"hypothesis": "<one sentence: what you changed and why the judge should score it higher>",
 "files": {"<path>": "<the complete new content of that file>"}}

Only include files you actually change, give their full content (not a diff), and only use paths listed above.
"""


def artifact_files(workdir: Path, patterns: list[str]) -> list[str]:
    found = []
    for dirpath, dirnames, filenames in os.walk(workdir):
        dirnames[:] = [d for d in dirnames if d not in {".git", ".rsi", "__pycache__", "node_modules"}]
        for name in filenames:
            rel = (Path(dirpath) / name).relative_to(workdir).as_posix()
            if matches(rel, patterns):
                found.append(rel)
    return sorted(found)


class APIAgent(Agent):
    def __init__(self, model: str):
        self.ref = llm.parse(model)
        self.name = f"api:{model}"
        self.artifact: list[str] = []

    def run(self, workdir: Path, prompt: str, round_dir: Path, timeout: int) -> AgentResult:
        started = time.perf_counter()
        files = artifact_files(workdir, self.artifact)
        blocks, total = [], 0
        for rel in files:
            text = (workdir / rel).read_text(encoding="utf-8", errors="replace")
            total += len(text)
            if total > MAX_CHARS:
                return AgentResult(False, error=f"artifact files exceed {MAX_CHARS} characters; use a coding-agent CLI")
            blocks.append(f"### {rel}\n```\n{text}\n```")
        full = prompt + "\n\n## Current files\n\n" + ("\n\n".join(blocks) or "(none yet: create them)") + _FORMAT
        (round_dir / "prompt-full.md").write_text(full, encoding="utf-8")
        try:
            reply = llm.ask(self.ref, full, timeout=timeout, json_mode=self.ref.kind == "api")
            (round_dir / "agent.log").write_text(reply.text, encoding="utf-8")
            data = llm.extract_json(reply.text)
        except llm.LLMError as exc:
            return AgentResult(False, seconds=time.perf_counter() - started, error=str(exc))
        written = []
        for rel, content in (data.get("files") or {}).items():
            try:
                rel = normalize(rel)
            except ValueError:
                continue
            if not matches(rel, self.artifact) or not isinstance(content, str):
                continue
            target = workdir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            written.append(rel)
        hypothesis = str(data.get("hypothesis", ""))[:300]
        return AgentResult(True, f"wrote {', '.join(written) or 'nothing'}\nHYPOTHESIS: {hypothesis}", hypothesis,
                           time.perf_counter() - started, reply.cost_usd)
