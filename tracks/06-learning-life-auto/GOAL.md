---
name: "Feynman guide and ATS resume"
track: learning-life
direction: maximize
target_score: 90
max_iterations: 8
eval_cmd: "python3 eval_packet.py"
mutable_paths: ["packet.md"]
frozen_paths:
  - rubric.yaml
  - job.txt
  - eval_packet.py
upstream_credits:
  - zou-group/textgrad
  - stanfordnlp/dspy
---

# What good looks like

Teach one idea in plain language, then show a resume a keyword screen can score. The job description and the rubric stay frozen.
