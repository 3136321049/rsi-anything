from __future__ import annotations

def test_separate_verbatim_evidence_quotes_are_checked_individually():
    from rsi_anything.judges.rubric import _quote_found
    artifact = "赶地铁先约时段。\n修车先报价，经同意再换。\n陶艺作品两周后领取。"
    assert _quote_found('“赶地铁先约时段”“修车先报价，经同意再换”“陶艺作品两周后领取”', artifact)
    assert _quote_found(["赶地铁先约时段", "陶艺作品两周后领取"], artifact)
    assert not _quote_found('“赶地铁先约时段”“当天领取陶艺作品”', artifact)
    assert not _quote_found([], artifact)


def test_prepare_service_failure_does_not_become_quality_zero(tmp_path):
    from rsi_anything.contract import JudgeSpec
    from rsi_anything.judges.base import Judge
    (tmp_path / "prep.py").write_text(
        'import json, pathlib, sys\npathlib.Path("out").mkdir()\n'
        'pathlib.Path("out/error.json").write_text(json.dumps({"quality_result":"unknown","stage":"generation","error":"quota unavailable"}))\nsys.exit(2)\n')
    verdict = Judge(JudgeSpec(type="command", prepare="{python} prep.py")).evaluate(tmp_path, 0)
    assert verdict.score is None and "quota unavailable" in verdict.error
    assert verdict.metrics["quality_result"] == "unknown"

import json
import textwrap

import pytest

from rsi_anything import llm
from rsi_anything.contract import JudgeSpec
from rsi_anything.judges.base import Verdict
from rsi_anything.judges.rubric import RubricJudge

RUBRIC = textwrap.dedent("""\
    task: A short product post.
    context: [brief.md]
    criteria:
      - {name: hook, weight: 60, question: "Does it grab attention?"}
      - {name: facts, weight: 40, question: "Are facts right?"}
    gates: {min_chars: 10, must_not_include: ["best ever"]}
    checks: ["No invented numbers."]
    """)


@pytest.fixture
def workspace(tmp_path):
    (tmp_path / "rubric.yaml").write_text(RUBRIC)
    (tmp_path / "brief.md").write_text("Price is 129.")
    (tmp_path / "post.md").write_text("A calm night desk for 129 a month.")
    return tmp_path


def judge(models=("fake:a", "fake:b"), pairwise=True):
    spec = JudgeSpec(type="rubric", rubric="rubric.yaml", inputs=["post.md"], models=list(models), pairwise=pairwise)
    return RubricJudge(spec)


def fake_ask(score_by_model, manipulation=False, winner="A", seen=None, evidence="calm night desk"):
    def ask(ref, prompt, system="", images=None, timeout=600, json_mode=False):
        if seen is not None:
            seen.append(prompt)
        if "Which version better" in prompt:
            return llm.Reply(json.dumps({"winner": winner(prompt) if callable(winner) else winner}))
        score = score_by_model[ref.raw]
        return llm.Reply(json.dumps({
            "criteria": {"hook": {"score": score, "evidence": evidence}, "facts": {"score": score, "evidence": evidence}},
            "checks": {"No invented numbers.": {"pass": True}},
            "manipulation": manipulation, "top_fix": "sharper first line"}))
    return ask


@pytest.fixture(autouse=True)
def fake_models(monkeypatch):
    real_parse = llm.parse
    monkeypatch.setattr(llm, "parse", lambda spec: llm.ModelRef(spec, "api", "fake", spec) if spec.startswith("fake:") else real_parse(spec))


def test_jury_average_gates_and_context(monkeypatch, workspace):
    seen = []
    monkeypatch.setattr(llm, "ask", fake_ask({"fake:a": 8, "fake:b": 6}, seen=seen))
    verdict = judge().evaluate(workspace, 1)
    assert verdict.score == 70.0
    assert verdict.passed
    assert "Price is 129." in seen[0]  # the trusted brief reaches the judges
    assert "sharper first line" in verdict.feedback


