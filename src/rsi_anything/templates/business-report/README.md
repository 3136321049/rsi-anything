# D08: Business analysis on fixed data

[简体中文](README.zh-CN.md)

This template uses Apple's official historical financial statements to show a report improving round by round. The agent edits `report.md` and `charts.json`, a program computes the figures and charts, and a model judge rates the conclusions, explanations and readability. The default starting draft was written by a person; there are no preset later candidates or scores.

## Getting started

After setting up your own coding agent or personal model account, run:

```sh
rsi init business-report demo-business-report
cd demo-business-report
python3 judge/prepare.py
rsi run --rounds 6
```

The prepare script doesn't go online or call a model; the actual multi-round run uses your own account's resources. Use `rsi run --agent codex --rounds 6` to choose the agent; the judge is set in `rsi.yaml`.

## Data and figures

`judge/facts.json` holds Apple's officially published full-year GAAP figures, with sources and notes on how each figure is defined. Keys such as `{{revenue_2024}}` in the text are replaced with values that include units; year-over-year changes and the services share are computed from the data. Fiscal years 2023 and 2024 can be written directly; any other number written in digits must use a data key. All key names are listed under `template_keys` in the input.

`metrics` in `charts.json` can select one to three different metrics: `revenue`, `products`, `services`, `operating_income`, `net_income`. Chart data comes from the frozen data; the agent can't fill in its own numbers.

The program checks number keys, citation IDs, key metrics and the chart selection. The model judge assesses whether claims are supported, and whether the report keeps operating income apart from net income, quarterly from full-year figures, and facts from inferences. A candidate with a higher model score must also beat the previous draft head to head before it is kept.

## Outputs and replacing the inputs

`out/report.html` and `out/report.md` are the finished report, the `chart-*.mmd` files are Mermaid charts, and `metrics.json` holds the figures used for checking; `evaluation.md`, `gates.json` and `notes.txt` are for the review. The HTML charts need an internet connection to load Mermaid 11; offline, the text and the data table on the same page are still readable. `outputs: [out]` lets the main loop save each round's outputs; the agent doesn't edit `out/` directly.

To switch to another company or year, first update the sources, data, units and notes in `judge/facts.json`, then update the two-year basis in the prepare script, the starting draft, the goal and the scoring rubric to match. Keeping the existing metric structure is the least work. Commit the new inputs, then start a new run; don't change the data within a run.

## Dependencies and status

The prepare script uses only the Python standard library, and the loop uses the project's existing PyYAML and model interfaces. No extra optimization framework or company service is used. Sources were checked on 2026-10-23. The demo uses saved historical data, not the latest financial report, and isn't investment advice.

A real three-round experiment is complete: the final kept score rose from 53.5 to 74, and the candidates from the last two rounds were rejected. Report versions, charts and the figure-check records are saved in the repository under `examples/business-report/`. Scores reflect how the report was rated on fixed data, not investment returns.
