# Switching Computers and Assistant Handoff

Updated: 2026-10-24. This project lets a user give a goal, after which AI repeatedly edits artifacts such as code, articles, prompts, and video plans, runs checks and takes feedback, keeps the better version, and keeps trying. The first release prioritizes showing the process and the work clearly; evaluation and search methods get stronger later.

## What is done so far

Current version is `0.3.0.dev0`, and the development mainline is **`rebuild`**. `main` is still an older version; when switching computers, explicitly check out `rebuild`.

- All 16 domains and 18 templates are in place (D16 visual was added after the first release). 14 domains have complete real multi-round runs, initial/intermediate/final work, and independent re-verification; the copywriting domain includes both a single article and a writing handbook.
- The general loop saves per-round work, config, changes, scores, and accept/reject reasons, with interrupt recovery, timeout cleanup, and media export added.
- `examples/index.html` provides domain, run, and version comparison; `examples/showcase-media/openrsi-demo.mp4` is a 35-second short of real work.
- Before this upload, the full regression of 115 tests passed, the install includes 16 templates, and a clean environment ran init, scoring, a test-agent run, and export. Exact results and limits are in the [progress table](GOAL-PROGRESS.md) and [release audit](RELEASE-AUDIT.md).

D07 got real generated videos for the initial version and round one; the free service then errored, and no new work was produced. D15 has no personal GPU, only a template and real device detection, with empty performance results. Both are kept pending resources and are not counted toward complete multi-round runs.

## First takeover on another computer

Clone with your own GitHub login or SSH identity:

```bash
git clone --branch rebuild git@github.com:3136321049/rsi-anything.git
cd rsi-anything
git config user.name 3136321049
git config user.email 3136321049@users.noreply.github.com
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
```

If the repo is already cloned, first run `git status --short` and save uncommitted local work, then run `git fetch origin`, `git switch rebuild`, `git pull --ff-only origin rebuild`. If the branch has diverged, inspect the differences first; don't overwrite with a force push or hard reset.

Training and backtesting cases need each template's `requirements.txt` installed separately; video cases need FFmpeg/ffprobe. Personal assistants log in independently on the new computer. For CLI paths, models, APIs, and isolation config, see the [install guide](INSTALL.zh-CN.md); don't copy credentials or global config from another computer.

Viewing completed results needs no model account:

```bash
python scripts/build_showcase.py
python -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/examples/index.html` in your own browser. GitHub's file preview can't run this interactive page.

## How Codex and Claude Code hand off

Both share the root [AGENTS.md](../AGENTS.md), and Claude Code pulls in the same conventions via [CLAUDE.md](../CLAUDE.md). Work is passed through Git and shared docs, not any one computer's chat history.

Only one computer owns changes on `rebuild` at a time. Pull the latest commits before starting; at the end, check the upload scope, commit, and push; pull again after switching computers. For parallel development, use separate topic branches and integrate with normal merges, so two computers never edit the same raw experiment at once.

Each handoff updates `docs/DEVLOG.md` with the date, the assistant used, what changed, verification results, open issues, and next steps. Update `docs/GOAL-PROGRESS.md` when a domain's status changes; commands, work, and re-verification records for specific tasks go in the corresponding `examples/<template>/README.md`.

You can give this to the assistant on the new computer:

> First read the root AGENTS.md, docs/COLLABORATION.md, docs/HANDOFF.md, and docs/GOAL-PROGRESS.md, and check the current branch, remote, and uncommitted changes. Take over from the repo's current source and raw experiments, keeping failed and unknown results. Don't rerun all the model experiments that are already done; first state the one concrete problem you'll advance this session, then complete and verify it using the existing implementation, and update the shared dev log.

## What syncs and what stays on the original computer

Git syncs source, templates, public research, project docs, tests, exported cases, and media. `dist/` is committed only with explicitly reviewed install artifacts; the compressed full delivery bundle stays as a local archive. See the install guide for build steps.

The experiment repos, run branches, and caches in `.rsi/` are not uploaded. Another computer can read the exported results in `examples/` but can't directly restore this computer's run branches. To continue the same interrupted run, resume it on the original computer per the takeover notes; on a new computer, usually start a new experiment from a template, with a new run ID that keeps its relationship to the old experiment.

Accounts, keys, browser logins, personal CLI config, virtual environments, machine paths, and raw sessions each stay on their own machine. This repo only holds an independent personal project and public or approved material; check staged files and history before uploading, and don't use shared rule files to sync unrelated work context.

## What to prioritize next

First build the main showcase around code fixing, the writing handbook, and video editing, replacing generic inputs with the user's own public or approved material and showing the first draft, a representative intermediate version, the final version, and the reasons for keeping it. The existing main loop is sufficient for the first version; prioritize problems hit in real use.

D07 gets a full multi-round run once a usable personal generation service is available; D15 gets numerical checks, real timing, and small-module comparisons once a personal GPU is available. No renting hardware or automatic payments for now. Official public release, deployment, or merging into the main branch happens only with explicit authorization.
