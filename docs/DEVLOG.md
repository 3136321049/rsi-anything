# Development Log

For current usage see the [Chinese README](../README.zh-CN.md); for the handoff entry point see [HANDOFF](HANDOFF.md); for live domain status see the [progress table](GOAL-PROGRESS.md). This log keeps engineering conclusions that still matter for the current implementation and results; the raw experiment files are the basis for judging outcomes.

## 2026-11-16 · Claude Code: light and dark site themes

- The site gains a dark theme: it follows the system by default, a new sun/moon button in the header switches manually, the choice is saved in the browser (`darwin-theme`), and a small script in `<head>` restores it before the first frame to avoid flicker. The light look is unchanged.
- The implementation only swaps design variables in `site.css`: new `--on-ink`, `--ink-hover`, `--header-bg`, code-diff and syntax-highlighting variables replace the previously hard-coded white text, light-green borders, diff backgrounds and so on; banners and toasts use dark styling in both themes. Work content such as screenshots and iframes keeps a white background.
- Added the missing English translation of "Service or environment not completed…", which had been making the site build fail.
- English remains the default language (`/`); Chinese is at `/zh/`.

Verification: `tests/test_site.py` 15 tests pass; headless Chrome forced into light and dark mode to check screenshots of the home page and the code lab. The full regression shows 39 failures and 19 errors on this machine, identical before and after the change and unrelated to it (not investigated one by one). No model calls.

Deployment: updated the same day at https://www.riseai.top/darwin/ (release directory `20261116-darwin-theme-v2`; the previous version is kept for rollback). The live CSP is `script-src 'self'`, so the theme-restore script lives in `assets/theme.js`. Checks are in `release/darwin-deployment.json`.

Next: the server's root partition is almost full (about 180MB free); free up space before the next deployment.

## 2026-10-30 · Claude Code: package 0.3.0.dev0 and the Get Started page (batch 5)

- Version bumped to `0.3.0.dev0` and rebuilt with `uv build --wheel`: 207 files, 18 templates; the packaged source matches the repo byte for byte, with no cache files and no local paths. The first-release `0.2.0.dev0` package and receipts are kept as-is; the new receipts are `release/build-validation-0.3.0.dev0.json` and `release/install-receipt-0.3.0.dev0.json`.
- Clean install (fresh virtualenv, temporary home directory, offline, no model calls): command entry points and template list, `rsi plugins`, `rsi setup --check` (no coding agent in the test environment, so it reports it missing as expected), fixed scoring of the code-repair template, one round and export with the test agent, an `rsi new` tests-type task (1/2 passing scores 50), and offline screenshots for the drawing template all pass.
- Install testing found that under a temporary home directory Chrome crashed on exit after writing a screenshot (the crash reporter could not find the home directory), so the scoring toolkit wrongly concluded "cannot render". Now a screenshot is accepted whenever Chrome reports "written" and the PNG is complete (ends with IEND); a truncated image or a missing write report is still recorded as outcome unknown. All three cases are tested. `rsi setup` also treats `GIT_AUTHOR_*`/`GIT_COMMITTER_*` environment variables as a configured Git identity.
- Get Started page: after installing, run `rsi setup`; template choices now include the pelican drawing and the landing page (with a note that they need a browser and a judge that can see images, and commands carry `--jury cli:claude --live`); new section "Improve your own thing" introduces `rsi new`. Template and domain counts updated to 18 and 14. Versions and counts synced across README, install guide, architecture, sources, handoff, collaboration notes, progress table and collaboration conventions; the first-release audit, brief and first-release receipt stay unchanged.

Verification: full regression 181 passed, 1 skipped (new Get Started tests: options match the lab templates, page contains `rsi setup` and `rsi new`, links to the new package). Get Started page checked in a browser. No model calls.

Next: upload the new package when deploying the site; optionally export the `rsi new` lighthouse mini-run as a case; scoring resolution (multiple samples or half points).

## 2026-10-30 · Claude Code: onboarding commands, roles and plugins (batch 4)

