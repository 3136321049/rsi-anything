"""网站须使用真实实验、中英文完整，并保留未评审轮次的边界。"""
import json
import re
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site
import site_i18n


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    return build_site.build(ROOT, tmp_path_factory.mktemp("public-site"))


def pages(site):
    return [site / prefix / route / "index.html" for prefix in build_site.LANGS.values() for route in build_site.PAGES]


def test_site_routes_and_asset_links(site):
    assert len(pages(site)) == 14
    for path in pages(site):
        content = path.read_text(encoding="utf-8")
        assert not re.search(r"__[A-Z_]+__|\{\{", content), path
        for target in re.findall(r'(?:href|src)="([^"]+)"', content):
            if target.startswith(("http:", "https:", "#")):
                continue
            local = (path.parent / target.split("?")[0].split("#")[0]).resolve()
            assert local.exists(), (path, target)


def test_languages_link_to_each_other(site):
    for prefix, lang in (("", "en"), ("zh/", "zh-CN")):
        for route in build_site.PAGES:
            content = (site / prefix / route / "index.html").read_text(encoding="utf-8")
            assert f'<html lang="{lang}">' in content
            assert f'hreflang="en" href="{build_site.SITE_URL}{route}"' in content
            assert f'hreflang="zh-CN" href="{build_site.SITE_URL}zh/{route}"' in content
            switch = re.search(r'class="nav-lang" href="([^"]+)"', content)[1]
            other = (site / prefix / route / switch / "index.html").resolve()
            assert other.exists() and other != (site / prefix / route / "index.html").resolve()


def test_dictionaries_cover_templates_and_script():
    en, zh = (json.loads((ROOT / f"web/i18n/{lang}.json").read_text(encoding="utf-8")) for lang in ("en", "zh"))

    def keys(node, prefix=""):
        return {k for key, value in node.items() for k in (keys(value, prefix + key + ".") if isinstance(value, dict) else [prefix + key])}
    assert keys(en) == keys(zh)
    script = (ROOT / "web/assets/app.js").read_text(encoding="utf-8")
    used = set(re.findall(r'\bt\("([\w.]+)"\s*[,)]', script))
    used |= {f"status.{s}" for s in ("BASELINE", "KEEP", "REVERT", "NO_CHANGE", "AGENT_FAIL", "JUDGE_FAIL", "final", "unknown")}
    for template in build_site.CASES:
        used |= {f"lab.limits.{template}", f"start.pre.{template}"}
    for template in build_site.VISUAL:
        used |= {f"lab.limits.{template}", f"start.pre.{template}"}
        rubric = yaml.safe_load((ROOT / "src/rsi_anything/templates" / template / "judge/rubric.yaml").read_text(encoding="utf-8"))
        used |= {f"lab.visual.criteria.{item['name']}" for item in rubric["criteria"]}
    used |= {f"lab.video.summary.{n}" for n in range(5)}
    assert used <= keys(en), used - keys(en)


def test_english_pages_and_data_have_no_untranslated_records(site):
    data = json.loads((site / "data/en/cases.json").read_text(encoding="utf-8"))
    seen = []
    site_i18n.walk(data, lambda text: seen.append(text) or text)
    assert seen and not [text for text in seen if site_i18n.CJK.search(text)]
    for name in [*build_site.CASES, *build_site.VISUAL]:
        lab = json.loads((site / f"data/en/{name}.json").read_text(encoding="utf-8"))
        assert not site_i18n.CJK.search(lab["title"] + lab["metric"] + lab["unit"])
    for name in build_site.VISUAL:
        lab = json.loads((site / f"data/en/{name}.json").read_text(encoding="utf-8"))
        assert not [r for r in lab["rounds"] if site_i18n.CJK.search(r["hypothesis"] + r["note"])]
    body = (site / "index.html").read_text(encoding="utf-8").split('<script id="i18n"')[0]
    visible = re.sub(r"<[^>]+>", " ", body.split("<main", 1)[1])
    assert not site_i18n.CJK.search(visible.replace("中文版", "").replace("中文", ""))  # 语言切换入口


