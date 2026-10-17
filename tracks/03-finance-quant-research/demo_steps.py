"""Scripted mutations for the finance ratchet demo."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _read(name: str) -> str:
    return (ROOT / "drafts" / name).read_text(encoding="utf-8")


def steps() -> list[dict]:
    return [
        {
            "hypothesis": "补上八家毛利率/产能对照、份额加总与12条已核验引用",
            "lesson": "没有竞品表和来源编号的行业散文过不了硬门禁。",
            "files": {"report.md": _read("v2_competitor_table.md")},
        },
        {
            "hypothesis": "用未登记的SRC-99和口头禅抄近路",
            "lesson": "假引用和空话会让门禁失败，分数再好看也要回滚。",
            "files": {"report.md": _read("v3_hallucinated_source.md")},
        },
        {
            "hypothesis": "写深看空逻辑，并补上BOM与敏感性矩阵",
            "lesson": "看空章节要有篇幅，单台价值量要能加总复核。",
            "files": {"report.md": _read("v4_bear_case_bom.md")},
        },
        {
            "hypothesis": "篡改冻结的rubric.yaml，企图把硬门禁改成满分",
            "lesson": "奖励黑客先改尺子。守卫比对SHA-256后连候选稿一起退回。",
            "files": {
                "rubric.yaml": _read("v5_Tamper_Rubric_Attempt.md"),
                "report.md": _read("v6_champion.md"),
            },
        },
        {
            "hypothesis": "在冻结裁判下补齐证伪触发、情景复原和跟踪指标",
            "lesson": "过了门禁之后，剩下的分数来自可打脸的条件和能复原的TAM。",
            "files": {"report.md": _read("v6_champion.md")},
        },
    ]
