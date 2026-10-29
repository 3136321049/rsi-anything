"""实时页面与分享页：只读运行目录，图片随版本保存，分享文件自带全部内容且去掉本机路径。"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

from rsi_anything import ledger, live
from rsi_anything.agents import make_agent
from rsi_anything.contract import load
from rsi_anything.engine import Ratchet

PNG = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082")


@pytest.fixture
def finished(toy):
    project = toy([{"write": {"value.txt": "5"}, "hypothesis": "bigger"}, {"write": {"value.txt": "2"}}], rounds=2)
    # 评审时生成一张图，模拟视觉类模板保存的渲染结果。
    judge = (project / "judge.py").read_text()
    (project / "judge.py").write_text("import os, pathlib\npathlib.Path('out').mkdir(exist_ok=True)\n"
                                      f"pathlib.Path('out/view.png').write_bytes({PNG!r})\n" + judge)
    (project / "rsi.yaml").write_text((project / "rsi.yaml").read_text() + "outputs: [out]\n")
    from conftest import git
    git(project, "commit", "-qam", "render a picture")
    contract = load(project)
    summary = Ratchet(project, contract, make_agent(contract.agent), log=lambda _: None).run()
    return project, ledger.RunStore(project, summary.run_id).dir


def test_state_reads_rounds_snapshots_and_status(finished):
    _, run = finished
    data = live.state(run)
    assert data["status"] == "finished" and data["active"] is None and data["strategy"] == "greedy"
    assert [r["status"] for r in data["rows"]] == ["BASELINE", "KEEP", "REVERT"]
    kept = data["rows"][1]["snapshot"]
    assert kept["text"] == {"value.txt": "5"}
    assert kept["images"] == [{"name": "out/view.png", "src": f"files/{run.name}/rounds/r001/artifacts/files/out/view.png"}]
    assert data["runs"] == [{"run": 1, "run_id": run.name, "stop_reason": "reached 2 rounds", "change": []}]


def test_active_round_is_reported_while_running(finished):
    _, run = finished
    meta = json.loads((run / "run.json").read_text())
    meta["status"] = "running"
    (run / "run.json").write_text(json.dumps(meta))
    with (run / "events.jsonl").open("a") as stream:
        stream.write(json.dumps({"type": "round_started", "round": 3, "agent": "command"}) + "\n")
        stream.write(json.dumps({"type": "agent_finished", "round": 3}) + "\n")
    assert live.state(run)["active"] == {"round": 3, "phase": "judging", "agent": "command"}


def test_watcher_serves_state_and_only_files_inside_the_run(finished):
    _, run = finished
    server = live.serve(lambda: run, port=0, open_browser=False)
    base = f"http://127.0.0.1:{server.server_address[1]}/"
    try:
        assert b"DARWIN" in urllib.request.urlopen(base).read()
        state = json.loads(urllib.request.urlopen(base + "api/state").read())
        assert state["rows"][1]["status"] == "KEEP"
        assert urllib.request.urlopen(base + state["rows"][1]["snapshot"]["images"][0]["src"]).read() == PNG
        for escape in ("files/../../../../etc/hosts", "files/%2e%2e/%2e%2e/rsi.yaml"):
            with pytest.raises(urllib.error.HTTPError):
                urllib.request.urlopen(base + escape)
    finally:
        server.shutdown()


def test_share_is_one_file_with_images_inline_and_paths_scrubbed(finished, tmp_path):
    project, run = finished
    rows = (run / "ledger.jsonl").read_text().splitlines()
    first = json.loads(rows[1])
    first["note"] = f"edited {project}/value.txt"
    (run / "ledger.jsonl").write_text("\n".join([rows[0], json.dumps(first), *rows[2:]]) + "\n")
    from rsi_anything.export import scrubber
    page = live.share(run, tmp_path / "share.html", scrub=scrubber(project)).read_text(encoding="utf-8")
    state = json.loads(page.split('<script id="state" type="application/json">')[1].split("</script>")[0].replace("<\\/", "</"))
    assert state["rows"][1]["snapshot"]["images"][0]["src"].startswith("data:image/png;base64,")
    assert state["rows"][1]["note"] == "edited <project>/value.txt"
    assert str(project) not in page and "files/rounds" not in page


def test_a_run_that_continues_an_earlier_one_shares_its_timeline(finished):
    project, first = finished
    from conftest import git
    git(project, "merge", "-q", "--ff-only", f"rsi/{first.name}")
    (project / "rsi.yaml").write_text((project / "rsi.yaml").read_text().replace("rounds: 2", "rounds: 1"))
    git(project, "commit", "-qam", "one more round")
    (project.parent / "tools/plan.json").write_text(json.dumps([{"write": {"value.txt": "8"}}]))
    contract = load(project)
    second = ledger.RunStore(project, Ratchet(project, contract, make_agent(contract.agent),
                                               log=lambda _: None).run().run_id).dir
    data = live.state(second)
    assert [(r["run"], r["round"], r["status"]) for r in data["rows"]] == [
        (1, 0, "BASELINE"), (1, 1, "KEEP"), (1, 2, "REVERT"), (2, 0, "BASELINE"), (2, 1, "KEEP")]
    assert data["runs"][1]["change"] == ["-  rounds: 2", "+  rounds: 1"]
    assert live.state(first)["runs"][0]["run_id"] == first.name and len(live.state(first)["runs"]) == 1
    assert len(live.state(second, follow=False)["runs"]) == 1


def test_exported_runs_keep_events_and_can_still_be_shared(finished, tmp_path):
    project, run = finished
    from rsi_anything.export import export_run
    dest = tmp_path / "examples" / "runs" / run.name
    export_run(ledger.RunStore(project, run.name), project, dest)
    assert (dest / "events.jsonl").read_text() == (run / "events.jsonl").read_text()
    exported = live.state(dest)
    assert [r["status"] for r in exported["rows"]] == ["BASELINE", "KEEP", "REVERT"]
    assert exported["rows"][1]["snapshot"]["images"][0]["name"] == "out/view.png"


def test_share_can_link_images_next_to_exported_runs(finished, tmp_path):
    _, run = finished
    page = live.share(run, run.parent / "evolution.html", embed=False).read_text(encoding="utf-8")
    assert f'"src": "{run.name}/rounds/r001/artifacts/files/out/view.png"' in page and "data:image" not in page
