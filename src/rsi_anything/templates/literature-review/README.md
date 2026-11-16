# D10: Literature review from supplied sources

[简体中文](README.zh-CN.md)

This template organizes summaries of two real studies and a UNESCO guidance document into a review for a reading group, built around the question "how do digital tools change what we remember and where information is located?" The agent edits `review.md` and `evidence.json` to improve the central question, how the evidence is organized, and the account of research limits. The default starting draft was written by a person; there are no preset later candidates or scores.

## Getting started

After setting up your own coding agent or personal model account, run:

```sh
rsi init literature-review demo-literature-review
cd demo-literature-review
python3 judge/prepare.py
rsi run --rounds 6
```

The prepare script doesn't go online or call a model; the actual multi-round run uses your own account's resources. Use `rsi run --agent codex --rounds 6` to choose the agent; the judge is set in `rsi.yaml`.

## Citations and evaluation

The frozen `judge/sources.json` contains each source's title, authors, year, evidence type, summary, limits and exact link. All summaries were rewritten by the project author; they aren't quotations from the originals. The text cites them as `[S1]`, `[S2]` and `[S3]`.

The `claims` list in `evidence.json` must contain at least three different sentences quoted verbatim from the text. Each claim's `sources` lists the relevant source IDs, and the citation must be in the same paragraph as the sentence. The program checks the IDs, the quoted sentences, citation positions and coverage. The model checks whether the sources support the neighboring claims, and whether experiments are confused with reviews and policy. Older retrieval research can't be presented as direct proof of the effects of generative AI.

## Outputs and replacing the inputs

`out/review.html` and `review.md` hold the text and sources, and `source-map.json` holds the claim-by-claim evidence mapping; `evaluation.md`, `gates.json` and `notes.txt` are for the review. The HTML can be read offline. `outputs: [out]` lets the main loop save each round's outputs; the agent doesn't edit `out/` directly.

To change the topic, first update the sources and summaries in `judge/sources.json`, then update the starting draft, the evidence mapping, the goal and the scoring rubric. If the number of sources changes, update the minimum number of mappings in the prepare script to match. Commit the new inputs before starting a new run. Questions the sources can't answer should stay as research questions; don't make up literature, numbers or quotations.

## Dependencies and status

The prepare script uses only the Python standard library, and the loop uses the project's existing PyYAML and model interfaces. No literature-search service or extra optimization framework is used. Sources were checked on 2026-10-23, and runs use only the saved summaries.

A real three-round experiment is complete: the final kept score rose from 61 to 91.5, and the candidates from the last two rounds were rejected. Review versions, source mappings and independent verification records are saved in the repository under `examples/literature-review/`. The evaluation is limited to the supplied sources and this example's rules.
