from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from core.controller import run_ratchet_loop
from core.guard import parse_goal, snapshot_hashes, verify_guard
from core.judge import run_evaluator
from core.memory import append_lesson, append_result, init_ledger, read_lessons
from core.rubric_inducer import evaluate_markdown_with_rubric, induce_rubric
from core.worktree import claim_task_lock, create_worktree, release_task_lock, remove_worktree


def test_goal_and_guard(tmp_path):
    goal = tmp_path / "GOAL.md"
    goal.write_text("""---
name: "Example"
track: demo
direction: maximize
target_score: 9.5
max_iterations: 3
eval_cmd: "python3 eval.py"
mutable_paths: [a.py, "dir/b.py"]
frozen_paths:
  - test.py
upstream_credits: []
enabled: true
---
# Body
""")
    parsed = parse_goal(goal)
    assert parsed["mutable_paths"] == ["a.py", "dir/b.py"] and parsed["enabled"] is True
    assert parsed["target_score"] == 9.5 and parsed["body"].startswith("# Body")
    (tmp_path / "test.py").write_text("safe")
    frozen = snapshot_hashes(tmp_path, ["test.py"])
    assert verify_guard(tmp_path, frozen, ["a.py"], ["a.py"])[0]
    assert not verify_guard(tmp_path, frozen, ["a.py"], ["other.py"])[0]
    (tmp_path / "test.py").write_text("bad")
    assert not verify_guard(tmp_path, frozen, ["a.py"])[0]
    (tmp_path / "test.py").unlink()
    assert not verify_guard(tmp_path, frozen, ["a.py"])[0]


def test_memory(tmp_path):
    init_ledger(tmp_path)
    append_result(tmp_path, 0, "BASELINE", 1, 1, "BASELINE")
    append_lesson(tmp_path, "first")
    append_lesson(tmp_path, "second")
    assert (tmp_path / "results.tsv").read_text().startswith("round\ttimestamp")
    assert read_lessons(tmp_path, 1).endswith("second")


def test_judge_json_score_and_error(tmp_path):
    cmd = """python3 -c 'import json; print(json.dumps({"score":7.5,"passed_gates":True,"critique":{"x":1}}))'"""
    result = run_evaluator(tmp_path, cmd)
    assert result.score == 7.5 and result.passed_gates and result.critique["x"] == 1
    assert run_evaluator(tmp_path, """python3 -c 'print("SCORE: 4.25")'""").score == 4.25
    assert not run_evaluator(tmp_path, "python3 -c 'print(123)'").passed_gates


def test_rubric():
    rubric = induce_rubric("finance", "risk")
    assert not evaluate_markdown_with_rubric("# Executive Summary\nObviously great.", rubric)["passed_gates"]
    words = " ".join(["measured analysis"] * 200)
    text = (f"# Executive Summary\n{words} [SRC-1] [SRC-2] [SRC-3]\n"
            "# Bear Case\nRisk.\n# Sources\n| Source | Claim |\n|---|---|\n| A | B |\n")
    assert evaluate_markdown_with_rubric(text, rubric)["score"] == 100


def test_chinese_fluff_and_bad_share_math():
    rubric = induce_rubric("finance", "机器人")
    words = " ".join(["measured analysis"] * 200)
    text = (f"# Executive Summary\n{words} 众所周知 [SRC-1] [SRC-2] [SRC-3]\n"
            "# Bear Case\nRisk.\n# Sources\n| 占比 |\n|---|\n| 40% |\n| 40% |\n")
    result = evaluate_markdown_with_rubric(text, rubric)
    assert not result["passed_gates"]
    assert any("众所周知" in item for item in result["violations"])
    assert any("100" in item for item in result["violations"])
    assert result["suggestions"]