- `rsi new`: asks what should get better and writes a task that runs as-is. Four kinds: `text` (a model scores the text on listed dimensions), `visual` (one SVG or HTML, screenshotted offline and scored by looking at it), `tests` (frozen tests, scored by pass ratio, reading pytest/unittest output), `number` (the last number a command prints, optionally lower-is-better). Before writing, the config is checked with the same validation as `rsi check`; it refuses if `rsi.yaml` or `judge/` already exists; existing work files are not overwritten; outside a repo it creates one and makes the first commit.
- `rsi setup`: checks Python, Git and identity, logged-in coding agents, optional browser and FFmpeg, and whether each agent's `/rsi` skill is up to date; suggests editor and judge (when Codex edits prefer Claude to judge, and vice versa) and gives `RSI_AGENT`/`RSI_JURY` settings. `--check` only reports; by default it asks before installing skills, and writes nothing when non-interactive.
- `roles:`: declares the four roles editor, judge, compare and task in one place in rsi.yaml, filling the existing settings; when both are set they must agree. New `judge.compare` (the model used for head-to-head comparison, defaults to the judge); during runs and `rsi check`, `roles.task` is passed to scoring scripts as `$RSI_TASK_MODEL` and the original value is restored afterwards; `execution.json` now records the resolved `roles`.
- Plugins: a new `plugins.py` registry looks up judge types, agents and search strategies by name; other packages provide names through `rsi_anything.judges/agents/strategies` entry points, loaded only when used, with a clear error on load failure. rsi.yaml gains `strategy:`; plugin judges receive the other keys of their config block in `spec.options`; an agent plugin can be a factory function or just a `CLISpec` describing another CLI. `rsi plugins` lists all names by source.

Real check: from a one-line goal, `rsi new` generated a "dusk lighthouse" vector-drawing task (4 dimensions); the local personal Codex (`gpt-6.1-sol`, isolated user config) edited and personal Claude scored by viewing images. 2 rounds 10 → 65 → 67.5, both kept, about 10 minutes; records left in a local temp directory, not added as a case. With a PATH exposing only Codex, Claude and git, `rsi setup --check` recommended "codex edits, claude judges". CodeBuddy and Cursor were not part of the check.

Verification: full regression 177 passed, 1 skipped. New `tests/test_scaffold.py` (all four kinds pass validation, tests kind scores 1/2 as 50, number kind reads the last number and fails the gate when the command fails, interactive Q&A, real screenshots, `setup` writes skills only after confirmation) and `tests/test_plugins.py` (registry, entry-point loading and failure, plugin judge options, plugin agents and CLISpec, choosing a strategy in rsi.yaml, role filling and conflicts, task-model env restore, execution record).

Next: rebuild the package (with the two visual templates, new commands and English docs), add visual templates and `rsi new` to the Get Started page, sync counts across docs.

## 2026-10-30 · Claude Code: site visual lab (batch 3)

- All Experiments gains D16 "Draw it better" (creative), with two sub-cases: pelican and landing page. The catalog now has 16 domains, 14 of them with full multi-round runs. Counts on the home page, collection page and All Experiments page are generated from the catalog.
- New page Lab 04 Visual Work (`labs/visual/`, English and Chinese): per-round screenshots, per-dimension score bars with a marker for the best version so far, reasoning and raw judge text, plus "play kept versions". The two pelican runs are joined into one timeline: the second run is connected only when its starting work is byte-identical to the first run's final work, and the new rule is marked at the boundary. The landing page can toggle desktop and mobile screenshots between this round and the best so far, and explains why the first two runs were excluded.
- Home page: the evolution replay gains a "Visual work" tab whose details show each round's drawing; lab cards become four (four per row on wide screens, two/one column on narrow); footer and collection-page counts synced.
- The ledger note for tie comparisons now displays in both languages: `tied at 75; won head-to-head 2/2` is shown as "tied with the current best (75), won head-to-head 2/2"; it was previously misdisplayed as "higher score but lost the comparison".
- English pages gained translations for 23 edit ideas, titles and descriptions; Chinese pages gained Chinese translations for 20 English judge comments and 2 task goals (line for line; lines truncated in the original stay truncated).

