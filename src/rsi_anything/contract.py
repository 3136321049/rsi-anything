"""The contract (`rsi.yaml`): what may change, who judges, how long to try.

The human owns this file. A run freezes it together with the judge files, so
changing it later starts a new experiment instead of moving the goalposts.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

from .paths import normalize, overlap

CONTRACT_FILE = "rsi.yaml"
JUDGE_TYPES = {"command", "rubric"}   # built in; plugins add more (see plugins.py)
ROLES = ("editor", "judge", "compare", "task")
_NAME = re.compile(r"[A-Za-z0-9][\w.-]*")
_JUDGE_KEYS = {"type", "files", "direction", "min_delta", "min_gain", "repeats", "timeout", "run", "prepare", "rubric",
               "inputs", "models", "compare", "samples", "pairwise", "ties"}


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
    # any type: a command run in the judge workspace first (render a video, build a report...).
    # It may write out/gates.json ({"name": bool}) and out/notes.txt, which join the verdict.
    prepare: str = ""
    # type: rubric
    rubric: str = ""
    inputs: list[str] = field(default_factory=list)
    models: list[str] = field(default_factory=list)
    samples: int = 1
    pairwise: bool = True
    ties: str = "reject"     # or "compare": an equal score is settled by the head-to-head comparison
    compare: list[str] = field(default_factory=list)   # models for head-to-head; empty = the jury itself
    # a plugin judge: every key of the block that rsi does not know
    options: dict[str, Any] = field(default_factory=dict)

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
    outputs: list[str] = field(default_factory=list)  # 评审生成的报告、图表或视频，需要随轮次保存。
    strategy: str = "greedy"  # what a round does (strategy.py); plugins add more
    task_model: str = ""      # roles.task: the model the task itself calls, given to judges as $RSI_TASK_MODEL
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
    kind = str(raw.get("type", "command" if "run" in raw else "rubric" if "rubric" in raw else ""))
    if not _NAME.fullmatch(kind):
        raise ContractError(f"`{key}.type` must be {' or '.join(sorted(JUDGE_TYPES))}, or the name of a judge plugin")
    spec = JudgeSpec(
        type=kind,
        files=_list(raw.get("files"), f"{key}.files"),
        direction=str(raw.get("direction", "maximize")),
        min_delta=float(raw.get("min_delta", 0.0)),
        min_gain=_fraction(raw.get("min_gain", 0.0)),
        repeats=max(1, int(raw.get("repeats", 1))),
        timeout=int(raw.get("timeout", 600)),
        run=str(raw.get("run", "")),
        prepare=str(raw.get("prepare", "")),
        rubric=normalize(raw["rubric"]) if raw.get("rubric") else "",
        inputs=_list(raw.get("inputs"), f"{key}.inputs"),
        models=[str(m) for m in (raw.get("models") or [])],
        samples=max(1, int(raw.get("samples", 1))),
        pairwise=bool(raw.get("pairwise", True)),
        ties=str(raw.get("ties", "reject")),
        compare=[str(m) for m in _models(raw.get("compare"), f"{key}.compare")],
        options={k: v for k, v in raw.items() if k not in _JUDGE_KEYS} if kind not in JUDGE_TYPES else {},
    )
    if spec.direction not in {"maximize", "minimize"}:
        raise ContractError(f"`{key}.direction` must be maximize or minimize")
    if spec.ties not in {"reject", "compare"}:
        raise ContractError(f"`{key}.ties` must be reject or compare")
    if spec.ties == "compare" and not (kind == "rubric" and spec.pairwise):
        raise ContractError(f"`{key}.ties: compare` needs a rubric judge with `pairwise: true`")
    if spec.compare and not (kind == "rubric" and spec.pairwise):
        raise ContractError(f"`{key}.compare` (roles.compare) needs a rubric judge with `pairwise: true`")
    if kind == "command" and not spec.run:
        raise ContractError(f"`{key}.run` is required for a command judge")
    if kind == "rubric" and not (spec.rubric and spec.models):
        raise ContractError(f"`{key}` needs `rubric` and at least one entry in `models`")
    return spec


def _models(value: Any, key: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
        raise ContractError(f"`{key}` must be a model reference or a list of them")
    return value


def _apply_roles(raw: dict) -> tuple[dict, dict, str]:
    """`roles:` says in one place who edits, who judges, who breaks ties and which model the task calls.
    It fills `agent.use/model`, `judge.models` and `judge.compare`; saying the same thing twice must agree."""
    roles = raw.get("roles") or {}
    if not isinstance(roles, dict):
        raise ContractError("`roles` must be a mapping, e.g. {editor: codex, judge: cli:claude}")
    unknown = sorted(set(roles) - set(ROLES))
    if unknown:
        raise ContractError(f"unknown role(s) {', '.join(unknown)}; roles are {', '.join(ROLES)}")
    agent, judge = dict(raw.get("agent") or {}), raw.get("judge")
    if "editor" in roles:
        use, _, model = str(roles["editor"]).partition(":")
        if agent.get("use", use) != use or (model and agent.get("model", model) != model):
            raise ContractError("`roles.editor` and the `agent:` block name different editors; say it once")
        agent["use"] = use
        if model:
            agent["model"] = model
    for role, field_name in (("judge", "models"), ("compare", "compare")):
        if role not in roles:
            continue
        models = _models(roles[role], f"roles.{role}")
        if not isinstance(judge, dict):
            raise ContractError("`judge` must be a mapping")
        if judge.get(field_name) not in (None, models, models[0] if len(models) == 1 else None):
            raise ContractError(f"`roles.{role}` and `judge.{field_name}` disagree; say it once")
        judge = {**judge, field_name: models}
    task = str(roles.get("task") or "").strip()
    return agent, judge, task


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
    agent_raw, judge_raw, task_model = _apply_roles(raw)
    judge = _judge(judge_raw, "judge")
    holdout = _judge(raw["holdout"], "holdout") if raw.get("holdout") else None
    budget_raw = raw.get("budget") or {}
    if (raw.get("roles") or {}).get("judge") and judge.type == "command":
        raise ContractError("`roles.judge` names the models of a rubric judge; a command judge scores itself")
    strategy = str(raw.get("strategy") or "greedy")
    if not _NAME.fullmatch(strategy):
        raise ContractError("`strategy` must be greedy or the name of a strategy plugin")
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
        outputs=_list(raw.get("outputs"), "outputs"),
        strategy=strategy,
        task_model=task_model,
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
