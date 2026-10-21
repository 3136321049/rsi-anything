---
name: rsi-ralph-kanban
description: Claim Kanban tasks safely, execute them in isolated Git worktrees, and require tests plus an independent diff audit.
---

# `/rsi-kanban` — Ralph-Style Kanban Ratchet

Use for a bounded queue in `.rsi/kanban.md`. Continuous execution never means
unbounded execution: obey task count, iteration, runtime, and cost limits.

## Kanban contract

Use stable task IDs and this state vocabulary:

```markdown
- [ ] TASK-001 | P1 | deps:none | Fix description | tests:pytest tests/x.py
- [~] TASK-002 | owner:worker-id | worktree:.rsi/worktrees/TASK-002 | ...
- [x] TASK-003 | commit:abc123 | gates:PASS,PASS | ...
- [!] TASK-004 | reason:circuit-breaker | ...
```

Do not claim tasks with unmet dependencies or unclear acceptance criteria.
Update state under an atomic lock such as `.rsi/locks/TASK-001.lock`; include
worker ID, PID/session, timestamp, and lease expiry. Reclaim an expired lease
only after proving its worker is gone and preserving its branch.

## Claim and isolate

1. Confirm the main checkout has no unowned changes.
2. Select the highest-priority ready task and atomically change `[ ]` to `[~]`.
3. Create a unique branch and worktree:

   ```bash
   git worktree add .rsi/worktrees/TASK-001 -b rsi/TASK-001 <base-sha>
   ```

4. Perform all candidate edits and tests inside that worktree. Never share a
   mutable build directory, virtual environment, port, database, or cache
   between workers unless explicitly concurrency-safe.
5. Read repository instructions and run the task's narrow reproduction before
   editing.

## Bounded repair loop

For each attempt, state one hypothesis, inspect current evidence, make the
smallest coherent change, and rerun the narrow check. Periodically run the full
declared suite. Do not mark complete from code inspection alone.

Stop-hook behavior: if the agent tries to finish while either gate is missing,
return the failing evidence and continue only within remaining budgets.

### Gate 1 — deterministic verification

Require the task reproduction plus the repository's declared tests, lint,
types, build, security checks, and relevant benchmark. Capture exact commands,
exit codes, and concise results. Deleted or weakened tests fail the gate unless
the task explicitly requires a reviewed test correction.

### Gate 2 — cross-model diff audit

Give an independent reviewer the task contract, base-to-candidate diff, and
Gate 1 evidence, but not the worker's self-justification. The reviewer checks:

- task is fully satisfied and scope is minimal;
- no hard-coded answers, evaluator weakening, or hidden regressions;
- error handling, compatibility, concurrency, security, and data migration;
- tests exercise the failure and would fail on the base revision.

The verdict must be `PASS` or `FAIL` with file/line evidence. `FAIL` becomes
the next bounded repair input. If a second model is unavailable, report Gate 2
as blocked; do not pretend self-review is cross-model review.

## Integrate and close

Commit the isolated branch only after both gates pass. Before integration,
verify the base has not drifted; rebase or recreate and rerun gates if it has.
Use the repository's requested integration workflow. Mark `[x]` with commit and
gate evidence only after integration succeeds. Remove the worktree and lock,
but retain logs according to policy.

## Circuit breakers

Stop and mark `[!]` when any configured limit is hit:

- maximum attempts, wall time, tokens/cost, or concurrent workers;
- repeated identical failure (default: 3);
- no progress for the configured stagnation window;
- frozen-file change, unsafe command, secret exposure, or scope escape;
- flaky verification beyond tolerance;
- merge conflict requiring a product decision;
- cross-model reviewer unavailable for a mandatory audit.

Never bypass a breaker, expand scope, force-push, delete another worker's
branch, or silently downgrade a gate. Leave the task recoverable with branch,
worktree, latest evidence, attempts, and one explicit next action.
