"""网站须使用真实实验并保留未评审轮次的边界。"""
import importlib.util
import json
import re
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    return build_site.build(ROOT, tmp_path_factory.mktemp("public-site"))


def test_site_routes_and_asset_links(site):
    for path in [site / "index.html", site / "start/index.html", *site.glob("labs/*/index.html")]:
        content = path.read_text(encoding="utf-8")
        assert "__BASE__" not in content and "__CONTENT__" not in content
        for target in re.findall(r'(?:href|src)="([^"]+)"', content):
            if target.startswith(("http:", "https:", "#")):
                continue
            local = (path.parent / target.split("?")[0].split("#")[0]).resolve()
            assert local.exists(), (path, target)
    assert len(list(site.glob("labs/*/index.html"))) == 3


def test_site_preserves_unjudged_model_rounds(site):
    data = json.loads((site / "data/cpu-classifier.json").read_text())
    assert data["best_round"] == 1
    assert data["rounds"][1]["metrics"]["mistakes"] == 3
    for row in data["rounds"][2:]:
        assert row["status"] == "NO_CHANGE"
        assert row["score"] is None
        assert row["formal"] is False
        assert "metrics" not in row
        assert "predictions" not in row


def test_site_uses_original_timing_and_keeps_rejections(site):
    code = json.loads((site / "data/code-speed.json").read_text())
    assert [r["score"] for r in code["rounds"]] == [1, 4.45, 17.83, 27.45]
    assert code["reconstructed"]
    video = json.loads((site / "data/video-cut.json").read_text())
    assert video["best_round"] == 1
    assert video["rounds"][3]["score"] == 77
    assert video["rounds"][3]["status"] == "REVERT"
    assert video["rounds"][3]["previous_best"] == 1


def test_video_cues_use_rendered_timeline(site):
    video = json.loads((site / "data/video-cut.json").read_text())
    for row in video["rounds"]:
        assert row["cues"]
        assert row["cues"][0]["start"] < 0.1
        assert row["cues"][-1]["end"] <= row["duration"] + 0.1
        assert all(c["start"] < c["end"] for c in row["cues"])
        assert (site / row["files_base"] / "out/cut.vtt").read_text().startswith("WEBVTT")


def test_public_site_contains_only_selected_roots_and_downloads(site):
    for path in site.rglob("*"):
        assert not any(p in {".git", ".agents", ".venv", ".rsi", "__pycache__"} for p in path.relative_to(site).parts)
    assert not (site / "src/rsi_anything/engine.py").exists()
    for name in build_site.CASES:
        with zipfile.ZipFile(site / "downloads" / (name + ".zip")) as archive:
            assert archive.testzip() is None
            assert any(p.endswith("/ledger.jsonl") for p in archive.namelist())
