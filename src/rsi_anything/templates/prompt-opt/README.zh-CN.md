# 外卖客服八分类提示词

[English](README.md)

修改 `prompt.md`，让固定任务模型把消息分为退款、延迟配送、错餐、取消/修改订单、账号、支付、表扬或其他。开发集48条、留出集29条均为本项目构造的中英文示例，不含真实用户资料。

```bash
rsi init prompt-opt prompt-demo
cd prompt-demo
export RSI_TASK_MODEL=cli:codex:gpt-5.6-sol
rsi run --agent codex --model gpt-6.1-sol --rounds 5
rsi report
```

先登录自己的编程助手；型号按个人账号可用情况明确指定。开发集准确率用于接受改动，至少提升2个百分点；开始和结束另评留出集。所有 `out/development.json`、`out/holdout.json` 与错例说明随对应阶段保存。模型分数有波动。

替换输入：编辑 `judge/dev.jsonl` 和 `holdout/test.jsonl`，每行含 `text` 与 `label`。修改标签集合时同时修改 `judge/evaluate.py` 中的定义。先提交完整材料，再开始新实验。API模型默认逐条评价；CLI默认每批20条，可用 `RSI_TASK_BATCH` 和 `RSI_TASK_WORKERS` 控制。

本模板由项目自行实现，未接入外部提示词优化框架。历史实验及未提升结果见仓库 `examples/prompt-opt/`。
