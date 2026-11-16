import importlib.util
import json
import shutil
from pathlib import Path

from rsi_anything.llm import Reply

TEMPLATE = Path(__file__).resolve().parents[1] / "src/rsi_anything/templates/writing-guide"


def test_guide_generates_all_briefs_and_separates_new_input(tmp_path, monkeypatch):
    shutil.copytree(TEMPLATE, tmp_path, dirs_exist_ok=True)
    monkeypatch.setenv("RSI_WRITER_MODEL", "cli:codex:fixed-writer")
    spec = importlib.util.spec_from_file_location("guide_generate", tmp_path / "judge/generate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    seen = []
    def ask(model, prompt, **kwargs):
        seen.append(prompt)
        return Reply("Test draft\nMatches the given facts.", model="fixed-writer", usage={"output_tokens": 20})
    dev = module.generate(tmp_path, "development", ask)
    assert len(dev) == 3 and all(r["requested_model"] == "cli:codex:fixed-writer" for r in dev)
    assert all("Slow Read Wednesdays" not in prompt for prompt in seen)
    holdout = module.generate(tmp_path, "holdout", ask)
    assert len(holdout) == 1 and "Slow Read Wednesdays" in seen[-1]
    assert json.loads((tmp_path / "out/gates.json").read_text())["all_briefs_generated"]
    assert (tmp_path / "out/posts.html").is_file()
