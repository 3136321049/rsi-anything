# Add your own task

[简体中文](EXTENDING.zh-CN.md)

Start from the closest template, keep the existing loop, and replace only this domain's inputs, editable artifact and evaluation. For command-based evaluation, start from `code-repair` or `cpu-classifier`; for text evaluation, start from `business-report` or `literature-review`. When a model has to actually carry out the method, look at `writing-guide` and `lesson-builder`.

13 domains currently have complete multi-round runs and independent verification. For the writing guide, the contract exercise and the lesson, you can refer directly to real artifacts and records. D07 is a partial measured run limited by the service, and D15 is waiting for a GPU; their templates or probes can't stand in for a successful run. The full list is in the [domain list (Chinese)](DEMO-PLAN.zh-CN.md).

## Define the task clearly

A minimal domain package has to answer: what material is given, what the AI changes, how the artifact is produced, how better and worse are compared, when to stop, and where results are saved. The model edits the artifact; fixed programs handle rendering, training or checking. Don't let the model write its own final score.

```yaml
name: my-writing-task
goal: Improve draft.md using the fixed material in judge/brief.md so the target reader can understand it more easily.
artifact: [draft.md]
outputs: [out]
judge:
  type: rubric
  prepare: "{python} judge/prepare.py"
  rubric: judge/rubric.yaml
  files: [judge]
  inputs: [out/article.md]
  models: [cli:codex:gpt-6.1-sol]
  pairwise: true
  timeout: 600
agent:
  use: codex
  model: gpt-6.1-sol
  timeout: 600
budget:
  rounds: 5
  minutes: 60
  stagnation: 3
```

This config needs a matching first draft, fixed material, a prepare script and a scoring rubric. Replace the model with one your account can use, and keep it fixed within a run.

| Setting | What it means |
|---|---|
| `artifact` | Relative paths that may be edited and form the candidate; must not overlap with the frozen evaluator files |
| `judge.files` | Fixed tests, material and evaluator; snapshotted from the starting commit when the run begins |
| `prepare` | A command run in the evaluation copy before scoring; it can produce a report, a video or model answers |
| `inputs` | The artifact paths the model judge sees; defaults to `artifact` when not set |
| `outputs` | Generated files or directories saved with the starting, candidate and final versions; not extra editable scope |
| `assets` | Entry point for large external material; the evaluation uses the link and doesn't automatically copy the external files into every export |
| `holdout` | An optional separate evaluation, run at the start and the end; its results are kept apart from the dev scores |

Paths can't point outside the project. The simplest layout is `judge/` for fixed material and `out/` for generated files. After init, or after changing the material, commit first, then start a new run.

## Program-based evaluation

`judge.type: command` uses `judge.run`, for example `"{python} judge/evaluate.py"`. `{python}` is replaced with the interpreter that runs `rsi`. The evaluator writes its result to the file named by `RSI_RESULT`; the project's `report_result` does this for you. Standard output logs are never treated as a score.

Here is an interface snippet; `checks` should come from fixed tests that actually ran:

```python
from rsi_anything import report_result

passed = sum(checks.values())
score = 100 * passed / len(checks)
report_result(
    score,
    gates={"executed": True},
    feedback=f"Passed {passed}/{len(checks)} tests",
    metrics={"checks": checks},
)
```

If every business check must pass, put them in `gates`. If the task is fixing things step by step, the test pass rate can be the actual score, with conditions such as a valid structure or the program having actually run as gates. When a model or service can't be called, write out the error and exit with a nonzero status; don't fake a quality score.

You can set `direction: maximize` or `minimize`, `min_delta` and `min_gain: 5%`, and use `repeats` to evaluate several times and take the median. Only improvements that exceed the required threshold are kept.

## Model evaluation and the prepare step

`rubric.yaml` spells out the task, the fixed reference material, the evaluation criteria and concrete score levels. Start with a few criteria that explain which way to improve, such as factual consistency, reasoning, and whether the reader understands. `context` can list fixed reference files; `checks` are required conditions judged by the model; `gates` provide basic rules such as length, required words and banned words.

