#!/usr/bin/env python3
"""在独立实验仓库里运行模板，并将完整或中断记录导出到 examples。"""
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
    parser.add_argument("--model", required=True, help="显式固定写手型号")
    parser.add_argument("--jury", nargs="+")
    parser.add_argument("--task-model")
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--minutes", type=float, default=90)
    parser.add_argument("--continue-after-target", action="store_true", help="新实验不按目标分数提前结束，仍受轮数和停滞条件限制")
    parser.add_argument("--project", type=Path, help="续跑时指定原实验目录")
    parser.add_argument("--resume", help="明确指定原 run id，避免无意重复实验")
    parser.add_argument("--codex-isolated", action="store_true")
    parser.add_argument("--allow-commands", action="store_true")
    args = parser.parse_args()
    if args.rounds < 1 or args.minutes <= 0:
        parser.error("轮数与时间必须大于零")
    if bool(args.project) != bool(args.resume):
        parser.error("--project 与 --resume 必须同时给出")
    template = ROOT / "src" / "rsi_anything" / "templates" / args.template
    if not template.is_dir() or not (template / "rsi.yaml").is_file():
        parser.error("模板不存在")
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
                raise RuntimeError("模板素材准备失败，已保留目录，可检查后重新启动")
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
        gitops.git(project, "commit", "-q", "-m", f"准备 {args.template} 实验输入与评价")
    if gitops.toplevel(project) != project:
        raise RuntimeError("实验必须位于独立 Git 仓库，不能修改主开发工作区")
    print(f"实验目录：{project.relative_to(ROOT) if project.is_relative_to(ROOT) else project.name}", flush=True)
    contract = load(project)
    # 从已保存配置续跑，不覆盖原实验的模型和预算。
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
            print(f"保存记录：{destination.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
