"""One way to ask a model a question, whatever the user already has.

Model references are short strings:

    deepseek:deepseek-chat        OpenAI-compatible API, key from DEEPSEEK_API_KEY
    qwen:qwen-plus                DashScope compatible mode, DASHSCOPE_API_KEY
    anthropic:claude-sonnet-4-5   Anthropic Messages API, ANTHROPIC_API_KEY
    openai:gpt-5@https://my-gateway/v1   any OpenAI-compatible base URL
    cli:claude                    a logged-in coding agent CLI, no API key needed
    cli:codex:gpt-5               CLI with an explicit model

Every provider's base URL can be overridden with `<PROVIDER>_BASE_URL`.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .process import run as run_process

# provider -> (wire protocol, default base URL, API key env var)
PROVIDERS: dict[str, tuple[str, str, str]] = {
    "openai": ("openai", "https://api.openai.com/v1", "OPENAI_API_KEY"),
    "anthropic": ("anthropic", "https://api.anthropic.com", "ANTHROPIC_API_KEY"),
    "gemini": ("openai", "https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY"),
    "openrouter": ("openai", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "deepseek": ("openai", "https://api.deepseek.com", "DEEPSEEK_API_KEY"),
    "qwen": ("openai", "https://dashscope.aliyuncs.com/compatible-mode/v1", "DASHSCOPE_API_KEY"),
    "kimi": ("openai", "https://api.moonshot.cn/v1", "MOONSHOT_API_KEY"),
    "glm": ("openai", "https://open.bigmodel.cn/api/paas/v4", "ZHIPUAI_API_KEY"),
    "doubao": ("openai", "https://ark.cn-beijing.volces.com/api/v3", "ARK_API_KEY"),
    "siliconflow": ("openai", "https://api.siliconflow.cn/v1", "SILICONFLOW_API_KEY"),
    "minimax": ("openai", "https://api.minimax.cn/v1", "MINIMAX_API_KEY"),
    "ollama": ("openai", "http://localhost:11434/v1", ""),
}


class LLMError(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelRef:
    raw: str
    kind: str          # "api" or "cli"
    provider: str      # api provider name, or cli name
    model: str = ""
    protocol: str = ""
    base_url: str = ""
    key_env: str = ""

    @property
    def label(self) -> str:
        return self.raw


def parse(spec: str) -> ModelRef:
    spec = spec.strip()
    if spec.startswith("cli:"):
        parts = spec.split(":", 2)
        return ModelRef(spec, "cli", parts[1], parts[2] if len(parts) > 2 else "")
    provider, _, rest = spec.partition(":")
    if provider not in PROVIDERS or not rest:
        known = ", ".join(sorted(PROVIDERS))
        raise LLMError(f"unknown model reference {spec!r}; use <provider>:<model> with provider in [{known}] or cli:<agent>")
    protocol, base_url, key_env = PROVIDERS[provider]
    model, _, custom_url = rest.partition("@")
    base_url = custom_url or os.environ.get(f"{provider.upper()}_BASE_URL", base_url)
    return ModelRef(spec, "api", provider, model, protocol, base_url.rstrip("/"), key_env)


@dataclass
class Reply:
    text: str
    cost_usd: Optional[float] = None
    seconds: float = 0.0
    model: str = ""
    usage: dict = field(default_factory=dict)


def ask(ref: ModelRef, prompt: str, system: str = "", images: Optional[list[Path]] = None,
        timeout: int = 600, json_mode: bool = False) -> Reply:
    started = time.perf_counter()
    if ref.kind == "cli":
        reply = _ask_cli(ref, prompt if not system else f"{system}\n\n{prompt}", images or [], timeout)
    elif ref.protocol == "anthropic":
        reply = _ask_anthropic(ref, prompt, system, images or [], timeout)
    else:
        reply = _ask_openai(ref, prompt, system, images or [], timeout, json_mode)
    reply.seconds = time.perf_counter() - started
    usage_log = os.environ.get("RSI_USAGE_LOG")
    if usage_log:
        # 只记调用元信息，任务正文与账号凭据不进用量记录。
        record = {"requested_model": ref.raw, "actual_model": reply.model or None,
                  "usage": reply.usage, "seconds": round(reply.seconds, 3), "cost_usd": reply.cost_usd}
        destination = Path(usage_log)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    return reply


# ---------------------------------------------------------------- HTTP APIs

def _api_key(ref: ModelRef) -> str:
    if not ref.key_env:
        return os.environ.get("RSI_API_KEY", "none")
    key = os.environ.get(ref.key_env) or os.environ.get("RSI_API_KEY")
    if not key:
        raise LLMError(f"{ref.raw} needs an API key in ${ref.key_env}")
    return key


def _post(url: str, headers: dict[str, str], body: dict, timeout: int) -> dict:
    data = json.dumps(body).encode("utf-8")
    delay = 2.0
    for attempt in range(5):
        request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            if exc.code in (429, 500, 502, 503, 504, 529) and attempt < 4:
                time.sleep(delay)
                delay *= 2
                continue
            raise LLMError(f"HTTP {exc.code} from {url}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt < 4:
                time.sleep(delay)
                delay *= 2
                continue
            raise LLMError(f"cannot reach {url}: {exc}") from exc
    raise LLMError(f"giving up on {url}")


def _data_uri(path: Path) -> tuple[str, str]:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return mime, base64.b64encode(Path(path).read_bytes()).decode("ascii")


def _ask_openai(ref, prompt, system, images, timeout, json_mode) -> Reply:
    content: list[dict] | str = prompt
    if images:
        content = [{"type": "text", "text": prompt}]
        for image in images:
            mime, data = _data_uri(image)
            content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}})
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": content}]
    body: dict = {"model": ref.model, "messages": messages}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    data = _post(f"{ref.base_url}/chat/completions", {"Authorization": f"Bearer {_api_key(ref)}"}, body, timeout)
    try:
        return Reply(data["choices"][0]["message"]["content"] or "",
                     model=str(data.get("model") or ""), usage=data.get("usage") or {})
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(f"unexpected response from {ref.raw}: {str(data)[:300]}") from exc


def _ask_anthropic(ref, prompt, system, images, timeout) -> Reply:
    content: list[dict] = []
    for image in images:
        mime, data = _data_uri(image)
        content.append({"type": "image", "source": {"type": "base64", "media_type": mime, "data": data}})
    content.append({"type": "text", "text": prompt})
    body: dict = {"model": ref.model, "max_tokens": 8000, "messages": [{"role": "user", "content": content}]}
    if system:
        body["system"] = system
    headers = {"x-api-key": _api_key(ref), "anthropic-version": "2023-06-01"}
    data = _post(f"{ref.base_url}/v1/messages", headers, body, timeout)
    text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
    return Reply(text, model=str(data.get("model") or ""), usage=data.get("usage") or {})


# ---------------------------------------------------------------- coding-agent CLIs

def cli_available(name: str) -> bool:
    from .agents.registry import CLI_AGENTS

    spec = CLI_AGENTS.get(name)
    return bool(spec and shutil.which(spec.binary))


def _ask_cli(ref: ModelRef, prompt: str, images: list[Path], timeout: int) -> Reply:
    """Ask a coding-agent CLI a one-shot question inside an empty scratch directory."""
    from .agents.registry import CLI_AGENTS, check_auth

    spec = CLI_AGENTS.get(ref.provider)
    if spec is None:
        raise LLMError(f"unknown CLI {ref.provider!r}; known: {', '.join(sorted(CLI_AGENTS))}")
    if not shutil.which(spec.binary):
        raise LLMError(f"`{spec.binary}` is not installed or not on PATH")
    try:
        check_auth(spec, min(timeout, 10))
    except RuntimeError as exc:
        raise LLMError(str(exc)) from exc
    with tempfile.TemporaryDirectory(prefix="rsi-ask-") as scratch:
        scratch_dir = Path(scratch)
        attached = []
        for image in images:
            target = scratch_dir / Path(image).name
            shutil.copyfile(image, target)
            attached.append(target)
        if attached:
            prompt += "\n\nImages to inspect (read them before answering):\n" + "\n".join(f"- {p.name}" for p in attached)
        command, stdin, out_file, extra_env = spec.ask_command(prompt, ref.model, scratch_dir, attached)
        try:
            run = run_process(command, cwd=scratch_dir, input=stdin,
                              timeout=timeout, env=spec.env(extra_env))
        except subprocess.TimeoutExpired as exc:
            raise LLMError(f"{ref.raw} timed out after {timeout}s") from exc
        if run.returncode != 0:
            raise LLMError(f"{ref.raw} exited {run.returncode}: {(run.stderr or run.stdout)[-600:]}")
        text, cost = spec.parse_output(run.stdout, out_file)
        metadata = spec.metadata(run.stdout)
        return Reply(text, cost, model=metadata["actual_model"] or "", usage=metadata["usage"])


# ---------------------------------------------------------------- choosing models

# Used only when a contract says `auto` and an API key is present (IDs as of 2026-10; they change often,
# so contracts should name models explicitly when reproducibility matters).
DEFAULT_MODELS = {
    "openai": "gpt-6.1-sol",
    "anthropic": "claude-sonnet-5-5",
    "gemini": "gemini-3.8-flash",
    "qwen": "qwen3.8-max",
    "doubao": "doubao-seed-2-1-pro-260915",
    "deepseek": "deepseek-chat",
    "kimi": "kimi-k3",
    "glm": "glm-5.3-flash",
    "minimax": "MiniMax-M3",
}


def available_models(avoid: str = "") -> list[str]:
    """Model references usable right now: logged-in CLIs first, then providers with a key set."""
    from .agents.registry import detect

    found = [f"cli:{spec.name}" for spec in detect() if spec.name != avoid]
    for provider, model in DEFAULT_MODELS.items():
        env = PROVIDERS[provider][2]
        if env and os.environ.get(env):
            found.append(f"{provider}:{model}")
    if not found and avoid:
        found = [f"cli:{avoid}"]
    return found


def resolve_models(models: list[str], avoid: str = "", limit: int = 2) -> list[str]:
    """Expand `auto` into up to `limit` available models, preferring vendors other than the agent's."""
    resolved: list[str] = []
    for model in models:
        if model == "auto":
            resolved += [m for m in available_models(avoid) if m not in resolved][:limit]
        else:
            resolved.append(model)
    if not resolved:
        raise LLMError("no judge model available: install a coding-agent CLI or set an API key (see `rsi agents`)")
    return resolved


# ---------------------------------------------------------------- helpers

def extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model reply (fenced or bare)."""
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    candidates = [fenced.group(1)] if fenced else []
    start = text.find("{")
    while start != -1:
        depth = 0
        for index in range(start, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    candidates.append(text[start:index + 1])
                    break
        start = text.find("{", start + 1)
    for candidate in candidates:
        try:
            value = json.loads(candidate)
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            continue
    raise LLMError(f"no JSON object in model reply: {text[:300]!r}")