The prepare script can write `out/gates.json` in the form `{"condition name": true}`, plus `out/notes.txt`. If these rules fail, the model judge isn't called. Once they pass, the model scores the artifact against the rubric; text tasks can then also run a head-to-head comparison of the new version against the current best, in both orders. Image and video inputs currently skip that comparison. Video is evaluated from evenly sampled frames, which doesn't represent full audiovisual quality.

When external generation or the environment fails, the prepare script should also write `out/error.json` stating `quality_result: "unknown"`, and exit with a nonzero status. The current engine records this as an evaluation failure with no quality score. Don't rewrite old records that are already saved. Instead, as [D07's derived verification](../examples/video-generation/runs/20261024-003656-warm-morning-product-video/outcome-audit.json) does, link to the original ledger's hash and explain the original failure and the valid interpretation.

Program checks and model checks each have a limited scope. A body text containing a real citation number doesn't mean that source actually supports the sentence, and a higher model score doesn't mean real business gains. Writing the current scope of the checks into the template README is enough; you don't need research-grade calibration before you can build a demo.

## Models as part of the task

Prompt optimization, the writing guide and the lesson all need "generate, then evaluate". Pin the personal model that carries out the task, and keep the inputs, model answers, call details and mistakes.

- `prompt-opt` runs classification through `RSI_TASK_MODEL`, then compares the results with fixed labels.
- `writing-guide` has `RSI_WRITER_MODEL` write articles following the guide, then passes them to the model judge.
- `lesson-builder` has `RSI_TASK_MODEL` read the lesson and answer fixed exercises, then checks the answers and their support in the lesson.

Don't pre-write a series of increasingly better candidates and present them as automatic iteration results. Tests may mock the model interface, but test outputs must stay in the test directory and can't count as real demo runs.

## Saving, resuming and acceptance

The engine saves `artifact + outputs` before the temporary evaluation copy is cleaned up. Each snapshot has a file list, byte counts and SHA256, and is labeled with its source: the formal evaluation or the agent's working directory. Rounds without formal changes may contain the agent's trial files; don't treat those as formal evaluation results.

When a task depends on expensive external work, follow `video-generation` and cache event IDs and finished videos persistently outside the project. Recover an accepted request first; don't turn a single timeout straight into a second submission. When the service's result is uncertain, stop automatic resubmission explicitly.

A new package needs at least: fixed inputs and a readable first draft, offline program tests, one real multi-round run, starting and final outputs, records of failures and rejections, an independent review, a way to swap in other material, and source notes. Anything missing for lack of resources is listed separately as a resource exception under the first-release brief and can't be described as a successful measured run.

Put the package in `src/rsi_anything/templates/<name>/` with at least `rsi.yaml`, `ABOUT.txt`, `README.md`, the first draft and `judge/`. Add `rsi_init.py` if material needs to be downloaded or data prepared; `rsi init` actually runs this script, so the README must explain the network and resource requirements.

To add a run to the showcase collection, first save the original run and its independent verification with `rsi export`, then register it in `examples/catalog.json`, and finally rerun `scripts/build_showcase.py`. To count as accepted, a run needs a normal finish, at least two valid attempts, a final artifact and a passing independent verification; video, held-out evaluation and GPU runs have additional result requirements. The internal `out` from a round with no changes doesn't serve as a formal artifact, and the quality score of a service failure stays blank. The showcase page is built from the original records and must never overwrite the ledger. If the original material and data aren't packaged with the export, provide their source, version and how to obtain them.

For promotional material, use the saved artifacts directly and list their sources. The existing [35-second showcase clip](../examples/showcase-media/openrsi-demo.mp4) and its [source record](../examples/showcase-media/demo-video.json) can serve as a reference; the showcase clip itself isn't a new optimization experiment.
