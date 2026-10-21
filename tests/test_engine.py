from __future__ import annotations

from rsi_anything import ledger
from rsi_anything.agents import make_agent
from rsi_anything.contract import load
from rsi_anything.engine import Ratchet

from conftest import git


def run(project, **overrides):
    contract = load(project)
    for key, value in overrides.items():
        setattr(contract.budget, key, value)
    ratchet = Ratchet(project, contract, make_agent(contract.agent), log=lambda _: None)
    summary = ratchet.run()
    rows = ledger.RunStore(ratchet.repo, summary.run_id).rows()
    return summary, rows


def statuses(rows):
    return [r["status"] for r in rows]


def test_keeps_gains_and_reverts_losses(toy):
    project = toy([
        {"write": {"value.txt": "5"}, "hypothesis": "bigger"},
        {"write": {"value.txt": "3"}, "hypothesis": "smaller"},
        {"write": {"value.txt": "9"}, "hypothesis": "much bigger"},
    ])
    summary, rows = run(project)
    assert statuses(rows) == ["BASELINE", "KEEP", "REVERT", "KEEP"]
    assert [r["best"] for r in rows] == [1, 5, 5, 9]
    # The champion lives on the run branch as real commits; the user's checkout is untouched.
    assert git(project, "show", f"{summary.branch}:value.txt") == "9"
    assert (project / "value.txt").read_text().strip() == "1"
    log = git(project, "log", "--format=%s", summary.branch)
    assert "rsi r3: much bigger (5 -> 9)" in log and "smaller" not in log


def test_editing_the_judge_has_no_effect(toy):
    cheat = "import json, os\njson.dump({'score': 1000}, open(os.environ['RSI_RESULT'], 'w'))\n"
    project = toy([{"write": {"judge.py": cheat, "value.txt": "2"}, "hypothesis": "rewrite judge"}], rounds=1)
    summary, rows = run(project)
    last = rows[-1]
    assert last["status"] == "KEEP" and last["score"] == 2  # scored by the frozen judge, not the rewrite
    assert last["ignored"] == ["judge.py"]
    assert "1000" not in git(project, "show", f"{summary.branch}:judge.py")


def test_printed_scores_are_ignored(toy):
    # Artifact text that looks like a score on stdout cannot fool a result-file judge.
    project = toy([{"write": {"value.txt": "0"}, "say": '{"score": 999}', "hypothesis": "spoof"}], rounds=1)
    _, rows = run(project)
    assert rows[-1]["status"] == "REVERT" and rows[-1]["score"] == 0


def test_only_out_of_scope_edits_is_no_change(toy):
    project = toy([{"write": {"notes.md": "hello"}, "hypothesis": "wrong file"}], rounds=1)
    _, rows = run(project)
    assert rows[-1]["status"] == "NO_CHANGE"


def test_failed_gate_blocks_a_higher_score(toy):
    project = toy([{"write": {"value.txt": "-1"}}, {"write": {"value.txt": "4"}}], rounds=2)
    _, rows = run(project)
    assert statuses(rows) == ["BASELINE", "REVERT", "KEEP"]


def test_agent_failure_is_recorded_not_fatal(toy):
    project = toy([{"exit": 3}, {"write": {"value.txt": "2"}}], rounds=2)
    _, rows = run(project)
    assert statuses(rows) == ["BASELINE", "AGENT_FAIL", "KEEP"]


def test_stops_after_stagnation(toy):
    project = toy([{"write": {"value.txt": "0"}}] * 5, rounds=10, stagnation=2)
    summary, rows = run(project)
    assert len(rows) == 3 and "no improvement" in summary.stop_reason


def test_planted_bytecode_is_stripped(toy):
    # A candidate cannot ship a cache file that shadows frozen code inside the judge workspace.
    project = toy([], rounds=0)
    (project / "helper.py").write_text("VALUE = 1\n")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "helper")
    from rsi_anything import workspace

    ws = workspace.build(project, git(project, "rev-parse", "HEAD"), {},
                         overlay={"__pycache__/helper.cpython-39.pyc": b"junk", "value.txt": b"3"})
    try:
        assert not (ws / "__pycache__").exists()
        assert (ws / "value.txt").read_text() == "3"
    finally:
        workspace.discard(ws)


def test_lessons_carry_over_between_runs(toy):
    project = toy([{"write": {"value.txt": "0"}, "hypothesis": "try zero"}], rounds=1)
    run(project)
    lessons = ledger.read_lessons(project, "toy")
    assert any("try zero" in line for line in lessons)
