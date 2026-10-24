# D05：单篇文案迭代

为虚构自习室写一篇小红书笔记。2026-10-21 的真实五轮运行从 **16.5 分提高到最终保留的 96 分**。第 2 轮虽然得到 98 分，但新旧稿比较没有获胜，因此拒绝；后两轮同样没有保留。

[运行报告](runs/2026-10-21-codex-5-rounds/report.html) · [初稿](runs/2026-10-21-codex-5-rounds/first-draft.md) · [最终稿](runs/2026-10-21-codex-5-rounds/final-post.md) · [逐版核验](runs/2026-10-21-codex-5-rounds/verification.json) · [模板与替换输入](../../src/rsi_anything/templates/copywriting/README.md)

所有逐轮稿件从原始补丁恢复，最终稿与原保存文件逐字节一致。原始评分和拒绝记录保留。该结果只代表固定模型评委的评价；本例未测点击、传播或销售效果。当前评分细则已收紧，新运行不应直接与历史绝对分数比较。

```bash
rsi init copywriting post-demo
cd post-demo
rsi run --agent codex --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 5
rsi report
```

该命令使用自己的个人账号启动新实验，型号须在账号内可用。可复用写作方法的五轮实验及新简报结果见 [写作手册](../writing-guide/README.md)。
