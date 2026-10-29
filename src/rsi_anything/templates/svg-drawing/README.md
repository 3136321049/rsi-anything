# 矢量画进化：鹈鹕骑自行车

[English](README.en.md)

每轮助手只改 `drawing.svg`。评分前先检查它是干净的矢量画：能解析、有 `viewBox`、只用图形元素（不嵌位图、不引外部资源、没有脚本）、不写文字、不超过 60 KB。通过后用本机无头 Chrome 渲染成 1024×768 的 `out/drawing.png`，交给能看图的模型评委按评分表打分：鹈鹕像不像、自行车完不完整、是不是真的在骑、画得好不好。分数更高的候选还要和当前最好版本并排比较，正反顺序各看一次，多数票胜出才保留。

不允许写字，是为了防止用 “PELICAN” 之类的标签讨好评委。渲染时断网，画里引用的外部资源不会加载。

```bash
rsi init svg-drawing pelican
cd pelican
rsi check --jury cli:claude
rsi run --agent codex --jury cli:claude --rounds 6 --live
rsi share --to pelican.html
```

需要本机有 Chrome、Chromium 或 Edge；找不到时设置 `RSI_BROWSER` 指向浏览器程序。评委需要能看图的模型：`cli:claude`、`cli:codex`，或支持图片的 API 模型。渲染失败按“结果未知”记录，不记 0 分。

换主题时改 `rsi.yaml` 的 `goal` 和 `judge/rubric.yaml` 的任务与评分锚点，起点画稿越简单，进化过程越好看。评分来自模型评委，只代表这份评分表下的判断，不是美术专业评审。
