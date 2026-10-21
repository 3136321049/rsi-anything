"""Coding-agent CLIs the ratchet can drive, US and China.

Each entry knows two invocations:
  * a *round*: edit files in the worktree, headless, with edits auto-approved;
  * an *ask*: a one-shot question in an empty scratch dir (used by LLM judges
    when the user has no API key but has a logged-in CLI).

Whatever a CLI allows, the engine only keeps edits inside the contract's
artifact paths and judges in a separate copy, so the CLI's own permission
model is a convenience, not the safety boundary.
"""
from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

Command = tuple[list[str], Optional[str], Optional[Path]]  # argv, stdin, file holding the final message

_NESTED_SESSION_VARS = ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_SSE_PORT")


@dataclass
class CLISpec:
    name: str
    binary: str
    title: str
    region: str           # where it is easiest to use: "global", "cn", or "global+cn"
    output: str = "text"  # "claude-json" | "file" | "text" | "gemini-json"
    notes: str = ""
    extra_env: dict[str, str] = field(default_factory=dict)

    def env(self) -> dict[str, str]:
        env = {k: v for k, v in os.environ.items() if k not in _NESTED_SESSION_VARS and not k.startswith("RSI_")}
        env.update(self.extra_env)
        return env

    # ---- per-CLI argument building -------------------------------------------------

    def round_command(self, prompt: str, model: str, workdir: Path, allow_commands: bool,
                      extra_args: list[str], out_file: Path) -> Command:
        n, m = self.name, (model or "")
        if n == "claude" or n == "codebuddy":
            argv = [self.binary, "-p", "--output-format", "json", "--permission-mode", "acceptEdits"]
            argv += ["--allowedTools", "Bash"] if allow_commands else []
            argv += ["--model", m] if m else []
            return argv + extra_args, prompt, None
        if n == "codex":
            argv = [self.binary, "exec", "--skip-git-repo-check", "--color", "never",
                    "--sandbox", "workspace-write", "-C", str(workdir), "-o", str(out_file)]
            argv += ["-m", m] if m else []
            return argv + extra_args + ["-"], prompt, out_file
        if n == "cursor":
            argv = [self.binary, "-p", "--output-format", "json", "--trust", "--workspace", str(workdir)]
            argv += ["--force"] if allow_commands else []
            argv += ["--model", m] if m else []
            return argv + extra_args + [prompt], None, None
        if n in ("gemini", "qwen"):
            argv = [self.binary, "-p", prompt, "--approval-mode", "yolo" if allow_commands else "auto_edit"]
            argv += ["-m", m] if m else []
            return argv + extra_args, None, None
        if n == "opencode":
            argv = [self.binary, "run"] + (["--model", m] if m else []) + extra_args + [prompt]
            return argv, None, None
        if n == "kimi":
            argv = [self.binary, "--print", "--yolo"] + (["--model", m] if m else []) + extra_args + ["-c", prompt]
            return argv, None, None
        raise ValueError(f"no round command for {n}")

    def ask_command(self, prompt: str, model: str, scratch: Path, images: list[Path]) -> Command:
        n, m = self.name, (model or "")
        if n in ("claude", "codebuddy"):
            return [self.binary, "-p", "--output-format", "json"] + (["--model", m] if m else []), prompt, None
        if n == "codex":
            out_file = scratch / ".last-message.txt"
            argv = [self.binary, "exec", "--skip-git-repo-check", "--color", "never", "--sandbox", "read-only",
                    "--ephemeral", "-C", str(scratch), "-o", str(out_file)]
            for image in images:
                argv += ["-i", str(image)]
            argv += ["-m", m] if m else []
            return argv + ["-"], prompt, out_file
        if n == "cursor":
            argv = [self.binary, "-p", "--output-format", "json", "--trust", "--workspace", str(scratch)]
            return argv + (["--model", m] if m else []) + [prompt], None, None
        if n in ("gemini", "qwen"):
            return [self.binary, "-p", prompt] + (["-m", m] if m else []), None, None
        if n == "opencode":
            return [self.binary, "run"] + (["--model", m] if m else []) + [prompt], None, None
        if n == "kimi":
            return [self.binary, "--print"] + (["--model", m] if m else []) + ["-c", prompt], None, None
        raise ValueError(f"no ask command for {n}")

    def parse_output(self, stdout: str, out_file: Optional[Path]) -> tuple[str, Optional[float]]:
        if out_file is not None and Path(out_file).exists():
            return Path(out_file).read_text(encoding="utf-8").strip(), None
        if self.output == "claude-json":
            data = _last_json(stdout)
            if data is not None:
                cost = data.get("total_cost_usd")
                return str(data.get("result", "")), float(cost) if isinstance(cost, (int, float)) else None
        return stdout.strip(), None


def _last_json(stdout: str) -> Optional[dict]:
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    try:
        value = json.loads(stdout)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        return None


CLI_AGENTS: dict[str, CLISpec] = {spec.name: spec for spec in [
    CLISpec("claude", "claude", "Claude Code", "global", "claude-json"),
    CLISpec("codex", "codex", "OpenAI Codex CLI", "global", "file"),
    CLISpec("cursor", "cursor-agent", "Cursor CLI", "global", "claude-json"),
    CLISpec("gemini", "gemini", "Gemini CLI", "global"),
    CLISpec("opencode", "opencode", "OpenCode", "global+cn", notes="any provider, incl. DeepSeek/Qwen/Kimi/GLM"),
    CLISpec("qwen", "qwen", "Qwen Code", "global+cn"),
    CLISpec("kimi", "kimi", "Kimi CLI", "cn"),
    CLISpec("codebuddy", "codebuddy", "CodeBuddy Code", "cn", "claude-json"),
]}

# Preference order when the contract says `use: auto`.
AUTO_ORDER = ["claude", "codex", "cursor", "gemini", "qwen", "kimi", "codebuddy", "opencode"]


def detect() -> list[CLISpec]:
    return [CLI_AGENTS[name] for name in AUTO_ORDER if shutil.which(CLI_AGENTS[name].binary)]


def make_agent(spec, allow_commands: bool = False):
    """Build the agent named in the contract's `agent:` block."""
    from .builtin import APIAgent
    from .cli import CLIAgent, CommandAgent

    use = spec.use
    if use == "auto":
        found = detect()
        if not found:
            raise RuntimeError("no coding agent CLI found; install one (see `rsi agents`) or set `agent.use: api`")
        use = found[0].name
    if use == "command":
        return CommandAgent(spec.command)
    if use == "api":
        if not spec.model:
            raise RuntimeError("`agent.use: api` needs `agent.model`, e.g. deepseek:deepseek-chat")
        return APIAgent(spec.model)
    if use not in CLI_AGENTS:
        raise RuntimeError(f"unknown agent {use!r}; choose from auto, api, command, {', '.join(CLI_AGENTS)}")
    return CLIAgent(CLI_AGENTS[use], spec.model or "", spec.extra_args, allow_commands)
