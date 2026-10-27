# D10: Organizing a literature review around one question

[简体中文](README.md)

This experiment turned two cognitive-research summaries and the UNESCO guidance into a reading-group article on how digital tools change memory for content and memory for where information is located. The final draft clearly separates experimental findings, the theoretical framework, policy requirements and the author's inferences, and proposes follow-up questions that can be tested. It doesn't treat older retrieval research as direct evidence of the effects of generative AI.

| Version | Score | Outcome |
|---|---:|---|
| Starting | 61 | Baseline |
| Round 1 | 91.5 | Kept; sets up a central question and uses a cognitive-offloading framework to connect the sources |
| Round 2 | 68.5 | Rejected; the full candidate text and the reasons are kept |
| Round 3 | 70 | Rejected; round 1 remains the final version |

[Open the full experiment report](runs/20261024-000801-cognitive-offloading-review/report.html) · [Read the final review and source map](runs/20261024-000801-cognitive-offloading-review/artifacts/final/files/out/review.html) · [Final Markdown](runs/20261024-000801-cognitive-offloading-review/artifacts/final/files/out/review.md) · [Verification record](runs/20261024-000801-cognitive-offloading-review/verification.json)

The full final text was read, and all five evidence mappings were checked independently: each one really appears in the text, its citation is in the same paragraph, and together they cover all three sources. Each of the five exported versions was rerun through the original frozen prepare script, and every generated file matched byte for byte. In a browser, the text, source types and evidence mappings are all readable.

In rounds 2 and 3, two of the judge's evidence quotes in each round failed the text match used at the time, which triggered the 3-point cap. The old rule may have wrongly rejected quotes stitched together from several sentences; the raw judge JSON wasn't kept for this run, so the exact cause can't be confirmed. The scores of these two rounds therefore can't, on their own, show that the article got worse. All formal results are kept and weren't overwritten by re-scoring.

Both the agent and the judge explicitly requested `gpt-6.1-sol` at `medium` through a personal Codex account; the actual model and cost weren't returned and stay unknown. This shows how an article is organized and rewritten from the supplied summaries. It isn't a systematic review, a real education experiment or independent expert endorsement.

To start a new experiment with your own personal Codex login, run this from the project root:

```bash
python3 scripts/run_demo.py literature-review --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

The sources are [the memory experiments by Sparrow et al.](https://pubmed.ncbi.nlm.nih.gov/21764755/), [Risko and Gilbert's review of cognitive offloading](https://pubmed.ncbi.nlm.nih.gov/27542527/) and [UNESCO's guidance on generative AI in education and research](https://www.unesco.org/en/articles/guidance-generative-ai-education-and-research?hub=387). The official indexes were checked on 2026-10-24 for this run; the summaries, sources and limits used during generation are frozen in full in the experiment record.
