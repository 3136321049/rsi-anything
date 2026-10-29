# DARWIN · Open RSI

**Give AI a goal. Keep only what gets better.**

[Website](https://www.riseai.top/darwin/) · [简体中文](README.zh-CN.md) · [All experiments](https://www.riseai.top/darwin/cases/) · [Get started](https://www.riseai.top/darwin/start/)

DARWIN is an evolution lab by RiseAI, built on the Open RSI toolkit (`rsi-anything`). A coding agent edits a real artifact — code, a prompt, a model configuration, an article, a video cut — one round at a time. A fixed evaluator checks every attempt: tests, a metric, or a model jury. Better versions become Git commits; rejected and failed attempts are saved next to them. You can inspect the starting point, every attempt, the final artifact and the reason behind each decision.

The current development version is `0.2.0.dev0`: **15 domains, 16 templates, 13 domains with complete multi-round runs** and independent verification. Two domains are resource exceptions and are not counted as complete: video generation is partially measured because the public generation service stopped responding, and GPU kernels have only a template and an environment probe because no personal GPU is available.

## A few real runs

| Run | What happened | Evidence |
|---|---|---|
| Fuzzy search speedup | Three kept rounds: 1× → 4.45× → 17.83× → 27.45×, with every result checked before timing | [Code lab](https://www.riseai.top/darwin/labs/code/) |
| Python expense repair | Fixed tests went from 6/15 to 9/15, 12/15 and 15/15 | [Code and tests](examples/code-repair/README.en.md) |
| CPU digit classifier | Validation accuracy rose from 46.889% to 99.333%; the next two rounds produced no formal change | [Model lab](https://www.riseai.top/darwin/labs/experiments/) |
| Speech → short video | Kept 75.5 from 18.5. A later 77-point cut lost both head-to-head comparisons and was rejected | [Video lab](https://www.riseai.top/darwin/labs/video/) |
| Customer-support prompt | Three candidates failed to improve; the original prompt stayed (89.6% dev, 82.8% held out) | [Prompts and mistakes](examples/prompt-opt/README.en.md) |
| Synthetic contract | Kept a 91.5-point draft covering 7/7 issue categories; weaker candidates stay visible | [Drafts and review](examples/contract-review/README.en.md) |

These results belong to their tasks and evaluation settings. Repeated tuning on a fixed validation set isn't independent evidence of generalization, and a model score isn't expert approval. Plateaus, rejections and failures stay in the record.

## Quick start

Requires Python 3.11 (3.9+ is declared), Git, and a coding agent you're signed in to. Install the package from the website into a fresh virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install https://www.riseai.top/darwin/dist/rsi_anything-0.2.0.dev0-py3-none-any.whl
rsi agents
rsi init code-repair my-first-run
cd my-first-run
rsi check
rsi run --agent codex --model YOUR_MODEL --rounds 3
rsi report
rsi export --to ../my-first-result
```

From a source checkout, use `python -m pip install -e '.[dev]'` instead. The package is not published on PyPI.

`rsi check` runs the real evaluator; templates with model judges or video generation make real calls. Code repair only runs local tests, which makes it a good first task. `rsi init` creates a Git repository for the task; configure a Git identity if the first commit fails. CLI versions, optional dependencies and API setup are covered in the [install guide](docs/INSTALL.md).

Watch a run as it evolves with `rsi run --live` (or `rsi watch` from another terminal): a local page shows the score chart and every version next to the best at the time. `rsi share --to run.html` saves the same view as one self-contained file with images embedded and local paths removed.

## Templates

Run `rsi init` to list templates. Each one ships with inputs, a starting artifact, an evaluator, output paths, and notes on replacing the inputs. English guides sit next to the Chinese ones as `src/rsi_anything/templates/<name>/README.en.md`.

| Domain | Template | What changes each round |
|---|---|---|
| D01 Code performance | `code-speed` | Fuzzy-search implementation |
| D02 Code repair | `code-repair` | A small expense program |
| D03 Prompt optimization | `prompt-opt` | Eight-class support prompt |
| D04 Model training | `cpu-classifier` | CPU classifier and preprocessing settings |
| D05 Writing | `copywriting`, `writing-guide` | An article, or a reusable guide followed by a fixed writer model |
| D06 Video editing | `video-cut` | Selected speech segments and their order |
| D07 Video generation | `video-generation` | Prompt, negative prompt and seed |
| D08 Business analysis | `business-report` | Report and chart selection |
| D09 Quantitative research | `quant-backtest` | Strategy parameters on fixed historical data |
| D10 Literature review | `literature-review` | Argument structure and source mapping |
| D11 Contract exercise | `contract-review` | Issues and suggested wording for a synthetic contract |
| D12 Health education | `medical-explainer` | Public explanation of supplied WHO material |
| D13 Learning materials | `lesson-builder` | Lesson and worked examples, checked through a student model |
| D14 Planning | `weekly-planner` | A weekly schedule |
| D15 GPU kernels | `kernel-speed` | Softmax implementation and launch parameters |
| Visual (new) | `svg-drawing`, `landing-page` | An SVG drawing, or a one-page website, judged from screenshots by an image-capable jury |

The two visual templates are new in the source tree and not yet in the downloadable package; see the [pelican](examples/svg-drawing/README.en.md) and [landing page](examples/landing-page/README.en.md) runs. A template isn't a finished experiment. D01–D06 and D08–D14 have verified multi-round runs; D07 and D15 are the resource exceptions described above. Empty GPU results and failed generation requests are never simulated or counted as complete.

## How a run works

`rsi.yaml` defines the goal, the files the agent may change, the frozen evaluator inputs, the agent and the budget. Each round starts from the best retained commit. Only changes inside the artifact paths become a candidate, and evaluation runs in a fresh copy with the original frozen evaluator files.

Required checks come first, then the improvement threshold. Text tasks can also compare candidate and current best in both orders. Accepted changes become commits on a dedicated `rsi/<run-id>` branch; rejected and failed attempts keep their records. `rsi run --resume <run-id>` continues a compatible interrupted run; changing the configuration starts a new experiment.

This improves task artifacts and reusable instructions. It doesn't train the agent's weights or demonstrate general recursive self-improvement. Evaluator commands run on your machine, and separate workspaces are not a strong security sandbox — only run templates you understand.

## Models and resources

- Agent: `rsi run --agent codex --model <model>`. Adapters also exist for Claude Code, Cursor, Gemini, Qwen Code, Kimi, OpenCode, Copilot, CodeBuddy and Qoder; the complete runs here used Codex, and not every adapter is tested end to end.
- Judge: `--jury cli:codex:<model>`, or a supported API reference such as `deepseek:deepseek-chat`.
- Task model: `RSI_TASK_MODEL` for prompt optimization and lesson exercises; writer model: `RSI_WRITER_MODEL` for writing guides.

The requested model, the model the service reports, usage and cost are recorded separately; missing values stay unknown. CPU training and backtesting use their template `requirements.txt`. Video tasks need FFmpeg and ffprobe. GPU kernels need the hardware described in their template; CPU or MPS measurements don't substitute for GPU results.

## The website

The DARWIN site replays saved runs in English and Chinese and never calls a model. Build it locally from a source checkout:

```bash
python scripts/build_site.py
python -m http.server 8765 --bind 127.0.0.1 --directory build/site
```

Open `http://127.0.0.1:8765/` (Chinese at `/zh/`). See [web/README.md](web/README.md) for the structure and translation workflow. `python scripts/build_showcase.py` still generates the older single-file browser at `examples/index.html` for local use.

## Sources and limits

The loop is this project's own implementation on Git, Python and PyYAML, with optional scikit-learn, Matplotlib, FFmpeg, PyTorch/Triton and a public video-generation service. GEPA, OpenEvolve, RD-Agent, FunClip and video-use are research references, not installed engines.

Project code is MIT licensed. Third-party software, model weights, data, videos and documents keep their own terms — notably, the default backtest market data and its derived outputs are non-commercial. Contract and health examples are synthetic exercises or supplied public material, not legal or medical advice; backtests describe historical simulations, not future returns. Details are in [components and sources](docs/OPEN-SOURCE.md).

Contributors: start with [AGENTS.md](AGENTS.md) (Chinese), the [architecture](docs/PLAN.md) and the guide to [building templates](docs/EXTENDING.md).
