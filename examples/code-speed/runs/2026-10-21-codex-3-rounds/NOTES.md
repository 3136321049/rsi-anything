# Real run: code-speed with Codex CLI, 3 rounds

- Date: 2026-10-21. Agent: OpenAI Codex CLI (`codex exec`, the account's default model, reasoning effort high).
- Template: `code-speed` (fuzzy name search; score = speedup over the frozen original, correctness is a hard gate).
- Nothing in this folder was edited by hand. It was produced by `rsi run --agent codex --rounds 3`
  and `rsi export`, which only replaces local paths with placeholders.

| round | result | speedup | what the agent did |
|---:|---|---:|---|
| 0 | baseline | 1.0x | original dynamic-programming edit distance |
| 1 | kept | 4.45x | bit-parallel edit distance, query masks computed once |
| 2 | kept | 17.8x | keep only the current top-k and skip names whose lower bound cannot make it |
| 3 | kept | 27.5x | precompute per-name character counts once per name list, tighter lower bound |

Agent time was 95 to 150 seconds per round; each judge run took under a second.

After the run the template's judge gained one more check (the same list object changed in place between calls,
so cached precomputation must notice). The round-3 champion passes it too and measured 29x on a re-run.
The hypotheses are in Chinese because the machine's Codex was configured to answer in Chinese.
