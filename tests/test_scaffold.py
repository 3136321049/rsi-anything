"""`rsi new` must write tasks that run as written, and `rsi setup` must only change what it is asked to."""
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from rsi_anything import cli, contract, onboard, scaffold, sdk
from rsi_anything.agents import CLI_AGENTS
from rsi_anything.judges import make_judge


@pytest.fixture(autouse=True)
def git_identity(monkeypatch):
    for key in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{key}_NAME", "rsi test")
        monkeypatch.setenv(f"GIT_{key}_EMAIL", "rsi@example.invalid")


def plan(kind, **extra):
    base = {"text": dict(artifact=["post.md"], criteria=["hook", "clarity"]),
            "visual": dict(artifact=["page.html"], criteria=["first impression", "layout"]),
            "tests": dict(artifact=["calc.py"], command="pytest -q", frozen=["tests"]),
            "number": dict(artifact=["fast.py"], command="python bench.py", maximize=False)}[kind]
    return scaffold.Plan(kind=kind, goal="Make it better for its readers.", **{**base, **extra})


@pytest.mark.parametrize("kind", list(scaffold.KINDS))
def test_every_kind_writes_a_valid_contract_and_python(kind, tmp_path):
    files = scaffold.files(plan(kind))
    loaded = contract.load(tmp_path, files["rsi.yaml"])
    assert loaded.goal and loaded.budget.rounds == 5
    for name, text in files.items():
        if name.endswith(".py"):
            compile(text, name, "exec")
    if kind in ("text", "visual"):
        rubric = yaml.safe_load(files["judge/rubric.yaml"])
        assert sum(c["weight"] for c in rubric["criteria"]) == 100
        assert loaded.judge.type == "rubric" and loaded.judge.ties == "compare"
    else:
        assert loaded.judge.type == "command" and "tests" not in loaded.artifact
    if kind == "number":
        assert loaded.judge.direction == "minimize"
    if kind == "visual":
        assert loaded.judge.inputs == ["out/desktop.png", "out/mobile.png", "out/page.txt"]
        assert contract.load(tmp_path, scaffold.files(plan("visual", artifact=["art.svg"]))["rsi.yaml"]).judge.inputs == ["out/picture.png"]


def test_plan_problems_are_reported_before_writing(tmp_path):
    assert scaffold.Plan(kind="visual", artifact=["notes.md"], goal="x", criteria=["a"]).problems() == \
        ["a visual task edits exactly one .svg or .html file"]
    assert "a tests task needs the command to run" in scaffold.Plan(kind="tests", artifact=["a.py"], goal="x").problems()
    with pytest.raises(ValueError, match="frozen judge files"):  # the agent may not edit what judges it
        scaffold.write(plan("tests", artifact=["tests/test_calc.py"]), tmp_path)
    assert not (tmp_path / "rsi.yaml").exists()


def _project(root, files):
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text, encoding="utf-8")


def test_tests_task_scores_the_share_of_passing_tests(tmp_path):
    _project(tmp_path, {"calc.py": "def add(a, b):\n    return a - b\n\ndef neg(a):\n    return -a\n",
                        "tests/test_calc.py": "from calc import add, neg\n\ndef test_add():\n    assert add(2, 2) == 4\n\n"
                                              "def test_neg():\n    assert neg(3) == -3\n"})
    code = cli.main(["new", str(tmp_path), "--kind", "tests", "--artifact", "calc.py", "--frozen", "tests",
                     "--command", f"{sys.executable} -m pytest -q -p no:cacheprovider tests", "--goal", "Fix calc.py.", "--yes"])
    assert code == 0
    assert (tmp_path / "calc.py").read_text().startswith("def add")       # work files are never overwritten
    loaded = contract.load(tmp_path)
    verdict = make_judge(loaded.judge).evaluate(tmp_path, 0)
    assert verdict.ok and verdict.score == 50 and verdict.gates["tests_ran"]
    assert "1/2 tests pass" in verdict.feedback
    log = subprocess.run(["git", "log", "--oneline"], cwd=tmp_path, capture_output=True, text=True).stdout
    assert "start an rsi task" in log