def test_manipulation_fails_a_gate(monkeypatch, workspace):
    monkeypatch.setattr(llm, "ask", fake_ask({"fake:a": 10, "fake:b": 10}, manipulation=True))
    verdict = judge().evaluate(workspace, 1)
    assert verdict.gates["no_judge_manipulation"] is False and not verdict.passed


def test_code_gates_apply_before_models(monkeypatch, workspace):
    (workspace / "post.md").write_text("the best ever desk")
    monkeypatch.setattr(llm, "ask", fake_ask({"fake:a": 10, "fake:b": 10}))
    verdict = judge().evaluate(workspace, 1)
    assert verdict.gates["excludes:best ever"] is False


def test_higher_score_must_also_win_head_to_head(monkeypatch, tmp_path, workspace):
    champion_ws = tmp_path / "champion"
    champion_ws.mkdir()
    for name in ("rubric.yaml", "brief.md"):
        (champion_ws / name).write_text((workspace / name).read_text())
    (champion_ws / "post.md").write_text("Old post text here.")
    better, worse = Verdict(80.0, {"x": True}), Verdict(70.0, {"x": True})

    # Judges always pick whichever text is shown first: position bias, no real preference -> rejected.
    monkeypatch.setattr(llm, "ask", fake_ask({}, winner="A"))
    keep, reason = judge().prefers(workspace, champion_ws, better, worse)
    assert not keep and "head-to-head" in reason

    # Judges pick the candidate in both orders -> kept.
    def pick_candidate(prompt):
        a_part = prompt.split("<A_")[1]
        return "A" if "calm night desk" in a_part.split("</A_")[0] else "B"
    monkeypatch.setattr(llm, "ask", fake_ask({}, winner=pick_candidate))
    keep, reason = judge().prefers(workspace, champion_ws, better, worse)
    assert keep and "4/4" in reason


def test_empty_artifact_scores_zero(monkeypatch, workspace):
    (workspace / "post.md").write_text("   ")
    monkeypatch.setattr(llm, "ask", fake_ask({"fake:a": 10, "fake:b": 10}))
    verdict = judge().evaluate(workspace, 1)
    assert verdict.score == 0.0 and not verdict.passed


def test_praise_without_real_evidence_is_capped(monkeypatch, workspace):
    monkeypatch.setattr(llm, "ask", fake_ask({"fake:a": 9, "fake:b": 9}, evidence="a sentence that is not in the post"))
    verdict = judge().evaluate(workspace, 1)
    assert verdict.score == 30.0 and verdict.metrics["unsupported_evidence"] == 4


def test_degenerate_text_fails_before_models_matter(monkeypatch, workspace):
    (workspace / "post.md").write_text("desk desk desk desk " * 40)
    monkeypatch.setattr(llm, "ask", fake_ask({"fake:a": 10, "fake:b": 10}, evidence="desk desk"))
    verdict = judge().evaluate(workspace, 1)
    assert verdict.gates["not_repetitive"] is False and not verdict.passed


def test_prepare_step_feeds_gates_and_short_circuits(monkeypatch, workspace):
    calls = []
    monkeypatch.setattr(llm, "ask", lambda *a, **k: calls.append(1) or llm.Reply("{}"))
    (workspace / "prep.py").write_text(
        "import json, pathlib\npathlib.Path('out').mkdir(exist_ok=True)\n"
        "json.dump({'duration_ok': False}, open('out/gates.json', 'w'))\nopen('out/notes.txt', 'w').write('too long')\n")
    spec = JudgeSpec(type="rubric", rubric="rubric.yaml", inputs=["post.md"], models=["fake:a"], prepare="{python} prep.py")
    verdict = RubricJudge(spec).evaluate(workspace, 1)
    assert verdict.gates == {"duration_ok": False} and verdict.feedback == "too long"
    assert calls == []  # failed preparation gates mean no model calls at all
