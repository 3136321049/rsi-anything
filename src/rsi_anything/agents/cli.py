from __future__ import annotations

import shlex
import shutil
import subprocess
import time
from pathlib import Path

from .base import Agent, AgentResult, hypothesis_from
from .registry import CLISpec


def _run(argv: list[str], cwd: Path, stdin, env, timeout: int, log: Path):
    started = time.perf_counter()
    try:
        run = subprocess.run(argv, cwd=cwd, input=stdin, capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired as exc:
        log.write_text(f"$ {shlex.join(argv[:6])} ...\n\nTIMEOUT after {timeout}s\n{exc.stdout or ''}", encoding="utf-8")
        return None, time.perf_counter() - started
    log.write_text(f"$ {shlex.join(argv[:6])} ...\nexit {run.returncode}\n\n--- stdout\n{run.stdout}\n--- stderr\n{run.stderr}",
                   encoding="utf-8")
    return run, time.perf_counter() - started


class CLIAgent(Agent):
    def __init__(self, spec: CLISpec, model: str, extra_args: list[str], allow_commands: bool):
        self.spec, self.model, self.extra_args, self.allow_commands = spec, model, extra_args, allow_commands
        self.name = spec.name

    def run(self, workdir: Path, prompt: str, round_dir: Path, timeout: int) -> AgentResult:
        if not shutil.which(self.spec.binary):
            return AgentResult(False, error=f"`{self.spec.binary}` not found on PATH")
        out_file = round_dir / "agent-final.txt"
        argv, stdin, out = self.spec.round_command(prompt, self.model, workdir, self.allow_commands,
                                                   self.extra_args, out_file)
        run, seconds = _run(argv, workdir, stdin, self.spec.env(), timeout, round_dir / "agent.log")
        if run is None:
            return AgentResult(False, seconds=seconds, error=f"timed out after {timeout}s")
        text, cost = self.spec.parse_output(run.stdout, out)
        if run.returncode != 0:
            return AgentResult(False, text, seconds=seconds, cost_usd=cost,
                               error=f"exit {run.returncode}: {(run.stderr or run.stdout)[-400:]}")
        return AgentResult(True, text, hypothesis_from(text), seconds, cost)


class CommandAgent(Agent):
    """Any program: `agent.command: "my-agent --prompt {prompt_file}"`, run inside the worktree."""

    name = "command"

    def __init__(self, template: str):
        if not template:
            raise ValueError("`agent.use: command` needs `agent.command`")
        self.template = template

    def run(self, workdir: Path, prompt: str, round_dir: Path, timeout: int) -> AgentResult:
        prompt_file = round_dir / "prompt.md"
        prompt_file.write_text(prompt, encoding="utf-8")
        command = self.template.format(prompt_file=shlex.quote(str(prompt_file)), workdir=shlex.quote(str(workdir)))
        run, seconds = _run(["/bin/sh", "-c", command], workdir, None, None, timeout, round_dir / "agent.log")
        if run is None:
            return AgentResult(False, seconds=seconds, error=f"timed out after {timeout}s")
        if run.returncode != 0:
            return AgentResult(False, run.stdout, seconds=seconds, error=f"exit {run.returncode}: {run.stderr[-400:]}")
        return AgentResult(True, run.stdout, hypothesis_from(run.stdout), seconds)
