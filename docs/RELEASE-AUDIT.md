# First-Release Completion Audit

Audit date: 2026-10-24. Scope was checked against the current [GOAL-FIRST-RELEASE](GOAL-FIRST-RELEASE.md) and [GOAL-PROGRESS](GOAL-PROGRESS.md), including the resource exception the user granted: where a personal API/GPU is unavailable, an entry point for the pending real measurement is kept instead. This document only checks files, offline programs, and existing evidence. It made no new model calls, generation requests, or browser visits, and did not commit, push, or publish anything.

**Current conclusion: under the task brief and the resource exception, the required local first-release deliverables meet acceptance criteria. 13 domains have complete multi-round runs and artifacts; D07 is partially measured and D15 awaits a personal GPU, and neither counts toward the number of complete real runs. The unified showcase, short demo, documentation, final wheel, and clean-install record have been verified, and no remaining gap blocks this local delivery.** The source archive and the all-examples bundle are outside this completion conclusion; committing, pushing, deploying, and public release are not inferred by this audit either.

## Checks actually performed

- Loaded all 16 `rsi.yaml` files with the current source; all succeeded. Every initial editable file declared by each template exists. Checked each package's default inputs, README, launch, and replacement instructions.
- Walked every artifact manifest in `examples/` and recomputed SHA256 for **598 file records**; no missing files or hash mismatches. This count includes failed and partial experiments and does not indicate the number of successful examples.
- Ran `PYTHONDONTWRITEBYTECODE=1 .venv311/bin/python -m pytest -q -p no:cacheprovider`: **114 passed in 26.50 s**. Tests use temporary directories and mocked interfaces and do not generate real Demo candidates.
- Read the data embedded in the final collection page: status is **13 complete domains, 2 resource exceptions**; independently verified that all **698 local file entries** exist. The [final showcase receipt](../release/showcase-validation.json) also records a link check of 28 Markdown files with nothing missing; the nine main documents are synced to the final status.
- Independently read the final wheel and recomputed its SHA256, which matches both the build and install receipts; the ZIP integrity check passed, and the **159 source and resource files** in the package are byte-identical to the current source, with none missing and **16 templates** included. The clean-install record confirms loading from the installed wheel without borrowing the repo `PYTHONPATH`.
- Independently verified the short demo's SHA256, source files, and full decode; the file is a **35-second, 1280×720, silent MP4**, and `ffmpeg -v error -i ... -f null -` succeeds.
- Scanned **1461 text files** in `src/`, `docs/`, `examples/`, `scripts/`, `tests/`, and the main READMEs for internal domains, local user paths, and common secret patterns; no matches. This check has a defined scope and does not prove that no sensitive information of any form exists.

## Eight capabilities of the general engine

| Capability | Conclusion | Evidence and limits |
|---|---|---|
| Task configuration | Pass | All 16 configs load; goal, editable files, frozen materials, scoring, budget, and outputs are all defined. `contract.py` checks for conflicts between editable paths and frozen scoring files. |
| Model calls | Pass, with unknown model retained | Multiple runs have the assistant's final reply, patches, usage, and real outputs; `config/execution.json` pins the requested model and parameters. When the CLI does not return the server-side model or cost, the value stays empty; the requested model is not passed off as confirmed. |
| Multi-round runs | Pass | Ledgers actually contain `KEEP`, `REVERT`, `NO_CHANGE`, and failures; D02's three commits fix issues step by step, D03 had three rounds with no gain, and the D05 guide ended normally after five rounds. This is not playback of prewritten candidates. |
| External tools | Pass | Fixed business tests, scikit-learn training, backtests, FFmpeg editing, report generation, and real public video generation all produced output; GPU is listed separately as having no device, with no fabricated execution. |
| Artifact storage | Pass | Initial, per-round, and final artifact directories and manifests are all present; all 598 file records were verified this time. Informal internal trial output from CPU classification is listed separately in the example notes. |
| Interruption handling | Pass for current implementation | `test_artifact_lifecycle.py`, `test_cli_process.py`, and the video cache tests pass; saved baselines can be reused, run phase and interrupted round are identifiable, and accepted video events are not resubmitted automatically. No claim of covering every power loss or remote state. |
| Resource control | Pass for current Demo requirements | Round count, per-step timeout, total duration, and stall conditions are explicit; raw usage is saved as far as available. Total duration is checked between rounds; unknown dollar costs are kept as unknown, with no promise of a hard cost cap. |
| Export | Pass for file and regression checks | Each export contains config, original ledger, patches, artifacts, and evaluations; images and videos are stored byte-for-byte, and text files' manifest hashes match after path handling. Large external assets must be stored separately per their source notes; no claim that a single HTML file contains all media. |

