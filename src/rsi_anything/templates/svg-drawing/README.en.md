# Evolving a vector drawing: a pelican riding a bicycle

[简体中文](README.md)

Each round the agent changes only `drawing.svg`. Before scoring, a check confirms it's a clean vector drawing: it parses, has a `viewBox`, uses only shape elements (no embedded bitmaps, external resources or scripts), contains no text, and stays under 60 KB. If it passes, headless Chrome on your machine renders it to a 1024×768 `out/drawing.png`, and an image-capable model judge scores it against the rubric: is it a pelican, is the bicycle complete, is the bird really riding, and is it well drawn. A higher-scoring candidate must also beat the current best side by side, viewed in both orders, and win the majority of votes before it's kept.

Text is banned so a label like "PELICAN" can't flatter the judge. Rendering runs with the network blocked, so external resources referenced by the drawing never load.

```bash
rsi init svg-drawing pelican
cd pelican
rsi check --jury cli:claude
rsi run --agent codex --jury cli:claude --rounds 6 --live
rsi share --to pelican.html
```

You need Chrome, Chromium or Edge on the machine; if it isn't found, set `RSI_BROWSER` to the browser executable. The judge needs a model that can see images: `cli:claude`, `cli:codex`, or an API model with image input. A failed render is recorded as quality unknown, not as a score of 0.

To change the subject, edit `goal` in `rsi.yaml` and the task and anchors in `judge/rubric.yaml`. The simpler the starting drawing, the better the evolution looks. Scores come from a model judge and reflect this rubric only; they aren't a professional art review.
