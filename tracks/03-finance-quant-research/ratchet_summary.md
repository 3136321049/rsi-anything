# Ratchet summary — 人形机器人核心零部件深度研报

**Best score: 94.5 / target 92.0 / reached: True**

| Round | Status | Score | Best |
|---:|---|---:|---:|
| 0 | BASELINE | 58.0 | 58.0 |
| 1 | KEEP | 72.5 | 72.5 |
| 2 | REVERT_SCORE | 64.5 | 72.5 |
| 3 | KEEP | 84.0 | 84.0 |
| 4 | REVERT_GUARD | 84.0 | 84.0 |
| 5 | KEEP | 94.5 | 94.5 |

```text
R 0 BASELINE       58.0 ███████████████████
R 1 KEEP           72.5 ███████████████████████
R 2 REVERT_SCORE   64.5 █████████████████████
R 3 KEEP           84.0 ███████████████████████████
R 4 REVERT_GUARD   84.0 ███████████████████████████
R 5 KEEP           94.5 ██████████████████████████████
```

Round 0 is the 58-point draft. Round 2 is the fake-source revert.
Round 4 never reaches the judge: the frozen rubric hash changed, so both the rubric and the candidate report are restored.

---
Upstream inspiration: karpathy/autoresearch · stanford-oval/storm · assafelovic/gpt-researcher · Future-House/paper-qa