Verification: full regression 168 passed, 1 skipped; `tests/test_site.py` adds visual-lab checks (join point of the two runs, score sequence, explanation of tie losses, every frame's screenshot exists, download contains both runs). The browser checked the English and Chinese visual lab, home replay and All Experiments page at 1440px and 390px with no horizontal overflow; in headless screenshots the home animation stops at its start, so it was rechecked with reduced-motion settings. No model calls.

Next: `rsi new` / `rsi setup` to lower the barrier to entry; registry for judges, agents and strategies, plus model roles in rsi.yaml; finally rebuild the package and add the two visual templates to the Get Started page.

## 2026-10-29 · Claude Code: visual demos, live page and share page (batch 2)

- New `sdk.py` scoring toolkit: write gates and explanations, record tool or service failures as "outcome unknown", render HTML/SVG offline with local headless Chrome, extract visible page text. Chrome does not lay out at widths under 500px, so mobile width is rendered in a same-width iframe and then enlarged, confirming `innerWidth` is 390 inside the page.
- Head-to-head comparison in model judging supports images and video frames; images are prefixed by version and their order is listed in the prompt. Previously the comparison was skipped when images were present. No existing template enables both image input and comparison, so behavior is unchanged.
- New templates `svg-drawing` (a pelican riding a bicycle, vector shapes only, no text) and `landing-page` (an English landing page for the night membership of a fictional late-night study room, with key-fact and self-contained checks, desktop and mobile screenshots).
- New commands `rsi watch`, `rsi run --live` and `rsi share`: one page reads the run directory and shows the score curve live, per-round thumbnails and side-by-side comparison of candidate and best-so-far; the share page embeds images and strips local paths.

- New optional rule `ties: compare`: candidates with equal scores go through the same side-by-side head-to-head comparison and are kept only on a majority win; the default is still to reject ties. Run IDs are precise to the second, so two runs started in the same second would land in the same directory; a suffix is now added automatically. Run directories gain an `events.jsonl` export, and `execution.json` records the rsi-anything version and scoring-toolkit hash (the toolkit is not frozen with the scoring files).
- The live page and share page join runs that "continue from the previous best" (starting work byte-identical to the previous final work) into one timeline and show the rsi.yaml changes at the boundary.

Real runs: local personal Codex (`gpt-6.1-sol`, isolated user config) edited, personal Claude (`cli:claude`) scored by viewing images, cross-vendor review.
- Pelican first run 37 → 68 → 75; after that, three visibly better candidates got exactly the same per-dimension scores (7/8/8/7), were all rejected as ties at 75, and the run stopped after three rounds without improvement. The cause is that single-sample integer dimension scores are too coarse, so the tie-comparison rule was added and a second run started: 75 → 78, 4 of 6 rounds kept, of which 3 tie comparisons won 2/2 and 1 lost 0/2. 20 minutes total for both runs.
- The first two landing-page runs (23 → 72.5, then stalled) exposed a scoring-toolkit bug: when the mobile screenshot enlarged the iframe with `transform: scale`, Chrome painted only up to the unscaled height, leaving about 22% blank at the bottom, and the judge three times ruled "layout broken" on that basis. Switched to CSS `zoom` and added a pixel-level regression test (which fails with the old approach). Those two runs were based on wrong screenshots and cannot be reproduced after the fix, so they are not included as cases; the raw records stay only on the local machine. Rerun after the fix: 25 → 70 → 72.5 → 74.5, 3 of 6 rounds kept, 13.8 minutes.
- The same page scored 72.5 and 71 on two scorings, so judge noise is about 1.5 points; with a zero improvement margin, close candidates can be decided by noise.

Verification: full regression 156 passed, 1 skipped. The three selected runs were re-verified with each directory's `verify_saved_results.py`: the frozen scoring program re-rendered all 20 versions, and gates, screenshots and page text matched byte for byte (the bottom few rows of mobile screenshots occasionally differ; up to three retries), and every keep in the ledger was a real improvement or a won tie comparison. No model calls; model scores are kept as originally recorded. Case notes and share pages are in `examples/svg-drawing/` and `examples/landing-page/`.

Next: bring the visual cases into the site (new domain, English translations, home-page showcase); rebuild the package to include the new templates and English docs; trade-offs between scoring resolution (multiple samples or half points) and improvement margin.

## 2026-10-29 · Claude Code: layering the core loop (batch 1)

Incremental refactor on the `claude/arch-layers` branch, keeping rsi.yaml and saved records compatible. New `domain.py` (pure data such as score results, decisions, candidates and ledger rows; old import locations kept); `selection.py` separates "keep or not" from the judge, with `GatesThenScore` and a stackable `HeadToHead` forming the default rule, and `Ratchet` accepts a custom selection rule; `strategy.py` pulls the per-round approach out of the engine, the existing behavior becoming `Greedy`, and each round the engine goes through an `Arena` for the strategy to propose, score, judge and commit; `events.py` makes terminal progress and the new `events.jsonl` come from the same event stream. New runs' `run.json` records `schema: 1` and `strategy`.

Verification: the same scripted scenarios (keep, reject by score, gate failure, no change, agent failure) give identical terminal output and ledgers before and after the refactor; full regression 140 passed, 1 skipped for a missing optional classifier dependency. New `tests/test_architecture.py` checks that dependencies only point inward, and a temporary violating import confirms the check fails. No model calls.

Next: model roles in rsi.yaml, scoring toolkit and template manifest, registry for judges/agents/strategies, unified run-record reading, and moving the site build into the package; then the two new demos, pelican SVG and landing page.

## 2026-10-27 · Claude Code: site redesign and bilingual English/Chinese

Using `codex/neo-lab-site` (`8abdc83`, identical to production) as the baseline, the DARWIN visuals were redone on the `claude/darwin-redesign` branch and an English version added. English is the default language (`/`), Chinese is at `/zh/`; the header switches between them and keeps the current round. 12 pages in total: home, three labs, All Experiments and Get Started. The visual style now matches the RiseAI main site with a light background, black text and large headings; fluorescent green marks only kept versions, rejections use orange. The home hero is an "evolution replay" of a real run: the solid line is the current best version, dashed branches are rejected candidates. Fonts are self-hosted Latin subsets of Inter and JetBrains Mono; Chinese uses system fonts.

The old single-file collection page became an on-site "All Experiments" page with the same design, supporting side-by-side versions, text diffs, judge feedback and evidence downloads; the old URL redirects to it. UI strings live in `web/i18n/`, experiment-record translations in `records.*.json`, and the build fails when an English page is missing a translation. The site no longer copies `AGENTS.md`, `CLAUDE.md`, the handoff notes, dev log or release audits; the source repo is private, so repo links are removed and the Get Started page installs the wheel from the site. The English and Chinese READMEs became public-facing introductions, with the handoff entry at the end. Fixed horizontal overflow on the Get Started page on narrow screens.

After the owner approved the visuals and copy, English versions of the public docs were added: the four `docs/` pages on installation, extending, open-source sources and architecture (`X.md` corresponds to `X.zh-CN.md`), `README.en.md` for 16 templates, 16 cases and 2 environment probes, and `THIRD_PARTY.en.md` for the GPU template. Language links were added between English and Chinese; on English pages the doc buttons, case notes, template notes and probe links now open the English versions, and the "(Chinese)" labels were removed. Both languages of the install guide gained an "Install from the website" section and dropped descriptions that only mattered for local development. Chinese text the program must match verbatim (such as the contract template's “示例、不构成法律意见”) and task data keep the original with an English explanation.

Verification: full regression 127 passed, 1 skipped for a missing optional classifier dependency (Python 3.11 isolated environment); new site checks cover cross-language links, matching string keys, no missing translations in English data, case file entry points, public scope, an English version for every public Chinese doc, and all relative links in English docs pointing to English versions. A headless browser checked both languages on desktop and at 390px narrow width with no horizontal overflow or script errors; replay switching, round links, code diffs, matrix filters, All Experiments filters and diffs, doc previews and old-URL redirects all work. Headless Chromium does not support H.264, so actual video playback needs rechecking in a real browser. No model calls, commits or deployments this round.

After owner approval: the source includes handoff notes, dev log and research notes, which the site no longer serves; it serves only the wheel. The wheel in `dist/` is the first-release build snapshot and was not rebuilt, so templates in the package still have only Chinese notes; English notes are on the site and in the source.

Next: on the authorized server, pull `rebuild`, rebuild with the original process and update the release directory of `https://www.riseai.top/darwin/`, while removing the source package from the old release directory.

## 2026-10-25 · Codex: official DARWIN showcase entry

The site brand is DARWIN, with the tagline "An evolution lab by RiseAI."; the Chinese copy is “用真实反馈，持续改进作品。” ("Keep improving your work with real feedback."). The official entry is [DARWIN](https://www.riseai.top/darwin/), a separate path on RiseAI's existing HTTPS site. Navigation, page titles, share metadata and canonical URLs all point to this entry; the core runtime project keeps the Open RSI name.

Deployment serves only a standalone build directory and does not expose the source working directory or any endpoint for running new experiments. Public access checks confirmed that the home page, three domain pages, usage guide, scripts and styles, case collection and result downloads all return 200, and video range requests return 206. The HTTPS entries of the main site and ModelPick still work. Five site tests pass after the brand and URL changes; deployment receipts are in `release/darwin-deployment.json`.

Future site updates: rebuild, run the relevant checks, then update the standalone release directory. Personal runtime environments, backups and server configuration stay on the server; the repo does not store this machine configuration.

## 2026-10-25 · Codex: brand home page and three domain pages

Built five standalone pages in a research-lab style: home, code optimization, model experiments, video creation and usage guide. The home page offers a real-data preview, a 35-second demo, domain selection, a process explanation and FAQ; the three domains have their own layouts. The code page supports switching between speed-up and repair cases, linked rounds, and source and diff comparison; the model page supports confusion-matrix filters, prediction tables, parameters and error-case images; the video page supports switching official candidates, real playback, subtitle jumps in the final cut, and downloads. Links preserve the selected round, and docs can be read in-page.

Added `scripts/build_site.py` and `web/`. The build uses four explicit official runs and produces a standalone `build/site/` with media, subtitles, original records, template notes and full result download bundles; browsing makes no model calls. Public hosting should use only the build directory. Video posters are frames from existing final cuts, with sources and hashes in `web/assets/media-sources.json`; the original experiment files were not changed.

Added five site checks covering file entry points, official rounds, result boundaries for no-change rounds, subtitle timing and result bundles. Full regression 119 passed, 1 skipped for a missing optional classifier dependency, in 16.24 seconds. The browser confirmed code switching and diffs, model-matrix filters and no-change rounds, video playback and subtitle jumps, doc previews and copy feedback, on desktop and 390px narrow screens. Detailed acceptance is in `release/site-validation.json`.

Development is on `codex/neo-lab-site`; source, docs and pages are stored on the server. The site currently offers browsing, comparison and download of real experiments; new experiments run via the command line described in the usage guide, and a web run service will follow actual usage needs. Next priorities: update the main cases with personal public or approved material, and run real user trials.

## 2026-10-25 · Codex: project review and product page planning

Using `2f6df82` as the baseline, reviewed source, shared docs and exported results; the working tree was clean at the start and the development mainline matched the remote. The remote default ref still points to the old `main`, so public entry points should make the current version clear.

This regression: 114 passed, 1 skipped for a missing optional classifier training dependency; 598 work-manifest hashes match, all 698 showcase file entry points exist, and the wheel hash matches the original install receipt. Domain status remains 13 complete domains, D07 partially tested, D15 awaiting GPU. The browser confirmed classification error-case comparison, code repair and text diffs; not all cases, mobile or video playback were covered.

[Product direction](PRODUCT.md) defines a brand home page, selectable domain entries and pages designed per work type. The first recommended set is code optimization, model experiments and video creation, sharing existing task, round, work and evaluation records. Public browsing first offers real replays, followed by default tasks, minimal input, single-task execution on the server, status and recovery. The web run service is not yet implemented.

[Research notes](research/G-project-ui-review.md) record source boundaries and official sources. This round looked at the Periodic Labs and General Intuition home pages, and reviewed other research-lab pages, autoresearch upstream, Manus replays and Remotion video-production material. The home promo film and the official domain experiments are stored separately; the capability boundaries of code speed-up, CPU classification and GPU training stay accurate.

Site implementation and acceptance are in this file's brand home page entry. Further improvements continue on a topic branch on the authorized server, preparing personal models and domain dependencies as needed. This round only updated planning and handoff docs; no new model experiments, web code, deployments or paid resources.

## 2026-10-24 · Codex: cross-machine handoff and upload checks

The current development mainline is `rebuild`. The English and Chinese READMEs link to [Cross-machine collaboration](COLLABORATION.md), which covers recent work, next steps, cloning and installing on a new machine, serial handoff, and branch conventions for parallel development. The root `AGENTS.md` and `CLAUDE.md` share project rules, development conclusions go in this file, and personal sessions and account configuration stay on each machine.

Source, docs, all exported cases, media and the two install artifacts were checked against an explicit manifest; local experiment repos, caches, virtualenvs, private work records and full local archives are not uploaded. All candidate text was fully scanned; media sources, images, video frames and metadata were reviewed separately, and Git history was also checked for secrets. Video cache digests recomputed from public requests match; original experiments and work are not rewritten. See `release/github-sync-audit.json`.

Full regression before upload: **115 passed**. The 13 complete domains and the resource gaps of D07/D15 keep their status; next priority is replacing material with personal approved material for the main showcase. Syncing code does not transfer personal logins, nor does it restore experiment-run branches that were not uploaded from the other machine.

## 2026-10-24: multi-domain templates and delivery structure

There are now 15 domains and 16 standalone templates, covering code, training, copywriting, editing, generation, research and scheduling. 13 domains (D01–D06, D08–D14) have completed real multi-round runs, saved work and independent verification; D05 has both single-piece and guide results. D07 delivers a partial test limited by the service, and D15 has no personal GPU so real device metrics are left empty; both keep their entries as resource exceptions.

Added `outputs`: initial, official candidate and final versions are saved before the review copy is cleaned; the file manifest records byte size, SHA256, source and evaluation status. No-change or failed rounds may keep the agent's internal output, which must not be treated as an official evaluation. Exports keep binary files byte-exact; text has local paths replaced and its export hash recomputed.

Run state is persisted per stage. On resume, the saved baseline and best artifact are reused, prior elapsed time is accumulated, and unfinished rounds are clearly marked; if the run branch and ledger disagree, it stops and asks for a check first. Model call records distinguish the requested model, the model actually returned, usage and cost; fields not returned stay unknown.

`examples/catalog.json` and `scripts/build_showcase.py` provide a local case collection supporting side-by-side versions, text diffs, images and video. The showcase is generated from raw records and does not overwrite the ledger. Installation uses the current source or a local wheel; this document does not yet claim a public release.

Generated a [35-second real-artifact showcase](../examples/showcase-media/openrsi-demo.mp4), cut from saved code repairs, guide scoring, before/after voiceover clips and classification error cases; the [receipt](../examples/showcase-media/demo-video.json) records sources, 1280×720 size, hashes and decode results, and the showcase cut does not count as a new experiment. The page had domain switching, diff viewing, schedule preview and video loading checked; later updates after browser access became restricted got only static checks, and the original QA records are kept.

## 2026-10-24: archived real experiments

Code speed-up, code repair, support prompts, CPU classification, single-piece copy and writing guide, video editing, business analysis, quant, literature review, contract drills, public science explainers, lessons and scheduling all have complete multi-round runs and independent verification; specific numbers and limits are in each `examples/<template>/README.md`.

The prompt task's full three rounds brought no improvement, so the original prompt was kept; older partial experiments are stored separately and must not be stitched into one curve. CPU classification's last two rounds had no official change, and the agent's trial outputs are not backfilled as official candidates. Quant's higher returns came with larger drawdown; the same-period buy-and-hold baseline and non-commercial data conditions are kept.

Some older scores in business analysis and literature review were affected by limits in source-quote checking: when the model stitched several original sentences together, the old logic might fail to match. Multi-segment evidence checking is now supported and raw judge results are recorded; the old scores were not overwritten, and the case notes keep this limitation. The science-explainer experiment already used the current checking logic.

The writing guide ran five real rounds, with development scores kept at 62→69.5→74.5 and weaker candidates rejected in the last three rounds; the new book-club brief scored 69→77.5. The old experiment with a scoring quote-parsing anomaly is kept as-is and not mixed into the official showcase. The contract drill kept a 91.5-point draft after three rounds, correctly locating 7/7 issue types; round two was rejected by the program for overly long suggestions, and its 0 points does not mean all the legal analysis was wrong. The lesson went from 2/10 to 10/10 grounded and correct answers over three rounds, but this does not represent real human learning or generalization to new questions.

Video editing uses an excerpt of a real historical speech with a public source record, saving the rough cut, candidates and final video, subtitles, text and media verification. Content scoring does not replace a full audiovisual evaluation. Video generation got real videos for the initial version and round 1; the last two rounds returned `error/null` and produced no work, and one diagnostic with the same short description also failed, cause unknown. The successful videos were decode-verified, and requests, events, sources and a [derived outcome audit](../examples/video-generation/runs/20261024-003656-warm-morning-product-video/outcome-audit.json) are saved. The raw ledger is unchanged, quality scores for the last two rounds are left empty, and D07 remains partially tested.

## 2026-10-24: environment and external tasks

A Python 3.11 isolated environment is used for training and building; the system Python does not take these dependency changes. When dependency downloads hit network errors, check actual connectivity and public sources, and do not attribute environment failures to model performance.

Recent Codex CLI can be set via `RSI_CODEX_BIN`; `RSI_CODEX_ISOLATED=1` avoids inheriting personal global config and other projects' instructions, and `RSI_CODEX_REASONING_EFFORT` fixes the reasoning effort. Exact parameters follow the current adapter and CLI help; when an older version does not recognize a parameter, it does not automatically fall back to a higher-privilege mode.

Video generation uses Gradio's submit and event-stream interfaces; accepted requests resume waiting or downloading, and after completion the same request's output is reused; when a submission's result is uncertain it is not automatically resent. Public endpoints may rate-limit or pause, and there is no paid fallback. The lesson template uses a real student model to answer fixed exercises, saving raw replies and error cases; protocol errors are listed separately as run failures.

## 2026-10-22: background process reliability

Claude login status is checked before calls. CLI detection, model queries, agent execution, scoring and setup steps share process-launch logic; on supported systems they use process groups and clean up child processes on timeout or cancellation. Core Git calls disable hooks and file monitors, and detect repo config being modified during a run.

These measures help normal operation and troubleshooting but do not constitute a strong permission sandbox. External tools still need to use explicitly approved personal resources.

## 2026-10-21: code speed-up and single-piece copy records

Code speed-up ran three real rounds with Codex, taking the original experiment from about 1x to 4.45x, 17.83x and 27.45x, with versions saved as real Git commits. The goal allows reusing preprocessing for the same list across queries; fixed checks include cache invalidation after the list changes in place. The later rebuilt initial, candidate and final sources were checked independently; the original run timings were not overwritten by re-measurement. [Raw records](../examples/code-speed/runs/2026-10-21-codex-3-rounds/NOTES.md)

Single-piece copy ran five real rounds: the first draft scored 16.5 and the final kept version 96; a 98-point candidate was rejected for not winning the old-vs-new comparison. The original judge gave high scores early, so this experiment only shows selection and work changes under the rules of the time. Historical drafts were rebuilt from the original patches with source notes kept, and are not a new experiment under the current scoring rules. [Raw records](../examples/copywriting/runs/2026-10-21-codex-5-rounds/NOTES.md)

## Collaboration conventions

Local work, commits and remote sync are checked separately; do not infer from docs that something has been released. Keep original failure and retry records; within a run, materials and evaluation are fixed, and adjustments start a new experiment. The repo contains no secrets, private identity paths or non-public work material. Sources and redistribution terms are in [OPEN-SOURCE](OPEN-SOURCE.zh-CN.md).
