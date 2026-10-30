"""Judges turn a workspace into a verdict. See `base.Verdict`."""
from __future__ import annotations

from ..contract import JudgeSpec
from ..plugins import Registry
from .base import Judge, Verdict
from .command import CommandJudge
from .rubric import RubricJudge

# `judge.type` in rsi.yaml; packages add types through the `rsi_anything.judges` entry point.
JUDGES = Registry("rsi_anything.judges", "judge type")
JUDGES.register("command", CommandJudge, "built-in")
JUDGES.register("rubric", RubricJudge, "built-in")


def make_judge(spec: JudgeSpec) -> Judge:
    return JUDGES.get(spec.type)(spec)


__all__ = ["JUDGES", "Judge", "Verdict", "make_judge"]
