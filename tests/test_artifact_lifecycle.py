from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from rsi_anything import artifacts, ledger, report
from rsi_anything.agents import make_agent
from rsi_anything.contract import load
from rsi_anything.engine import Ratchet
from rsi_anything.export import export_run
from rsi_anything.judges import make_judge
from rsi_anything.judges.base import Judge, Verdict

from conftest import git


def configured(project, rounds=None, judge=None, agent=None):
    contract = load(project)
    if rounds is not None:
        contract.budget.rounds = rounds
    return Ratchet(project, contract, agent or make_agent(contract.agent), log=lambda _: None, judge=judge)


def render_project(toy):
    project = toy([{"write": {"value.txt": "5"}}, {"write": {"value.txt": "3"}}], rounds=2)
    with (project / "judge.py").open("a") as stream:
        stream.write("\nfrom pathlib import Path\nPath('out').mkdir(exist_ok=True)\n"
                     "Path('out/result.txt').write_text(f'rendered {value} at {Path.cwd()}')\n"
                     "Path('out/video.mp4').write_bytes(b'\\x00\\xff\\x80video' + bytes([value]))\n")
    with (project / "rsi.yaml").open("a") as stream:
        stream.write("\noutputs: [out, absent.txt]\n")
    git(project, "add", "-A")
    git(project, "commit", "-qm", "render")
    return project


def test_preserves_baseline_rejected_and_final_outputs(toy):
    project = render_project(toy)
    summary = configured(project).run()
    store = ledger.RunStore(project, summary.run_id)
    locations = {"artifacts/baseline": "1", "rounds/r001/artifacts": "5",
                 "rounds/r002/artifacts": "3", "artifacts/final": "5"}
    for relative, value in locations.items():
        snapshot = store.dir / relative
        assert (snapshot / "files/value.txt").read_text().strip() == value
        assert (snapshot / "files/out/result.txt").read_text().startswith("rendered " + value)
        assert (snapshot / "files/out/video.mp4").read_bytes() == b"\x00\xff\x80video" + bytes([int(value)])
        assert json.loads((snapshot / "manifest.json").read_text())["missing_patterns"] == ["absent.txt"]
    assert store.rows()[-1]["status"] == "REVERT"
    assert json.loads((store.dir / "rounds/r002/artifacts/manifest.json").read_text())["source"] == "judge_workspace"
    assert json.loads((store.dir / "artifacts/final/manifest.json").read_text())["evaluation_status"] == "evaluated"
    assert store.meta()["status"] == "finished"
    assert not store.worktree.exists()
    assert (store.dir / "config/frozen/judge.py").read_bytes() == (project / "judge.py").read_bytes()
    assert json.loads((store.dir / "config/execution.json").read_text())["agent"]["actual_model"] is None