def test_site_preserves_unjudged_model_rounds(site):
    for lang in build_site.LANGS:
        data = json.loads((site / f"data/{lang}/cpu-classifier.json").read_text())
        assert data["best_round"] == 1
        assert data["rounds"][1]["metrics"]["mistakes"] == 3
        for row in data["rounds"][2:]:
            assert row["status"] == "NO_CHANGE"
            assert row["score"] is None
            assert row["formal"] is False
            assert "metrics" not in row
            assert "predictions" not in row


def test_site_uses_original_timing_and_keeps_rejections(site):
    code = json.loads((site / "data/en/code-speed.json").read_text())
    assert [r["score"] for r in code["rounds"]] == [1, 4.45, 17.83, 27.45]
    assert code["reconstructed"]
    video = json.loads((site / "data/en/video-cut.json").read_text())
    assert video["best_round"] == 1
    assert video["rounds"][3]["score"] == 77
    assert video["rounds"][3]["status"] == "REVERT"
    assert video["rounds"][3]["previous_best"] == 1
    home = (site / "index.html").read_text(encoding="utf-8")
    replay = json.loads(re.search(r'<script id="home-data" type="application/json">(.*?)</script>', home)[1])
    assert [r["status"] for r in replay["series"]["video-cut"]["rounds"]] == ["BASELINE", "KEEP", "REVERT", "REVERT", "REVERT"]
    assert [r["score"] for r in replay["series"]["code-speed"]["rounds"]] == [1, 4.45, 17.83, 27.45]


def test_visual_lab_chains_runs_and_keeps_every_frame(site):
    drawing = json.loads((site / "data/en/svg-drawing.json").read_text())
    assert [r["score"] for r in drawing["rounds"]] == [37, 68, 75, 75, 75, 75, 75, 75, 78, 75, 78, 78, 78]
    assert [r["status"] for r in drawing["rounds"]].count("KEEP") == 6
    first, second = drawing["runs"]
    assert not first["continues"] and not first["ties"]
    assert second["continues"] and second["ties"] and second["first"] == 6
    # 第二次运行的起点就是第一次的最终作品；之后的比较对象仍是那一版。
    assert drawing["rounds"][7]["previous_best"] == 2 and drawing["rounds"][7]["best_before"] == 75
    assert drawing["rounds"][drawing["best_round"]]["number"] == 6
    tie_lost = drawing["rounds"][11]
    assert tie_lost["status"] == "REVERT" and tie_lost["note"] == "Tied with the best version at 78; lost the head-to-head (0/2)."
    assert set(drawing["rounds"][0]["criteria"]) == {c["name"] for c in drawing["criteria"]}
    landing = json.loads((site / "data/zh/landing-page.json").read_text())
    assert [r["score"] for r in landing["rounds"]] == [25, 70, 72.5, 70, 72, 74.5, 72.5]
    assert landing["best_round"] == 5
    for lab in (drawing, landing):
        for row in lab["rounds"]:
            assert row["images"]
            for image in row["images"]:
                assert (site / row["files_base"] / image).is_file()
    home = (site / "index.html").read_text(encoding="utf-8")
    replay = json.loads(re.search(r'<script id="home-data" type="application/json">(.*?)</script>', home)[1])
    assert [r["label"] for r in replay["series"]["svg-drawing"]["rounds"]][5:8] == ["R5", "2·R0", "2·R1"]


def test_video_cues_use_rendered_timeline(site):
    video = json.loads((site / "data/en/video-cut.json").read_text())
    for row in video["rounds"]:
        assert row["cues"]
        assert row["cues"][0]["start"] < 0.1
        assert row["cues"][-1]["end"] <= row["duration"] + 0.1
        assert all(c["start"] < c["end"] for c in row["cues"])
        assert (site / row["files_base"] / "out/cut.vtt").read_text().startswith("WEBVTT")


def test_case_files_resolve(site):
    data = json.loads((site / "data/zh/cases.json").read_text(encoding="utf-8"))
    for domain in data["domains"]:
        for case in domain["cases"]:
            for run in case["runs"]:
                for item in [*run["inputs"], *run["evidence"], *(f for v in run["versions"] for f in v["files"])]:
                    assert (site / item["url"]).resolve().is_file(), item["url"]


