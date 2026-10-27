# D12: Physical activity explainer for adults

[简体中文](README.md)

This template turns public WHO guidelines into an explanation that generally healthy adults can understand. It shows the path from excerpts of source material to an article that is accurate, readable and of practical help. The agent edits only `explainer.md`. The default starting draft was written by a person; there are no preset later candidates or scores.

## Getting started

After setting up your own coding agent or personal model account, run:

```sh
rsi init medical-explainer demo-medical-explainer
cd demo-medical-explainer
python3 judge/prepare.py
rsi run --rounds 6
```

The prepare script doesn't go online or call a model; the actual multi-round run uses your own account's resources. Use `rsi run --agent codex --rounds 6` to choose the agent; the judge is set in `rsi.yaml`.

## Sources and evaluation

The frozen `judge/sources.json` holds the WHO sources, short summaries rewritten by the author, and the limits on how they may be used. Key quantities are interpolated through `{{adult_age}}`, `{{moderate_minutes}}`, `{{vigorous_minutes}}` and `{{strength_days}}`, and sources are marked `[W1]` and `[W2]`. Don't write any other numbers in digits.

The program checks the quantities, the sources, the notes on starting small and on sedentary time, the health-education purpose, and some obviously prohibited wording. The model judge separately decides whether the material is restated accurately, whether it overpromises, and whether it gives individualized medical instructions, and rates whether ordinary readers can understand it and get started. A disclaimer by itself won't earn a high score.

## Outputs and replacing the inputs

`out/explainer.html` and `explainer.md` are the readable finished article, and `checklist.json` holds the quantities and the checklist; `evaluation.md`, `gates.json` and `notes.txt` are for the review. The HTML can be read offline. `outputs: [out]` lets the main loop save each round's outputs; the agent doesn't edit `out/` directly.

To change the health topic, a person must first check the authoritative sources, the quantities and the population they apply to, then update the inputs, the prepare script, the goal, the starting draft and the scoring rubric to match. Changing only the title doesn't move the template to a new topic. This package doesn't accept medical records and doesn't create diagnosis or treatment plans for patients, or personal training plans.

## Dependencies and status

The prepare script uses only the Python standard library, and the loop uses the project's existing PyYAML and model interfaces. No additional medical service, model or company resource is used. The official sources were checked on 2026-10-23, and runs use the saved snapshot of the material.

A real three-round experiment is complete: the final kept score rose from 58.5 to 80, and the candidates from the last two rounds were rejected. The explainer texts, sources, quantity checks and re-verification records are saved in the repository under `examples/medical-explainer/`. This result only describes health-explainer writing from the supplied material; it isn't a judgment of clinical effectiveness.
