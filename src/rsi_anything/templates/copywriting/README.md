# 小红书文案迭代

[English](README.en.md)

为虚构“夜航自习室”的夜间会员写笔记。AI 每轮只改 `post.md`；产品事实固定在 `judge/brief.md`。基本规则检查长度和指定信息，模型按评分细则打分，并交换顺序比较新旧版本。

```bash
rsi init copywriting post-demo
cd post-demo
rsi run --agent codex --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 5
rsi report
```

使用自己的个人账号并明确写手/评委型号。分数只是该评委下的评价，不等于实际点击或销售效果。

替换输入：修改 `judge/brief.md` 中的产品、人群、价格和行动入口，再同步 `judge/rubric.yaml` 的必要信息/禁词检查，准备正常初稿 `post.md`，提交后新开实验。每轮正文和修改说明会保存，拒绝稿也保留。

本模板没有外部文案框架依赖。完整历史稿件见仓库 `examples/copywriting/`；跨多个简报改进写作方法使用另一个 `writing-guide` 模板。
