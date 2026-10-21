# Real run: Xiaohongshu post, Codex writes, a different Codex model judges, 5 rounds

- Date: 2026-10-21. Writer: OpenAI Codex CLI (`codex exec`, the account's default model).
  Jury: one model, `cli:codex:gpt-5.6-sol`, i.e. a different model than the writer but the same vendor.
  That was the only personal account available on the machine; a cross-vendor jury is the recommended setup.
- Template: `copywriting`. Facts may only come from the frozen brief; hard gates check length, the
  title length, the required price, banned absolute claims and AI clichés; an LLM check verifies every fact.
- Produced by `rsi run --agent codex --jury cli:codex:gpt-5.6-sol --rounds 5` and `rsi export`. Not edited by hand.
  `first-draft.md` is the starting post, `final-post.md` is the champion.

| round | result | score | why |
|---:|---|---:|---|
| 0 | baseline | 16.5 | too short, no price, two clichés, a vague claim |
| 1 | kept | 95.5 | all gates now pass (gates come before score) |
| 2 | thrown away | 98 | higher score, but lost the head-to-head against the champion (1 of 2 votes) |
| 3 | kept | 96 | higher score and won head-to-head in both orders |
| 4 | thrown away | 95.5 | not better |
| 5 | thrown away | 95.5 | not better |

What this run taught us: the judge scored the first decent draft 95.5, leaving almost no room to improve.
After this run the rubric judge was told to use the whole scale (competent but unremarkable = 5-6, 9-10 rare),
and the template's anchors were tightened.
