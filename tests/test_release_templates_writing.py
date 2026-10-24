"""离线验证三个资料写作模板的产物和关键事实检查，不调用模型。"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from rsi_anything.judges.rubric import code_gates, load_rubric


TEMPLATES = Path(__file__).resolve().parents[1] / "src/rsi_anything/templates"
DOMAINS = {
    "business-report": ("report.md", "report.html"),
    "literature-review": ("review.md", "review.html"),
    "medical-explainer": ("explainer.md", "explainer.html"),
}


def prepare(tmp_path, domain, changes=None):
    project = tmp_path / domain
    shutil.copytree(TEMPLATES / domain, project)
    for name, content in (changes or {}).items():
        (project / name).write_text(content, encoding="utf-8")
    result = subprocess.run([sys.executable, "judge/prepare.py"], cwd=project,
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    gates = json.loads((project / "out/gates.json").read_text(encoding="utf-8"))
    return project, gates


@pytest.mark.parametrize("domain", DOMAINS)
def test_default_writing_templates_prepare_and_pass_basic_gates(tmp_path, domain):
    project, gates = prepare(tmp_path, domain)
    assert gates and all(gates.values()), gates
    artifact, page = DOMAINS[domain]
    assert (project / "out" / artifact).stat().st_size > 300
    assert '<html lang="zh-CN">' in (project / "out" / page).read_text(encoding="utf-8")
    rubric = load_rubric(project / "judge/rubric.yaml")
    rendered = (project / "out/evaluation.md").read_text(encoding="utf-8")
    assert all(code_gates(rendered, rubric["gates"]).values())
    config = yaml.safe_load((project / "rsi.yaml").read_text(encoding="utf-8"))
    assert config["outputs"] == ["out"]
    assert config["judge"]["prepare"] == "{python} judge/prepare.py"
    assert set(config["artifact"]).isdisjoint(config["judge"]["files"])


def test_business_numbers_are_computed_from_frozen_figures(tmp_path):
    project, _ = prepare(tmp_path, "business-report")
    values = json.loads((project / "out/metrics.json").read_text(encoding="utf-8"))["rendered_values"]
    assert values["revenue_2024"] == "391,035 百万美元"
    assert values["revenue_growth"] == "+2.02%"
    assert values["net_income_growth"] == "-3.36%"
    assert values["services_share_2024"] == "24.59%"
    chart = (project / "out/chart-1.mmd").read_text(encoding="utf-8")
    assert "bar [383285, 391035]" in chart


def test_business_rejects_fabricated_literal_and_unknown_chart(tmp_path):
    text = (TEMPLATES / "business-report/report.md").read_text(encoding="utf-8")
    text += "\n总营收是999999百万美元。\n"
    _, gates = prepare(tmp_path, "business-report", {
        "report.md": text, "charts.json": '{"metrics":["invented_metric"]}'})
    assert gates["金额和比率使用资料插值"] is False
    assert gates["图表指标有效"] is False


def test_business_reports_unknown_placeholder(tmp_path):
    text = (TEMPLATES / "business-report/report.md").read_text(encoding="utf-8")
    _, gates = prepare(tmp_path, "business-report", {"report.md": text + "\n{{made_up_profit}}"})
    assert gates["数字资料键存在"] is False


def test_literature_mapping_cannot_claim_a_sentence_missing_from_article(tmp_path):
    mapping = json.loads((TEMPLATES / "literature-review/evidence.json").read_text(encoding="utf-8"))
    mapping["claims"][0]["claim"] = "这句论断没有出现在待评审的实际文章中。"
    _, gates = prepare(tmp_path, "literature-review", {"evidence.json": json.dumps(mapping, ensure_ascii=False)})
    assert gates["证据映射有效"] is False
    assert gates["映射覆盖全部来源"] is False


def test_literature_rejects_unknown_source_and_unrelated_reference(tmp_path):
    text = (TEMPLATES / "literature-review/review.md").read_text(encoding="utf-8")
    text = text.replace("[S1]", "[S99]")
    text += "\nhttps://example.org/fabricated-paper\n"
    _, gates = prepare(tmp_path, "literature-review", {"review.md": text})
    assert gates["来源编号有效"] is False
    assert gates["未引入资料外链接"] is False
    assert gates["证据映射有效"] is False


def test_literature_invalid_json_is_feedback_not_crash(tmp_path):
    project, gates = prepare(tmp_path, "literature-review", {"evidence.json": "{broken"})
    assert gates["证据映射有效"] is False
    assert "证据映射有效" in (project / "out/notes.txt").read_text(encoding="utf-8")


def test_medical_rejects_manual_guideline_number_and_dosing(tmp_path):
    text = (TEMPLATES / "medical-explainer/explainer.md").read_text(encoding="utf-8")
    text = text.replace("{{moderate_minutes}}", "600分钟") + "\n每天服用10毫克药物。\n"
    _, gates = prepare(tmp_path, "medical-explainer", {"explainer.md": text})
    assert gates["指南数量使用固定资料"] is False
    assert gates["没有药物剂量或疗效保证"] is False


def test_medical_keeps_audience_and_public_education_scope(tmp_path):
    text = (TEMPLATES / "medical-explainer/explainer.md").read_text(encoding="utf-8")
    text = text.replace("一般健康成人", "所有患者").replace("不能替代", "完全替代")
    _, gates = prepare(tmp_path, "medical-explainer", {"explainer.md": text})
    assert gates["适用边界清楚"] is False


@pytest.mark.parametrize("domain", DOMAINS)
def test_empty_article_is_rejected(tmp_path, domain):
    _, gates = prepare(tmp_path, domain, {DOMAINS[domain][0]: ""})
    assert gates["正文有实质内容"] is False


@pytest.mark.parametrize("domain", DOMAINS)
def test_html_previews_escape_candidate_markup(tmp_path, domain):
    name, output = DOMAINS[domain]
    original = (TEMPLATES / domain / name).read_text(encoding="utf-8")
    project, _ = prepare(tmp_path, domain, {name: original + "\n<script>alert('candidate')</script>\n"})
    page = (project / "out" / output).read_text(encoding="utf-8")
    assert "<script>alert('candidate')</script>" not in page
    assert "&lt;script&gt;" in page
