# D05：写作手册在多份简报上迭代

[English](README.md)

正式展示实验：`runs/20261024-001816-reusable-writing-guide/`，真实5轮，开发评分62→69.5→74.5，后三轮72/72/69未被接受。

每轮由固定写手为咖啡自取、自行车检查、陶艺入门课三份虚构简报写稿，评委读实际稿件后反馈；助手只修改可复用手册。初始与最终手册再用于一份新的读书会简报，评分69→77.5。这个新简报案例展示了一次迁移结果，不代表一般写作能力或真实商业效果。

- 手册：各快照的 `files/writing-guide.md`。
- 三份开发稿：`files/out/posts.html` 与各产品 `.md`。
- 新简报：`artifacts/final/holdout-artifacts/files/out/posts.html`。
- 原始模型评分细节、接受与拒绝原因、调用元信息均随实验保存。
- `verification.json` 核对文件哈希、每个阶段的实际生成记录和新简报结果；最终快照是最佳轮次的副本，不重复计算它的生成调用。

较早的 `20261024-000057-reusable-writing-guide` 存在评分引用解析问题及给评委的简报遗漏，原样保留并单列说明，不与修复后的实验混合。

复现新实验：

```bash
export RSI_WRITER_MODEL=cli:codex:gpt-6.1-sol
python scripts/run_demo.py writing-guide --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 5 --minutes 60 --codex-isolated
```

使用已登录的个人账号；模型引用按账号可用情况固定。替换简报办法见模板README。
