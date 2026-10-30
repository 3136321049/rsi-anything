"""Plugins add judge types, agents and strategies by name; `roles:` says who does what in one place."""
import json
import os
import sys
from importlib import metadata

import pytest
from conftest import git

from rsi_anything import cli, ledger, plugins, strategy
from rsi_anything.agents import make_agent
from rsi_anything.agents.registry import AGENTS, CLI_AGENTS
from rsi_anything.agents.cli import CLIAgent
from rsi_anything.contract import ContractError, load
from rsi_anything.engine import Ratchet, task_model
from rsi_anything.judges import JUDGES, Judge, Verdict, make_judge
from rsi_anything.judges.rubric import RubricJudge


@pytest.fixture
def registered():
    """Registrations made in a test are removed afterwards."""
    added = []

    def add(registry, name, item):
        registry.register(name, item)
        added.append((registry, name))
    yield add
    for registry, name in added:
        registry._items.pop(name, None)
        registry._origins.pop(name, None)


class FixedJudge(Judge):
    """Scores whatever `value` the contract gives it; proves plugin options arrive."""

    def score(self, workspace, round_no):
        return Verdict(float(self.spec.options["value"]), {"ok": True}, "fixed")


def test_registry_lookup_decorator_and_errors(registered):
    registry = plugins.Registry("rsi_anything.tests-nothing", "widget")

    @registry.register("square")
    def square(x):
        return x * x
    assert registry.get("square")(3) == 9 and square(2) == 4
    assert registry.names() == ["square"] and registry.origins() == {"square": "registered"}
    with pytest.raises(plugins.PluginError, match="unknown widget 'cube'; available: square"):
        registry.get("cube")
    assert issubclass(plugins.PluginError, ValueError)
    with pytest.raises(ValueError):  # unknown strategies still raise ValueError
        strategy.make_strategy("population")


