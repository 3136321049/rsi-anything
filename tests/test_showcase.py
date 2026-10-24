"""展示必须尊重原始轮次和未完成状态，不把探测或单轮算作多轮完成。"""
import importlib.util
import hashlib
import json
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("showcase_test_module", Path(__file__).resolve().parents[1] / "scripts/build_showcase.py")
SHOWCASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SHOWCASE)


def fixture_run(tmp_path, *, rounds=3, finished=True, invalid=False):
    root = tmp_path
    run = root / "examples/demo/runs/real-run"
    run.mkdir(parents=True)
    (run / "run.json").write_text(json.dumps({"run_id": "real-run", "finished": "2026-10-24" if finished else None,
                                            "agent": "codex", "status": "finished" if finished else "running"}))
    rows = [{"round": 0, "status": "BASELINE", "score": 1, "best": 1}]
    rows += [{"round": n, "status": "KEEP", "score": n + 1, "best": n + 1} for n in range(1, rounds + 1)]
    (run / "ledger.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
    (run / "verification.json").write_text(json.dumps({"final_verified": True, "all_formally_judged_snapshots_passed": True}))
    for name in ["artifacts/baseline", "artifacts/final"]:
        folder = run / name / "files"
        folder.mkdir(parents=True)
        (folder / "post.md").write_text("正文\n</script><script>alert(1)</script>", encoding="utf-8")
    case = {"template": "demo", "title": "示例", "primary": ["post.md"], "inputs": [],
            "invalid_runs": {"real-run": "评分解析问题"} if invalid else {}}
    catalog = {"title": "示例", "description": "本地", "domains": [{"id": "D01", "title": "示例",
               "pending": "developing", "cases": [case]}]}
    (root / "examples/catalog.json").write_text(json.dumps(catalog))
    return root, run, catalog


def test_showcase_requires_real_multi_round_completion(tmp_path):
    root, _, _ = fixture_run(tmp_path, rounds=1)
    assert SHOWCASE.collect(root)["domains"][0]["state"] == "partial"


def test_showcase_incomplete_and_invalid_score_remain_visible(tmp_path):
    root, run, catalog = fixture_run(tmp_path, invalid=True)
    domain = SHOWCASE.collect(root)["domains"][0]
    assert domain["state"] == "partial"
    result = domain["cases"][0]["runs"][0]
    assert result["invalid_reason"] and result["baseline"] is None and result["best"] is None
    assert all(row["score"] is None for row in result["rows"])
    catalog["domains"][0]["cases"][0]["invalid_runs"] = {}
    (run / "run.json").write_text(json.dumps({"status": "running", "finished": None}))
    assert SHOWCASE.collect(root, catalog)["domains"][0]["state"] == "partial"


def test_showcase_does_not_overwrite_runs_and_escapes_embedded_content(tmp_path):
    root, run, _ = fixture_run(tmp_path)
    original = (run / "ledger.jsonl").read_bytes()
    data = SHOWCASE.build(root)
    page = (root / "examples/index.html").read_text()
    assert data["domains"][0]["state"] == "complete"
    assert (run / "ledger.jsonl").read_bytes() == original
    assert "</script><script>alert(1)" not in page
    assert "\\u003c/script\\u003e" in page


def test_showcase_hides_unjudged_generated_outputs_and_requires_video(tmp_path):
    root, run, catalog = fixture_run(tmp_path)
    directory = run / "rounds/r002/artifacts/files"
    (directory / "out").mkdir(parents=True)
    (directory / "post.md").write_text("已恢复配置")
    (directory / "out/report.md").write_text("未评审的内部实验")
    rows = [json.loads(line) for line in (run / "ledger.jsonl").read_text().splitlines()]
    rows[2].update(status="NO_CHANGE", score=None)
    (run / "ledger.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
    data = SHOWCASE.collect(root)
    version = next(v for v in data["domains"][0]["cases"][0]["runs"][0]["versions"] if v["status"] == "NO_CHANGE")
    assert version["note"] and [f["name"] for f in version["files"]] == ["post.md"]
    catalog["domains"][0]["require_video"] = True
    assert SHOWCASE.collect(root, catalog)["domains"][0]["state"] == "partial"


def test_showcase_domain_needs_every_subcase(tmp_path):
    root, _, catalog = fixture_run(tmp_path)
    catalog["domains"][0]["cases"].append({"template": "unfinished-guide", "title": "手册", "primary": [], "inputs": []})
    assert SHOWCASE.collect(root, catalog)["domains"][0]["state"] == "partial"


def test_showcase_finished_run_needs_independent_verification(tmp_path):
    root, run, _ = fixture_run(tmp_path)
    (run / "verification.json").unlink()
    data = SHOWCASE.collect(root)
    assert data["domains"][0]["state"] == "partial"
    assert any("独立验证" in reason for reason in data["domains"][0]["cases"][0]["runs"][0]["reasons"])


def test_service_error_is_unknown_without_changing_original_ledger(tmp_path):
    root, run, _ = fixture_run(tmp_path, rounds=2)
    rows = [json.loads(line) for line in (run / "ledger.jsonl").read_text().splitlines()]
    rows[2].update(status="REVERT", score=0, best=2)
    raw = "\n".join(json.dumps(row) for row in rows).encode()
    (run / "ledger.jsonl").write_bytes(raw)
    out = run / "rounds/r002/artifacts/files/out"
    out.mkdir(parents=True)
    (out / "error.json").write_text(json.dumps({"quality_result": "unknown", "error": "service error: null"}))
    (run / "outcome-audit.json").write_text(json.dumps({"raw_ledger_sha256": hashlib.sha256(raw).hexdigest(),
        "complete_multiround": False, "rounds": [{"round": 2, "quality_result": "unknown", "reason": "未生成作品"}]}))
    data = SHOWCASE.collect(root)
    domain = data["domains"][0]
    record = domain["cases"][0]["runs"][0]
    assert domain["state"] == "partial"
    assert record["rows"][2]["status"] == "JUDGE_FAIL" and record["rows"][2]["score"] is None
    assert record["quality_unknown_rounds"] == [2]
    assert (run / "ledger.jsonl").read_bytes() == raw
