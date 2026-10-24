# Open RSI / RSI-Anything

**Give an AI a goal, let it make real attempts, and keep the versions that improve under your evaluation.**

Open RSI is a local demo toolkit for iterative work on code, text, prompts, configurations, and media. A coding agent changes an artifact; a program or model evaluates it; the loop keeps or rejects the change and saves the work. You can inspect the starting point, every attempt, the final artifact, and the reasons behind each decision.

The current development version is `0.2.0.dev0`, with **15 domains and 16 templates**. Writing has separate single-article and reusable-guide templates. Install from the source checkout you received or a locally built wheel; this page does not claim a PyPI release or that a remote branch contains the latest local changes. Real runs require your own coding-agent login or model account.

**Current evidence: 13 domains have complete multi-round runs, saved artifacts, and independent verification.** D07 video generation has two real clips but only one successful improvement round; later service failures remain quality-unknown. D15 GPU measurements are deferred because no compatible personal GPU is available. Both resource exceptions remain visible and are excluded from the completed-run count.

[Watch the 35-second artifact demo](examples/showcase-media/openrsi-demo.mp4) · [Demo sources and media verification](examples/showcase-media/demo-video.json) · [Browse the local showcase](examples/index.html)

**Continue on another computer:** use the `rebuild` branch and read the [cross-computer collaboration guide](docs/COLLABORATION.zh-CN.md) and [developer handoff](docs/HANDOFF.zh-CN.md). Codex and Claude Code share the repository's [AGENTS.md](AGENTS.md); the current results and next steps travel with Git. Each computer configures its own accounts and runtime.

[简体中文](README.zh-CN.md) · [Installation and personal accounts](docs/INSTALL.zh-CN.md) · [Demo status](docs/DEMO-PLAN.zh-CN.md) · [Build a template](docs/EXTENDING.zh-CN.md) · [Components and sources](docs/OPEN-SOURCE.zh-CN.md)

## A few real runs

| Demo | What happened in this run | Evidence |
|---|---|---|
| Python expense repair | Three rounds took fixed tests from 6/15 to 9/15, 12/15, and 15/15 | [Code, tests, and artifacts](examples/code-repair/README.md) |
| CPU digit classification | Fixed validation accuracy rose from 46.889% to 99.333%; the next two rounds produced no formal change | [Confusion matrix and mistakes](examples/cpu-classifier/README.md) |
| Business report | Started at 53.5; kept the 74-point report. A higher-scoring candidate was rejected by the comparison | [Report, charts, and decisions](examples/business-report/README.md) |
| Customer-support prompt | Three candidates failed to improve. Kept the initial prompt: 89.6% development, 82.8% held out | [Prompts and mistakes](examples/prompt-opt/README.md) |
| Reusable writing guide | Five rounds retained 62 → 69.5 → 74.5 on three briefs; a separate new brief went from 69 to 77.5 | [Guide, generated articles, and verification](examples/writing-guide/README.md) |
| Contract exercise | Three rounds retained a 91.5-point draft covering 7/7 issue categories; failed and weaker candidates remain visible | [Synthetic contract and reviewed drafts](examples/contract-review/README.md) |
| Learning materials | Three rounds took supported answers from 2/10 to 10/10 under a fixed student-model prompt | [Lesson, answers, and limits](examples/lesson-builder/README.md) |

These are results for particular examples and evaluation settings. Repeated tuning on a fixed validation set is not independent generalization evidence, and a model score is not expert approval. Rejections, failures, and plateaus remain in the record.

## Quick start

