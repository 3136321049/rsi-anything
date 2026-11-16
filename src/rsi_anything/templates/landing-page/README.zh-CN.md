# 落地页进化：夜航自习室夜间会员

[English](README.md)

每轮助手只改 `index.html`，为虚构的“夜航自习室”夜间会员做一页英文落地页。评分前先检查：
- `judge/facts.json` 里的关键事实都出现在页面文字中；
- 页面自带全部样式和图形，不引用外部字体、图片或脚本；
- 没有占位文字，有标题和 viewport，图片都有替代文字，不超过 100 KB。

通过后用本机无头 Chrome 截两张图：桌面 1280px 宽；手机 390px 宽，按真实手机宽度排版后放大到 500px 宽的图片。页面文字另存为 `out/page.txt`。能看图的模型评委对照 `judge/brief.md` 评分，事实只能来自资料，编造的评价、人数或福利都会让检查不通过。分数更高的候选还要和当前最好版本并排比较，正反各看一次。

```bash
rsi init landing-page landing
cd landing
rsi check --jury cli:claude
rsi run --agent codex --jury cli:claude --rounds 6 --live
rsi share --to landing.html
```

需要本机有 Chrome、Chromium 或 Edge，找不到时设置 `RSI_BROWSER`。换成自己的产品时，同时改 `judge/brief.md`、`judge/facts.json` 和评分表里的任务描述；起点 `index.html` 应包含全部关键事实，进化只改表达和设计。评分只代表这份评分表和评委模型的判断，不等于真实转化率，上线前仍需真人检查。
