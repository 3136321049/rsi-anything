# D03：客服提示词优化

[English](README.md)

完整三轮实验：`runs/20261023-234624-support-intent-prompt/`。

- 初始开发集89.6%，三轮候选分别89.6%、83.3%、89.6%，均未超过所需提升幅度，最终保留初始提示词。
- 初始和最终留出集均82.8%（24/29），实际调用无失败。
- 每轮提示词和错例、初始及最终留出结果均已导出。本例展示了完整迭代与拒绝，没有获得分数提升。
- 写手显式请求 `gpt-6.1-sol`，任务模型显式请求 `cli:codex:gpt-5.6-sol`；CLI未提供服务端实际型号确认，按未知记录。
- `USAGE.zh-CN.md` 解释历史导出中复制调用记录的去重口径；原始记录未改。
- `runs/2026-10-21-codex-partial/` 是更早的部分实验，不能与本次拼成一条提升曲线。

复现新实验：

```bash
python scripts/run_demo.py prompt-opt --model gpt-6.1-sol --task-model cli:codex:gpt-5.6-sol --rounds 3 --minutes 30 --codex-isolated
```

个人Codex需已登录且支持这些型号；初始化和替换输入见模板README。模型输出有波动，重跑会单独形成新记录。
