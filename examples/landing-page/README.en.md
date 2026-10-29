# Evolving a landing page: Night Voyage Study Room

[简体中文](README.md)

Each round a personal Codex account on this machine (`gpt-6.1-sol`, user config isolated) changes only `index.html`, a one-page English landing page for the Night Membership of the fictional "Night Voyage Study Room". The evaluator first checks that every key fact is present and that the page carries all its own resources. Then headless Chrome takes two screenshots: desktop (1280px) and phone (laid out at 390px). A personal Claude account (`cli:claude`) scores them against the product brief. A higher-scoring candidate must also beat the best version at the time side by side, viewed in both orders, and ties are settled by the same comparison (`ties: compare`).

Open [evolution.html](evolution.html) to see every round's screenshots and decisions. Serve it over HTTP first, for example by running `python -m http.server` in `examples/`.

## The run: 25 → 74.5

`runs/20261029-212726-night-study-landing-page/`, 13.8 minutes, 3 of 6 rounds kept.

| Round | Result | Score | What changed |
|---|---|---|---|
| Start | Baseline | 25 | A list of facts in browser default styles |
| r1 | Kept | 70 | A night-themed first screen tying together the audience, the ¥129 trial and how to claim it; head-to-head 2/2 |
| r2 | Kept | 72.5 | A complete claim section at the bottom: offer, spot limit and steps; head-to-head 2/2 |
| r3 | Rejected | 70 | Night-time safety and transport info as a prominent block |
| r4 | Rejected | 72 | A tighter first screen, fixing an italic headline that overhung |
| r5 | Kept | 74.5 | The keyword on the first screen becomes a working "copy NIGHT" button, and both claim actions match; head-to-head 2/2 |
| r6 | Rejected | 72.5 | A sticky price and claim button at the bottom of the phone screen |

The criteria start between 1 and 4. After r1 all five sit at 7; r2 raises first impression to 8, and r5 raises visual craft to 8. Round 4's 72 is only 0.5 below the best at the time, within the judge's wobble, but "the score must go up" still rejects it.

## Two excluded runs

Two earlier landing page runs went 23 → 72.5 and then stalled, but the phone screenshot was rendered incorrectly at the time. The zoomed page was only painted down to about 1092px, leaving the rest blank. The judge therefore flagged "broken layout" three times, and those three rejections weren't the pages' fault. The defect was fixed in the scoring toolkit and a regression test was added. Those two runs were judged on faulty screenshots and can't be reproduced byte for byte after the fix, so they aren't included as cases; the dev log records why. The pelican case renders at desktop width and isn't affected.

## Verification and limits

`verify_saved_results.py` makes no model calls. It re-renders all 7 versions with the frozen evaluator and requires byte-identical gate results, screenshots and page text. The bottom few pixel rows of a phone screenshot occasionally differ between browser launches, so it retries up to three times. It also checks the ledger: every kept version really raised the score, and the final version is the last one kept. The results are in `verification.json`. The model scores are kept as recorded, not recomputed.

The product, prices and amenities are fictional. Scores come from a single judge model, one sample at a time. They reflect this rubric only, not real conversion rates; have a person review the page before it goes live. The agent wrote its change notes in Chinese; they're kept as recorded.
