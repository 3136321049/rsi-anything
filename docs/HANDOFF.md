# Development Handoff

If you are switching machines, read [Cross-Machine Collaboration](COLLABORATION.md) first: the current development mainline is `rebuild`, and that doc covers the clone command, shared rules for both assistants, shared records, and the boundary for local experiments.

Start with the [Chinese README](../README.zh-CN.md), the [first-release brief](GOAL-FIRST-RELEASE.md), and the [progress table](GOAL-PROGRESS.md). The brief defines the 15 first-release domains and the API/GPU resource exception; after the first release, D16 visual (pelican drawing and landing page) was added. The progress table and the raw experiments together decide the next step. Research docs are for looking up choices and do not override the current scope.

Current results are complete: **14 domains have complete multi-round runs with independent verification (including D16, added after the first release), D07 is a partial measurement limited by the service, and D15 awaits GPU measurement.** The D05 single piece and writing guide are both accepted, as are the D11 contract and the D13 handout. Look at the [domain list](DEMO-PLAN.md) and the [35-second short of real outputs](../examples/showcase-media/openrsi-demo.mp4) first; there is no need to rerun these complete experiments.

## Restore local state

Before starting, check the current branch, uncommitted files, running experiments, and `.agents/WORKLOG.md`. Keep existing changes, do not reset the working tree, and do not switch back to an old state just because a doc mentions an old commit. The current delivery is whatever source you received; remote and PyPI state must be checked separately and cannot be assumed to be in sync.

Prefer reusing an available isolated Python environment. This round used Python 3.11 in `.venv311`; the environment directory itself is not delivered. On a new machine, create one per the [install guide](INSTALL.zh-CN.md). Before running model tasks, check the personal login, actual CLI location, explicit model, and available resources, so you don't inherit another project's configuration.

```bash
git status --short
python -m pytest -q
rsi agents
```

Tests are program regressions and do not launch full domain model experiments. Also check whether dependency-related tests were skipped; don't report only the green total.

## Where the current deliverables live

| Location | What to look at when taking over |
|---|---|
| `src/rsi_anything/templates/` | 16 task templates, inputs, first drafts, READMEs, and scoring programs |
| `examples/<template>/runs/<run-id>/` | Exported formal records; see `run.json`, `ledger.jsonl`, and `verification.json` |
| `.rsi/projects/` | Local experiment repos created by maintenance scripts; may contain unfinished tasks |
| `examples/catalog.json`, `examples/index.html` | Collection catalog and the generated local showcase; not a substitute for raw records |
| `examples/showcase-media/openrsi-demo.mp4`, `demo-video.json` | 35-second showcase edit with sources, hashes, and media verification |
| `docs/GOAL-PROGRESS.md` | Current acceptance, resource limits, and next steps |
| `docs/DEVLOG.md` | Retained engineering conclusions and key experiment records |