def test_entry_points_load_on_first_use(tmp_path, monkeypatch):
    (tmp_path / "rsi_demo_plugin.py").write_text("class Shout:\n    name = 'shout'\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    good = metadata.EntryPoint("shout", "rsi_demo_plugin:Shout", "rsi_anything.strategies")
    bad = metadata.EntryPoint("broken", "rsi_demo_missing:Nope", "rsi_anything.strategies")
    registry = plugins.Registry("rsi_anything.strategies", "strategy")
    monkeypatch.setattr(registry, "_points", lambda: [good, bad])
    assert registry.names() == ["shout", "broken"]
    assert registry.get("shout").name == "shout"
    assert registry.origins()["shout"].startswith("package")
    with pytest.raises(plugins.PluginError, match="failed to load"):
        registry.get("broken")


def test_plugin_judge_gets_its_own_options(tmp_path, registered):
    registered(JUDGES, "fixed", FixedJudge)
    (tmp_path / "a.txt").write_text("x")
    contract = load(tmp_path, "goal: g\nartifact: [a.txt]\njudge: {type: fixed, value: 42, files: [j]}\n")
    assert contract.judge.type == "fixed" and contract.judge.options == {"value": 42}
    assert make_judge(contract.judge).evaluate(tmp_path, 0).score == 42
    with pytest.raises(plugins.PluginError, match="unknown judge type 'vision'; available: command, rubric"):
        make_judge(load(tmp_path, "goal: g\nartifact: [a.txt]\njudge: {type: vision}\n").judge)
    with pytest.raises(ContractError, match="name of a judge plugin"):
        load(tmp_path, "goal: g\nartifact: [a.txt]\njudge: {type: 'two words'}\n")


def test_plugin_agent_and_cli_spec(registered):
    from rsi_anything.contract import AgentSpec

    made = []
    registered(AGENTS, "scripted", lambda spec, allow: made.append((spec.use, allow)) or "an agent")
    assert make_agent(AgentSpec(use="scripted"), allow_commands=True) == "an agent" and made == [("scripted", True)]
    registered(AGENTS, "claude-clone", CLI_AGENTS["claude"])
    assert isinstance(make_agent(AgentSpec(use="claude-clone", model="m")), CLIAgent)
    with pytest.raises(RuntimeError, match="unknown agent 'nobody'; choose from auto, api, command, claude"):
        make_agent(AgentSpec(use="nobody"))


def test_contract_strategy_drives_the_engine(toy, registered):
    played = []

    class Counting(strategy.Greedy):
        name = "counting"

        def play(self, arena, number, best):
            played.append(number)
            return super().play(arena, number, best)

    registered(strategy.STRATEGIES, "counting", Counting)
    project = toy([{"write": {"value.txt": "5"}}], rounds=1)
    (project / "rsi.yaml").write_text((project / "rsi.yaml").read_text() + "strategy: counting\n")
    git(project, "commit", "-qam", "use the counting strategy")
    contract = load(project)
    summary = Ratchet(project, contract, make_agent(contract.agent), log=lambda _: None).run()
    assert played == [1] and ledger.RunStore(project, summary.run_id).meta()["strategy"] == "counting"


def test_roles_fill_agent_judge_compare_and_task(tmp_path):
    rubric = "judge: {rubric: r.yaml, files: [r.yaml]}\n"
    text = ("goal: g\nartifact: [a.md]\n" + rubric +
            "roles:\n  editor: codex:gpt-x\n  judge: cli:claude\n  compare: [cli:codex, cli:claude]\n  task: deepseek:deepseek-chat\n")
    contract = load(tmp_path, text)
    assert (contract.agent.use, contract.agent.model) == ("codex", "gpt-x")
    assert contract.judge.models == ["cli:claude"] and contract.judge.compare == ["cli:codex", "cli:claude"]
    assert contract.task_model == "deepseek:deepseek-chat"
    assert RubricJudge(contract.judge).compare_models == ["cli:codex", "cli:claude"]
    assert RubricJudge(load(tmp_path, "goal: g\nartifact: [a.md]\n" + rubric + "roles: {judge: cli:claude}\n").judge).compare_models == ["cli:claude"]
    # saying the same thing twice is fine; saying two different things is not
    assert load(tmp_path, "goal: g\nartifact: [a.md]\njudge: {rubric: r.yaml, models: [cli:claude]}\n"
                          "agent: {use: codex}\nroles: {editor: codex, judge: cli:claude}\n").agent.use == "codex"
    judged = "judge: {rubric: r.yaml, models: [cli:claude]}\n"
    for body, message in (("agent: {use: claude}\nroles: {editor: codex}\n" + judged, "say it once"),
                          ("roles: {editor: codex, writer: x}\n" + judged, "unknown role"),
                          ("roles: {judge: [cli:claude], compare: [cli:codex]}\njudge: {rubric: r.yaml, pairwise: false}\n", "pairwise"),
                          ("roles: {judge: cli:claude}\njudge: {run: python j.py}\n", "command judge"),
                          ("roles: [codex]\n" + judged, "must be a mapping")):
        with pytest.raises(ContractError, match=message):
            load(tmp_path, "goal: g\nartifact: [a.md]\n" + body)


def test_task_role_reaches_judges_and_is_restored(monkeypatch, tmp_path):
    monkeypatch.setenv("RSI_TASK_MODEL", "from-shell")
    contract = load(tmp_path, "goal: g\nartifact: [a]\njudge: {run: x}\nroles: {task: from-contract}\n")
    with task_model(contract):
        assert os.environ["RSI_TASK_MODEL"] == "from-contract"
    assert os.environ["RSI_TASK_MODEL"] == "from-shell"
    monkeypatch.delenv("RSI_TASK_MODEL")
    with task_model(contract):
        pass
    assert "RSI_TASK_MODEL" not in os.environ


def test_execution_records_roles(toy):
    project = toy([{"write": {"value.txt": "3"}}], rounds=1)
    contract = load(project)
    summary = Ratchet(project, contract, make_agent(contract.agent), log=lambda _: None).run()
    execution = json.loads((ledger.RunStore(project, summary.run_id).dir / "config/execution.json").read_text())
    assert execution["roles"]["editor"] == "command" and execution["roles"]["judge"] == "command"


def test_plugins_command_lists_everything(capsys, registered):
    registered(JUDGES, "fixed", FixedJudge)
    assert cli.main(["plugins"]) == 0
    out = capsys.readouterr().out
    assert "built-in: command, rubric" in out and "registered: fixed" in out and "built-in: greedy" in out