def test_lock_and_worktree(tmp_path):
    assert claim_task_lock(tmp_path, "task one") and not claim_task_lock(tmp_path, "task one")
    release_task_lock(tmp_path, "task one")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / "x").write_text("x")
    subprocess.run(["git", "add", "x"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)
    assert (create_worktree(repo, "trial") / "x").exists()
    remove_worktree(repo, "trial")


def test_ratchet_keep_score_revert_and_guard(tmp_path):
    (tmp_path / "value.txt").write_text("1")
    evaluator = tmp_path / "eval.py"
    evaluator.write_text("import json\nscore=float(open('value.txt').read())\n"
                         "print(json.dumps({'score':score,'passed_gates':score>=0}))\n")
    (tmp_path / "GOAL.md").write_text("""---
name: Ratchet test
track: test
direction: maximize
target_score: 99
max_iterations: 3
eval_cmd: "python3 eval.py"
mutable_paths: [value.txt]
frozen_paths: [eval.py]
upstream_credits: []
---
""")
    steps = [{"hypothesis": "improve", "files": {"value.txt": "2"}},
             {"hypothesis": "regress", "files": {"value.txt": "0"}},
             {"hypothesis": "tamper", "files": {"eval.py": "# hacked"}}]
    assert run_ratchet_loop(tmp_path, steps=steps)["best_score"] == 2
    assert (tmp_path / "value.txt").read_text() == "2" and "score=float" in evaluator.read_text()
    rows = (tmp_path / "results.tsv").read_text().splitlines()[1:]
    assert [row.split("\t")[5] for row in rows] == ["BASELINE", "KEEP", "REVERT_SCORE", "REVERT_GUARD"]


def test_security_and_hardening_guards(tmp_path):
    import pytest

    # 1. Path traversal in task_id is rejected
    with pytest.raises(ValueError):
        claim_task_lock(tmp_path, "..")
    with pytest.raises(ValueError):
        claim_task_lock(tmp_path, "../escape")

    # 2. Dotfile (.env) is NOT conflated with env in verify_guard
    (tmp_path / "eval.py").write_text("pass")
    frozen = snapshot_hashes(tmp_path, ["eval.py"])
    assert not verify_guard(tmp_path, frozen, ["env"], [".env"])[0]
    assert not verify_guard(tmp_path, frozen, ["env"], ["../secret.txt"])[0]

    # 3. Malformed JSON score type is handled safely
    bad_cmd = """python3 -c 'import json; print(json.dumps({"score":[1],"passed_gates":True}))'"""
    res = run_evaluator(tmp_path, bad_cmd)
    assert res.score == 0.0 and not res.passed_gates

    # 4. Table-less pipe lines do not satisfy require_table
    rubric = induce_rubric("finance", "risk")
    words = " ".join(["measured analysis"] * 200)
    fake_table = (f"# Executive Summary\n{words} [SRC-1] [SRC-2] [SRC-3]\n"
                  "# Bear Case\nRisk.\n# Sources\n| 占比 | 40% | 40% |\n")
    r_fake = evaluate_markdown_with_rubric(fake_table, rubric)
    assert not r_fake["passed_gates"]
    assert "missing markdown table" in r_fake["violations"]

    # 5. Pre-existing unrelated files survive a REVERT_GUARD round
    (tmp_path / "notes_untouched.txt").write_text("keep me")
    (tmp_path / "value.txt").write_text("1")
    (tmp_path / "eval.py").write_text(
        "import json\nscore=float(open('value.txt').read())\n"
        "print(json.dumps({'score':score,'passed_gates':True}))\n"
    )
    (tmp_path / "GOAL.md").write_text("""---
name: Preserve unrelated
track: test
direction: maximize
target_score: 99
max_iterations: 1
eval_cmd: "python3 eval.py"
mutable_paths: [value.txt]
frozen_paths: [eval.py]
upstream_credits: []
---
""")
    steps = [{"hypothesis": "modify unrelated", "files": {"notes_untouched.txt": "hacked"}}]
    run_ratchet_loop(tmp_path, steps=steps)
    assert (tmp_path / "notes_untouched.txt").read_text() == "keep me"

    # 6. Eval-time tampering of frozen file or results.tsv is caught and reverted
    (tmp_path / "eval.py").write_text(
        "import json, pathlib\n"
        "exec(open('value.txt').read())\n"
        "print(json.dumps({'score': 99.0, 'passed_gates': True}))\n"
    )
    (tmp_path / "value.txt").write_text("pass\n")
    (tmp_path / "GOAL.md").write_text("""---
name: Eval tamper test
track: test
direction: maximize
target_score: 100
max_iterations: 2
eval_cmd: "python3 eval.py"
mutable_paths: [value.txt]
frozen_paths: [eval.py]
upstream_credits: []
---
""")
    steps = [
        {"hypothesis": "overwrite frozen file during eval",
         "files": {"value.txt": "open('eval.py', 'w').write('# tampered during eval\\n')\n"}},
        {"hypothesis": "forge results.tsv during eval",
         "files": {"value.txt": "open('results.tsv', 'w').write('forged\\n')\n"}},
    ]
    res_tamper = run_ratchet_loop(tmp_path, steps=steps)
    assert [r["status"] for r in res_tamper["rounds"]] == ["BASELINE", "REVERT_GUARD", "REVERT_GUARD"]
    assert "exec(open('value.txt')" in (tmp_path / "eval.py").read_text()
    assert (tmp_path / "results.tsv").read_text().startswith("round\ttimestamp\thypothesis")


