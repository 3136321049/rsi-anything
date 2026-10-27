# D05: Iterating on a writing guide across several briefs

[简体中文](README.md)

Main showcase experiment: `runs/20261024-001816-reusable-writing-guide/`, 5 real rounds. The dev score went 62 → 69.5 → 74.5; the last three rounds, at 72/72/69, weren't accepted.

Each round, a fixed writer model writes copy for three fictional briefs (morning coffee pickup, a bike check-up and a beginner pottery class), and the judge reads the actual drafts and gives feedback. The agent changes only the reusable guide. The starting and final guides were also used on a new reading-group brief, which scored 69 → 77.5. This new-brief case shows one transfer result; it doesn't represent general writing ability or real business impact.

- Guide: `files/writing-guide.md` in each snapshot.
- Three dev drafts: `files/out/posts.html` and the `.md` file for each product.
- New brief: `artifacts/final/holdout-artifacts/files/out/posts.html`.
- The raw model scoring details, reasons for acceptance and rejection, and call metadata are all saved with the experiment.
- `verification.json` checks file hashes, the actual generation records for each stage, and the new-brief results. The final snapshot is a copy of the best round, so its generation calls aren't counted twice.

The earlier `20261024-000057-reusable-writing-guide` had a problem parsing the quotes cited in scores, and the brief given to the judge left something out. It's kept as is and documented separately, not mixed with the fixed experiment.

To reproduce as a new experiment:

```bash
export RSI_WRITER_MODEL=cli:codex:gpt-6.1-sol
python scripts/run_demo.py writing-guide --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 5 --minutes 60 --codex-isolated
```

Use a personal account you're signed in to, and fix the model references based on what the account can use. For how to replace the briefs, see the template README.
