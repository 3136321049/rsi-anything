"""分层边界、可替换的选择规则与搜索策略、运行事件流。"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from rsi_anything import events, ledger, selection, strategy
from rsi_anything.agents import make_agent
from rsi_anything.contract import JudgeSpec, load
from rsi_anything.domain import Decision, Verdict
from rsi_anything.engine import Ratchet

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "rsi_anything"

# 由内到外；外层可以依赖内层，反过来不行。新模块须先归入某一层。
LAYERS = [
    {"domain", "paths", "contract", "degenerate"},                          # 纯数据与规则
    {"selection", "strategy", "events", "prompt", "plugins"},               # 策略：怎么选、怎么搜、怎么播报、插件名册
    {"process", "gitops", "workspace", "artifacts", "ledger", "llm", "result", "sdk", "agents", "judges"},  # 适配：外部世界
    {"engine", "stress", "report", "export", "scaffold", "onboard"},        # 应用：编排一次运行、新建任务、检查本机
    {"cli", "live", "__init__"},                                            # 接口：命令行、实时页面与分享页
]


def _layer(module: str) -> int:
    top = module.split(".")[0]
    return next(i for i, names in enumerate(LAYERS) if top in names)


def _imports(path: Path) -> set[str]:
    rel = path.relative_to(PACKAGE).with_suffix("").parts
    package = list(rel[:-1]) if path.name != "__init__.py" else list(rel[:-1])
    found = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom) and node.level:
            base = package[: len(package) - (node.level - 1)]
            if node.module:
                found.add(".".join(base + node.module.split(".")))
            else:  # `from . import x`: a submodule, or a name defined in the package's __init__
                for alias in node.names:
                    target = PACKAGE.joinpath(*base, alias.name)
                    found.add(".".join(base + [alias.name]) if target.is_dir() or target.with_suffix(".py").is_file()
                              else ".".join(base) or "__init__")
        elif isinstance(node, ast.Import):
            found |= {a.name.removeprefix("rsi_anything.") for a in node.names if a.name.startswith("rsi_anything.")}
    return {name for name in found if name}


def _modules():
    for path in sorted(PACKAGE.rglob("*.py")):
        if "templates" in path.relative_to(PACKAGE).parts:
            continue
        rel = path.relative_to(PACKAGE).with_suffix("")
        name = ".".join(rel.parts[:-1]) if rel.name == "__init__" and len(rel.parts) > 1 else ".".join(rel.parts)
        yield name, path


def test_every_module_belongs_to_a_layer():
    for name, _ in _modules():
        assert any(name.split(".")[0] in layer for layer in LAYERS), f"{name} 未归入任何层"


def test_dependencies_point_inward():
    problems = []
    for name, path in _modules():
        for target in _imports(path):
            if _layer(target) > _layer(name):
                problems.append(f"{name} (layer {_layer(name)}) imports {target} (layer {_layer(target)})")
    assert not problems, "\n".join(problems)


# ---------------------------------------------------------------- selection

SPEC = JudgeSpec(type="command", run="x", min_delta=1)


def test_gates_come_before_score():
    rule = selection.GatesThenScore(SPEC)
    assert rule.decide(None, None, Verdict(9, {"t": False}), Verdict(1)) == Decision(False, "failed gates: t")
    assert rule.decide(None, None, Verdict(1), Verdict(9, {"t": False})).keep
    assert rule.decide(None, None, Verdict(5.5), Verdict(5)).reason.startswith("score 5.5 is not better than 5")
    assert rule.decide(None, None, Verdict(7), Verdict(5)) == Decision(True, "score 5 -> 7")


@pytest.mark.parametrize("comparison, keep, reason", [
    (selection.Comparison(3, 4), True, "score 5 -> 7; head-to-head 3/4"),
    (selection.Comparison(2, 4), False, "higher score but lost head-to-head (2/4 votes)"),
    (selection.Comparison(skipped="pairwise skipped for image inputs"), True,
     "score 5 -> 7 (pairwise skipped for image inputs)"),
    (selection.Comparison(error="timeout"), False, "pairwise check failed: timeout"),
])
def test_head_to_head_stacks_on_the_score_rule(comparison, keep, reason):
    rule = selection.default(SPEC, lambda candidate, champion: comparison)
    assert tuple(rule.decide(None, None, Verdict(7), Verdict(5))) == (keep, reason)


def test_head_to_head_is_not_asked_when_the_score_already_loses():
    def never(*_):
        raise AssertionError("compared although the score lost")
    assert not selection.default(SPEC, never).decide(None, None, Verdict(5), Verdict(5)).keep


# ---------------------------------------------------------------- engine seams

def _ratchet(project, **kwargs):
    contract = load(project)
    return Ratchet(project, contract, make_agent(contract.agent), log=kwargs.pop("log", lambda _: None), **kwargs)


def test_custom_selector_decides_instead_of_the_judge(toy):
    class Contrarian:
        def decide(self, candidate_ws, champion_ws, candidate, champion):
            return Decision(candidate.score < champion.score, "smaller wins here")

    project = toy([{"write": {"value.txt": "5"}}, {"write": {"value.txt": "0"}}], rounds=2)
    summary = _ratchet(project, selector=Contrarian()).run()
    rows = ledger.RunStore(project, summary.run_id).rows()
    assert [(r["status"], r["note"]) for r in rows[1:]] == [("REVERT", "smaller wins here"), ("KEEP", "smaller wins here")]


def test_custom_strategy_plays_the_rounds(toy):
    class Counting(strategy.Greedy):
        name = "counting"
        played = []

        def play(self, arena, number, best):
            self.played.append((number, best))
            return super().play(arena, number, best)

    project = toy([{"write": {"value.txt": "5"}}, {"write": {"value.txt": "7"}}], rounds=2)
    summary = _ratchet(project, strategy=Counting()).run()
    assert Counting.played == [(1, 1), (2, 5)] and summary.best == 7
    assert ledger.RunStore(project, summary.run_id).meta()["strategy"] == "counting"
    with pytest.raises(ValueError):
        strategy.make_strategy("population")


def test_run_streams_events_and_prints_the_same_lines(toy):
    project = toy([{"write": {"value.txt": "5"}, "hypothesis": "bigger"}, {"write": {"other.txt": "x"}}], rounds=2)
    lines, seen = [], []

    class Collect:
        def emit(self, event):
            seen.append(event["type"])

    summary = _ratchet(project, log=lines.append, events=(Collect(),)).run()
    store = ledger.RunStore(project, summary.run_id)
    recorded = events.read(store.dir / "events.jsonl")
    assert [e["type"] for e in recorded] == seen == [
        "run_started", "round_finished",
        "round_started", "agent_finished", "judged", "round_finished",
        "round_started", "agent_finished", "round_finished", "run_finished"]
    assert recorded[-1]["best"] == 5 and recorded[1]["row"]["status"] == "BASELINE"
    assert lines[1:] == ["r0  BASELINE  score 1", "r1  command is working...", "r1  KEEP       score 5  bigger",
                         "r2  command is working...",
                         "r2  NO_CHANGE  no edits inside the artifact paths; ignored 1 other edits"]
    assert store.meta()["schema"] == ledger.SCHEMA_VERSION
    toolkit = json.loads((store.dir / "config/execution.json").read_text())["rsi_anything"]
    assert len(toolkit["sdk_sha256"]) == 64 and "version" in toolkit


def test_failed_run_reports_through_events(toy):
    project = toy([{"write": {"value.txt": "5"}}], rounds=1)
    (project / "judge.py").write_text("raise SystemExit(1)\n")
    from conftest import git
    git(project, "commit", "-qam", "break the judge")
    with pytest.raises(Exception):
        _ratchet(project).run()
    store = ledger.RunStore(project, ledger.list_runs(project)[0])
    last = events.read(store.dir / "events.jsonl")[-1]
    assert last["type"] == "run_failed" and last["status"] == "failed" and "cannot score" in last["error"]


def test_half_written_event_line_is_skipped(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(json.dumps({"type": "run_started"}) + "\n" + '{"type": "rou')
    assert [e["type"] for e in events.read(path)] == ["run_started"]


@pytest.mark.parametrize("comparison, keep, reason", [
    (selection.Comparison(2, 2), True, "tied at 75; won head-to-head 2/2"),
    (selection.Comparison(1, 2), False, "tied at 75 and lost head-to-head (1/2 votes)"),
])
def test_ties_can_be_settled_head_to_head(comparison, keep, reason):
    rule = selection.default(SPEC, lambda *_: comparison, ties=True)
    tie = Verdict(75), Verdict(75)
    assert tuple(rule.decide(None, None, *tie)) == (keep, reason)
    # 默认规则下平分直接拒绝，不额外比较。
    assert not selection.default(SPEC, lambda *_: pytest.fail("compared a tie")).decide(None, None, *tie).keep
    # 低于幅度要求但高于对方，也算平分；明显更差则不比较。
    assert rule.decide(None, None, Verdict(75.5), Verdict(75)).keep == keep
    assert selection.default(SPEC, lambda *_: pytest.fail("compared a loss"), ties=True).decide(
        None, None, Verdict(70), Verdict(75)).reason.startswith("score 70 is not better")


def test_ties_compare_needs_a_pairwise_rubric(tmp_path):
    from rsi_anything.contract import ContractError
    (tmp_path / "rsi.yaml").write_text("goal: g\nartifact: [a.txt]\njudge: {run: x, ties: compare}\n")
    with pytest.raises(ContractError, match="ties"):
        load(tmp_path)


def test_runs_started_in_the_same_second_get_separate_folders(toy, monkeypatch):
    project = toy([{"write": {"value.txt": "5"}}, {"write": {"value.txt": "6"}}], rounds=1)
    monkeypatch.setattr(ledger.time, "strftime", lambda _: "20261029-120000")
    first, second = (_ratchet(project).run().run_id for _ in range(2))
    assert (first, second) == ("20261029-120000-toy", "20261029-120000-toy-2")
