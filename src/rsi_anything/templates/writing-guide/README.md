# 可复用写作手册

本案例对应 D05 的手册部分。AI 每轮修改 `writing-guide.md`；固定写手真实生成三份简报的文案，评委按读者匹配、组织、表达和行动提示评分。开始与结束另用一份新简报。全部简报为本项目独立编写的虚构产品资料。

安装本项目并登录个人编程助手后：

```bash
rsi init writing-guide guide-demo
cd guide-demo
export RSI_WRITER_MODEL=cli:codex:gpt-6.1-sol
rsi check --jury cli:codex:gpt-6.1-sol
rsi run --agent codex --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 5
rsi report
```

运行前固定写手与评委型号。一轮包含三个写手调用，以及评分和可能的新旧比较。使用已有个人订阅或自备接口，不自动购买资源。模型名称按个人账号实际可用情况选择。

替换输入：修改 `judge/briefs.json`，为每份简报提供不同 `id`、产品名称、目标读者、事实与行动入口；新简报放 `holdout/briefs.json`。先提交资料再开始新实验。`out/posts.html` 可直接查看；各稿、调用元信息和错误都在 `out/`，随轮次保存。模型分数是本评委下的反馈，不表示真实点击或销售效果。

依赖仅为本项目模型调用层和 Python 标准库，未导入外部优化引擎。当前模板已实现，真实多轮状态以 `examples/writing-guide/` 的记录为准。
