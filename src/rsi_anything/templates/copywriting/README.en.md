# Iterating on a Xiaohongshu post

[简体中文](README.md)

Write a post about the night membership of the fictional "Night Voyage Study Room" (夜航自习室). Each round, the AI changes only `post.md`; the product facts are fixed in `judge/brief.md`. Basic rule checks cover length and required information. A model scores the post against the rubric and runs a head-to-head comparison of the new and current versions in both orders.

```bash
rsi init copywriting post-demo
cd post-demo
rsi run --agent codex --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 5
rsi report
```

Use your own personal account and name the writing agent's and judge's models explicitly. A score is only this judge's assessment, not actual clicks or sales.

Replacing inputs: change the product, audience, price and call to action in `judge/brief.md`, and update the required-information and banned-phrase checks in `judge/rubric.yaml` to match. Prepare an ordinary first draft in `post.md`, commit, and start a new experiment. Each round's text and change notes are saved, and rejected drafts are kept too.

This template doesn't depend on any external copywriting framework. The full history of drafts is in `examples/copywriting/` in the repository. To improve a writing method across several briefs, use the separate `writing-guide` template.
