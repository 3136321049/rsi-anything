# Open RSI First Release Progress

Updated: 2026-10-24. Acceptance scope is D01–D15 of the [first-release brief](GOAL-FIRST-RELEASE.md), including the resource exception under which the user allows items lacking a personal API/GPU to remain pending real testing.

**Current result: 13 domains have passed acceptance for real multi-round runs and artifacts; D07 is partially tested, D15 is waiting on a GPU. The final wheel and clean-environment install have passed, and the local first-release candidate is accepted under the resource exception.** A complete multi-round run means the run and artifacts are complete, not that every round improved. 114 tests pass, and hashes for 598 artifact-manifest entries and 698 showcase entry points check out.

**2026-10-30 update: D16 visual was added after the first release, now 16 domains, 18 templates, 14 domains with complete multi-round runs.** Added `rsi new`, `rsi setup`, `roles:` and the plugin registry; the `0.3.0.dev0` wheel installed offline in a clean environment under a temporary home directory. Full regression: 180 passed, 1 skipped; details in the [devlog](DEVLOG.md).

## Domain acceptance table

Template names correspond to `src/rsi_anything/templates/`. The linked docs below contain the exact run directory, artifacts, fixed inputs, evaluation method and launch command; each template README explains how to replace inputs with your own.

| ID | Status | Demo / template | Results and acceptance basis | Records, artifacts and launch entry | Next step |
|---|---|---|---|---|---|
| D01 | Accepted | Fuzzy search speedup / `code-speed` | Historical 3 rounds, 1→27.45x; 5 source files restored from the original patches and pass correctness checks | [Case](../examples/code-speed/README.md) | Ready for showcase; start a new run when changing the workload |
| D02 | Accepted | Bookkeeping code repair / `code-repair` | 3 rounds 40→60→80→100; final 15/15 tests pass | [Case](../examples/code-repair/README.md) | Usable to demo category-by-category fixes |
| D03 | Accepted | Customer-service 8-way classification / `prompt-opt` | All 3 rounds rejected; dev 89.6%, held-out 82.8%, no improvement; answers and error cases kept | [Case](../examples/prompt-opt/README.md) | Start a new experiment when there is a clear change to try |
| D04 | Accepted | CPU digit classification / `cpu-classifier` | 3 rounds 46.889%→99.333%, misclassifications 239→3; last two rounds had no formal changes | [Case](../examples/cpu-classifier/README.md) | Keep the caveat about repeated tuning on a fixed validation set |
| D05 | Accepted | Copywriting and guide / `copywriting`, `writing-guide` | Single piece: historical 5 rounds; guide: formal 5 rounds 62→74.5, new brief 69→77.5; anomalous runs listed separately | [Copywriting](../examples/copywriting/README.md), [Guide](../examples/writing-guide/README.md) | Main showcase |
| D06 | Accepted | Real talking-head edit / `video-cut` | 4 rounds 18.5→75.5; source footage and 6 edited versions playable; audio track, subtitles, duration and full decode pass | [Case](../examples/video-cut/README.md) | Main video showcase; scoring emphasizes content |
| D07 | Waiting on external condition | Real video generation / `video-generation` | Initial and round 1 real generations 60.5→61; the next two rounds hit service errors, score unknown, cannot count as complete multi-round | [Case](../examples/video-generation/README.md) | Delivered under the resource exception; add more rounds once a working generation service is available; do not buy a service |
| D08 | Accepted | Fixed financial-report analysis / `business-report` | 3 rounds 53.5→74; five report versions regenerated, numbers and charts checked | [Case](../examples/business-report/README.md) | Usable to show materials-to-report |
| D09 | Accepted | Historical strategy backtest / `quant-backtest` | 3 rounds 7.567→49.058; returns and drawdown both rose; transaction costs, buy-and-hold comparison and data usage terms kept | [Case](../examples/quant-backtest/README.md) | Present only as historical simulation results |
| D10 | Accepted | Review of given materials / `literature-review` | 3 rounds 61→91.5; five text versions and source mappings re-verified | [Case](../examples/literature-review/README.md) | Usable to show changes in material organization |
| D11 | Accepted | Sample contract review / `contract-review` | 3 rounds 41→91.5, issue coverage 2/7→7/7; round 2 failed the rules for excess length, original candidate kept | [Case](../examples/contract-review/README.md) | Keep the example-use restriction |
| D12 | Accepted | WHO-based health explainer / `medical-explainer` | 3 rounds 58.5→80; five text versions, figures and sources re-verified | [Case](../examples/medical-explainer/README.md) | Keep the public-education-use restriction |
| D13 | Accepted | Percentages handout / `lesson-builder` | 3 rounds, constrained student model 2/10→10/10; raw responses saved and grading replayed offline | [Case](../examples/lesson-builder/README.md) | Do not extrapolate to real human learning outcomes |
| D14 | Accepted | One-week schedule / `weekly-planner` | Formal 3 rounds 38.08→100; fourteen activities with no conflicts, preferences met; last two rounds had no changes | [Case](../examples/weekly-planner/README.md) | Before/after schedules viewable directly |
| D16 | Accepted (added after first release) | Pelican drawing and landing page / `svg-drawing`, `landing-page` | Pelican: two runs 37→75 (three ties rejected), 75→78 after adding tie comparison; landing page 25→74.5; all versions re-render offline byte-identical | [Pelican](../examples/svg-drawing/README.md), [Landing page](../examples/landing-page/README.md) | Shown in the website's visual lab; scoring resolution still coarse |
| D15 | Waiting on external condition | Softmax and small module / `kernel-speed` | Template and no-GPU check pass; actual result is environment unavailable, score empty; no GPU experiment | [Case](../examples/kernel-speed/README.md) | User confirmed no personal GPU; delivered under the resource exception; no renting devices, no company resources |

