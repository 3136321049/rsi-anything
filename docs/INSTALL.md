# Installation, personal accounts and runs

[简体中文](INSTALL.zh-CN.md)

This guide covers `0.3.0.dev0`. Python 3.11 is recommended. The code declares support for Python 3.9+; video, training, GPU and each agent's CLI have their own dependencies. The package isn't published on PyPI: download it from the website, or install from a source checkout.

14 domains currently have complete multi-round runs with independent verification, including the writing guide, the contract exercise and the lesson. D07 keeps the videos it generated and a partial measured run limited by the service; D15 keeps an environment probe run without a GPU. These two resource exceptions don't count as complete measured runs. Watch the [35-second clip of real outputs](../examples/showcase-media/openrsi-demo.mp4) or check the [run status (Chinese)](DEMO-PLAN.zh-CN.md) before you pick a template to run.

## Install from the website

Install the wheel from the website into a fresh virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install https://www.riseai.top/darwin/dist/rsi_anything-0.3.0.dev0-py3-none-any.whl
rsi --version
rsi init
```

On Windows, activate with `.venv\Scripts\Activate.ps1`. Installing dependencies, running `rsi` and running the evaluator must all use the same Python.

## Install from the current source

From the root of a source checkout:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
rsi --version
rsi init
```

If you already have a working isolated environment, you can reuse it. Virtual environments are local and don't ship with the repository.

## Use a local wheel

Build from the source root:

```bash
python -m pip install build
python -m build --wheel
```

Install the file that was actually built into a separate, clean virtual environment, for example:

```bash
python -m pip install /path/to/rsi_anything-0.3.0.dev0-py3-none-any.whl
rsi --version
rsi init
```

The delivered `dist/rsi_anything-0.3.0.dev0-py3-none-any.whl` passed an offline install in a clean environment with a temporary home folder: all 18 templates match the source byte for byte, and init, fixed evaluation, a test-agent run, export, `rsi plugins`, `rsi setup --check`, a `rsi new` tests task and an offline screenshot of the drawing template all passed. See [package contents and SHA256](../release/build-validation-0.3.0.dev0.json) and the [install receipt](../release/install-receipt-0.3.0.dev0.json); the first release's receipts for `0.2.0.dev0` stay in the same folder. The install test made no model calls and doesn't count as a new real experiment. Source-level tests and `scripts/` aren't part of the command-line package in the wheel.

## Choose the agent and model explicitly

`rsi agents` lists the adapters and what it detected. There are currently ten CLI adapters. The complete runs were done mainly with a personal Codex account; the other adapters haven't each been verified. The most direct setup is to pin the agent and the requested model:

```bash
rsi run --agent codex --model gpt-6.1-sol --rounds 3
```

The model name is an example that has been used during development; if your account doesn't support it, use a model you have access to. Pin the text model judge explicitly too, for example `--jury cli:codex:gpt-6.1-sol`. You can also set `RSI_AGENT=codex` and `RSI_JURY=cli:codex:gpt-6.1-sol` before running. Don't rely on `auto` for strict reproduction.

There are two kinds of model reference: `cli:<agent>:<model>` reuses your personal CLI login, and `<provider>:<model>` goes through a personal API you've configured, for example `deepseek:deepseek-chat`. Keep API keys in environment variables only; never write them into `rsi.yaml`, the repository or reports. `src/rsi_anything/llm.py` is the source of truth for the available backends and variable names; current adapters include OpenAI, Anthropic, Gemini, OpenRouter, DeepSeek, Qwen, Kimi, GLM, Doubao, SiliconFlow, MiniMax and Ollama.

For a personal project, use personal accounts and public or permitted material, and don't inherit service settings from other work. The requested model, the model the service actually reports, usage and cost in US dollars are recorded separately. Fields the service doesn't return stay unknown: a requested model isn't confirmation from the service, and an unknown cost isn't zero.

### Codex CLI settings

Run `codex --version` first and confirm the CLI recognizes your account's models. This project configures the adapter through these environment variables:

| Variable | Purpose |
|---|---|
| `RSI_CODEX_BIN` | The Codex CLI executable you want to use; set it before starting `rsi` |
| `RSI_CODEX_ISOLATED=1` | Uses newer CLI flags such as `--ignore-user-config` and `--ignore-rules` so the run doesn't inherit your global personal config or other projects' instructions |
| `RSI_CODEX_REASONING_EFFORT=medium` | Pins the reasoning effort explicitly; the current code accepts `low`, `medium`, `high`, `xhigh` |

The isolation flags need a recent CLI. If you see `unexpected argument`, check the path of the executable that actually runs and its `exec --help`, and use a personal CLI that supports these flags. Don't treat a flag error as a model failure, and don't automatically switch to a mode with broader permissions. The Claude adapter checks the login status first and stops before sending the task if you aren't signed in.

The prompt and lesson templates also need `RSI_TASK_MODEL` pinned; the writing-guide template pins `RSI_WRITER_MODEL`. These are "the models that the method being optimized actually calls". Their role is different from the agent that edits files and the judge that scores. They can use the same account, but each is recorded separately.

## Your first complete run

From the source directory, initialize into a sibling directory so experiment files don't mix into the development repository:

```bash
rsi init code-repair ../open-rsi-demo
cd ../open-rsi-demo
rsi check
rsi run --agent codex --model gpt-6.1-sol --rounds 3
rsi status
rsi report
rsi export --to ../open-rsi-result
```

