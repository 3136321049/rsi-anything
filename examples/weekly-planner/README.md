# D14: Filling out the week outside work

[简体中文](README.zh-CN.md)

The input is a fictional office worker's work hours, commute, dinners and a get-together, plus 14 sessions across 8 kinds of activity. In round 1, the real model brought task and preference coverage up to 100%. In the next two rounds it judged there was no room left to improve the score and didn't change the file. All three attempts are kept, showing what happens when changes stop once the target is reached.

| Version | Formal status | Score | Change |
|---|---|---:|---|
| Starting | BASELINE | 38.08 | Only some activities scheduled; several are outside their preferred time slots |
| Round 1 | KEEP | 100 | Adds all 14 sessions and moves them into preferred time slots; every time constraint passes |
| Round 2 | NO_CHANGE | Not rescored | File unchanged; the current best score stays at 100 |
| Round 3 | NO_CHANGE | Not rescored | File unchanged; ended on reaching the three-round budget |

[Open the three-round experiment report](runs/20261023-235500-weekly-life-planner/report.html) · [View the final seven-day schedule](runs/20261023-235500-weekly-life-planner/artifacts/final/files/out/schedule.html) · [Final editable input](runs/20261023-235500-weekly-life-planner/artifacts/final/files/schedule.json) · [Independent re-verification record](runs/20261023-235500-weekly-life-planner/verification.json)

The final schedule has 3 exercise sessions, 3 reading sessions and 2 study sessions, plus grocery shopping, meal prep, family time, sorting out bills and 2 rest periods. The time ranges of every activity and fixed item were checked independently: there are 0 conflicts, and every preference and the 240-minute daily cap on schedulable activities are met. The seven-day schedule page includes all fixed items. This result shouldn't be taken as a substitute for checking against a real personal calendar.

The agent was the Codex CLI on a personal ChatGPT account, explicitly requesting `gpt-6.1-sol` with `medium` reasoning effort and an isolated configuration. The CLI didn't return the actual model or cost, so both are kept as unknown; each round's usage is recorded in `agent-metadata.json`.

From the project root, you can start a new experiment with your own personal Codex login. To point to a specific CLI, set `RSI_CODEX_BIN` to the executable on your machine.

```bash
python3 scripts/run_demo.py weekly-planner --model gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

`--continue-after-target` turns off the early stop at the target score before the new experiment starts, keeping a fixed three-round observation window; it doesn't change the evaluation rules or scores. There's also a [complete record of a single-round run that stopped early after reaching 100](runs/20261023-235110-weekly-life-planner/report.html), saved separately and not mixed in with the three-round experiment. Every candidate came from a real call; no candidate sequence was prefilled.
