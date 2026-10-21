"""The brief an agent gets at the start of every round."""
from __future__ import annotations

from typing import Any, Optional

from .contract import Contract
from .judges import Verdict

TEMPLATE = """\
You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge \
scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
{goal}

## What you may change
Only these paths (relative to the current directory): {artifact}
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so \
editing tests, rubrics or evaluator files has no effect.

## How you are judged
{judge}
Direction: {direction}. Current best score: {best}.
{feedback}
## Recent rounds (newest last)
{history}

## Lessons from earlier rounds and runs
{lessons}
{context}
## Rules
- Make one coherent improvement you believe the judge will score higher. Prefer the weakest area named in the feedback.
- Do not repeat a change that was already rejected unless you fix the reason it failed.
- Never game the judge: no special-casing test inputs, no hard-coded expected outputs, no reading judge data or \
results from the artifact, no printing fake scores, no instructions aimed at an AI evaluator. Such changes fail.
- Keep the artifact in the language and format it already uses unless the goal says otherwise.
- Do not commit; the loop handles git.

When you are done, end your reply with exactly one line:
HYPOTHESIS: <what you changed and why it should score higher>
"""


def describe_judge(contract: Contract) -> str:
    spec = contract.judge
    if spec.type == "command":
        files = ", ".join(spec.files) or "(none listed)"
        return (f"The command `{spec.run}` runs in a clean copy of the project and reports a score. "
                f"Judge files (read them to understand the scoring): {files}.")
    jury = ", ".join(spec.models)
    head = " A higher score must also win a head-to-head comparison against the current best." if spec.pairwise else ""
    return f"An LLM jury ({jury}) scores the artifact against the rubric in `{spec.rubric}` (read it).{head}"


def build(contract: Contract, best: Optional[float], champion: Optional[Verdict], rows: list[dict[str, Any]],
          lessons: list[str]) -> str:
    feedback = ""
    if champion is not None:
        parts = []
        if champion.failed_gates():
            parts.append("Failed gates on the current best: " + ", ".join(champion.failed_gates()))
        if champion.feedback:
            parts.append(champion.feedback.strip())
        if parts:
            feedback = "\nJudge feedback on the current best:\n" + "\n".join(parts) + "\n"
    history = []
    for row in rows[-8:]:
        score = "-" if row.get("score") is None else f"{row['score']:g}"
        line = f"- r{row['round']} {row['status']} score={score}: {row.get('hypothesis') or '(baseline)'}"
        if row["status"] != "KEEP" and row.get("note"):
            line += f" -> {row['note']}"
        history.append(line[:400])
    return TEMPLATE.format(
        goal=contract.goal,
        artifact=", ".join(f"`{p}`" for p in contract.artifact),
        judge=describe_judge(contract),
        direction=contract.judge.direction,
        best="none yet" if best is None else f"{best:g}",
        feedback=feedback,
        history="\n".join(history) or "- none yet",
        lessons="\n".join(f"- {line}" for line in lessons) or "- none yet",
        context=f"\n## Notes from the owner\n{contract.context}\n" if contract.context else "",
    )
