# Evolving a vector drawing: a pelican riding a bicycle

[简体中文](README.zh-CN.md)

The prompt borrows "a pelican riding a bicycle", which Simon Willison often uses to test how models draw SVG. Each round a personal Codex account on this machine (`gpt-6.1-sol`, user config isolated) changes only `drawing.svg`. The evaluator first checks that it's a clean vector drawing, then renders it to PNG with headless Chrome, and a personal Claude account (`cli:claude`) scores the image against the rubric. A higher-scoring candidate must also beat the best version at the time side by side, viewed in both orders. The editor and the judge come from two different vendors, so no model grades its own work.

Open [evolution.html](evolution.html) to see both runs as one timeline. Serve it over HTTP first, for example by running `python -m http.server` in `examples/`. Inside a project, `rsi watch` shows the same view live.

## Run 1: 37 → 75, then stuck on the same score

`runs/20261029-210134-pelican-on-a-bicycle/`, 8.4 minutes.

| Round | Result | Score | What changed |
|---|---|---|---|
| Start | Baseline | 37 | Two circles, a few lines and an oval body |
| r1 | Kept | 68 | Pelican features (pouch, legs, feet) and contact with the bike; head-to-head 2/2 |
| r2 | Kept | 75 | Frame, chain and drivetrain; head-to-head 2/2 |
| r3 | Rejected | 75 | Wings reach forward and grip the handlebars |
| r4 | Rejected | 75 | Legs with thickness and joints, clearer webbed feet |
| r5 | Rejected | 75 | Ground shadow and speed lines |

Rounds 3 to 5 are three visible improvements, but the judge gave identical criterion scores every time (pelican 7, bicycle 8, riding 8, craft 7), so each totalled 75. Under "the score must go up" all three were rejected, and after three rounds without improvement the run stopped on budget. The problem is the judge's resolution: one integer per criterion and a single sample can't register small gains.

## Rule change: settle ties side by side

`rsi.yaml` gained `ties: compare`: a candidate with an equal score goes to the same both-orders side-by-side comparison and is kept only if it wins the majority. A rule change means a new experiment, since a run never switches rules midway, so a second run started.

## Run 2: 75 → 78

`runs/20261029-211118-pelican-on-a-bicycle/`, 11.4 minutes. It starts from the drawing run 1 ended with, which scored 75 again when re-judged.

| Round | Result | Score | Decision | What changed |
|---|---|---|---|---|
| Start | Baseline | 75 | | The final version from run 1 |
| r1 | Kept | 75 | tie, head-to-head 2/2 | Scaled up 20% and centered |
| r2 | Kept | 78 | 75 → 78, head-to-head 2/2 | Larger three-toed webbed feet curling over the pedals |
| r3 | Rejected | 75 | lower score | Wings with joints and feather direction |
| r4 | Kept | 78 | tie, head-to-head 2/2 | A naturally drooping throat pouch with warm shading |
| r5 | Rejected | 78 | tie, head-to-head 0/2 | A fuller body outline |
| r6 | Kept | 78 | tie, head-to-head 2/2 | Chain links and detailed front and rear sprockets |

Four of six rounds were kept, and the run stopped when its round budget ran out. Round 5 shows that the tie rule isn't "equal means keep": after looking side by side, the judge picked the existing version both times.

## Verification and limits

Each run folder has a `verify_saved_results.py` that makes no model calls. It re-renders every judged version with the frozen evaluator and requires the same gate results and byte-identical screenshots. It also checks the ledger: every kept version either raised the score or won a tie comparison, and the final version is the last one kept. All 13 versions across both runs pass; the results are in `verification.json`. The model scores are kept as recorded, not recomputed.

Scores come from a single judge model, one sample at a time, with integer criteria; that coarseness caused run 1's plateau. Ties are settled by the same judge, with two votes per comparison (one model, both orders). These scores reflect this rubric only. They aren't an art review and say nothing about a model's general drawing ability. The agent wrote its change notes in Chinese; they're kept as recorded.
