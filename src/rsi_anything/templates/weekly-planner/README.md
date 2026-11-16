# D14: Plan the week outside work

[简体中文](README.zh-CN.md)

The input is an ordinary office worker's fixed work hours, commute, dinners and a get-together, plus 14 schedulable sessions across 8 kinds of activity. The starting draft already schedules some activities, but not enough sessions, and some times don't match preferences. The AI edits only `schedule.json`, filling in and adjusting the schedule step by step.

```bash
rsi init weekly-planner my-week
cd my-week
python judge/evaluate.py
rsi check
rsi run --agent codex --rounds 6
```

`out/schedule.html` is a seven-day schedule you can open in a browser, `out/schedule.md` is the text version, `out/schedule.json` contains the fixed items and the candidate sessions, and `out/metrics.json` records the score and specific problems. `outputs: [out]` in the configuration lets the engine save each round's outputs, so changes to the schedule can be compared.

Before scoring, the evaluator checks the format, time conflicts, waking hours, allowed days, session length, count limits and a cap of 240 minutes of activities per day. Fixed items can't move; one item may end at the same time the next one starts. The score is 70 points of weighted task coverage plus 30 points of weighted preference coverage, and each kind of activity counts only up to its required number of sessions. Scheduling too few activities leaves room to improve, while adding extra repeats can't pad the score. An empty schedule has no conflicts but scores zero.

Replacing the inputs: before starting a new experiment, edit `fixed`, `tasks`, `awake` and the other fields in `judge/requirements.json`, then commit. Each task states its `id`, name, number of sessions, minutes, weight, allowed weekdays and preferred time windows. `schedule.json` uses a `sessions` array, with items like `{"task":"exercise","day":1,"start":"07:00","end":"07:45"}`; days 1–7 mean Monday to Sunday, and sessions don't cross midnight. Reviews currently use local clock time for a single week, with no handling of dates, time zones or daylight saving time.

The data is a set of fictional everyday needs written for this project; it doesn't access any personal calendar. It uses only the Python 3.9+ standard library, with no extra dependencies or service fees. `judge/evaluate.py` uses [datetime.strptime](https://docs.python.org/3/library/datetime.html) to validate times and [html.escape](https://docs.python.org/3/library/html.html) to build the readable page; the official docs were consulted on 2026-10-23. At the current size, checking each item directly is enough, so no extra scheduling solver is used.

Baseline and evaluator tests don't mean a real model has completed multi-round planning. Model experiments should be saved separately under `examples/weekly-planner/runs/`, with complete records.
