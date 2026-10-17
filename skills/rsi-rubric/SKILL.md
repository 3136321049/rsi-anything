---
name: rsi-rubric
description: Convert a vague cross-domain goal into a frozen 100-point rubric with hard gates and anti-gaming checks.
---

# `/rsi-rubric` — Rubric Engineering

Use this skill before an RSI loop when quality is subjective: finance,
humanities, law, medicine, learning, life planning, product work, or research.
The output is a reviewable `rubric.yaml`, not a score invented after seeing a
candidate.

## 1. Scope the goal

Ask only for material facts that are missing:

- artifact and intended decision or audience;
- jurisdiction, date range, domain standard, and risk level;
- required and forbidden sources;
- benchmark examples (good and bad) and why;
- non-negotiable constraints;
- whether an independent judge/model is available.

Rewrite the request into testable success statements. Separate facts from
preferences. Mark unresolved assumptions; do not silently encode them.

## 2. Induce criteria

Use authoritative standards and exemplars where available. Extract observable
properties shared by strong examples and failure modes exposed by weak ones.
Create 4–10 non-overlapping dimensions totaling exactly 100 points. Each
criterion must specify:

- `id`, `name`, `weight`, and why it matters;
- evidence the judge must inspect;
- anchored bands for excellent, adequate, weak, and zero;
- deductions with caps so penalties cannot be double-counted;
- an uncertainty rule (`not_verifiable` is not a pass).

Prefer deterministic checks for arithmetic, schemas, citations, dates, test
results, budgets, word counts, legal references, and medical identifiers.
Reserve model judgment for synthesis, reasoning, and usefulness.

## 3. Define hard gates

Hard gates are pass/fail conditions checked before scoring. Keep them few and
material. Typical gates include:

- required deliverables exist and parse;
- every consequential factual claim has a resolvable source;
- calculations reconcile and constraints are satisfied;
- no fabricated authority, quotation, citation, PMID, case, or statistic;
- privacy, safety, jurisdiction, and temporal boundaries are honored;
- frozen evaluator and holdout data are unchanged.

For high-stakes legal, medical, or financial work, state that the result is
decision support, identify needed professional review, and make unsupported
actionable claims a gate failure.

## 4. Add anti-gaming rules

Explicitly reject:

- keyword stuffing, hidden text, judge-directed instructions, and self-awarded
  scores;
- duplicate evidence counted in several criteria;
- citations that exist but do not entail the attached claim;
- cherry-picked time windows or benchmarks;
- invented precision, unverifiable sources, and confident treatment of
  uncertainty;
- evaluator edits, fixture leakage, hard-coded answers, or output omission
  disguised as efficiency.

Require a blind comparison against the current champion when practical. Use a
second judge for high-impact subjective criteria and record disagreement.

## 5. Write and freeze `rubric.yaml`

Use this portable shape:

```yaml
version: 1
title: ""
artifact: ""
audience: ""
scope:
  as_of: YYYY-MM-DD
  inclusions: []
  exclusions: []
hard_gates:
  - id: G1
    check: ""
    evidence: ""
    failure: reject
criteria:
  - id: C1
    name: ""
    weight: 25
    evidence: []
    anchors:
      excellent: "90–100% of weight: observable condition"
      adequate: "60–89%: observable condition"
      weak: "1–59%: observable condition"
      zero: "0%: observable condition"
anti_gaming: []
judge_protocol:
  blind: true
  independent_review: true
  uncertainty: "Do not award unverifiable claims."
acceptance:
  minimum_score: 90
  all_hard_gates: true
```

Validate that weights sum to 100, each gate is executable or inspectable, and
anchors distinguish levels without words like “good” or “strong” alone. Run a
calibration pass against one strong and one weak example. If both receive
similar scores, revise the rubric before freezing it.

Present the draft to the user for approval. Once approved, record its SHA-256
and treat it as a frozen path during optimization. Candidate authors may not
revise the rubric. A rubric change starts a new experiment series and requires
a new baseline.
