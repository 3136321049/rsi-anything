---
name: "Literature review ratchet"
track: humanities
direction: maximize
target_score: 85
max_iterations: 6
eval_cmd: "python3 eval_review.py"
mutable_paths: ["essay.md"]
frozen_paths:
  - rubric.yaml
  - eval_review.py
upstream_credits:
  - stanford-oval/storm
  - assafelovic/gpt-researcher
  - Future-House/paper-qa
---

# What good looks like

Answer one falsifiable historical or social question. Map the scholarship, keep a counterargument section, and attach `[SRC-]` tags. The rubric is frozen.