Source map (layers in the [architecture doc](PLAN.md#code-layers)): `domain.py` holds pure data (score results, decisions, candidates, ledger rows), `contract.py` reads config; `strategy.py` decides how each round searches, `selection.py` decides whether a candidate wins, `events.py` reports progress and writes `events.jsonl`; `engine.py` manages a run's lifecycle, `workspace.py` builds the judging copy, `agents/` adapts assistants, `llm.py` calls models, `judges/` only scores, `ledger.py` writes state, `artifacts.py` stores artifacts, and `export.py` and `report.py` handle export and display; `sdk.py` is the toolkit for scoring scripts (gates, unknown results, headless Chrome rendering), `live.py` provides `rsi watch`, `rsi run --live`, and `rsi share`; `plugins.py` is the registry of judges, assistants, and strategies (extensible via entry points from other packages), `scaffold.py` implements `rsi new`, and `onboard.py` implements `rsi setup`. Real examples for the visual templates `svg-drawing` and `landing-page` are in `examples/svg-drawing/` and `examples/landing-page/`; the website's visual lab is `web/visual.html`.

## What to do next

The official website brand is DARWIN, at [https://www.riseai.top/darwin/](https://www.riseai.top/darwin/). The standalone path under the main site's HTTPS is deployed and currently supports browsing, comparing, and downloading real experiments; the deployment check is in `release/darwin-deployment.json`.

The brand home page, three domain pages, all experiments, and usage docs are implemented in Chinese and English (English is the default, Chinese is under `/zh/`); see the [website notes](../web/README.md) and the [product plan](PRODUCT.md). Run `python scripts/build_site.py` to generate `build/site/`. Pages support real round comparison, media playback, filtering, share links, and downloads. Public docs (install, extension, sources, architecture, templates, examples, and probe notes) all have English versions, and English pages open the English version automatically. After the 2026-10-27 redesign, the full regression had 127 passed and 1 skipped for a missing optional training dependency; the check record is `release/site-validation.json`. The redesign is on `claude/darwin-redesign` and not yet deployed. Next priorities are replacing the main example assets with ones the user personally has permission to use and running a trial; the service for launching new experiments from the web is still pending.

D01–D06 and D08–D14 have complete results. Keep the existing records, independent verification, and showcase entries; do not overwrite experiments to get prettier curves. The D05 guide keeps the 74.5 version on three dev briefs, which took a new book-club brief from 69 to 77.5; D11 ends up covering 7/7 issue categories; D13 ends with all ten questions grounded and answered correctly. See each example's notes for result boundaries.

D07 keeps the initial and round-1 real generated videos; the last two rounds and one anonymous short-description diagnostic all returned `error/null`, and the specific service cause was not confirmed. The [derived verification](../examples/video-generation/runs/20261024-003656-warm-morning-product-video/outcome-audit.json) interprets the last two rounds as unknown quality; the original ledger is unmodified. It is kept as a partial measurement under the resource exception. Start a new experiment once the service recovers or a separately approved free compatible resource is available; do not auto-retry, switch accounts, or pay.

D15 is confirmed to lack a personal GPU, and under the resource exception it ships the template, probe evidence, and notes for the pending measurement. Without hardware, keep the score empty; do not rent devices or use resources from other work. Once a suitable personal device is available, follow the GPU template for numerical verification, real multi-round runs, and a small inference-module comparison.

The current wheel is `0.3.0.dev0`. It installs offline in a fresh environment (temporary home directory), and the files of all 18 templates are byte-identical to the source; init, scoring, test-agent runs, export, `rsi new`, `rsi setup --check`, and offline screenshots pass. See the [build acceptance](../release/build-validation-0.3.0.dev0.json) and [install receipt](../release/install-receipt-0.3.0.dev0.json); the receipts for the first release `0.2.0.dev0` are kept. The current priority is choosing the main showcase from code repair, the writing guide, and video cutting, and replacing its input with the user's own public or approved input; D07/D15 and similar experiments are added once personal resources are available. Releasing, pushing, merging, or buying resources follows the current authorization.

The collection page and 35-second short demo are generated, and the media and independent verification evidence are saved. The showcase page previously passed browser checks for domain switching, text diffs, schedule preview, and video loading; later browser access was denied, and the updated derived view only got generator unit tests, JavaScript syntax checks, and link checks, so you cannot claim a UI re-review was done. Do not switch browsers or ports to get around the denial.

## Continue an experiment

First check the project's `.rsi/runs/<run-id>/run.json` for status and execution phase; then check the ledger, the last round's files, and running processes. Keep saved rounds separate from interrupted ones; a report file existing does not mean the run is finished.

Regular users run `rsi run --resume <run-id>` in the Demo directory. Maintainers using `scripts/run_demo.py` should pass both the original `--project` and `--resume` when resuming, rather than creating a new experiment that overwrites results with the same name. That maintenance script creates standalone experiments under this repo's anonymous commit identity; users of other projects should prefer the general `rsi init` entry point.

New experiments explicitly pin the assistant, judge, and task model. Example source-maintenance entry point:

```bash
python scripts/run_demo.py code-repair --model gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated
```

Add `--jury` when a template has model evaluation; add `--task-model` for prompts and handouts; set `RSI_WRITER_MODEL` separately for the writing guide. These models are only examples used in this round; if your account doesn't support them, switch to available models in the new experiment.

## Verify, don't embellish, results

- Before rerunning fixed scoring, copy to a separate temporary directory and use the original frozen materials; save the verification record and do not overwrite the formal score.
- Distinguish formal judging snapshots from the assistant's internal trial output. `NO_CHANGE` or failed rounds must not be backfilled as new formal scores.
- Keep the requested model and the actually returned model separate. Unknown costs and models stay unknown; don't guess from tool names.
- List held-out evaluation separately and don't mix it with dev scores; keep the limits on repeated tuning for training and backtests.
- Older text experiments were affected by spliced-citation matching; the specific limitations are written into the business-report and literature-review examples. Original scores are kept, and the current improved checking logic is not applied retroactively to history.
- For video generation, prefer restoring cached events; never pass off screen recordings, still frames, or earlier clips as "newly generated".
- An "accepted" label on the showcase page requires an independent verification record. D07/D15 are resource exceptions and don't count toward measured passes; D07's raw 0 is a failure code, not a quality score.

## Current engineering limits

Local scoring is not a strong sandbox, and held-out files are not absolutely hidden from an assistant with access to Git history. Total duration is checked between rounds and is not a hard billing cap. Frame-sampled scoring for video generation doesn't cover full motion or audio, the student restriction in handouts is a prompt constraint, and model scores don't equal human preference or business impact.

The next round of changes should only address real blockers; the existing main loop is enough for the first version. New templates and source changes should come with docs and necessary regressions; write detailed conclusions into project files and keep user-facing replies short and clear.
