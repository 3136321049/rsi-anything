---
name: rsi-loop
description: Run a bounded, evidence-driven Git ratchet that keeps measured improvements and rejects regressions.
---

# `/rsi` — Universal RSI Ratchet

Use this skill when the user asks to improve an artifact repeatedly against an
objective evaluator. Treat `GOAL.md` as the human-owned contract. Never invent
permission to widen its paths, edit its evaluator, or relax its gates.

## Preconditions

1. Work in a Git repository with a clean or intentionally documented baseline.
2. Read `GOAL.md` completely. It must define:
   - `objective`
   - `mutable_paths`: the only files candidates may change
   - `frozen_paths`: evaluator, tests, fixtures, rubric, and safety policy
   - `eval_cmd`: one non-interactive command
   - optimization direction or score parser
   - stopping limits: iterations, cost/time, and stagnation
3. If any field is missing or contradictory, stop and ask the user to freeze
   the contract. Do not infer destructive commands.
4. Create `.rsi/` if needed. Keep `.rsi/lessons.md`, `.rsi/results.tsv`, and a
   snapshot manifest there. Confirm these bookkeeping files are permitted.

## Freeze the judge

Before the baseline and before every candidate evaluation:

```bash
sha256sum <each frozen file, in stable sorted order> > .rsi/frozen.sha256
sha256sum --check .rsi/frozen.sha256
```

For directories, enumerate regular files in byte-sorted order. Include command
configuration and hidden fixtures. A missing, added, or changed frozen file is
a hard violation: discard the candidate, record `FROZEN_PATH_CHANGED`, and
stop if repository restoration is not unambiguous.

## Establish the champion

Run `eval_cmd` without changing anything. Record the baseline score, hard-gate
status, runtime, commit SHA, and evaluator hash in `.rsi/results.tsv`:

```text
iteration	timestamp	hypothesis	score	gates	status	commit	evaluator_sha
```

If the baseline cannot be evaluated reproducibly, stop. Never optimize a
broken or nondeterministic judge; first report the variance or failure.

## One iteration

1. Read `GOAL.md`, `.rsi/lessons.md`, and the ledger.
2. State one falsifiable hypothesis and one small atomic mutation.
3. Snapshot the current champion commit and working-tree diff.
4. Change only `mutable_paths`. Reject unrelated formatting and dependency
   churn.
5. Check the frozen manifest and changed-path allowlist before evaluation.
6. Run `eval_cmd` exactly as frozen. Capture stdout, stderr, exit code, score,
   hard gates, and runtime.
7. Accept only when all hard gates pass and the score strictly improves in the
   declared direction. Account for the declared tolerance when measurements
   are noisy.
8. On acceptance:
   - stage only the allowed mutation and RSI ledger updates;
   - commit with `rsi: <hypothesis> (<old> -> <new>)`;
   - mark the row `KEPT` and make this commit the champion.
9. On regression, tie, invalid score, timeout, or gate failure:
   - save the evidence needed for the ledger;
   - restore only this iteration's candidate changes to the known champion;
   - never erase pre-existing user work;
   - mark the row `REVERTED`.
10. Append one short, generalizable lesson for every iteration:
    `round N — hypothesis — evidence — rule for future rounds`.

Do not use a blanket destructive reset when unrelated or user-authored changes
exist. A reset is valid only inside a clean, isolated worktree whose baseline
was explicitly captured.

## Anti-gaming and stopping

- Never edit, skip, mock, weaken, or special-case the evaluator.
- Reject hard-coded fixture answers, deleted assertions, empty-result speedups,
  hidden network calls, and metric parsing changes.
- Use holdout checks when available; do not expose hidden data to the worker.
- Stop at any budget limit, safety violation, user interrupt, evaluator drift,
  or repeated nondeterminism.
- Trigger stagnation stop after the frozen number of non-improving rounds.
- Finish with champion SHA, baseline/final scores, accepted/reverted counts,
  remaining risks, and paths to `results.tsv` and `lessons.md`.

An iteration is not a win because it looks better. It is a win only when the
unchanged evaluator proves it.
