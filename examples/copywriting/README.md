# D05: Iterating on a single post

[简体中文](README.zh-CN.md)

A Xiaohongshu post for a fictional study room. A real five-round run on 2026-10-21 went **from 16.5 points to a final kept score of 96**. Round 2 scored 98 but didn't win the head-to-head comparison with the current best, so it was rejected. The last two rounds weren't kept either.

[Run report](runs/2026-10-21-codex-5-rounds/report.html) · [First draft](runs/2026-10-21-codex-5-rounds/first-draft.md) · [Final post](runs/2026-10-21-codex-5-rounds/final-post.md) · [Per-version verification](runs/2026-10-21-codex-5-rounds/verification.json) · [Template and replacing inputs](../../src/rsi_anything/templates/copywriting/README.md)

Every round's draft was recovered from the original patches, and the final post matches the originally saved file byte for byte. The original scores and rejection records are kept. The result reflects only the fixed model judge's assessment; this example didn't measure clicks, reach or sales. The rubric has since been tightened, so new runs shouldn't be compared directly with the historical absolute scores.

```bash
rsi init copywriting post-demo
cd post-demo
rsi run --agent codex --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 5
rsi report
```

This command starts a new experiment with your own personal account; the models must be available on that account. The five-round experiment on a reusable writing method, with its result on a new brief, is in [Writing guide](../writing-guide/README.md).
