---
name: rsi
description: Set up and run an RSI-Anything ratchet that keeps improving a file (code, prompt, report, post, script, config) against a frozen judge, unattended. Use when the user wants something improved over many rounds, "overnight", "until it's good", "keep iterating", "自己迭代", "反复改到更好", or mentions rsi / self-improvement loops.
---

# RSI-Anything ratchet

The `rsi` command runs the loop; your job is to help the user define it well and then let it run.
A loop is only as good as its judge, so spend most of your effort there.

## 1. Agree on the contract with the user

Ask (briefly) until these are concrete:

- **Artifact**: the exact files the loop may change. Keep it small: one module, one post, one prompt file.
- **Judge**: how a version is scored, without a human, in minutes. Either
  - a command that measures it (tests + benchmark, eval script, metric on a dataset), or
  - a rubric scored by an LLM jury, for writing and other subjective work.
- **Gates**: things that must never break (tests pass, facts match a brief, length limits, no banned claims).
- **Budget**: rounds, minutes, how many non-improving rounds before stopping.

If the user cannot say what "better" means, help them write it down before anything else.

## 2. Start from a template when one fits

```bash
rsi init            # lists templates
rsi init code-speed my-speedup
rsi init copywriting my-post
```

Otherwise create `rsi.yaml` in the project:

```yaml
name: short-name
goal: |
  Plain words: what better means and what must not change.
artifact: [path/to/file]
judge:
  type: command                 # or: rubric
  run: python3 judge/score.py   # writes {"score", "gates", "feedback"} to $RSI_RESULT
  files: [judge]                # frozen: the agent can never change these
  direction: maximize
  min_gain: 3%                  # ignore noise-sized gains
agent:
  use: auto                     # claude, codex, gemini, qwen, kimi, opencode, codebuddy, api, command
budget: {rounds: 10, minutes: 120, stagnation: 4}
```

Python judges can call `from rsi_anything import report_result` and
`report_result(score, gates={...}, feedback="...")`. For rubric judges see the
`copywriting` template: criteria with anchors, code gates, yes/no checks, a
trusted `context` file, and `models: [auto]` or explicit models such as
`[cli:codex, deepseek:deepseek-chat]`.

## 3. Make the judge hard to fool before running

- Feed it an empty or nonsense artifact: it must fail a gate or score near zero.
- Correctness before speed: compare against a frozen reference on fresh random inputs.
- Report through `$RSI_RESULT`, never by printing a score.
- Keep judge data out of the artifact paths. Put anything the agent must not see outside the repo.
- For writing: put the facts in a frozen brief and add a check that nothing outside it is claimed.

## 4. Run it

```bash
git add -A && git commit -m "rsi: contract and judge"
rsi check                     # validates the contract and scores the current version
rsi run                       # add --agent codex / --rounds 20 / --allow-commands as needed
rsi status                    # progress table
rsi report                    # writes report.md and a shareable report.html
```

Runs can take a long time; start `rsi run` in the background when your environment allows it.
Each run works on its own branch `rsi/<run-id>` and never touches the user's checkout.

## 5. Report honestly

Tell the user the baseline and best score, how many rounds were kept, what changed (from the
report), the stop reason, and anything suspicious in the kept diffs. Merging is their call:
`git merge rsi/<run-id>`.
