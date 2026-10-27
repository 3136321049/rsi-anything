# D02: Fix a small expense tracker

[简体中文](README.md)

The default project covers amount parsing, bill splitting and monthly summaries. The starting implementation handles common inputs, but precision, remainders, refunds and date edge cases aren't fully handled yet. Each round, the AI may change only `expense.py`; the 15 business tests and the sample input are frozen in `judge/`.

```bash
rsi init code-repair my-repair
cd my-repair
python judge/evaluate.py
rsi check
rsi run --agent codex --rounds 6
```

Running it by hand writes the current outputs to `out/report.md`, `out/tests.json`, `out/example.json` and `out/metrics.json`. The declared `outputs: [out]` lets the engine save each round's outputs during a run. `python example.py` shows the monthly totals by category and a three-way bill split on its own.

The score is tests passed divided by total tests, so partial fixes can be kept too. The tests must actually run and can't be skipped. Only a score of 100 means every fixed test passes, and even that doesn't mean every business scenario is covered. Each failure comes with the specific test and error, so the next round can fix one class of root cause.

Replacing inputs: before starting a new experiment, edit `judge/sample.json` to change the demo entries. To replace the business requirements, also update `judge/test_expense.py`, `example.py` and the goal in the configuration, commit, and then run. Keep the tests unchanged during a run.

Dependencies and sources (checked 2026-10-23): only the Python standard library, which works with the Python 3.9+ the project requires. `judge/evaluate.py` uses the [unittest test suite and result API](https://docs.python.org/3/library/unittest.html). Expected behavior for amounts and dates follows [Decimal](https://docs.python.org/3/library/decimal.html) and [datetime](https://docs.python.org/3/library/datetime.html). The template's business data are fictional entries written for this project, with no network access and no cost.

This package's baseline and evaluator tests are verified during development. Real multi-round model runs are saved separately in `examples/code-repair/runs/`; the template itself doesn't generate preset candidates.