def test_export_preserves_binary_scrubs_text_and_links_versions(toy, tmp_path):
    project = render_project(toy)
    summary = configured(project).run()
    store = ledger.RunStore(project, summary.run_id)
    dest = tmp_path / "exported"
    export_run(store, project, dest)
    relative = Path("artifacts/final/files/out/video.mp4")
    assert (dest / relative).read_bytes() == (store.dir / relative).read_bytes()
    assert not (dest / "rounds/r001/agent.log").exists()
    assert (dest / "config/rsi.yaml").exists() and (dest / "config/execution.json").exists()
    assert str(tmp_path) not in (dest / "config/rsi.yaml").read_text()
    assert "<tmp>/" in (dest / "artifacts/final/files/out/result.txt").read_text()
    assert str(Path(__import__("tempfile").gettempdir())) not in (dest / "artifacts/final/files/out/result.txt").read_text()
    page = (dest / "report.html").read_text()
    assert '<video controls preload="metadata"' in page
    assert "rounds/r002/artifacts/files/value.txt" in page
    assert "artifacts/final/files/value.txt" in page
    assert "模型与运行参数" in page
    for manifest in dest.rglob("manifest.json"):
        if manifest.parent.name in {"baseline", "final", "artifacts"}:
            for item in json.loads(manifest.read_text())["files"]:
                assert hashlib.sha256((manifest.parent / "files" / item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_resume_does_not_repeat_completed_evaluation(toy, monkeypatch):
    project = toy([{"write": {"value.txt": "5"}}, {"write": {"value.txt": "9"}}], rounds=2)
    judge = make_judge(load(project).judge)
    calls = []
    score = judge.evaluate
    monkeypatch.setattr(judge, "evaluate", lambda path, number: calls.append(number) or score(path, number))
    first = configured(project, rounds=1, judge=judge).run()
    assert calls == [0, 1]
    second = configured(project, rounds=2, judge=judge).run(resume=first.run_id)
    assert calls == [0, 1, 2]
    assert second.best == 9 and second.rounds == 2
    assert (ledger.RunStore(project, first.run_id).dir / "artifacts/final/files/value.txt").read_text() == "9"


def test_interrupt_preserves_round_and_resumes_from_champion(toy, monkeypatch):
    project = toy([{"write": {"value.txt": "5"}}, {"write": {"value.txt": "9"}}], rounds=3)
    agent = make_agent(load(project).agent)
    original = agent.run
    attempts = []

    def interrupted(*args):
        attempts.append(1)
        if len(attempts) == 2:
            (args[0] / "value.txt").write_text("7")
            raise KeyboardInterrupt()
        return original(*args)

    monkeypatch.setattr(agent, "run", interrupted)
    with pytest.raises(KeyboardInterrupt):
        configured(project, agent=agent).run()
    run_id = ledger.list_runs(project)[0]
    store = ledger.RunStore(project, run_id)
    assert store.meta()["status"] == "interrupted" and store.meta()["active_round"] == 2
    assert (store.dir / "rounds/r002/artifacts/files/value.txt").read_text() == "7"
    manifest = json.loads((store.dir / "rounds/r002/artifacts/manifest.json").read_text())
    assert manifest["source"] == "agent_workspace" and manifest["evaluation_status"] == "round_incomplete"
    assert "未经本轮正式评审" in report.markdown(store)
    resumed = configured(project).run(resume=run_id)
    assert resumed.best == 9
    assert [row["status"] for row in store.rows()] == ["BASELINE", "KEEP", "INTERRUPTED", "KEEP"]
    assert len({row["round"] for row in store.rows()}) == 4


def test_complete_round_is_recovered_after_partial_ledger_write(toy, monkeypatch):
    project = toy([{"write": {"value.txt": "5"}}], rounds=1)
    first = configured(project).run()
    store = ledger.RunStore(project, first.run_id)
    baseline = store.ledger_path.read_bytes().splitlines()[0]
    store.ledger_path.write_bytes(baseline + b'\n{"round": 1, "stat')
    judge = make_judge(load(project).judge)
    monkeypatch.setattr(judge, "evaluate", lambda *args: pytest.fail("已完成评分不应重复"))
    resumed = configured(project, judge=judge).run(resume=first.run_id)
    assert resumed.best == 5 and len(store.rows()) == 2
    assert (store.dir / "ledger.interrupted-tail").exists()


def test_staged_out_of_scope_file_is_not_committed(toy):
    project = toy([{"write": {"value.txt": "5", "notes.txt": "outside"}}], rounds=1)
    contract = load(project)
    contract.agent.command += "; git add notes.txt"
    summary = Ratchet(project, contract, make_agent(contract.agent), log=lambda _: None).run()
    names = git(project, "ls-tree", "--name-only", summary.branch).splitlines()
    assert "notes.txt" not in names
    assert git(project, "show", f"{summary.branch}:value.txt") == "5"


def test_snapshot_reports_external_symlinks_without_copying_them(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    secret = tmp_path / "external.txt"
    secret.write_text("external material")
    (source / "linked.txt").symlink_to(secret)
    snapshot = tmp_path / "snapshot"
    manifest = artifacts.save(source, snapshot, ["linked.txt"])
    assert manifest["skipped"] == ["linked.txt"]
    assert not (snapshot / "files/linked.txt").exists()


class RecordingJudge(Judge):
    def __init__(self, spec, label="main", interrupt_on=None):
        super().__init__(spec)
        self.label, self.interrupt_on, self.calls = label, interrupt_on, 0

    def record(self, cost):
        with Path(os.environ["RSI_USAGE_LOG"]).open("a") as stream:
            stream.write(json.dumps({"requested_model": "fake:test", "actual_model": "test-model",
                                     "usage": {"input_tokens": 10}, "cost_usd": cost}) + "\n")

    def score(self, workspace, round_no):
        self.calls += 1
        if self.calls == self.interrupt_on:
            raise KeyboardInterrupt()
        self.record(0.1)
        (workspace / "out").mkdir(exist_ok=True)
        (workspace / "out/evaluation.txt").write_text(f"{self.label}: {round_no}")
        return Verdict(float((workspace / "value.txt").read_text()), metrics={"cost_usd": 0.1})

    def prefers(self, *args):
        self.record(0.2)
        return super().prefers(*args)


@pytest.mark.parametrize("candidate", ["5", "0"])
def test_judge_usage_and_holdout_outputs_are_saved_and_exported(toy, tmp_path, monkeypatch, candidate):
    project = toy([{"write": {"value.txt": candidate}}], rounds=1)
    contract = load(project)
    contract.outputs = ["out"]
    judge = RecordingJudge(contract.judge)
    holdout = RecordingJudge(contract.judge, "holdout")
    monkeypatch.setenv("RSI_USAGE_LOG", str(tmp_path / "outer.jsonl"))
    summary = Ratchet(project, contract, make_agent(contract.agent), judge=judge, holdout=holdout,
                      log=lambda _: None).run()
    store = ledger.RunStore(project, summary.run_id)
    assert os.environ["RSI_USAGE_LOG"] == str(tmp_path / "outer.jsonl")
    assert not (tmp_path / "outer.jsonl").exists()
    assert len((store.dir / "rounds/r001/judge-usage.jsonl").read_text().splitlines()) == 2
    assert (store.dir / "artifacts/final/holdout-artifacts/files/out/evaluation.txt").read_text() == "holdout: 1"
    assert (store.dir / "artifacts/baseline/holdout-artifacts/files/out/evaluation.txt").read_text() == "holdout: 0"
    assert not (store.dir / "artifacts/final/judge-usage.jsonl").exists()
    assert len((store.dir / "artifacts/final/holdout-usage.jsonl").read_text().splitlines()) == 1
    manifest = json.loads((store.dir / "artifacts/final/manifest.json").read_text())
    assert manifest["source_snapshot"] == ("rounds/r001/artifacts" if candidate == "5" else "artifacts/baseline")
    assert "$0.6000" in report.markdown(store)
    dest = tmp_path / "exported"
    export_run(store, project, dest)
    assert (dest / "rounds/r001/judge-usage.jsonl").exists()
    assert (dest / "artifacts/final/holdout-artifacts/files/out/evaluation.txt").exists()


def test_resume_after_final_holdout_interrupt_does_not_repeat_prior_calls(toy):
    project = toy([{"write": {"value.txt": "5"}}], rounds=1)
    contract = load(project)
    contract.outputs = ["out"]
    judge = RecordingJudge(contract.judge)
    holdout = RecordingJudge(contract.judge, "holdout", interrupt_on=2)

    def ratchet():
        return Ratchet(project, contract, make_agent(contract.agent), judge=judge, holdout=holdout,
                       log=lambda _: None)

    with pytest.raises(KeyboardInterrupt):
        ratchet().run()
    run_id = ledger.list_runs(project)[0]
    assert judge.calls == 2 and holdout.calls == 2
    summary = ratchet().run(resume=run_id)
    assert judge.calls == 2 and holdout.calls == 3
    assert summary.holdout == {"baseline": 1.0, "final": 5.0}
    assert ledger.RunStore(project, run_id).meta()["status"] == "finished"


def test_extending_finished_run_retains_previous_final_holdout_calls(toy):
    project = toy([{"write": {"value.txt": "5"}}, {"write": {"value.txt": "9"}}], rounds=2)
    contract = load(project)
    contract.outputs = ["out"]
    judge = RecordingJudge(contract.judge)
    holdout = RecordingJudge(contract.judge, "holdout")
    contract.budget.rounds = 1
    first = Ratchet(project, contract, make_agent(contract.agent), judge=judge, holdout=holdout, log=lambda _: None).run()
    store = ledger.RunStore(project, first.run_id)
    original = (store.dir / "artifacts/final/holdout-usage.jsonl").read_bytes()
    contract.budget.rounds = 2
    final = Ratchet(project, contract, make_agent(contract.agent), judge=judge, holdout=holdout,
                    log=lambda _: None).run(resume=first.run_id)
    saved = store.dir / "artifacts/final-history" / first.champion[:12]
    assert (saved / "holdout-usage.jsonl").read_bytes() == original
    assert (saved / "files/value.txt").read_text() == "5"
    assert (store.dir / "artifacts/final/files/value.txt").read_text() == "9"
    assert final.holdout == {"baseline": 1.0, "final": 9.0}
    assert "$1.0000" in report.markdown(store)
    assert judge.calls == 3 and holdout.calls == 3


@pytest.mark.parametrize("exit_code,status", [(0, "NO_CHANGE"), (3, "AGENT_FAIL")])
def test_unreviewed_agent_outputs_do_not_become_formal_results(toy, exit_code, status):
    project = toy([{"write": {"out/metrics.json": '{"score": 999}'}, "exit": exit_code}], rounds=1)
    contract = load(project)
    contract.outputs = ["out"]
    summary = Ratchet(project, contract, make_agent(contract.agent), log=lambda _: None).run()
    store = ledger.RunStore(project, summary.run_id)
    snapshot = store.dir / "rounds/r001/artifacts"
    manifest = json.loads((snapshot / "manifest.json").read_text())
    assert manifest["source"] == "agent_workspace" and manifest["evaluation_status"] == "unreviewed"
    assert (snapshot / "files/out/metrics.json").read_text() == '{"score": 999}'
    assert store.rows()[-1]["status"] == status and store.rows()[-1]["score"] is None
    assert summary.best == 1
    assert "999" not in report._chart(store.rows())
    assert "助手工作目录，未经本轮正式评审" in report.html_page(store, project)
    # 历史快照没有新字段时，报告按正式轮次状态补说明，不回写原文件。
    del manifest["source"]
    del manifest["evaluation_status"]
    (snapshot / "manifest.json").write_text(json.dumps(manifest))
    original = (snapshot / "manifest.json").read_bytes()
    assert "助手工作目录，未经本轮正式评审" in report.markdown(store)
    assert (snapshot / "manifest.json").read_bytes() == original


def test_interrupted_judged_snapshot_keeps_actual_source(toy, monkeypatch):
    project = toy([{"write": {"value.txt": "5"}}], rounds=1)
    judge = make_judge(load(project).judge)

    def interrupt(*args):
        raise KeyboardInterrupt()

    monkeypatch.setattr(judge, "prefers", interrupt)
    with pytest.raises(KeyboardInterrupt):
        configured(project, judge=judge).run()
    store = ledger.RunStore(project, ledger.list_runs(project)[0])
    snapshot = store.dir / "rounds/r001/artifacts"
    manifest = json.loads((snapshot / "manifest.json").read_text())
    assert manifest["source"] == "judge_workspace" and manifest["evaluation_status"] == "round_incomplete"
    assert len(store.rows()) == 1
    text = report.markdown(store)
    assert "中断轮的评审目录" in text and "尚无完整正式轮次结论" in text
