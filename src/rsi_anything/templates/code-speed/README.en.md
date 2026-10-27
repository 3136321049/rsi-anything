# Fuzzy search speedup

[简体中文](README.md)

Improve the search implementation in `search.py`. Given a query, a list of names and a result count, the output must match the frozen reference implementation. Repeated queries on the same list may use precomputation, but results must stay correct after the list changes.

```bash
rsi init code-speed speed-demo
cd speed-demo
rsi check
rsi run --agent codex --model gpt-6.1-sol --rounds 5
rsi report
```

You only need Python, Git and a personal coding agent you're signed in to. Basic correctness is checked first; the score is then the reference time divided by the candidate time. A candidate must improve by at least 5% to be kept. Results depend on the machine and on that run's inputs, so no fixed speedup is guaranteed.

By default, each check generates about 1,200 names and a set of queries. To replace the task, edit the input size and checks in `judge/check.py` and the fixed interface in `judge/reference.py`, update the goal, and start a new experiment. The artifact the agent may change is still set only by `artifact` in `rsi.yaml`.

The current measured run, with the per-round source recovered from patches, is in `examples/code-speed/` in the repository. The implementation is this project's own. The loop idea follows [autoresearch](https://github.com/karpathy/autoresearch); none of its training code is imported.
