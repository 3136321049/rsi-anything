import json

from rsi_anything import llm
from rsi_anything.agents.registry import CLI_AGENTS
from rsi_anything.contract import load


def test_codex_isolation_is_explicit_and_preserves_requested_model(monkeypatch, tmp_path):
    monkeypatch.setenv("RSI_CODEX_ISOLATED", "1")
    monkeypatch.setenv("RSI_CODEX_REASONING_EFFORT", "medium")
    spec = CLI_AGENTS["codex"]
    for command in [spec.ask_command("hello", "chosen-model", tmp_path, []),
                    spec.round_command("hello", "chosen-model", tmp_path, False, [], tmp_path / "answer")]:
        argv = command[0]
        assert "--ignore-user-config" in argv and "--ignore-rules" in argv
        assert "project_doc_max_bytes=0" in argv and "--json" in argv
        assert argv[argv.index("-m") + 1] == "chosen-model"
    monkeypatch.delenv("RSI_CODEX_ISOLATED")
    assert "--ignore-user-config" not in spec.ask_command("hello", "", tmp_path, [])[0]


def test_usage_comes_from_response_without_model_guessing():
    result = CLI_AGENTS["codex"].metadata('{"type":"turn.completed","usage":{"input_tokens":12,"output_tokens":3}}')
    assert result == {"actual_model": None, "usage": {"input_tokens": 12, "output_tokens": 3}}


def test_api_reply_preserves_model_usage_without_logging_prompt(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("RSI_USAGE_LOG", str(tmp_path / "usage.jsonl"))
    monkeypatch.setattr(llm, "_post", lambda *a, **kw: {
        "model": "returned-model", "usage": {"prompt_tokens": 11},
        "choices": [{"message": {"content": "ok"}}]})
    reply = llm.ask(llm.parse("openai:requested-model"), "private-prompt")
    assert reply.model == "returned-model" and reply.usage == {"prompt_tokens": 11}
    text = (tmp_path / "usage.jsonl").read_text()
    assert "private-prompt" not in text
    assert json.loads(text)["requested_model"] == "openai:requested-model"


def test_outputs_are_parsed_as_project_relative_paths(tmp_path):
    contract = load(tmp_path, "goal: g\nartifact: [a.txt]\noutputs: [out]\njudge: {run: echo}\n")
    assert contract.outputs == ["out"]
