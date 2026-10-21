"""Judges turn a workspace into a verdict. See `base.Verdict`."""
from __future__ import annotations

from ..contract import JudgeSpec
from .base import Judge, Verdict
from .command import CommandJudge
from .rubric import RubricJudge


def make_judge(spec: JudgeSpec) -> Judge:
    if spec.type == "command":
        return CommandJudge(spec)
    if spec.type == "rubric":
        return RubricJudge(spec)
    raise ValueError(f"unknown judge type {spec.type}")


__all__ = ["Judge", "Verdict", "make_judge"]