From the source checkout, use a virtual environment. Python 3.11 is recommended; the package declares Python 3.9+.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
rsi agents
rsi init code-repair ../open-rsi-demo
cd ../open-rsi-demo
rsi check
rsi run --agent codex --model gpt-6.1-sol --rounds 3
rsi report
rsi export --to ../open-rsi-result
```

The example requires a personal Codex CLI login with access to the named model. Replace the agent and model with ones your account supports. `rsi init` creates a Git repository and an initial commit when the destination is outside another repository; configure your own public Git identity if that commit fails.

`rsi check` runs the evaluator. For templates that use models or video generation, it makes real calls. It is not a free configuration-only check. Code repair evaluates local tests and is a small first example.

For a wheel, run `python -m pip install build` followed by `python -m build --wheel`, then install the actual wheel file in a clean environment. This builds locally; it does not publish a package. Repository scripts and example media are separate from the installed CLI package.

## Templates

Run `rsi init` to list the available templates. Each package includes inputs, a starting artifact, an evaluator, output paths, and instructions for replacing the inputs.

| Domain | Template | Artifact being changed |
|---|---|---|
| D01 Code performance | [`code-speed`](src/rsi_anything/templates/code-speed/README.md) | Fuzzy-search implementation |
| D02 Code repair | [`code-repair`](src/rsi_anything/templates/code-repair/README.md) | Small expense program |
| D03 Prompt optimization | [`prompt-opt`](src/rsi_anything/templates/prompt-opt/README.md) | Eight-class support prompt |
| D04 Training | [`cpu-classifier`](src/rsi_anything/templates/cpu-classifier/README.md) | CPU classifier and preprocessing settings |
| D05 Writing | [`copywriting`](src/rsi_anything/templates/copywriting/README.md), [`writing-guide`](src/rsi_anything/templates/writing-guide/README.md) | An article, or a reusable guide followed by a fixed writer model |
| D06 Video editing | [`video-cut`](src/rsi_anything/templates/video-cut/README.md) | Selected speech segments and their order |
| D07 Video generation | [`video-generation`](src/rsi_anything/templates/video-generation/README.md) | Prompt, negative prompt, and seed |
| D08 Business analysis | [`business-report`](src/rsi_anything/templates/business-report/README.md) | Report and chart selection |
| D09 Quantitative research | [`quant-backtest`](src/rsi_anything/templates/quant-backtest/README.md) | Strategy parameters on fixed historical data |
| D10 Literature review | [`literature-review`](src/rsi_anything/templates/literature-review/README.md) | Argument structure and source mapping |
| D11 Contract exercise | [`contract-review`](src/rsi_anything/templates/contract-review/README.md) | Issues and suggested wording for a synthetic contract |
| D12 Health education | [`medical-explainer`](src/rsi_anything/templates/medical-explainer/README.md) | Public explanation of supplied WHO material |
| D13 Learning materials | [`lesson-builder`](src/rsi_anything/templates/lesson-builder/README.md) | Lesson and worked explanations, evaluated through a student model |
| D14 Planning | [`weekly-planner`](src/rsi_anything/templates/weekly-planner/README.md) | A weekly schedule |
| D15 GPU kernels | [`kernel-speed`](src/rsi_anything/templates/kernel-speed/README.md) | Softmax implementation and launch parameters |

A template is not a completed experiment. D01–D06 and D08–D14 are independently verified multi-round examples; D05 includes both article and guide runs. [D07](examples/video-generation/README.md) is partially measured with service errors, and [D15](examples/kernel-speed/probes/2026-10-24-local/README.md) has only a template and environment probe. Read the [demo notes](docs/DEMO-PLAN.zh-CN.md), [progress tracker](docs/GOAL-PROGRESS.zh-CN.md), and original records for evidence. Empty GPU results and failed generation requests are not simulated or counted as completed experiments.

## How a run works

`rsi.yaml` defines the goal, allowed files, frozen evaluator inputs, agent, and budget. Each round starts from the best retained Git commit. Only changes inside `artifact` become a candidate. Evaluation runs in a fresh copy with the original frozen evaluator files.

Required checks come first, then the improvement threshold. Text tasks may also compare the candidate and current best in both orders. Accepted changes become real commits on a dedicated `rsi/<run-id>` branch; rejected and failed attempts retain their records.

The loop saves starting, per-round, and final artifacts before temporary evaluation directories are removed. Add generated reports, charts, or media to `outputs`. Run `rsi export --to <directory>` to copy the complete evidence, and `rsi run --resume <run-id>` to continue a compatible interrupted run. Configuration changes require a new experiment.

This improves task artifacts and reusable instructions. It does not train the agent's weights or demonstrate general recursive intelligence improvement. Evaluator commands still run on your machine; separate workspaces are not a strong security sandbox.

## Models and optional resources

Use explicit model references for reproducible runs:

- Agent: `rsi run --agent codex --model <model>`.
- Judge: `--jury cli:codex:<model>`, or a supported API reference such as `deepseek:deepseek-chat`.
- Task model: `RSI_TASK_MODEL` for prompt optimization and lesson exercises.
- Writer model: `RSI_WRITER_MODEL` for reusable writing guides.

The repository has multiple CLI and API adapters; complete runs primarily use personal Codex access. Adapter availability is not a claim that every provider has been tested. Requested model, returned model identity, usage, and cost are recorded separately. Missing values remain unknown.

Recent Codex versions can use `RSI_CODEX_BIN` for the executable, `RSI_CODEX_ISOLATED=1` to avoid inherited user configuration and rules, and `RSI_CODEX_REASONING_EFFORT=medium` to fix the effort setting. Check your CLI version before using these flags; see [installation details](docs/INSTALL.zh-CN.md).

CPU training and backtesting use their template `requirements.txt` files. Video tasks require FFmpeg/ffprobe. The default video-generation adapter uses an official public Space with no paid fallback. It produced the saved baseline and first-round clips, then returned `error/null` for later requests and one bounded diagnostic; the specific remote cause is unknown. Its persistent request cache avoids resubmitting accepted work after an interrupted wait or download. GPU kernels require the hardware and versions described in their template; CPU/MPS measurements do not substitute for GPU results.

## Browse the artifacts locally

From the source repository:

```bash
python scripts/build_showcase.py
python -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/examples/index.html`. Choose a domain, run, version, and file; compare text, view charts, and play videos. The page reads `examples/catalog.json` and original run exports without changing them. Keep the surrounding export directories when sharing media; the page does not embed all videos into one file.

The [35-second silent demo](examples/showcase-media/openrsi-demo.mp4) uses already saved repair results, writing-guide scores, speech cuts, and classification mistakes. It is a presentation edit, not another optimization run. Its [receipt](examples/showcase-media/demo-video.json) records sources, SHA256, duration, dimensions, and decoding verification.

## Sources and limits

The project implements its own loop. It uses Git, Python, and PyYAML, with optional scikit-learn, Matplotlib, FFmpeg, PyTorch/Triton, and the public Lightricks generation service. GEPA, OpenEvolve, RD-Agent, FunClip, and video-use are research references, not installed optimization engines.

Project code is MIT licensed. Third-party software, model weights, data, videos, and source documents retain their own conditions. In particular, default backtesting data and derived outputs carry noncommercial and other dataset conditions; the code's MIT license does not remove them. See [component and source details](docs/OPEN-SOURCE.zh-CN.md).

Contract and health examples use synthetic exercises or supplied public material, not individual legal or medical advice. Backtests describe historical simulations, not future returns. Video-frame judging does not establish complete motion or audio quality, and a prompted student model is not a validated human learner simulation.

For development, read the [architecture](docs/PLAN.zh-CN.md), [template guide](docs/EXTENDING.zh-CN.md), and [handoff](docs/HANDOFF.zh-CN.md). The current delivery requirements and resource exceptions are in the [release task](docs/GOAL-FIRST-RELEASE.zh-CN.md).
