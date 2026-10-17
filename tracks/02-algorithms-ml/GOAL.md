---
name: "Hold-out label accuracy"
track: algorithms-ml
direction: maximize
target_score: 0.9
max_iterations: 8
eval_cmd: "python3 eval_ml.py"
mutable_paths: ["solution.py"]
frozen_paths:
  - eval_ml.py
  - data/dev.jsonl
upstream_credits:
  - karpathy/autoresearch
  - zou-group/textgrad
  - stanfordnlp/dspy
---

# What to evolve

`solution.predict(text) -> str` returns `defect` or `config`. Improve the decision rule. Do not read or edit `data/dev.jsonl` from the mutable file, and do not change the evaluator.
