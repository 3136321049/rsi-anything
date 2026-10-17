---
name: "Contract redline and PRISMA memo"
track: law-medicine
direction: maximize
target_score: 90
max_iterations: 8
eval_cmd: "python3 eval_case.py"
mutable_paths: ["memo.md"]
frozen_paths:
  - rubric.yaml
  - statutes.json
  - eval_case.py
upstream_credits:
  - wanshuiyin/Auto-claude-code-research-in-sleep
  - Future-House/paper-qa
---

# What good looks like

Close one-sided clauses without inventing article numbers. For the clinical half, every PMID must be on the frozen ledger, and the PRISMA headings must be real sections rather than a copied checklist with no methods.
