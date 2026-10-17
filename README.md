<div align="center">

# ♾️ RSI-Anything · Open RSI

## RSI Belongs to Everyone. AGI Belongs to Everyone.

**If you can score it, you can evolve it while you sleep.**

[**English**](./README.md) · [**简体中文**](./README_CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-f4c430.svg)](./LICENSE)
[![Agent Ready](https://img.shields.io/badge/Agent_Ready-Cursor%20%7C%20Claude%20Code%20%7C%20Codex-635bff.svg)](#quick-start)
[![Six Tracks](https://img.shields.io/badge/Tracks-6-19a974.svg)](#six-discipline-tracks)
[![Provenance](https://img.shields.io/badge/Provenance-Three--Tier-blue.svg)](./UPSTREAM_CREDITS.md)

**One `GOAL.md`. One frozen judge. One hundred generations overnight.**

</div>

Most AI work stops when you stop prompting. RSI-Anything turns it into a
measured evolution loop: define what “better” means, let your existing coding
agent try one mutation, keep only verified gains, roll back regressions, and
carry every lesson into the next round.

No new agent platform. No mystical “self-improvement” claim. Just a portable,
auditable Git ratchet for code, models, research, law, learning, and life.

## The five-step Git Ratchet

```text
 HUMAN SETS THE CONTRACT                         THE LOOP NEVER MOVES BACKWARD

 ┌──────────────────┐     ┌────────────────┐     ┌──────────────────┐
 │ 1  GOAL & BOUNDS │ ──▶ │ 2  ONE MUTATION│ ──▶ │ 3  FROZEN JUDGE │
 │ GOAL.md          │     │ mutable_paths  │     │ tests + rubric   │
 └──────────────────┘     └────────────────┘     └────────┬─────────┘
          ▲                                                │
          │                                                ▼
 ┌────────┴─────────┐                              ┌──────────────────┐
 │ 5  LEARN         │ ◀─────────────────────────── │ 4  GIT RATCHET  │
 │ lessons + skills │    KEEP: commit ✅           │ better or not?   │
 └──────────────────┘    REJECT: rollback ↩        └──────────────────┘
          │
          └──────────────────── next atomic hypothesis ──────────────▶
```

The evaluator and safety boundaries are SHA-256 frozen before the first
candidate. A higher score counts only when every hard gate still passes.

## Live Evolution Ledger

<table>
<tr>
<th>Flagship Demo 1 · Engineering</th>
<th>Flagship Demo 2 · Finance Deep Report</th>
</tr>
<tr>
<td valign="top">

```text
Round  0  42.0 pts · 220.0ms   BASELINE
Round  2  67.4 pts · 118.0ms   KEEP ✅
Round  4  81.1 pts ·  42.0ms   KEEP ✅
Round  7  99.9 pts ·   0.1ms   REVERT ↩
          empty response = reward hacking
Round  9  88.0 pts ·   7.2ms   REVERT ↩
          regression test failed
Round 12  97.8 pts ·   4.5ms   CHAMPION 🏆
```

Bad mutations, broken tests, and reward-hacking shortcuts are automatically
rolled back. Only a faster **and correct** implementation advances the ratchet.

</td>
<td valign="top">

```text
Round 0   58.0 pts   "AI fluff"
Round 1   68.5 pts   primary-source map
Round 3   82.0 pts   company comparison
Round 4   79.5 pts   REVERT ↩ stale figures
Round 6   94.5 pts   CHAMPION 🏆
```

The winner is an institutional-grade 2026 report on **Humanoid Robot
Actuators & Roller Screws**: primary evidence, company-level economics,
counter-thesis, scenario triggers, and a claim-to-source ledger.

</td>
</tr>
</table>

The ledger is the product: it shows what changed, what failed, why a candidate
was rejected, and which commit is the current champion.

<a id="quick-start"></a>
## 30-second Quick Start

Install all four skills into detected Cursor, Claude Code, and Codex agent
directories:

```bash
npx rsi-anything setup
```

Or clone the repository and use the transparent local installer:

```bash
./setup.sh
python3 rsi.py demo
```

Run the two flagship tracks:

```bash
python3 rsi.py run tracks/01-engineering --demo
python3 rsi.py run tracks/03-finance-quant-research --demo
```

Then ask your agent:

```text
/rsi Improve this endpoint for 20 rounds. Never trade correctness for speed.
/rsi-report Research a market, freeze an institutional rubric, and reach 90+.
```

Preview installation without changing your machine:

```bash
./setup.sh --dry-run
```

## Four portable agent skills

| Command | What it does |
|---|---|
| [`/rsi`](./skills/rsi-loop/SKILL.md) | Reads `GOAL.md`, freezes evaluator hashes, makes one atomic change, measures, commits wins, reverts regressions, and records `results.tsv` plus `.rsi/lessons.md`. |
| [`/rsi-rubric`](./skills/rsi-rubric/SKILL.md) | Converts a vague cross-domain goal into hard gates, an anchored 100-point rubric, and anti-gaming rules. |
| [`/rsi-kanban`](./skills/rsi-ralph-kanban/SKILL.md) | Claims tasks safely, runs each in an isolated worktree, and requires tests plus an independent diff audit. |
| [`/rsi-report`](./skills/rsi-deep-report/SKILL.md) | Runs scoping → rubric induction → targeted retrieval/adversarial audit/revision → evidence-grounded delivery. |

They are Markdown-first and inspectable. The human owns the goal and frozen
judge; the agent owns candidate generation; Git owns the memory of what won.

<a id="six-discipline-tracks"></a>
## Six Discipline Tracks

| Track | Mutable target | Frozen feedback | Example outcome |
|---|---|---|---|
| `tracks/01-engineering` | source, config, performance path | tests, types, lint, benchmark, diff audit | bugs fixed and latency reduced without regressions |
| `tracks/02-algorithms-ml` | model config, prompts, data filters | holdout accuracy/loss, compute cap, leakage checks | better models and pipelines under a fixed budget |
| `tracks/03-finance-quant-research` | factors, strategies, reports | out-of-sample tests or institutional rubric | robust strategies and evidence-rich research |
| `tracks/04-humanities-social-sci` | thesis, outline, evidence synthesis | source integrity, argument rubric, countercase | deeper, traceable scholarship |
| `tracks/05-law-medicine` | redlines, briefs, protocols, reviews | authority/PMID verification, domain checklists | adversarially reviewed decision support |
| `tracks/06-learning-life-auto` | lessons, resumes, copy, schedules | quizzes, ATS, constraints, user feedback | practical artifacts that improve against real use |

The same loop crosses disciplines because the abstraction is stable:
**mutable artifact + frozen feedback + bounded search + retained evidence**.
High-stakes medical, legal, and investment outputs remain decision support and
require qualified human review.

## What prevents fake progress?

- **Frozen judge:** evaluator, rubric, fixtures, and holdouts are hashed before
  optimization.
- **Path allowlists:** candidates can edit `mutable_paths`, never the rules of
  the game.
- **Hard gates before scores:** a fast wrong answer, fabricated citation, or
  unsafe output scores no win.
- **Independent review:** subjective work uses blind cross-model audit and
  claim-level source checks.
- **Circuit breakers:** iteration, cost, time, stagnation, and integrity limits
  stop runaway loops.
- **Full history:** regressions and rejected hypotheses remain visible in the
  ledger and lessons.

Read the practical [Anti-Reward-Hacking Guide](./docs/knowledge-base/04-anti-reward-hacking.md).

## Three-Tier Attribution Protocol

Open source compounds only when credit travels with the idea:

1. **Machine-readable provenance** — [`ATTRIBUTION.yaml`](./ATTRIBUTION.yaml)
   records upstream URL, relationship, concrete influence, affected paths, and
   license-verification status.
2. **Runtime credit** — activated methods print a compact upstream banner and
   include the same records in output metadata.
3. **Discovery leaderboard** — [`UPSTREAM_CREDITS.md`](./UPSTREAM_CREDITS.md)
   links every upstream with live, time-stamped star badges rather than
   hard-coded popularity claims.

Inspiration is not authorship; interoperability is not endorsement. Derivative
material must record its exact revision and license notices.

## RSI Knowledge Base

Start in plain language, then build a system that deserves your trust:

1. [What Is RSI?](./docs/knowledge-base/01-what-is-rsi.md) — the practical loop,
   what it can do, and what it does not prove.
2. [Three Levels of RSI](./docs/knowledge-base/02-three-levels-of-rsi.md) —
   evolve artifacts, memory, then the harness.
3. [Rubric Engineering Guide](./docs/knowledge-base/03-rubric-engineering-guide.md) —
   turn expert judgment into gates and observable score anchors.
4. [Anti-Reward-Hacking](./docs/knowledge-base/04-anti-reward-hacking.md) —
   defend the metric from the optimizer.
5. [Curated Reading Path](./docs/knowledge-base/05-curated-reading-list.md) —
   practical loops, research systems, open-ended evolution, and safety.

## The contract

```yaml
objective: "Make the target measurably better"
mutable_paths: ["target/**"]
frozen_paths: ["tests/**", "rubric.yaml"]
eval_cmd: "python eval.py --json"
limits:
  max_iterations: 20
  max_stagnant_rounds: 5
```

If the judge changes, it is a new experiment. If the hard gates fail, it is not
an improvement. If the evidence is missing, the right output is uncertainty.

---

<div align="center">

**Chat is piecework. RSI is a compounding machine.**

Built independently, with explicit credit to the open-source researchers and
builders listed in [UPSTREAM_CREDITS.md](./UPSTREAM_CREDITS.md).

</div>
