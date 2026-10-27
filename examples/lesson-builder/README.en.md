# D13: Completing a percentages lesson for a restricted model to answer from

[简体中文](README.md)

The starting draft only introduced the definition of a percentage and finding a part of a known whole. In the real run, the agent added working backward, rates of change, successive changes, changes in the whole and percentage points, and explained the methods with worked examples that differ from the fixed exercises. A student model restricted by its prompt read the lesson and answered ten fixed original questions. The program checked the values, the derivation text and the supporting lesson quotes.

| Version | Correct with a supporting lesson quote | Numeric accuracy | Outcome |
|---|---:|---:|---|
| Starting | 2/10 | 20% | Baseline |
| Round 1 | 10/10 | 100% | Kept |
| Round 2 | 10/10 | 100% | Rejected; did not beat the current score |
| Round 3 | 10/10 | 100% | Rejected; round 1 remains the final version |

[Open the full experiment report](runs/20261024-003730-percent-lesson/report.html) · [Read the final lesson and the ten worked answers](runs/20261024-003730-percent-lesson/artifacts/final/files/out/lesson.html) · [Starting mistakes](runs/20261024-003730-percent-lesson/artifacts/baseline/files/out/mistakes.json) · [Independent re-verification record](runs/20261024-003730-percent-lesson/verification.json)

The agent explicitly requested `gpt-6.1-sol` from a personal Codex account, and the restricted student was fixed to request `cli:codex:gpt-5.6-sol`; reasoning effort was `medium`. Here a program scores the answers against the fixed answers; there's no separate model judge for the writing. The CLI didn't return the actual model or the cost in US dollars, so both stay unknown; all raw replies, derivations and usage are saved.

The fixed answers to all ten questions were recomputed independently, and the frozen grader replayed the raw student replies for the starting version, the three candidates and the final version. The results matched the ledger, with no extra model calls and no original scores overwritten. The final lesson and the ten derivations were read: the worked examples use new scenarios or number combinations, and the text doesn't copy any fixed question in full. A browser shows the full lesson, the student's answers, the supporting quotes and the fixed solutions.

This result only shows how the model's answers changed under the given prompt restrictions. The student model may already know this material, and the restriction is expressed through the prompt. A quote being present doesn't automatically prove semantic support, and the questions weren't kept as a hidden held-out set. So the move from 20% to 100% can't be read as learning outcomes for real people or as generalization to new questions.

To start a new experiment with your own personal Codex login, run this from the project root:

```bash
python3 scripts/run_demo.py lesson-builder --model gpt-6.1-sol --task-model cli:codex:gpt-5.6-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

After installing this project, you can run `python verify_saved_results.py` in the run folder to re-verify offline. The lesson and questions were written by the project author, using only [the OpenStax chapter on percents](https://openstax.org/books/prealgebra-2e/pages/6-introduction-to-percents) as a public reference for concepts; no textbook questions or text were copied.