## Per-domain check

In the table below, "input/replacement" means the template's default input and README replacement instructions were checked; "artifacts/re-verification" is based on actual files and verification records, not only on example notes. Input/replacement entry points are complete for every row.

| ID | Template and default input | Real rounds and kept results | Artifacts and re-verification | Verdict |
|---|---|---|---|---|
| D01 | `code-speed`, initial search implementation and fixed checks | Historical 3 rounds, 1→4.45→17.83→27.45× | Initial, 3 candidates, and final source rebuilt from original patches; `artifact-verification.json` has independent checks; manifests match | Complete example |
| D02 | `code-repair`, synthetic bookkeeping input and fixed tests | 3 rounds, 40→60→80→100; 15/15 tests pass | Source, sample output, and per-version re-verification, `all_passed=true` | Complete example |
| D03 | `prompt-opt`, 48 dev messages, 29 held-out messages | All 3 rounds rejected; dev 89.6%, final held-out 82.8% | All prompts and real model answers saved; offline recount and hash check done; early partial runs listed separately | Complete example, no gain |
| D04 | `cpu-classifier`, fixed digits split | 3 rounds, 46.889%→99.333%; no formal change in the last two rounds | Confusion matrix, errors, predictions, and retraining re-verification present; differences in informal internal output explicitly kept | Complete example |
| D05 | `copywriting`, `writing-guide`, fictional brief and new brief | Single piece: historical 5 rounds; guide: formal 5 rounds 62→74.5, new brief 69→77.5 | Drafts, guide, intermediate versions, and held-out outputs complete; historical draft restoration and new-experiment manifests verified; anomalous first-round experiment listed separately | Complete example |
| D06 | `video-cut`, real historical speech excerpt, 48 subtitle segments, and source | 4 rounds, 18.5→75.5; later rejections kept | Original video, rough cut, per-round and final clips, SRT, and text all present; existing per-version decode/audio-track/duration checks | Complete example, scoring weighted toward content |
| D07 | `video-generation`, self-written brief and real generation config | Baseline and round 1 produced real videos, 60.5→61; rounds 2 and 3 returned `error/null` from the remote service | Both generated results and the final reused clip decode; events, requests, service errors, and derived verification complete | Resource exception: partially measured |
| D08 | `business-report`, two years of Apple public financial facts | 3 rounds, 53.5→74; last two rounds rejected | Report, charts, numbers list, and five-version regeneration verification present; old citation-matching limitation documented | Complete example |
| D09 | `quant-backtest`, 731 public BTCUSDT historical daily bars | 3 rounds, score 7.567→49.058; return and drawdown both rose | Equity/drawdown, trade table, data source, and recomputed results complete; same-period buy-and-hold comparison, costs, and non-commercial terms kept | Complete example, historical simulation |
| D10 | `literature-review`, two research abstracts and UNESCO guidance | 3 rounds, 61→91.5; last two rounds rejected | Review, source mapping, and five-version re-verification present; effect of old citation matching not hidden | Complete example |
| D11 | `contract-review`, synthetic design services contract and seven check categories | 3 rounds, 41→91.5; coverage 2/7→7/7 | Structured suggestions, HTML, and per-version regeneration verification; round 2's overlong suggestions failed the rules, with the reason clear | Complete sample example |
| D12 | `medical-explainer`, fixed WHO materials and figures | 3 rounds, 58.5→80; last two rounds rejected | Explainer text, figures table, sources, and five-version re-verification present; limited to public health education | Complete example |
| D13 | `lesson-builder`, original handout and ten fixed questions | 3 rounds, restricted model 2/10→10/10; last two rounds tied and rejected | Raw student replies, derivations, errors, and grading replay complete; answers recomputed separately; not equivalent to real teaching outcomes | Complete example |
| D14 | `weekly-planner`, synthetic fixed tasks and preferences | Formal 3 rounds 38.08→100; no change in the last two rounds | Schedule HTML, fourteen activities, and conflict/preference independently re-verified; earlier single-round record listed separately | Complete example |
| D15 | `kernel-speed`, public Softmax approach and self-written cases | No GPU experiment; real device probe returned `environment_unavailable`, score empty | Template, dependencies, public sources, and no-device evidence complete; no candidate imported, no CPU substitute timing | Resource exception: awaiting GPU measurement |

Exact directories and reproduction commands for each complete run are in `examples/<template>/README.md`. D01's historical directory is `examples/code-speed/runs/2026-10-21-codex-3-rounds/`, and the single copywriting piece is `examples/copywriting/runs/2026-10-21-codex-5-rounds/`. These directories and all manifest files were read and checked directly.

### D07 failures and resource exception

