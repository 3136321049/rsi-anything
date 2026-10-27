# D03: Support prompt optimization

[简体中文](README.md)

Full three-round experiment: `runs/20261023-234624-support-intent-prompt/`.

- The starting prompt scored 89.6% on the dev set, and the three round candidates scored 89.6%, 83.3% and 89.6%. None cleared the required improvement threshold, so the starting prompt was kept.
- The starting and final prompts both scored 82.8% (24/29) on the held-out set, with no failed calls.
- Every round's prompt and mistakes, plus the starting and final held-out results, were exported. This example shows a complete iteration with rejections; the score did not improve.
- The agent explicitly requested `gpt-6.1-sol`, and the task model explicitly requested `cli:codex:gpt-5.6-sol`. The CLI gave no service-side confirmation of the actual model, so it's recorded as unknown.
- `USAGE.zh-CN.md` (Chinese) explains how call records that were copied in the historical export are deduplicated; the original records are unchanged.
- `runs/2026-10-21-codex-partial/` is an earlier partial experiment. It can't be joined with this run into a single improvement curve.

To reproduce as a new experiment:

```bash
python scripts/run_demo.py prompt-opt --model gpt-6.1-sol --task-model cli:codex:gpt-5.6-sol --rounds 3 --minutes 30 --codex-isolated
```

Your personal Codex must be signed in and support these models. For setup and replacing inputs, see the template README. Model outputs fluctuate, and each rerun creates its own new record.
