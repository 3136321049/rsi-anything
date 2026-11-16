"""`rsi` command line."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from . import __version__, gitops, ledger, llm, report
from .agents import CLI_AGENTS, detect, make_agent
from .contract import ContractError, load
from .engine import Ratchet, RunError, task_model
from .judges import make_judge
from .ledger import RunStore
from .onboard import SKILL, SKILL_DIRS
from .plugins import PluginError

TEMPLATES = Path(__file__).parent / "templates"


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
    if (dest / "rsi_init.py").exists():  # templates that need media or data generated on this machine
        print("preparing template files (this can take a minute)...")
        if subprocess.run([sys.executable, "rsi_init.py"], cwd=dest).returncode != 0:
            print("template setup failed; fix the problem above and rerun `python rsi_init.py` in", dest)
            return 1
    committed = _first_commit(dest, f"start from rsi template {args.template}")
    if committed is None:
        return 1
    print(f"created {dest} (new git repo, first commit done)" if committed
          else f"created {dest}; commit it before `rsi run` so the baseline is recorded")
    print(f"next:  cd {dest} && rsi check && rsi run")
    return 0


def _first_commit(dest: Path, message: str) -> Optional[bool]:
    """Outside a git repo: make one and commit everything (True). Inside one: leave committing to the user (False).
    None when git refused, usually because user.name/user.email are not set."""
    if subprocess.run(["git", "rev-parse"], cwd=dest, capture_output=True).returncode == 0:
        return False
    for step in (["git", "init", "-q"], ["git", "add", "-A"], ["git", "commit", "-q", "-m", message]):
        if subprocess.run(step, cwd=dest).returncode != 0:
            print("could not create the first commit; configure git user.name/user.email (`rsi setup` checks), then commit by hand")
            return None
    return True


def _ask(question: str, default: str = "") -> str:
    try:
        answer = input(f"{question}{f' [{default}]' if default else ''}: ").strip()
    except EOFError:
        answer = ""
    return answer or default


_NEW_FILES = {"rsi.yaml": "the task: goal, files the agent may edit, how it is judged",
              "judge/rubric.yaml": "what the judge scores; rewrite the questions in your own words",
              "judge/render.py": "checks the file and takes the screenshots the judge sees",
              "judge/score.py": "runs your command and turns its output into a score"}


def cmd_new(args) -> int:
    from . import scaffold

    ask = sys.stdin.isatty() and not args.yes
    dest = Path(args.dir).resolve()
    kind = args.kind
    if not kind and ask:
        print("What should get better?")
        for number, (name, text) in enumerate(scaffold.KINDS.items(), 1):
            print(f"  {number}) {name:<7} {text}")
        choice = _ask("choose 1-4", "1")
        kind = list(scaffold.KINDS)[int(choice) - 1] if choice in {"1", "2", "3", "4"} else choice
    kind = kind or "text"
    if kind not in scaffold.KINDS:
        print(f"rsi new: kind must be one of {', '.join(scaffold.KINDS)}", file=sys.stderr)
        return 2
    default_file = scaffold.DEFAULT_ARTIFACT.get(kind, "")
    artifact = args.artifact or (_ask("Which file should the agent edit", default_file).split() if ask else [default_file] if default_file else [])
    goal = args.goal or (_ask('In a sentence or two, what does "better" mean') if ask else "")
    criteria = [c.strip() for c in (args.criteria or "").split(",") if c.strip()]
    if kind in ("text", "visual") and not criteria:
        default = ", ".join(scaffold.DEFAULT_CRITERIA[kind])
        criteria = [c.strip() for c in (_ask("What should the judge score, comma-separated", default) if ask else default).split(",") if c.strip()]
    command, frozen, maximize = args.command or "", args.frozen or [], not args.minimize
    if kind == "tests":
        command = command or (_ask("Test command", "pytest -q") if ask else "pytest -q")
        if not frozen:
            default = "tests" if (dest / "tests").exists() else ""
            frozen = (_ask("Files or folders the agent must not change (the tests)", default) if ask else default).split()
    if kind == "number":
        command = command or (_ask("Command that prints the number") if ask else "")
        if ask and not args.minimize:
            maximize = not _ask("Is a higher number better? (Y/n)", "y").lower().startswith("n")
    plan = scaffold.Plan(kind=kind, artifact=artifact, goal=goal, name=scaffold.slug(dest.name).replace("_", "-"),
                         criteria=criteria, command=command, frozen=frozen, maximize=maximize,
                         agent=args.agent or "auto", jury=args.jury or ["auto"], rounds=args.rounds)
    problems = plan.problems()
    if problems:
        print("rsi new: " + "; ".join(problems) + " (see `rsi new --help`)", file=sys.stderr)
        return 2
    dest.mkdir(parents=True, exist_ok=True)
    try:
        written = scaffold.write(plan, dest)
    except (ValueError, ContractError) as exc:
        print(f"rsi new: {exc}", file=sys.stderr)
        return 2
    print(f"created in {dest}:")
    for name in written:
        print(f"  {name:<20} {_NEW_FILES.get(name, 'the starting version; replace it with your own if you have one')}")
    committed = _first_commit(dest, "start an rsi task")
    if committed is None:
        return 1
    print("  (new git repo, first commit done)" if committed
          else f"  commit these before `rsi run`:  git add {' '.join(written)} && git commit -m 'rsi task'")
    print(f"\nnext:\n  cd {dest}\n  rsi check --stress   score the starting point and test that the judge can't be fooled"
          "\n  rsi run --live       watch it improve in your browser")
    if "auto" in [plan.agent, *plan.jury]:
        print("`auto` uses the agents and models on this machine; `rsi setup` suggests who should edit and who should judge.")
    return 0


def cmd_setup(args) -> int:
    from . import onboard

    found, ready = onboard.checks()
    print("this machine:")
    for check in found:
        mark = "ok" if check.ok else "missing" if check.needed else "optional"
        print(f"  {mark:<9}{check.name:<22}{check.detail}")
    fixes = [check for check in found if not check.ok and check.fix and not check.name.startswith("/rsi skill")]
    if fixes:
        print("\nto fix:")
        for check in fixes:
            print(f"  {check.name}: {check.fix}" + ("" if check.needed else "  (only some templates need this)"))
    editor, judge = onboard.pairing(ready)
    if editor:
        same = judge == editor
        print(f"\nsuggested: {editor} edits, {judge} judges" + ("  (one model grading its own work; add a second vendor when you can)" if same else ""))
        print(f"  to make `auto` in rsi.yaml mean this here:  export RSI_AGENT={editor} RSI_JURY=cli:{judge}")
    stale = [name for name in ready if name in onboard.SKILL_DIRS and not onboard.skill_current(name)]
    if stale and not args.check:
        install = args.yes or (sys.stdin.isatty() and _ask(f"\ninstall the /rsi skill for {', '.join(stale)}? (y/N)", "n").lower().startswith("y"))
        if install:
            for line in onboard.install_skill(stale):
                print("  " + line)
        else:
            print(f"\nthe /rsi skill is not installed for {', '.join(stale)}; `rsi setup --yes` installs it")
    print("\nnext:  rsi new          set up a task of your own\n       rsi init         start from a template")
    return 1 if any(not check.ok and check.needed for check in found) else 0


def _contract(args):
    project = Path(args.dir).resolve()
    contract = load(project)
    # Per-machine defaults for contracts that say `auto`, e.g. RSI_AGENT=codex RSI_JURY="cli:codex deepseek:deepseek-chat"
    if contract.agent.use == "auto" and os.environ.get("RSI_AGENT"):
        contract.agent.use = os.environ["RSI_AGENT"]
    if contract.judge.models == ["auto"] and os.environ.get("RSI_JURY"):
        contract.judge.models = os.environ["RSI_JURY"].split()
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
    from .strategy import make_strategy

    make_strategy(contract.strategy)  # an unknown plugin name fails here, not after the baseline
    print(f"contract `{contract.name}` ok: artifact {contract.artifact}, judge {contract.judge.type}"
          + (f", strategy {contract.strategy}" if contract.strategy != "greedy" else ""))
    repo = gitops.toplevel(project)
    from . import workspace

    rel = "" if project == repo else project.relative_to(repo).as_posix()
    prefix = (lambda ps: [f"{rel}/{p}" for p in ps]) if rel else (lambda ps: ps)
    frozen = workspace.snapshot_frozen(repo, gitops.head(repo), prefix(contract.frozen_files))
    print(f"frozen judge files at HEAD: {', '.join(sorted(frozen)) or '(none committed yet!)'}")
    ws = workspace.build(repo, gitops.head(repo), frozen, assets=prefix(contract.assets))
    try:
        with task_model(contract):
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
    if not args.stress:
        return 0
    from . import stress

    print("\njudge health check: sabotaged copies of the artifact must all lose")
    judge = make_judge(contract.judge)
    probes = stress.run(repo, rel, gitops.head(repo), frozen, contract, judge, prefix(contract.assets))
    missed = [p.name for p in probes if not p.caught]
    print(f"caught {len(probes) - len(missed)}/{len(probes)}" + (f"; fix the judge before running: {', '.join(missed)}" if missed else ""))
    return 1 if missed else 0


def cmd_run(args) -> int:
    project, contract = _contract(args)
    agent = make_agent(contract.agent, allow_commands=args.allow_commands)
    ratchet = Ratchet(project, contract, agent, log=lambda line: print(line, flush=True))
    server = None
    if args.live:
        from . import live

        # Follow only the run started now (or the named run when resuming), without replaying old records first.
        runs = ratchet.repo / ledger.STATE_DIR / "runs"
        before = set(ledger.list_runs(ratchet.repo))
        target = runs / args.resume if args.resume else None
        server = live.serve(lambda: target or next((runs / r for r in reversed(ledger.list_runs(ratchet.repo))
                                                    if r not in before), None), args.port)
        print(f"live view: http://127.0.0.1:{server.server_address[1]}/", flush=True)
    try:
        summary = ratchet.run(resume=args.resume)
    finally:
        if server is not None:
            server.shutdown()
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


def cmd_export(args) -> int:
    from .export import export_run

    store, repo = _store(args)
    written = export_run(store, repo, Path(args.to).resolve(), with_logs=args.with_logs)
    print(f"exported {len(written)} files to {args.to} (local paths scrubbed; review before publishing)")
    return 0


def cmd_watch(args) -> int:
    import threading

    from . import live

    repo = gitops.toplevel(Path(args.dir).resolve())
    fixed = repo / ledger.STATE_DIR / "runs" / args.run if args.run else None
    if fixed is not None and not fixed.is_dir():
        raise RunError(f"no run named {args.run}")
    server = live.serve(lambda: fixed or live.latest(repo), args.port, open_browser=not args.no_open)
    print(f"watching {'run ' + args.run if args.run else 'the latest run'} at "
          f"http://127.0.0.1:{server.server_address[1]}/  (Ctrl-C to stop)")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        server.shutdown()
    return 0


def cmd_share(args) -> int:
    from . import live
    from .export import scrubber

    store, repo = _store(args)
    dest = Path(args.to or f"{store.run_id}.html").resolve()
    live.share(store.dir, dest, scrub=scrubber(repo))
    print(f"wrote {dest}: one file with images embedded and local paths removed; review it before sharing")
    return 0


def cmd_agents(args) -> int:
    installed = {spec.name for spec in detect(check=False)}
    responsive = {spec.name for spec in detect()}
    print("coding-agent CLIs (use with `agent.use` or as judges via cli:<name>):")
    for spec in CLI_AGENTS.values():
        mark = "ready" if spec.name in responsive else "installed, not responding to --version" if spec.name in installed else "-"
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
    from .onboard import install_skill

    targets = args.to or [spec.name for spec in detect() if spec.name in SKILL_DIRS]
    if not targets:
        print("no agent with a skills folder detected; copy this file into your agent's instructions:\n" + str(SKILL))
        return 0
    for line in install_skill(targets):
        print("  " + line)
    return 0


def cmd_plugins(args) -> int:
    from .agents.registry import AGENTS
    from .judges import JUDGES
    from .strategy import STRATEGIES

    def show(title: str, groups: dict[str, list[str]]) -> None:
        print(title)
        for origin, names in groups.items():
            print(f"  {origin}: {', '.join(names)}")

    def by_origin(origins: dict[str, str]) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = {}
        for name, origin in origins.items():
            groups.setdefault(origin, []).append(name)
        return groups

    show("judges (judge.type)", by_origin(JUDGES.origins()))
    show("agents (agent.use)", {"built-in": ["auto", "api", "command"], "coding-agent CLIs, see `rsi agents`": list(CLI_AGENTS),
                                **by_origin(AGENTS.origins())})
    show("strategies (strategy)", by_origin(STRATEGIES.origins()))
    print("\nPackages add their own through entry points; see EXTENDING.md, section Plugins.")
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

    p = sub.add_parser("setup", help="check this machine, suggest who edits and who judges, install the /rsi skill")
    p.add_argument("--check", action="store_true", help="only report; change nothing")
    p.add_argument("--yes", "-y", action="store_true", help="install the /rsi skill without asking")
    p.set_defaults(func=cmd_setup)

    p = sub.add_parser("new", help="set up a task of your own by answering a few questions",
                       description="Write rsi.yaml, a judge and a starting file. Asks for anything not given as an option.")
    p.add_argument("dir", nargs="?", default=".", help="task folder (default: here)")
    p.add_argument("--kind", help="text, visual, tests or number")
    p.add_argument("--artifact", nargs="+", help="file(s) the agent may edit")
    p.add_argument("--goal", help='what "better" means, in plain words')
    p.add_argument("--criteria", help="text/visual: what the judge scores, comma-separated")
    p.add_argument("--command", help="tests/number: the command to run")
    p.add_argument("--frozen", nargs="+", help="tests/number: files the agent must not change")
    p.add_argument("--minimize", action="store_true", help="number: lower is better")
    p.add_argument("--agent", help="coding agent (default auto)")
    p.add_argument("--jury", nargs="+", help="text/visual: judge models (default auto)")
    p.add_argument("--rounds", type=int, default=5)
    p.add_argument("--yes", "-y", action="store_true", help="never ask; use defaults for anything not given")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("init", help="start a project from a template")
    p.add_argument("template", nargs="?")
    p.add_argument("dir", nargs="?")
    p.set_defaults(func=cmd_init)

    for name, func, text in (("check", cmd_check, "validate rsi.yaml and score the current state"),
                             ("run", cmd_run, "run the ratchet")):
        p = sub.add_parser(name, help=text)
        p.add_argument("dir", nargs="?", default=".")
        p.add_argument("--jury", nargs="+", help="override judge models, e.g. cli:codex deepseek:deepseek-chat")
        if name == "check":
            p.add_argument("--stress", action="store_true",
                           help="also check the judge against sabotaged copies (empty, truncated, stuffed, injected...)")
        if name == "run":
            p.add_argument("--agent", help="auto, api, command, or a CLI name (see `rsi agents`)")
            p.add_argument("--model", help="model for the agent")
            p.add_argument("--rounds", type=int)
            p.add_argument("--minutes", type=float)
            p.add_argument("--allow-commands", action="store_true",
                           help="let the agent run shell commands (tests, benchmarks) without asking")
            p.add_argument("--resume", metavar="RUN_ID")
            p.add_argument("--live", action="store_true", help="open a page that follows the run as it evolves")
            p.add_argument("--port", type=int, default=8765, help="port for --live (default 8765)")
        p.set_defaults(func=func)

    for name, func in (("status", cmd_status), ("report", cmd_report)):
        p = sub.add_parser(name, help=f"{name} of the latest (or given) run")
        p.add_argument("run", nargs="?")
        p.add_argument("--dir", default=".")
        p.set_defaults(func=func)

    p = sub.add_parser("export", help="copy a run's ledger, diffs and report somewhere shareable")
    p.add_argument("run", nargs="?")
    p.add_argument("--to", required=True)
    p.add_argument("--dir", default=".")
    p.add_argument("--with-logs", action="store_true", help="include raw agent logs")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("watch", help="follow a run in the browser as it evolves (the latest run by default)")
    p.add_argument("run", nargs="?")
    p.add_argument("--dir", default=".")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-open", action="store_true", help="print the address instead of opening a browser")
    p.set_defaults(func=cmd_watch)

    p = sub.add_parser("share", help="save a run as one self-contained HTML page")
    p.add_argument("run", nargs="?")
    p.add_argument("--to", help="output file (default: <run-id>.html)")
    p.add_argument("--dir", default=".")
    p.set_defaults(func=cmd_share)

    sub.add_parser("agents", help="list supported coding agents and detected API keys").set_defaults(func=cmd_agents)
    sub.add_parser("plugins", help="list judge types, agents and strategies, including installed plugins").set_defaults(func=cmd_plugins)
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
    except (ContractError, PluginError, RunError, gitops.GitError, llm.LLMError, RuntimeError) as exc:
        print(f"rsi: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
