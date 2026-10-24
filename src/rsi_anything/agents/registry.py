"""Coding-agent CLIs the ratchet can drive, US and China.

Each entry knows two invocations:
  * a *round*: edit files in the worktree, headless, with edits auto-approved;
  * an *ask*: a one-shot question in an empty scratch dir (used by LLM judges
    when the user has no API key but has a logged-in CLI).

Flags follow each tool's documentation as of 2026-10 (see
docs/research/B-agents-and-models.md). Whatever a CLI allows, the engine only
keeps edits inside the contract's artifact paths and judges in a separate copy,
so a CLI's own permission model is a convenience, not the safety boundary.

Output families: claude-json (one JSON object with `.result`), file (final
message written to a file), gemini-json (`.response`), qwen-json (array, last
`.result`), opencode-jsonl (`text` events, `step_finish` costs), kimi-jsonl
(assistant messages), text (raw stdout).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ..process import run as run_process

Command = tuple[list[str], Optional[str], Optional[Path], dict]  # argv, stdin, final-message file, extra env

def _codex_config_args() -> list[str]:
    """个人实验可显式关闭用户配置和全局指令，不继承其他项目的工具。"""
    args = []
    if os.environ.get("RSI_CODEX_ISOLATED") == "1":
        args += ["--ignore-user-config", "--ignore-rules", "-c", "project_doc_max_bytes=0",
                 "-c", "skills.max_context_tokens=1"]
    effort = os.environ.get("RSI_CODEX_REASONING_EFFORT")
    if effort:
        if effort not in {"low", "medium", "high", "xhigh"}:
            raise ValueError("RSI_CODEX_REASONING_EFFORT 必须是 low、medium、high 或 xhigh")
        args += ["-c", f"model_reasoning_effort={json.dumps(effort)}"]
    return args

_NESTED_SESSION_VARS = ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_SSE_PORT")


@dataclass
class CLISpec:
    name: str
    binary: str
    title: str
    region: str           # "global", "cn" or "global+cn": where it is easiest to use
    output: str = "text"
    notes: str = ""
    extra_env: dict[str, str] = field(default_factory=dict)

    def env(self, extra: Optional[dict] = None) -> dict[str, str]:
        env = {k: v for k, v in os.environ.items() if k not in _NESTED_SESSION_VARS and not k.startswith("RSI_")}
        env.update(self.extra_env)
        env.update(extra or {})
        return env

    # ---- per-CLI argument building -------------------------------------------------

    def round_command(self, prompt: str, model: str, workdir: Path, allow_commands: bool,
                      extra_args: list[str], out_file: Path) -> Command:
        n, m = self.name, (model or "")
        if n == "claude":
            argv = [self.binary, "-p", "--output-format", "json", "--permission-mode", "acceptEdits"]
            argv += ["--allowedTools", "Bash"] if allow_commands else []
            return argv + (["--model", m] if m else []) + extra_args, prompt, None, {}
        if n == "codebuddy":  # Claude Code compatible flags; headless mode requires -y
            argv = [self.binary, "-p", prompt, "-y", "--output-format", "json"]
            return argv + (["--model", m] if m else []) + extra_args, None, None, {}
        if n == "codex":  # note: for codex, -p means --profile, so the prompt goes through stdin
            argv = [self.binary, "exec", "--skip-git-repo-check", "--color", "never", "-c", 'approval_policy="never"',
                    "--sandbox", "workspace-write", "-C", str(workdir), "-o", str(out_file)]
            return argv + ["--json"] + _codex_config_args() + (["-m", m] if m else []) + extra_args + ["-"], prompt, out_file, {}
        if n == "cursor":  # without --force, edits are only proposed, never written
            argv = [self.binary, "-p", "--output-format", "json", "--trust", "--force", "--workspace", str(workdir)]
            argv += [] if allow_commands else ["--sandbox", "enabled"]
            return argv + (["--model", m] if m else []) + extra_args + [prompt], None, None, {}
        if n == "gemini":
            argv = [self.binary, "-p", prompt, "-o", "json", "--approval-mode", "yolo" if allow_commands else "auto_edit"]
            return argv + (["-m", m] if m else []) + extra_args, None, None, {}
        if n == "qwen":
            argv = [self.binary, "-p", prompt, "-o", "json", "--approval-mode", "yolo" if allow_commands else "auto-edit"]
            return argv + (["-m", m] if m else []) + extra_args, None, None, {}
        if n == "kimi":  # -p never asks for approval; there is no workdir flag, cwd is the worktree
            argv = [self.binary, "-p", prompt, "--output-format", "stream-json"]
            return argv + (["-m", m] if m else []) + extra_args, None, None, {}
        if n == "qoder":
            mode = "bypass_permissions" if allow_commands else "accept_edits"
            argv = [self.binary, "-p", prompt, "-o", "json", "-w", str(workdir), "--permission-mode", mode]
            return argv + (["-m", m] if m else []) + extra_args, None, None, {}
        if n == "opencode":
            permission = {"external_directory": "deny"} if allow_commands else {"external_directory": "deny", "shell": "deny"}
            argv = [self.binary, "run", "--format", "json", "--auto"] + (["--model", m] if m else []) + extra_args + [prompt]
            return argv, None, None, {"OPENCODE_PERMISSION": json.dumps(permission)}
        if n == "copilot":
            argv = [self.binary, "-p", prompt, "-s", "--no-ask-user", "--allow-all-tools"]
            argv += [] if allow_commands else ["--deny-tool", "shell"]
            return argv + (["--model", m] if m else []) + extra_args, None, None, {}
        raise ValueError(f"no round command for {n}")

    def ask_command(self, prompt: str, model: str, scratch: Path, images: list[Path]) -> Command:
        n, m = self.name, (model or "")
        if n == "claude":
            return [self.binary, "-p", "--output-format", "json"] + (["--model", m] if m else []), prompt, None, {}
        if n == "codebuddy":
            return [self.binary, "-p", prompt, "-y", "--output-format", "json"] + (["--model", m] if m else []), None, None, {}
        if n == "codex":
            out_file = scratch / ".last-message.txt"
            argv = [self.binary, "exec", "--skip-git-repo-check", "--color", "never", "--sandbox", "read-only",
                    "--ephemeral", "-C", str(scratch), "-o", str(out_file)]
            for image in images:
                argv += ["-i", str(image)]
            return argv + ["--json"] + _codex_config_args() + (["-m", m] if m else []) + ["-"], prompt, out_file, {}
        if n == "cursor":
            argv = [self.binary, "-p", "--output-format", "json", "--trust", "--workspace", str(scratch)]
            return argv + (["--model", m] if m else []) + [prompt], None, None, {}
        if n in ("gemini", "qwen"):
            return [self.binary, "-p", prompt, "-o", "json"] + (["-m", m] if m else []), None, None, {}
        if n == "kimi":
            return [self.binary, "-p", prompt, "--output-format", "stream-json"] + (["-m", m] if m else []), None, None, {}
        if n == "qoder":
            return [self.binary, "-p", prompt, "-o", "json", "-w", str(scratch)] + (["-m", m] if m else []), None, None, {}
        if n == "opencode":  # without --auto every permission request is rejected: a pure question
            return [self.binary, "run", "--format", "json"] + (["--model", m] if m else []) + [prompt], None, None, {}
        if n == "copilot":
            return [self.binary, "-p", prompt, "-s", "--no-ask-user"] + (["--model", m] if m else []), None, None, {}
        raise ValueError(f"no ask command for {n}")

    def parse_output(self, stdout: str, out_file: Optional[Path]) -> tuple[str, Optional[float]]:
        if out_file is not None and Path(out_file).exists():
            return Path(out_file).read_text(encoding="utf-8").strip(), None
        family = self.output
        if family == "claude-json":
            data = _last_json(stdout)
            if isinstance(data, dict):
                cost = data.get("total_cost_usd")
                return str(data.get("result", "")), float(cost) if isinstance(cost, (int, float)) else None
        if family == "gemini-json":
            data = _last_json(stdout)
            if isinstance(data, dict) and "response" in data:
                return str(data["response"]), None
        if family == "qwen-json":
            data = _last_json(stdout)
            if isinstance(data, list) and data:
                data = data[-1]
            if isinstance(data, dict):
                return str(data.get("result", data.get("response", ""))), None
        if family == "opencode-jsonl":
            texts, cost = [], 0.0
            for event in _json_lines(stdout):
                part = event.get("part") or {}
                if event.get("type") == "text" and part.get("text"):
                    texts.append(str(part["text"]))
                if event.get("type") == "step_finish" and isinstance(part.get("cost"), (int, float)):
                    cost += float(part["cost"])
            if texts:
                return texts[-1], cost or None
        if family == "kimi-jsonl":
            replies = [_message_text(e) for e in _json_lines(stdout) if e.get("role") == "assistant"]
            replies = [r for r in replies if r]
            if replies:
                return replies[-1], None
        return stdout.strip(), None

    def metadata(self, stdout: str) -> dict[str, Any]:
        """只保存 CLI 明确返回的模型和用量，不推断订阅费用。"""
        usage, model = {}, ""
        for event in _json_lines(stdout):
            if isinstance(event.get("usage"), dict):
                usage = event["usage"]
            if isinstance(event.get("model"), str):
                model = event["model"]
        return {"actual_model": model or None, "usage": usage}


def _json_lines(stdout: str) -> list[dict[str, Any]]:
    events = []
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                events.append(value)
    return events


def _message_text(message: dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
    return ""


def _last_json(stdout: str) -> Any:
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        pass
    events = _json_lines(stdout)
    return events[-1] if events else None


CLI_AGENTS: dict[str, CLISpec] = {spec.name: spec for spec in [
    CLISpec("claude", "claude", "Claude Code", "global", "claude-json"),
    CLISpec("codex", os.environ.get("RSI_CODEX_BIN", "codex"), "OpenAI Codex CLI", "global", "file", notes="needs a recent version for current models"),
    CLISpec("opencode", "opencode", "OpenCode", "global+cn", "opencode-jsonl",
            notes="any OpenAI/Anthropic-compatible endpoint: DeepSeek, Qwen, Kimi, GLM, MiniMax"),
    CLISpec("qwen", "qwen", "Qwen Code", "global+cn", "qwen-json"),
    CLISpec("cursor", "cursor-agent", "Cursor CLI", "global", "claude-json", notes="reports no token usage"),
    CLISpec("gemini", "gemini", "Gemini CLI", "global", "gemini-json"),
    CLISpec("codebuddy", "codebuddy", "CodeBuddy Code", "global+cn", "claude-json"),
    CLISpec("kimi", "kimi", "Kimi Code CLI", "cn", "kimi-jsonl"),
    CLISpec("qoder", "qoder", "Qoder CLI", "global+cn", "claude-json", notes="JSON fields not documented"),
    CLISpec("copilot", "copilot", "GitHub Copilot CLI", "global"),
]}

# Preference order when the contract says `use: auto`.
AUTO_ORDER = ["claude", "codex", "opencode", "qwen", "gemini", "cursor", "kimi", "codebuddy", "qoder", "copilot"]


_READY: dict[str, bool] = {}


def check_auth(spec: CLISpec, timeout: float = 10) -> None:
    """后台调用 Claude 前只查询登录状态，未登录时直接报错。"""
    if spec.name != "claude":
        return
    try:
        result = run_process([spec.binary, "auth", "status", "--json"],
                             stdin=subprocess.DEVNULL, timeout=timeout, env=spec.env())
        status = json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        raise RuntimeError("无法确认 Claude 登录状态，已停止后台调用。") from exc
    if result.returncode != 0 or not isinstance(status, dict) or status.get("loggedIn") is not True:
        raise RuntimeError("Claude 尚未登录，请先在终端运行 claude auth login，完成后再重试。")


def ready(spec: CLISpec, timeout: float = 10) -> bool:
    """确认命令能正常返回版本，并在需要时检查登录状态。"""
    if spec.name not in _READY:
        ok = False
        if shutil.which(spec.binary):
            try:
                ok = run_process([spec.binary, "--version"], stdin=subprocess.DEVNULL,
                                 timeout=timeout, env=spec.env()).returncode == 0
                if ok:
                    check_auth(spec, timeout)
            except (subprocess.TimeoutExpired, OSError, RuntimeError):
                ok = False
        _READY[spec.name] = ok
    return _READY[spec.name]


def detect(check: bool = True) -> list[CLISpec]:
    """CLIs to use when a contract says `auto`, in preference order. `check=False` only looks at PATH."""
    found = [CLI_AGENTS[name] for name in AUTO_ORDER if shutil.which(CLI_AGENTS[name].binary)]
    return [spec for spec in found if ready(spec)] if check else found


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
