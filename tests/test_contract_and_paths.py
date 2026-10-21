from __future__ import annotations

import pytest

from rsi_anything import llm
from rsi_anything.contract import ContractError, load
from rsi_anything.judges.rubric import code_gates
from rsi_anything.paths import matches


def test_patterns():
    assert matches("src/app.py", ["src/*.py"])
    assert not matches("src/sub/app.py", ["src/*.py"])
    assert matches("src/sub/app.py", ["src/**"])
    assert matches("judge/data/x.csv", ["judge"])
    assert not matches("../etc/passwd", ["**"])


def test_artifact_cannot_overlap_judge(tmp_path):
    (tmp_path / "rsi.yaml").write_text("goal: g\nartifact: [tests/x.py]\njudge: {run: pytest, files: [tests]}\n")
    with pytest.raises(ContractError, match="overlap"):
        load(tmp_path)


def test_rubric_judge_defaults_inputs_to_artifact(tmp_path):
    (tmp_path / "rsi.yaml").write_text(
        "goal: g\nartifact: [post.md]\njudge: {type: rubric, rubric: judge/rubric.yaml, models: [cli:codex]}\n")
    contract = load(tmp_path)
    assert contract.judge.inputs == ["post.md"]
    assert "judge/rubric.yaml" in contract.frozen_files


def test_code_gates():
    gates = code_gates("hello world", {"min_chars": 5, "max_chars": 8, "must_not_include": ["world"]})
    assert gates == {"min_chars": True, "max_chars": False, "excludes:world": False}


def test_model_refs():
    ref = llm.parse("deepseek:deepseek-chat")
    assert ref.kind == "api" and ref.base_url.startswith("https://api.deepseek.com")
    assert llm.parse("openai:my-model@https://gw.example.com/v1").base_url == "https://gw.example.com/v1"
    assert llm.parse("cli:codex:gpt-5").model == "gpt-5"
    with pytest.raises(llm.LLMError):
        llm.parse("nope:model")


def test_extract_json_from_chatty_reply():
    assert llm.extract_json('Sure!\n```json\n{"winner": "A"}\n```') == {"winner": "A"}
    assert llm.extract_json('text {"a": {"b": 1}} more') == {"a": {"b": 1}}