## Shared deliverables

2026-10-25 website update: the brand homepage, three domain pages and usage guide are done; see the [website README](../web/README.md). Full regression: 119 passed, 1 skipped for a missing optional training dependency; desktop and narrow-screen acceptance in the [website record](../release/site-validation.json). Domain experiment statuses unchanged; the new web run service is still to be implemented.

| Item | Status | Acceptance and entry |
|---|---|---|
| Config and models | Accepted | Personal Codex config actually runs end to end; requested model, parameters and call method fixed. When the server returns no actual model or cost, the value is left empty; see the [install guide](INSTALL.zh-CN.md). |
| Artifacts and export | Accepted | Initial, per-round and final artifacts plus configs, patches and reports complete; binary media exported as-is; hashes of 598 artifact records match. |
| Interruption and resources | Accepted | Timeout cleanup, atomic state, reuse of completed baselines, round recovery and video event cache have regression tests; total duration is checked between rounds; unknown cost is never reported as zero. |
| Unified showcase | Accepted | The [local collection](../examples/index.html) covers 15 domains with version comparison, text diffs, video, charts and schedules; 7 showcase tests and 698 file entry-point checks pass. |
| Install and build | Accepted | First-release wheel contains 16 templates; see [build validation](../release/build-validation.json), [install receipt](../release/install-receipt.json). The current `0.3.0.dev0` contains 18 templates, with `rsi new`, `rsi setup --check` and offline screenshots additionally verified in a clean environment: [build validation](../release/build-validation-0.3.0.dev0.json), [install receipt](../release/install-receipt-0.3.0.dev0.json). |
| Docs and handoff | Accepted | Chinese and English READMEs, 16 template docs, [sources](OPEN-SOURCE.zh-CN.md), [handoff notes](HANDOFF.md) and [independent audit](RELEASE-AUDIT.md) all in place. |
| Promotional assets | Accepted | The [35-second short demo](../examples/showcase-media/openrsi-demo.mp4) is built from real saved artifacts, 1280×720, silent; source and SHA256 recorded, full decode passes. |

## Current boundaries and persistence

The development mainline is `rebuild`. Source, shared docs and exported cases are synced according to an explicit review list; another computer picks up via [cross-computer collaboration](COLLABORATION.md). New experiments run in separate directories; original ledgers, failed candidates and historical partial runs are kept; local caches, accounts and unexported run branches are not uploaded. Upload checks and review scope are in `release/github-sync-audit.json`; the most recent full regression passed 115 tests.

The full test suite passes 114 tests. Existing browser check records for the showcase and case pages are kept; a repeat browser visit to the local showcase was denied by a permission check, so the final data update only did file, logic and media checks, without bypassing the access restriction, and does not claim a new round of browser visual checks passed.

D07's free service returned an opaque error after accepting requests; limited diagnosis still failed, and it cannot be determined whether the cause is quota, GPU or the service itself. The original ledger is unchanged; the derived showcase marks rounds missing artifacts as quality unknown. D15 has no personal GPU and only delivers a runnable template, public sources, a no-device check and a rerun entry point.

All sources are limited to public materials and independent implementation. Personal model calls are isolated from user config; dependencies use an isolated Python environment. The install package contains no account config, experiment caches, internal materials or local username paths. A sensitive-text pattern scan within the current scope found no matches.