def test_public_site_contains_only_selected_roots_and_downloads(site):
    for path in site.rglob("*"):
        assert not any(p in {".git", ".agents", ".venv", ".rsi", "__pycache__", "release"} for p in path.relative_to(site).parts)
    for internal in ("AGENTS.md", "CLAUDE.md", "docs/HANDOFF.zh-CN.md", "docs/DEVLOG.zh-CN.md", "docs/COLLABORATION.zh-CN.md", "web"):
        assert not (site / internal).exists(), internal
    assert not (site / "src/rsi_anything/engine.py").exists()
    assert (site / "dist" / build_site.WHEEL).is_file()
    assert [p.name for p in (site / "dist").iterdir()] == [build_site.WHEEL]  # 源码包含内部文档，不上网站
    for name in [*build_site.CASES, *build_site.VISUAL]:
        with zipfile.ZipFile(site / "downloads" / (name + ".zip")) as archive:
            assert archive.testzip() is None
            assert any(p.endswith("/ledger.jsonl") for p in archive.namelist())
    with zipfile.ZipFile(site / "downloads/svg-drawing.zip") as archive:
        assert {p.split("/")[0] for p in archive.namelist()} == set(build_site.VISUAL["svg-drawing"])


def test_start_page_offers_every_lab_template(site):
    for prefix in build_site.LANGS.values():
        page = (site / prefix / "start/index.html").read_text(encoding="utf-8")
        offered = set(re.findall(r'<option value="([\w-]+)"', page))
        assert offered == {*build_site.CASES, *build_site.VISUAL}
        assert "rsi setup" in page and "rsi new my-task" in page
        assert build_site.WHEEL in page and "0.3.0.dev0" in page
        for template in offered:
            assert (ROOT / "src/rsi_anything/templates" / template / "rsi.yaml").is_file()


def test_pages_do_not_point_to_the_private_repository(site):
    for path in pages(site):
        assert "github.com/3136321049" not in path.read_text(encoding="utf-8")


LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def english_docs():
    return [ROOT / "README.md", *(ROOT / "docs" / n for n in build_site.PUBLIC_DOCS if not n.endswith(".zh-CN.md")),
            *ROOT.glob("src/rsi_anything/templates/*/*.en.md"), *ROOT.glob("examples/**/README.en.md")]


def test_public_docs_have_english_versions():
    chinese = [*(ROOT / "docs" / n for n in build_site.PUBLIC_DOCS if n.endswith(".zh-CN.md")),
               *ROOT.glob("src/rsi_anything/templates/*/README.md"), *ROOT.glob("src/rsi_anything/templates/*/THIRD_PARTY.md"),
               *ROOT.glob("examples/**/README.md")]
    assert len(chinese) > 30
    for path in chinese:
        rel = path.relative_to(ROOT).as_posix()
        assert build_site.english_doc(rel, ROOT) != rel, rel


def test_english_docs_link_english_versions():
    for path in english_docs():
        for label, href in LINK.findall(path.read_text(encoding="utf-8")):
            if href.startswith(("http:", "https:", "mailto:", "#")):
                continue
            target = (path.parent / href.split("#")[0]).resolve()
            assert target.exists(), (path, href)
            rel = target.relative_to(ROOT).as_posix()
            # 只有语言切换链接指向中文原文
            assert label == "简体中文" or build_site.english_doc(rel, ROOT) == rel, (path, href)


def test_english_pages_open_english_docs(site):
    start = (site / "start/index.html").read_text(encoding="utf-8")
    assert 'data-doc="docs/INSTALL.md"' in start and 'data-doc="docs/INSTALL.zh-CN.md"' not in start
    assert 'data-doc="docs/INSTALL.zh-CN.md"' in (site / "zh/start/index.html").read_text(encoding="utf-8")
    for lang, suffix in (("en", ".en.md"), ("zh", "/README.md")):
        data = json.loads((site / f"data/{lang}/cases.json").read_text(encoding="utf-8"))
        links = [item["url"] for domain in data["domains"] for item in
                 [domain["probe"], *(c[k] for c in domain["cases"] for k in ("readme", "template_readme"))] if item]
        assert links and all(link.endswith(suffix) and (site / link).is_file() for link in links), lang
