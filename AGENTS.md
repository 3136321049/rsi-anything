# Open RSI Collaboration Conventions

This repository is an independent personal demo project. The current development line is `rebuild`; `main` keeps an earlier version. Before starting, check the current branch, uncommitted changes and remote state, and preserve other people's work.

## Getting Started

Read `README.zh-CN.md`, `docs/COLLABORATION.md`, `docs/HANDOFF.md` and `docs/GOAL-PROGRESS.md` in that order. For architecture see `docs/PLAN.zh-CN.md`, for engineering conclusions `docs/DEVLOG.md`, for sources `docs/OPEN-SOURCE.zh-CN.md`. If this machine has `.agents/WORKLOG.md`, you may read it as a supplement, but never require another computer to have it.

There are currently 16 domains and 18 templates. 14 domains have complete real multi-round runs (D16 visual was added after the first release); D07 is a partial real run limited by the generation service, and D15 awaits a personal GPU. A complete run does not mean every round improved. Look at `examples/` first by default; do not rerun all model tasks just to take over.

## Changes and Experiments

Change only what the current task needs and do not overwrite existing uncommitted changes. When code is involved, run the relevant tests; the full regression is `python -m pytest -q`. Templates live separately in `src/rsi_anything/templates/`, multi-round results are exported to `examples/<template>/runs/<run-id>/`, and the collection page is generated with `python scripts/build_showcase.py`.

Keep the original ledgers, rejected drafts, failures and unknown results; start a new run after changing fixed materials or evaluation rules. Media, scores and promotional copy must correspond to artifacts that were actually saved. Without a personal API or GPU, finish what can be done and record what is missing; never pay automatically or borrow resources from other work.

After completing valuable work, record the date, tools, results, verification and next steps in `docs/DEVLOG.md`; when the status changes, update the execution table and handoff notes as well. Record only project conclusions; do not copy raw chats, global rules or machine configuration.

## Commits and Privacy

The repository accepts only this project's source code, public or explicitly approved materials, synthetic inputs and verified experiment artifacts. Never upload employer work materials, internal code or documents, internal addresses, real business samples, work screenshots, account credentials, browser state or raw sessions. Non-public material must not be brought into this project by renaming, rewriting or translating it.

`.rsi/`, `.agents/`, virtual environments, account configuration and caches stay on each computer. GitHub syncs code, shared documents and exported results; login and runtime environments are prepared independently on each computer. Before committing, stage an explicit list of files, then review the staged content, binary media and commit message; do not stage whole directories.

Commit messages, code comments and documentation are written in English. Chinese is used only for the Chinese version of the website: `web/i18n/zh.json`, `records.zh.json`, the `*.zh-CN.md` twins and `README.zh-CN.md`.

All authors and committers in this repository use `3136321049 <3136321049@users.noreply.github.com>`; do not add co-author trailers with other emails. Before pushing, check whether the remote has moved ahead; never force-push, never overwrite others' commits, and never automatically merge into `main` or create a formal release.
