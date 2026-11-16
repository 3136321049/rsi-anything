# Evolving a landing page: Night Voyage Study Room

[简体中文](README.zh-CN.md)

Each round the agent changes only `index.html`, a one-page English landing page for the Night Membership of the fictional "Night Voyage Study Room". Before scoring, a check confirms:
- every key fact in `judge/facts.json` appears in the page text;
- the page carries all its own styles and graphics, with no external fonts, images or scripts;
- there's no placeholder text, it has a title and a viewport, every image has alt text, and it stays under 100 KB.

If it passes, headless Chrome on your machine takes two screenshots: desktop at 1280px wide, and phone laid out at a real 390px width, then scaled up to a 500px-wide image. The page text is saved as `out/page.txt`. An image-capable model judge scores the page against `judge/brief.md`. Facts may only come from the brief: invented testimonials, member counts or perks fail the check. A higher-scoring candidate must also beat the current best side by side, viewed in both orders.

```bash
rsi init landing-page landing
cd landing
rsi check --jury cli:claude
rsi run --agent codex --jury cli:claude --rounds 6 --live
rsi share --to landing.html
```

You need Chrome, Chromium or Edge on the machine; if it isn't found, set `RSI_BROWSER`. To use your own product, update `judge/brief.md`, `judge/facts.json` and the task in the rubric together. The starting `index.html` should already contain every key fact, so evolution only changes wording and design. Scores reflect this rubric and the judge model, not real conversion rates; have a person review the page before it goes live.
