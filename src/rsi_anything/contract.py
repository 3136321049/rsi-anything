"""The contract (`rsi.yaml`): what may change, who judges, how long to try.

The human owns this file. A run freezes it together with the judge files, so
changing it later starts a new experiment instead of moving the goalposts.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

from .paths import normalize, overlap

CONTRACT_FILE = "rsi.yaml"
JUDGE_TYPES = {"command", "rubric"}


class ContractError(ValueError):
    pass


@dataclass
class JudgeSpec:
    type: str
    files: list[str] = field(default_factory=list)  # frozen: evaluator code, tests, rubric, data
    direction: str = "maximize"
    min_delta: float = 0.0   # absolute margin a new score must clear
    min_gain: float = 0.0    # relative margin, e.g. 0.05 = must be 5% better (good for noisy timings)
    repeats: int = 1
    timeout: int = 600
    # type: command
    run: str = ""
    # type: rubric
    rubric: str = ""
    inputs: list[str] = field(default_factory=list)
    models: list[str] = field(default_factory=list)
    samples: int = 1
    pairwise: bool = True

    def better(self, candidate: float, champion: float) -> bool:
        margin = max(self.min_delta, abs(champion) * self.min_gain)
        if self.direction == "maximize":
            return candidate > champion + margin
        return candidate < champion - margin


@dataclass
class AgentSpec:
    use: str = "auto"
    model: Optional[str] = None
    timeout: int = 1200
    command: str = ""  # for `use: command`; `{prompt_file}` and `{workdir}` are substituted
    extra_args: list[str] = field(default_factory=list)


@dataclass
class Budget:
    rounds: int = 10
    minutes: float = 120
    stagnation: int = 5
    target: Optional[float] = None


@dataclass
class Contract:
    name: str
    goal: str
    artifact: list[str]
    judge: JudgeSpec
    agent: AgentSpec
    budget: Budget
    holdout: Optional[JudgeSpec] = None
    context: str = ""
    assets: list[str] = field(default_factory=list)
    root: Path = Path(".")
    digest: str = ""

    @property
    def frozen_files(self) -> list[str]:
        files = [CONTRACT_FILE, *self.judge.files]
        if self.judge.rubric:
            files.append(self.judge.rubric)
        if self.holdout:
            files += self.holdout.files + ([self.holdout.rubric] if self.holdout.rubric else [])
        return list(dict.fromkeys(files))


def _list(value: Any, key: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ContractError(f"`{key}` must be a path or a list of paths")
    return [normalize(v) for v in value]


def _fraction(value: Any) -> float:
    text = str(value).strip()
    return float(text[:-1]) / 100 if text.endswith("%") else float(text)


def _judge(raw: Any, key: str) -> JudgeSpec:
    if not isinstance(raw, dict):
        raise ContractError(f"`{key}` must be a mapping")
    kind = raw.get("type", "command" if "run" in raw else "rubric" if "rubric" in raw else "")
    if kind not in JUDGE_TYPES:
        raise ContractError(f"`{key}.type` must be one of {sorted(JUDGE_TYPES)}")
    spec = JudgeSpec(
        type=kind,
        files=_list(raw.get("files"), f"{key}.files"),
        direction=str(raw.get("direction", "maximize")),
        min_delta=float(raw.get("min_delta", 0.0)),
        min_gain=_fraction(raw.get("min_gain", 0.0)),
        repeats=max(1, int(raw.get("repeats", 1))),
        timeout=int(raw.get("timeout", 600)),
        run=str(raw.get("run", "")),
        rubric=normalize(raw["rubric"]) if raw.get("rubric") else "",
        inputs=_list(raw.get("inputs"), f"{key}.inputs"),
        models=[str(m) for m in (raw.get("models") or [])],
        samples=max(1, int(raw.get("samples", 1))),
        pairwise=bool(raw.get("pairwise", True)),
    )
    if spec.direction not in {"maximize", "minimize"}:
        raise ContractError(f"`{key}.direction` must be maximize or minimize")
    if kind == "command" and not spec.run:
        raise ContractError(f"`{key}.run` is required for a command judge")
    if kind == "rubric" and not (spec.rubric and spec.models):
        raise ContractError(f"`{key}` needs `rubric` and at least one entry in `models`")
    return spec


def load(root: Path, text: Optional[str] = None) -> Contract:
    root = Path(root).resolve()
    path = root / CONTRACT_FILE
    if text is None:
        if not path.is_file():
            raise ContractError(f"no {CONTRACT_FILE} in {root}; run `rsi init` first")
        text = path.read_text(encoding="utf-8")
    try:
        raw = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        raise ContractError(f"{CONTRACT_FILE} is not valid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise ContractError(f"{CONTRACT_FILE} must be a mapping")

    artifact = _list(raw.get("artifact"), "artifact")
    if not artifact:
        raise ContractError("`artifact` must list at least one path the agent may change")
    judge = _judge(raw.get("judge"), "judge")
    holdout = _judge(raw["holdout"], "holdout") if raw.get("holdout") else None
    agent_raw, budget_raw = raw.get("agent") or {}, raw.get("budget") or {}
    contract = Contract(
        name=str(raw.get("name") or root.name),
        goal=str(raw.get("goal") or "").strip(),
        artifact=artifact,
        judge=judge,
        holdout=holdout,
        agent=AgentSpec(
            use=str(agent_raw.get("use", "auto")),
            model=agent_raw.get("model"),
            timeout=int(agent_raw.get("timeout", 1200)),
            command=str(agent_raw.get("command", "")),
            extra_args=[str(a) for a in (agent_raw.get("extra_args") or [])],
        ),
        budget=Budget(
            rounds=int(budget_raw.get("rounds", 10)),
            minutes=float(budget_raw.get("minutes", 120)),
            stagnation=int(budget_raw.get("stagnation", 5)),
            target=float(budget_raw["target"]) if budget_raw.get("target") is not None else None,
        ),
        context=str(raw.get("context") or "").strip(),
        assets=_list(raw.get("assets"), "assets"),
        root=root,
        digest=hashlib.sha256(text.encode("utf-8")).hexdigest()[:12],
    )
    if not contract.goal:
        raise ContractError("`goal` must describe what better means, in plain words")
    for spec in filter(None, [judge, holdout]):
        if spec.type == "rubric" and not spec.inputs:
            spec.inputs = list(artifact)
    clashes = overlap(contract.artifact, contract.frozen_files)
    if clashes:
        raise ContractError("artifact paths overlap frozen judge files: " + "; ".join(clashes))
    return contract