`rsi init` creates a Git repository and an initial commit in the new directory. If the directory is already inside another Git repository, commit the template files first. If the first commit fails because no Git identity is set, configure your own public identity in the demo directory, then run `git add -A` and `git commit`. Don't borrow someone else's commit identity.

`rsi check` runs the real evaluator, including any model calls, training or video generation in the template. The code-repair example only runs fixed local tests; on expensive templates, don't treat `check` as a free syntax check. `budget.rounds`, `budget.minutes` and `budget.stagnation` in the config control the loop; `agent.timeout` and `judge.timeout` limit each single execution. Total time is checked between rounds and isn't an exact cost cap.

## Optional dependencies and resources

| Template | What it needs | Current setup |
|---|---|---|
| `cpu-classifier` | scikit-learn and Matplotlib; a CPU is enough | Run `python -m pip install -r requirements.txt` in the template directory; the pinned versions match the original experiment |
| `quant-backtest` | Matplotlib, plus access to a public market-data API during init | Install `requirements.txt` the same way; if the market-data download fails, init stops and doesn't substitute synthetic data |
| `video-cut` | FFmpeg and ffprobe; an existing video or a speech-synthesis tool | On macOS, install FFmpeg with Homebrew; on Linux, use the system package manager. The default synthetic material also needs `say` or `espeak-ng` |
| `video-generation` | FFmpeg/ffprobe, a working official public Space, and a judge that can read images | Videos exist for the starting artifact and round 1. Later requests and one short-prompt diagnostic returned `error/null`, for an unknown reason. Once the service recovers or permitted resources are available, start a new experiment; there's no automatic paid fallback |
| `kernel-speed` | An authorized personal Linux NVIDIA GPU, a compatible driver, PyTorch/Triton | Run `python judge/check.py --probe` first; the template README lists the specific hardware range and versions |

Source developers can also run `python -m pip install -e '.[dev,training]'` to install the training dependencies with looser version ranges. To reproduce a saved run, use the pinned versions in the template's `requirements.txt`. Without a personal GPU, don't install the large CUDA packages or rent hardware; keep the probe record and the empty performance results. Under the current resource exception, D15 ships with an entry point for the measured run that's still to come.

For video generation, point `RSI_VIDEO_CACHE` at a persistent directory; the default is the user cache. Once a request has been accepted, its event ID and result are reused; when it's unclear whether a submission went through, automatic resubmission stops. When the service returns no artifact, quality stays unknown. For this run, the old ledger's failure codes are kept separately from the [derived verification](../examples/video-generation/runs/20261024-003656-warm-morning-product-video/outcome-audit.json), and the original score of 0 must not be read as a drop in quality. Terms of use for source footage, market data, models and other material are in [components and sources](OPEN-SOURCE.md).

## View results, resume and showcase

`rsi report` prints the report path. The run directory keeps the starting, per-round and final artifacts; `rsi export --to <dir>` copies them along with the config, ledger and patches. Media and images are saved byte for byte, and local machine paths in text are replaced. The agent's raw long logs are exported only with `--with-logs`. Linked external material isn't fully packaged automatically; before sharing, save the source material and where it came from separately, as the template describes.

After an interruption, first read `run.json`, the ledger and the last round's directory, and confirm that the same experiment isn't still running. Then run `rsi run --resume <run-id>`. A changed configuration needs a new experiment; don't use resume to mix old and new rules. The saved baseline and best output are reused, and a partially finished round is explicitly marked as interrupted. Don't manually change a failure into a success.

From the source root:

```bash
python scripts/build_showcase.py
python -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/examples/index.html`. This is a local preview and doesn't publish a website.

Without running any model, you can watch the [35-second demo](../examples/showcase-media/openrsi-demo.mp4) and check its [sources and decode evidence](../examples/showcase-media/demo-video.json). This media and `examples/` ship with the source, not in the CLI wheel; installing only the wheel doesn't give you the full set of runs.

## Common problems

| Symptom | Check first |
|---|---|
| `rsi: command not found`, or the package can't be imported | Whether the virtual environment is active; whether install and execution use the same interpreter |
| The starting state can't be evaluated | The baseline evaluation error and `out/error.json`; a missing dependency, a missing sign-in or an API failure doesn't mean the artifact is poor |
| A message says the config isn't committed or this isn't a Git project | Whether the template files, evaluator inputs and `rsi.yaml` have been committed |
| The CLI model isn't supported, or the isolation flags aren't recognized | The actual CLI path and version, and which models your personal account can use |
| `RSI_TASK_MODEL` is not set | The lesson template requires it explicitly; prompt experiments should also pin the task model |
| No video was generated, or the event stream broke off | `out/error.json`, `state.json` in the persistent cache, and the original event ID; don't resend requests at random |
| The model says it made changes, but the formal round shows none | Whether the files allowed to change actually changed; the agent may have experimented internally and then restored the original files |
| Higher score, but rejected | The required checks, the minimum improvement threshold and, for text, the result of the head-to-head comparison with the current best |
| Chart HTML shows no chart offline | The business-report Mermaid charts need internet access; the table of figures on the same page is still readable, or open the `.mmd` file |

When troubleshooting, start with the current source and the original run directory; specific tool flags in this document may change as external CLIs are updated.
