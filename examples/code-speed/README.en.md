# D01: Fuzzy search speedup

[简体中文](README.md)

A real three-round run on 2026-10-21 raised speed on a fixed workload from the baseline to **4.45×, 17.83× and 27.45×**, and all three rounds were kept. The rounds improved, in turn, the distance calculation, candidate pruning and reusable per-name statistics. The output still had to pass the correctness check against the reference implementation.

[Run report](runs/2026-10-21-codex-3-rounds/report.html) · [Raw ledger](runs/2026-10-21-codex-3-rounds/ledger.jsonl) · [Per-version correctness re-check](runs/2026-10-21-codex-3-rounds/artifact-verification.json) · [Template and replacing inputs](../../src/rsi_anything/templates/code-speed/README.en.md)

The starting source, the three round candidates and the final source were rebuilt from the original patches. They are in the run folder under `artifacts/baseline/`, `rounds/r001/artifacts/` to `rounds/r003/artifacts/`, and `artifacts/final/`. Every version passed this re-check; the re-check's timings don't replace the historical scores. Speedups depend on the machine and the input size.

```bash
rsi init code-speed speed-demo
cd speed-demo
rsi check
rsi run --agent codex --model gpt-6.1-sol --rounds 5
rsi report
```

This command starts a new experiment. It needs a personal agent you're signed in to and a model you can use. The historical run used the account's default model, and the service returned no separate confirmation of which model ran. The implementation is this project's own. The loop idea follows autoresearch; its run engine is not imported.
