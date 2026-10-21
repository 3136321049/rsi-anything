"""`rsi` command line."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__, gitops, ledger, llm, report
from .agents import CLI_AGENTS, detect, make_agent
from .contract import ContractError, load
from .engine import Ratchet, RunError
from .judges import make_judge
from .ledger import RunStore

TEMPLATES = Path(__file__).parent / "templates"
SKILL = Path(__file__).parent / "skill" / "SKILL.md"
# Where each agent looks for user-level skills (agents without a skills folder get printed instructions).
SKILL_DIRS = {
    "claude": "~/.claude/skills/rsi",
    "codex": "~/.codex/skills/rsi",
    "cursor": "~/.cursor/skills/rsi",
    "codebuddy": "~/.codebuddy/skills/rsi",
}


def _templates() -> dict[str, str]:
    found = {}
    for path in sorted(TEMPLATES.iterdir()) if TEMPLATES.exists() else []:
        if (path / "rsi.yaml").exists():
            about = (path / "ABOUT.txt").read_text(encoding="utf-8").strip() if (path / "ABOUT.txt").exists() else ""
            found[path.name] = about
    return found


def cmd_init(args) -> int:
    templates = _templates()
    if not args.template or args.template not in templates:
        print("templates:")
        for name, about in templates.items():
            print(f"  {name:<16} {about}")
        return 0 if not args.template else 2
    dest = Path(args.dir or args.template).resolve()
    if dest.exists() and any(dest.iterdir()):
        print(f"{dest} is not empty; choose another directory")
        return 2
    shutil.copytree(TEMPLATES / args.template, dest, ignore=shutil.ignore_patterns("ABOUT.txt", "__pycache__"),
                    dirs_exist_ok=True)
    inside_repo = subprocess.run(["git", "rev-parse"], cwd=dest, capture_output=True).returncode == 0
    if not inside_repo:
        for step in (["git", "init", "-q"], ["git", "add", "-A"],
                     ["git", "commit", "-q", "-m", f"start from rsi template {args.template}"]):
            if subprocess.run(step, cwd=dest).returncode != 0:
                print("could not create the first commit; configure git user.name/user.email, then commit by hand")
                return 1
        print(f"created {dest} (new git repo, first commit done)")
    else:
        print(f"created {dest}; commit it before `rsi run` so the baseline is recorded")
    print(f"next:  cd {dest} && rsi check && rsi run")
    return 0


def _contract(args):
    project = Path(args.dir).resolve()
    contract = load(project)
    if getattr(args, "agent", None):
        contract.agent.use = args.agent
    if getattr(args, "model", None):
        contract.agent.model = args.model
    if getattr(args, "rounds", None):
        contract.budget.rounds = args.rounds
    if getattr(args, "minutes", None):
        contract.budget.minutes = args.minutes
    if getattr(args, "jury", None):
        contract.judge.models = args.jury
    return project, contract


def cmd_check(args) -> int:
    project, contract = _contract(args)
    print(f"contract `{contract.name}` ok: artifact {contract.artifact}, judge {contract.judge.type}")
    repo = gitops.toplevel(project)
    from . import workspace

    rel = "" if project == repo else project.relative_to(repo).as_posix()
    prefix = (lambda ps: [f"{rel}/{p}" for p in ps]) if rel else (lambda ps: ps)
    frozen = workspace.snapshot_frozen(repo, gitops.head(repo), prefix(contract.frozen_files))
    print(f"frozen judge files at HEAD: {', '.join(sorted(frozen)) or '(none committed yet!)'}")
    ws = workspace.build(repo, gitops.head(repo), frozen, assets=prefix(contract.assets))
    try:
        verdict = make_judge(contract.judge).evaluate(ws / rel if rel else ws, 0)
    finally:
        workspace.discard(ws)
    if not verdict.ok:
        print(f"judge failed on HEAD: {verdict.error}")
        if verdict.metrics.get("output_tail"):
            print(verdict.metrics["output_tail"])
        return 1
    print(f"baseline score {verdict.score:g}; gates {verdict.gates}")
    if verdict.feedback:
        print("feedback:\n" + verdict.feedback)
    return 0


def cmd_run(args) -> int:
    project, contract = _contract(args)
    agent = make_agent(contract.agent, allow_commands=args.allow_commands)
    ratchet = Ratchet(project, contract, agent, log=lambda line: print(line, flush=True))
    summary = ratchet.run(resume=args.resume)
    store = RunStore(ratchet.repo, summary.run_id)
    md, page = report.write(store, ratchet.repo)
    print()
    print(report.terminal(store))
    print(f"\nstopped: {summary.stop_reason}")
    if summary.holdout:
        print(f"hold-out judge: {summary.holdout.get('baseline')} -> {summary.holdout.get('final')}")
    print(f"report: {page}")
    if summary.kept:
        print(f"keep the result:  git merge {summary.branch}")
    return 0


def _store(args) -> tuple[RunStore, Path]:
    repo = gitops.toplevel(Path(args.dir).resolve())
    runs = ledger.list_runs(repo)
    if not runs:
        raise RunError("no runs yet")
    run_id = args.run or runs[-1]
    return RunStore(repo, run_id), repo


def cmd_status(args) -> int:
    store, _ = _store(args)
    print(report.terminal(store))
    return 0


def cmd_report(args) -> int:
    store, repo = _store(args)
    md, page = report.write(store, repo)
    print(f"{md}\n{page}")
    return 0


def cmd_agents(args) -> int:
    found = {spec.name for spec in detect()}
    print("coding-agent CLIs (use with `agent.use` or as judges via cli:<name>):")
    for spec in CLI_AGENTS.values():
        mark = "installed" if spec.name in found else "-"
        print(f"  {spec.name:<10} {spec.title:<18} {spec.region:<10} {mark}")
    print("\nAPI keys found (use with `agent.use: api` or as judges via <provider>:<model>):")
    any_key = False
    for provider, (_, base, env) in llm.PROVIDERS.items():
        if env and os.environ.get(env):
            any_key = True
            print(f"  {provider:<12} ${env}")
    if not any_key:
        print("  none (that's fine if you have a CLI above)")
    return 0


def cmd_skill(args) -> int:
    if args.action == "show":
        print(SKILL.read_text(encoding="utf-8"))
        return 0
    targets = args.to or [spec.name for spec in detect() if spec.name in SKILL_DIRS]
    if not targets:
        print("no agent with a skills folder detected; copy this file into your agent's instructions:\n" + str(SKILL))
        return 0
    for name in targets:
        if name not in SKILL_DIRS:
            print(f"  {name}: no skills folder; add the text of `rsi skill show` to its instructions file")
            continue
        dest = Path(os.path.expanduser(SKILL_DIRS[name]))
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SKILL, dest / "SKILL.md")
        print(f"  {name}: installed {dest / 'SKILL.md'}")
    return 0


def cmd_ask(args) -> int:
    reply = llm.ask(llm.parse(args.model), args.prompt, timeout=args.timeout)
    print(reply.text)
    if reply.cost_usd is not None:
        print(f"\n(cost ${reply.cost_usd:.4f}, {reply.seconds:.1f}s)", file=sys.stderr)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="rsi", description="Improve anything you can score, one proven step at a time.")
    parser.add_argument("--version", action="version", version=f"rsi-anything {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="start a project from a template")
    p.add_argument("template", nargs="?")
    p.add_argument("dir", nargs="?")
    p.set_defaults(func=cmd_init)

    for name, func, text in (("check", cmd_check, "validate rsi.yaml and score the current state"),
                             ("run", cmd_run, "run the ratchet")):
        p = sub.add_parser(name, help=text)
        p.add_argument("dir", nargs="?", default=".")
        p.add_argument("--jury", nargs="+", help="override judge models, e.g. cli:codex deepseek:deepseek-chat")
        if name == "run":
            p.add_argument("--agent", help="auto, api, command, or a CLI name (see `rsi agents`)")
            p.add_argument("--model", help="model for the agent")
            p.add_argument("--rounds", type=int)
            p.add_argument("--minutes", type=float)
            p.add_argument("--allow-commands", action="store_true",
                           help="let the agent run shell commands (tests, benchmarks) without asking")
            p.add_argument("--resume", metavar="RUN_ID")
        p.set_defaults(func=func)

    for name, func in (("status", cmd_status), ("report", cmd_report)):
        p = sub.add_parser(name, help=f"{name} of the latest (or given) run")
        p.add_argument("run", nargs="?")
        p.add_argument("--dir", default=".")
        p.set_defaults(func=func)

    sub.add_parser("agents", help="list supported coding agents and detected API keys").set_defaults(func=cmd_agents)
    p = sub.add_parser("skill", help="install the /rsi skill into your coding agents, or print it")
    p.add_argument("action", choices=["install", "show"])
    p.add_argument("--to", nargs="+", help=f"agents to install into (default: detected among {', '.join(SKILL_DIRS)})")
    p.set_defaults(func=cmd_skill)
    p = sub.add_parser("ask", help="send one prompt to a model reference, to test access")
    p.add_argument("model")
    p.add_argument("prompt")
    p.add_argument("--timeout", type=int, default=300)
    p.set_defaults(func=cmd_ask)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ContractError, RunError, gitops.GitError, llm.LLMError, RuntimeError) as exc:
        print(f"rsi: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
