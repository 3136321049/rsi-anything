# D04: Three rounds of CPU handwritten digit classification

[简体中文](README.md)

On 2026-10-24, the Codex CLI on a personal ChatGPT account ran 3 real rounds, optimizing only `training.json`. Scores come from real training and prediction with scikit-learn on the CPU; there is no model judge. The fixed validation set has 450 digit images and the training set 1,347. The data and the split stayed the same for the whole experiment.

| Round | Formal status | Formal accuracy | Formal errors | Result |
|---|---|---:|---:|---|
| Start | Baseline | 46.889% | 239/450 | Three-level decision tree |
| Round 1 | Kept | 99.333% | 3/450 | Switched to an RBF-kernel SVM, C=10, gamma=scale, no scaling, no dimensionality reduction |
| Round 2 | No change | — | — | The agent tried adjusting gamma, then restored the configuration itself; the round never reached formal review |
| Round 3 | No change | — | — | The agent tried PCA, then restored the configuration itself; the round never reached formal review |

The round-1 configuration was kept in the end, and the real run stopped after reaching 3 rounds. The final raw training-plus-prediction time was 0.0248 seconds. Timing depends on the machine and isn't a model-quality score. The formal metric rose from 46.889% to 99.333%; the two no-change rounds must not be drawn as new formal score points.

[Full run report](runs/20261024-001122-cpu-digits-classifier/report.html) · [Baseline mistakes](runs/20261024-001122-cpu-digits-classifier/artifacts/baseline/files/out/mistakes.png) · [Final mistakes](runs/20261024-001122-cpu-digits-classifier/artifacts/final/files/out/mistakes.png) · [Final confusion matrix](runs/20261024-001122-cpu-digits-classifier/artifacts/final/files/out/confusion.png) · [Final configuration](runs/20261024-001122-cpu-digits-classifier/artifacts/final/files/training.json) · [Independent verification](runs/20261024-001122-cpu-digits-classifier/verification.json)

The calls explicitly requested `gpt-6.1-sol` with `medium` reasoning effort and an isolated configuration. The CLI didn't return the actual model from the service, so `actual_model` stays `null`. Usage is saved as originally returned; the cost in dollars wasn't returned. The baseline, per-round and final artifacts are all kept, and no hand-written sequence of candidates was used.

The exported baseline, round-1 and final configurations were each placed in a new temporary folder. After the old outputs were deleted, the frozen evaluator retrained each one. The scores and the SHA256 of the data and the split matched the original records, and the final version still misclassified 3 images. The `out` folders saved in rounds 2 and 3 are the agent's internal trial outputs, from configurations that changed gamma and used PCA respectively. `training.json` in those rounds had already been restored to the champion configuration, so these outputs aren't part of any formal candidate review. The independent verification marks this difference explicitly and doesn't overwrite the original records.

To reproduce, first install the template's `requirements.txt` in the same Python environment and set up a personal Codex login. Then run from the repository root:

```bash
python scripts/run_demo.py cpu-classifier --model gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

To use a specific CLI path, set `RSI_CODEX_BIN`. The evaluator is pinned to scikit-learn 1.6.1; this run used Python 3.11.14. The validation set was used repeatedly for tuning, so these numbers only describe improvement on this fixed task, not generalization to independent new data.
