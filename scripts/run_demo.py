#!/usr/bin/env python3
"""Run a template in its own experiment repository and export the complete or interrupted records to examples."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ["PYTHONPATH"] = str(ROOT / "src") + (os.pathsep + os.environ["PYTHONPATH"] if os.environ.get("PYTHONPATH") else "")

import yaml

from rsi_anything import gitops, ledger
from rsi_anything.agents import make_agent
from rsi_anything.contract import load
from rsi_anything.engine import Ratchet
from rsi_anything.export import export_run
from rsi_anything.ledger import RunStore
from rsi_anything.process import run as run_process


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template")
    parser.add_argument("--agent", default="codex")
    parser.add_argument("--model", required=True, help="pin the writer model explicitly")
    parser.add_argument("--jury", nargs="+")
    parser.add_argument("--task-model")
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--minutes", type=float, default=90)
    parser.add_argument("--continue-after-target", action="store_true", help="a new experiment does not stop early at the target score; round and stall limits still apply")
    parser.add_argument("--project", type=Path, help="the original experiment directory, when resuming")
    parser.add_argument("--resume", help="the original run id, named explicitly so no experiment is repeated by accident")
    parser.add_argument("--codex-isolated", action="store_true")
    parser.add_argument("--allow-commands", action="store_true")
    args = parser.parse_args()
    if args.rounds < 1 or args.minutes <= 0:
        parser.error("rounds and minutes must be greater than zero")
    if bool(args.project) != bool(args.resume):
        parser.error("--project and --resume must be given together")
    template = ROOT / "src" / "rsi_anything" / "templates" / args.template
    if not template.is_dir() or not (template / "rsi.yaml").is_file():
        parser.error("template not found")
    if args.codex_isolated:
        os.environ["RSI_CODEX_ISOLATED"] = "1"
        os.environ.setdefault("RSI_CODEX_REASONING_EFFORT", "medium")
    if args.task_model:
        os.environ["RSI_TASK_MODEL"] = args.task_model
    if args.project:
        project = args.project.resolve()
    else:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        project = ROOT / ".rsi" / "projects" / f"{stamp}-{args.template}"
        shutil.copytree(template, project, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "ABOUT.txt"))
        setup = project / "rsi_init.py"
        if setup.exists():
            result = run_process([sys.executable, str(setup)], cwd=project, timeout=900)
            print(result.stdout, end="", flush=True)
            if result.returncode:
                print(result.stderr, file=sys.stderr)
                raise RuntimeError("Preparing the template material failed; the directory is kept so you can inspect it and start again")
        config_path = project / "rsi.yaml"
        config = yaml.safe_load(config_path.read_text())
        config.setdefault("agent", {}).update(use=args.agent, model=args.model)
        config.setdefault("budget", {}).update(rounds=args.rounds, minutes=args.minutes)
        if args.continue_after_target:
            config["budget"].pop("target", None)
        for key in ("judge", "holdout"):
            if args.jury and config.get(key, {}).get("type") == "rubric":
                config[key]["models"] = args.jury
        config_path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")
        gitops.git(project, "init", "-q")
        gitops.git(project, "config", "user.name", "3136321049")
        gitops.git(project, "config", "user.email", "3136321049@users.noreply.github.com")
        gitops.git(project, "add", "--all")
        gitops.git(project, "commit", "-q", "-m", f"Prepare {args.template} experiment inputs and evaluation")
    if gitops.toplevel(project) != project:
        raise RuntimeError("The experiment must live in its own Git repository; it must not modify the main development worktree")
    print(f"Experiment directory: {project.relative_to(ROOT) if project.is_relative_to(ROOT) else project.name}", flush=True)
    contract = load(project)
    # Resume from the saved config without overwriting the original experiment's model and budget.
    agent = make_agent(contract.agent, allow_commands=args.allow_commands)
    previous = set(ledger.list_runs(project))
    try:
        summary = Ratchet(project, contract, agent).run(resume=args.resume)
        print(json.dumps({"run_id": summary.run_id, "best": summary.best, "rounds": summary.rounds,
                          "stop": summary.stop_reason}, ensure_ascii=False), flush=True)
    finally:
        current = ledger.list_runs(project)
        target = args.resume or next((r for r in reversed(current) if r not in previous), None)
        if target:
            store = RunStore(project, target)
            destination = ROOT / "examples" / args.template / "runs" / target
            export_run(store, project, destination)
            print(f"Saved records: {destination.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
