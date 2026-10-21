from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

JUDGE = textwrap.dedent("""\
    import json, os
    value = int(open("value.txt").read().strip() or 0)
    gates = {"not_negative": value >= 0}
    with open(os.environ["RSI_RESULT"], "w") as out:
        json.dump({"score": value, "gates": gates, "feedback": f"value is {value}"}, out)
    """)

# Each call pops the next action from plan.json: write files, then print a hypothesis.
AGENT = textwrap.dedent("""\
    import json, os, sys, pathlib
    plan_path = pathlib.Path(sys.argv[1])
    plan = json.loads(plan_path.read_text())
    step = plan.pop(0) if plan else {}
    plan_path.write_text(json.dumps(plan))
    for rel, content in step.get("write", {}).items():
        target = pathlib.Path(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    print(step.get("say", ""))
    print("HYPOTHESIS: " + step.get("hypothesis", "step"))
    sys.exit(step.get("exit", 0))
    """)

CONTRACT = textwrap.dedent("""\
    name: toy
    goal: Make the number in value.txt as large as possible.
    artifact: [value.txt]
    judge:
      run: python3 judge.py
      files: [judge.py]
    agent:
      use: command
      command: "python3 {agent} {plan}"
    budget:
      rounds: {rounds}
      stagnation: {stagnation}
    """)


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def toy(tmp_path):
    """A committed toy project plus a scripted agent. Returns a factory taking the agent's plan."""

    def make(plan: list[dict], rounds: int = 3, stagnation: int = 5) -> Path:
        project = tmp_path / "project"
        project.mkdir()
        tools = tmp_path / "tools"
        tools.mkdir()
        (tools / "agent.py").write_text(AGENT)
        (tools / "plan.json").write_text(json.dumps(plan))
        (project / "judge.py").write_text(JUDGE)
        (project / "value.txt").write_text("1\n")
        (project / "rsi.yaml").write_text(
            CONTRACT.replace("{agent}", str(tools / "agent.py")).replace("{plan}", str(tools / "plan.json"))
            .replace("{rounds}", str(rounds)).replace("{stagnation}", str(stagnation)))
        git(project, "init", "-q")
        git(project, "config", "user.email", "test@example.com")
        git(project, "config", "user.name", "test")
        git(project, "add", "-A")
        git(project, "commit", "-q", "-m", "start")
        return project

    return make
