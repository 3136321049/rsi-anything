# D08: Three rounds of rewriting a historical Apple business analysis

[简体中文](README.zh-CN.md)

This experiment uses fixed official data for Apple's fiscal 2023 and 2024, and the AI edits the report and the chart selection. The final draft links the product decline, the services growth and the diverging paths of operating income and net income into a traceable explanation. It separates numerical facts, possible causes and questions the data can't answer.

| Version | Score | Outcome |
|---|---:|---|
| Starting | 53.5 | Baseline |
| Round 1 | 74 | Kept; adds explanations of the revenue mix and the one-time income tax charge |
| Round 2 | 79 | Rejected; in the head-to-head comparison with the order swapped, the new draft won only 1 of 2 votes |
| Round 3 | 61.5 | Rejected; did not beat the currently kept draft |

[Open the full experiment report](runs/20261024-000043-apple-operating-report/report.html) · [Read the final report and charts](runs/20261024-000043-apple-operating-report/artifacts/final/files/out/report.html) · [View the final Markdown](runs/20261024-000043-apple-operating-report/artifacts/final/files/out/report.md) · [Verification record](runs/20261024-000043-apple-operating-report/verification.json)

The program checks number keys, units, citations and charts; the model rates the explanations and structure. Both the agent and the judge explicitly requested `gpt-6.1-sol` at `medium` from a personal Codex account. The CLI didn't return the actual model or the cost in US dollars, so both stay unknown. Each score is a judgment under the current evaluation settings, not endorsement by an independent financial expert.

In round 3, two of the judge's evidence quotes failed the text match used at the time, which triggered the rule that caps the affected criterion at 3. The old matching logic may have wrongly rejected quotes stitched together from several sentences. The raw scoring JSON wasn't saved for this run, so it can't be confirmed which case these two belong to, and 61.5 alone doesn't show that the text got much worse. The current template can only select up to three single-metric charts, so it can't produce the combined contribution chart the judge suggested; this limits further chart improvements.

The final draft was read, the full-year figures and the one-time tax charge were checked against the official statements, and the year-over-year changes and the product-plus-services revenue relationship were recomputed independently. The exported starting version, the three round candidates and the final version were each regenerated in a fresh temporary directory, and the outputs matched byte for byte. A browser displayed the text, the data table and all three charts. The charts need an internet connection to load Mermaid; offline, the text and the figures table are still readable.

To start a new experiment with your own personal Codex login, run this from the project root:

```bash
python3 scripts/run_demo.py business-report --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

The data comes from [Apple's official full-year financial statements](https://www.apple.com/newsroom/pdfs/fy2024-q4/FY24_Q4_Consolidated_Financial_Statements.pdf), checked on 2026-10-24 for this run. This is a business-analysis demo on fixed historical data, not the latest financial report or investment advice.