def test_number_task_reads_the_last_number(tmp_path):
    _project(tmp_path, {"fast.py": "print('warming up 3 items')\nprint(41.5)\n"})
    assert cli.main(["new", str(tmp_path), "--kind", "number", "--artifact", "fast.py", "--command",
                     f"{sys.executable} fast.py", "--goal", "Bigger is better.", "--yes"]) == 0
    verdict = make_judge(contract.load(tmp_path).judge).evaluate(tmp_path, 0)
    assert verdict.score == 41.5 and verdict.gates["command_ok"]
    (tmp_path / "fast.py").write_text("raise SystemExit(2)\n")
    assert make_judge(contract.load(tmp_path).judge).evaluate(tmp_path, 0).gates["command_ok"] is False


def test_new_refuses_an_existing_task(tmp_path, capsys):
    (tmp_path / "rsi.yaml").write_text("name: mine\n")
    assert cli.main(["new", str(tmp_path), "--kind", "text", "--goal", "x", "--yes"]) == 2
    assert "already exists" in capsys.readouterr().err
    assert (tmp_path / "rsi.yaml").read_text() == "name: mine\n"


def test_new_asks_for_what_is_missing(tmp_path, monkeypatch, capsys):
    answers = iter(["2", "art.svg", "A lighthouse at dusk, calm and clear.", "subject, mood"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    assert cli.main(["new", str(tmp_path / "lighthouse")]) == 0
    task = tmp_path / "lighthouse"
    loaded = contract.load(task)
    assert loaded.artifact == ["art.svg"] and loaded.name == "lighthouse"
    assert [c["name"] for c in yaml.safe_load((task / "judge/rubric.yaml").read_text())["criteria"]] == ["subject", "mood"]
    assert (task / "art.svg").read_text().startswith("<svg")
    out = capsys.readouterr().out
    assert "rsi check --stress" in out and "rsi setup" in out


@pytest.mark.skipif(not sdk.find_browser(), reason="needs a Chrome-family browser")
def test_visual_task_renders_its_starting_file(tmp_path):
    for source, outputs in (("art.svg", ["picture.png"]), ("page.html", ["desktop.png", "mobile.png", "page.txt"])):
        task = tmp_path / source.split(".")[0]
        task.mkdir()
        scaffold.write(plan("visual", artifact=[source]), task)
        run = subprocess.run([sys.executable, "judge/render.py"], cwd=task, capture_output=True, text=True)
        assert run.returncode == 0, run.stderr
        assert all(json.loads((task / "out/gates.json").read_text()).values())
        assert all((task / "out" / name).stat().st_size > 0 for name in outputs)


def test_setup_suggests_two_vendors_and_installs_only_when_asked(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(onboard, "detect", lambda check=True: [CLI_AGENTS["claude"], CLI_AGENTS["codex"]])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    assert onboard.pairing(["claude", "codex"]) == ("codex", "claude")
    assert onboard.pairing(["claude"]) == ("claude", "claude")
    assert onboard.pairing(["kimi", "qwen"]) == ("kimi", "qwen")
    cli.main(["setup", "--check"])
    out = capsys.readouterr().out
    assert "suggested: codex edits, claude judges" in out and "RSI_AGENT=codex RSI_JURY=cli:claude" in out
    assert not (tmp_path / ".claude").exists()                       # --check never writes
    cli.main(["setup"])
    assert "rsi setup --yes" in capsys.readouterr().out and not (tmp_path / ".claude").exists()
    cli.main(["setup", "--yes"])
    for agent in ("claude", "codex"):
        assert (tmp_path / f".{agent}/skills/rsi/SKILL.md").read_bytes() == onboard.SKILL.read_bytes()
    capsys.readouterr()
    cli.main(["setup", "--check"])
    assert "up to date" in capsys.readouterr().out