Evidence is [outcome-audit.json](../examples/video-generation/runs/20261024-003656-warm-morning-product-video/outcome-audit.json) and `verification.json` in the same directory. The 0 scores for rounds 2 and 3 in the original ledger are kept; the derived view marks them as `JUDGE_FAIL`, `quality_result=unknown`, with an empty score. The current collection page does use this derived view and does not treat the failures as a drop in artifact quality.

The original ledger's SHA256 was recomputed this time and matches `raw_ledger_sha256` in the derived verification. `successful_generated_candidates=1`, `multi_round_demo_complete=false`, `resource_exception=true`, so this cannot be called a complete multi-round video demo. The usable interface, real clips, failure notes, and resume entry point satisfy the delivery scope under the current resource exception.

### D15 empty result

The [device probe evidence](../examples/kernel-speed/probes/2026-10-24-local/verification.json) records a real exit code of 2, `gpu_measurement_performed=false`, `candidate_imported=false`, `score=null`. Lacking a personal GPU is a currently authorized resource limit; renting or borrowing other work resources is not required. Once a personal device is available, GPU multi-round runs and the module comparison will be added.

## Showcase, docs, install, and storage

| Deliverable | Current conclusion | What was checked |
|---|---|---|
| Unified collection page | Files and logic pass; no new browser QA this time | `examples/index.html` is generated; status for all 15 domains is correct, D05 includes two examples, and the 698 file entries exist; `test_showcase.py` passes with the full test suite. |
| Page visual check | Prior page QA recorded; no new visual check after the final status update | The final showcase receipt keeps the results of the earlier successful check of all 15 domain entries, text diffs, schedule, video playback, and no horizontal overflow; each example also has its own reading check. The local browser entry was blocked by policy this time; ports, browsers, or access surfaces were not changed to get around it, and file tests are not claimed as a new visual check. |
| Short demo | Passes this file and decode check | [openrsi-demo.mp4](../examples/showcase-media/openrsi-demo.mp4), 35 seconds, 1280×720; SHA256 matches `demo-video.json`, all sources exist, full decode succeeds. Explicitly a showcase edit of existing real artifacts, not a new experiment. |
| Chinese/English and handoff docs | Pass | README, install, extension, sources, architecture, dev log, Demo entry, and handoff notes are synced to the current status; new example entries are complete, and the final receipt's link check of 28 Markdown files found nothing missing. |
| Final wheel | **Pass** | The [package](../dist/rsi_anything-0.2.0.dev0-py3-none-any.whl) is 216992 bytes with 164 files in the ZIP; independently confirmed that 159 source and resource files match the current source and that all 16 templates and their materials are present. See the [build receipt](../release/build-validation.json). |
| Clean-environment install | **Pass** | The [install receipt](../release/install-receipt.json) records an offline install into a fresh Python 3.11.14 environment, with the repo `PYTHONPATH` removed and loading from `site-packages`; CLI, listing 16 templates, init, fixed tests, a single-round test agent, and a 31-file export all succeeded, with 0 network/model calls. The test agent does not count as a real model experiment. |
| Raw records and storage boundary | Kept locally; no claim of external release | Raw ledgers, failures, and historical partial runs are all present, and manifests match. Git still has local changes and new files; this audit did not commit, push, merge, or publish, and does not infer remote sync from local files. |
| Privacy and sources | Scoped check passes | This text-pattern scan found no matches; sources, non-commercial data terms, and GPU third-party notices all have entry points. No claim that the code's MIT license covers all assets. |

## Final install evidence and remaining boundaries

The final wheel's SHA256 is:

```text
6decf01ac333b45cb76a4b6636fd74e46e26863c076ce4476c27cc2a54cbd373
```

The independently computed value matches `release/build-validation.json` and `release/install-receipt.json` exactly; every command in the install receipt exited with 0. No source resources are missing from the package, and the single-round `NO_CHANGE` produced by the install test is clearly labeled as test-agent behavior and does not count as real-model evidence for the 13 domains.

At delivery, keep the framing "13 complete domains + D07 partially measured + D15 awaiting GPU", and provide entry points to the local collection, short demo, wheel, and handoff files. D07 gets complete multi-round runs once stable generation resources are available, and D15 gets real timing once a personal GPU is available. The browser visual check of the latest page status is limited by access restrictions; for now the existing successful QA plus the final file/logic checks stand, and the restriction is not bypassed to re-verify.

The source archive and the all-examples bundle have completed content checks and per-file hash verification. The full bundle includes source, docs, examples, media, the wheel, and a lightweight source package; it excludes account configs, experiment caches, Git history, and virtual environments. The external verification evidence `release/package-validation.json` and `release/SHA256SUMS` is kept with the local delivery. Unauthorized public release, deployment, or resource purchases are not part of what was completed here.
