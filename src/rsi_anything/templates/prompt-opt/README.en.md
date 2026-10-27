# Eight-class food-delivery support prompt

[简体中文](README.md)

Edit `prompt.md` so a fixed task model sorts each message into refund, late delivery, wrong item, cancel or change order, account, payment, praise, or other. The 48-message dev set and the 29-message held-out set are Chinese and English examples written for this project, with no real user data.

```bash
rsi init prompt-opt prompt-demo
cd prompt-demo
export RSI_TASK_MODEL=cli:codex:gpt-5.6-sol
rsi run --agent codex --model gpt-6.1-sol --rounds 5
rsi report
```

Sign in to your own coding agent first, and name the models explicitly based on what your personal account can use. Dev-set accuracy decides whether a change is accepted, and it must improve by at least 2 percentage points. The held-out set is evaluated separately at the start and at the end. All `out/development.json` and `out/holdout.json` files and the notes on mistakes are saved with the stage they belong to. Model scores fluctuate.

Replacing inputs: edit `judge/dev.jsonl` and `holdout/test.jsonl`; each line has `text` and `label`. If you change the label set, also change its definition in `judge/evaluate.py`. Commit the complete material first, then start a new experiment. API models are evaluated one message at a time by default; CLI models default to batches of 20. Use `RSI_TASK_BATCH` and `RSI_TASK_WORKERS` to control this.

This template is the project's own implementation and doesn't use an external prompt-optimization framework. Past experiments, including results with no improvement, are in `examples/prompt-opt/` in the repository.
