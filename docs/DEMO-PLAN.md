# First-Release Demo and Current Evidence

Updated: 2026-10-24. The first release offers 15 domains and 16 templates; the copywriting domain demonstrates both single-piece rewriting and a reusable writing guide. This document is the entry point to the cases; live acceptance and next steps follow the [progress table](GOAL-PROGRESS.md), and full scope and resource exceptions follow the [brief](GOAL-FIRST-RELEASE.md).

Current status: **13 domains with complete multi-round runs, D07 partially tested but service-limited, D15 awaiting GPU testing**. D05's guide and new-brief results and the independent verification for D11 and D13 are all in. The [35-second real-artifact short](../examples/showcase-media/openrsi-demo.mp4) can be watched directly, and [media verification and sources](../examples/showcase-media/demo-video.json) lists the actual work used.

The showcase centers on the work: first the task and first draft, then the actual attempts, why each was kept or rejected, and the final artifact. Scores explain selections; a single-case score is not presented as general capability. Real iteration can stall or fail; not every round has to go up.

## Domain entries

| ID | Template | Status and current result | Entry |
|---|---|---|---|
| D01 | `code-speed` | Accepted; historical three rounds 1→4.45→17.83→27.45x, source versions rebuilt and re-verified | [Historical record](../examples/code-speed/runs/2026-10-21-codex-3-rounds/NOTES.md) |
| D02 | `code-repair` | Accepted; three rounds, fixed tests 6/15→15/15 | [Full case](../examples/code-repair/README.md) |
| D03 | `prompt-opt` | Accepted; no improvement in any of three rounds, original prompt kept (dev 89.6%, held-out 82.8%) | [Full case and historical partial experiments](../examples/prompt-opt/README.md) |
| D04 | `cpu-classifier` | Accepted; fixed validation set 46.889%→99.333%, no official change in the last two rounds | [Config, confusion matrix and error cases](../examples/cpu-classifier/README.md) |
| D05 | `copywriting`, `writing-guide` | Accepted; single piece five rounds 16.5→96; guide five rounds kept at 74.5, new brief 69→77.5 | [Single-piece raw record](../examples/copywriting/runs/2026-10-21-codex-5-rounds/NOTES.md) · [Guide and new brief](../examples/writing-guide/README.md) |
| D06 | `video-cut` | Accepted; real voiceover four rounds, rough cut, candidates, final video and subtitles all saved | [Full case](../examples/video-cut/README.md) |
| D07 | `video-generation` | Partially tested, service-limited; initial 60.5 and round 1 61 have videos, last two rounds quality unknown | [Successful videos, failures and derived audit](../examples/video-generation/README.md) |
| D08 | `business-report` | Accepted; three rounds, final kept draft scored 74, numbers and charts checked | [Full case](../examples/business-report/README.md) |
| D09 | `quant-backtest` | Accepted; three rounds, return 27.722%→91.124%, drawdown 13.437%→28.0442%, buy-and-hold baseline kept | [Full case and data conditions](../examples/quant-backtest/README.md) |
| D10 | `literature-review` | Accepted; three rounds, review 61→91.5, source mapping re-verified | [Full case](../examples/literature-review/README.md) |
| D11 | `contract-review` | Accepted; three rounds, final kept draft scored 91.5, correctly located 7/7 issue types | [Contract discussion draft and independent verification](../examples/contract-review/README.md) |
| D12 | `medical-explainer` | Accepted; three rounds, explainer 58.5→80, fixed sources and usage boundaries kept | [Full case](../examples/medical-explainer/README.md) |
| D13 | `lesson-builder` | Accepted; three rounds from 2/10 to 10/10 grounded and correct, raw answers independently replayed | [Lesson, answers and verification](../examples/lesson-builder/README.md) |
| D14 | `weekly-planner` | Accepted; three rounds 38.08→100, final fourteen activities without conflicts | [Full case](../examples/weekly-planner/README.md) |
| D15 | `kernel-speed` | Awaiting GPU testing, resource exception; template and environment probe verified, performance results empty | [Template and pending entry](../src/rsi_anything/templates/kernel-speed/README.md) |

The raw `run.json`, ledger, candidate work and independent verification records together determine acceptance status. D07 and D15 are listed separately as resource exceptions and do not count toward the complete multi-round total; D07's raw 0 scores are the old service-failure encoding, the derived view keeps quality unknown, and they are not used to draw a quality-decline curve.

## Showcase structure

From the source root, run `python scripts/build_showcase.py`, then start a local HTTP server and open `examples/index.html`. The collection page offers selection of domain, run, left/right versions and file, with text diffs, charts and video playback. Before sharing publicly, check material terms, especially the non-commercial terms of quant market data and derived analysis.

The main showcase prefers clips and articles that general readers can compare directly. Engineering repair, code speed-up and CPU classification provide program metrics; the prompt case with no improvement shows that the system also rejects candidates. Model score curves must be shown together with the work and cannot stand alone as business impact.

## Current delivery and next entries

1. Official results and verification for the 13 complete domains are saved, including D05's single piece and writing guide, the D11 contract and the D13 lesson.
2. The case collection and the 35-second showcase cut have been generated. The page had functional checks in a desktop browser; later changes after access became restricted get only local generator, syntax and link checks, and earlier screenshots are kept.
3. Delivery uses the verified local wheel and the full case bundle; the 16 templates and the clean install path have been checked, and install, extending, sources and handoff docs are synced. Next, build the main showcase from personal input; release happens only with explicit authorization.
4. Once the D07 service recovers or another approved free resource is available, and once D15 has a suitable personal GPU, open new test records without overwriting the current resource exceptions or buying resources. Deployment, posting and official release happen only with explicit authorization.

Advanced search, strong sandboxing and research-grade judge calibration remain future directions and are not prerequisites for delivering the existing standard cases.
