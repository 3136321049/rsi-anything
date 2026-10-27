# D13: Percentages lesson and exercises

[简体中文](README.md)

The agent improves `lesson.md` so that a real student model can read it and then complete ten fixed original exercises. The content extends from finding a part to recovering the original amount, rates of change, successive increases and decreases, percentage points and changes in the whole. The starting draft covers only the basic definition and finding a part.

```sh
rsi init lesson-builder demo-lesson
cd demo-lesson
export RSI_TASK_MODEL='cli:codex'
rsi run --rounds 6
```

`RSI_TASK_MODEL` must be set explicitly. It can be an existing personal model reference, such as `cli:codex`, or an API model you've configured yourself. The student receives the lesson, the questions and the format requirements, but not the fixed answers. It may do arithmetic and derive answers with the lesson's methods, and says it is unsure when a needed method is missing. This restriction is expressed through the prompt; it isn't a calibrated simulation of a human student.

The program compares each value the real model gives with the fixed answer, and checks that the derivation text and the lesson quote exist. The main score is the share of answers that are "numerically correct with a supporting lesson quote"; plain numeric accuracy is also kept. A matching quote can't prove that it semantically supports the answer well enough. A strong model may already score full marks on the starting draft; that must be recorded truthfully, not hidden by artificially lowering the score.

`out/lesson.html` and `lesson.md` hold the lesson, `exercise-results.md` holds the answer to each question, `results.json` includes the actual model and call information, `mistakes.json` holds the mistakes, and `student-response.txt` keeps the raw reply. Model or response-format failures are written to `error.json` and exit as a run error; they aren't counted as wrong student answers. `outputs: [out]` saves each round's outputs.

This package uses the project's existing model-calling interface and adds no dependencies. Running `python3 judge/evaluate.py` directly makes a real call to the student model; for offline development, run the repository tests, which don't call a model. The fixed questions and the starting draft were written by the author. Public concepts follow [OpenStax Prealgebra 2e, chapter 6](https://openstax.org/books/prealgebra-2e/pages/6-introduction-to-percents), consulted on 2026-10-24; no textbook questions were copied.

Before changing the topic, update `judge/brief.md`, the questions, answers, tolerances and explanations in `exercises.json`, and the starting lesson. Keeping the numeric-answer format lets you reuse the existing grader. Commit the new inputs, then start a new run; don't change the fixed exercises within an experiment. A real three-round experiment is complete: the restricted student model went from 2/10 to 10/10. The records and an offline grading replay are saved in the repository under `examples/lesson-builder/`. This isn't the same as learning outcomes for real people.
