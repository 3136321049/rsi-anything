# Algorithms and ML starter

A tiny, CPU-only ratchet target. `solution.py` is the only mutable file. `eval_ml.py` and `data/dev.jsonl` stay frozen so the agent cannot edit the exam.

```bash
python3 eval_ml.py
```

The script prints a JSON verdict (`score` is hold-out accuracy). A keyword baseline lands well below the 0.90 target; the ratchet should keep a change only when accuracy rises without touching the frozen files.
