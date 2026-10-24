# RSI run `20261023-234624-support-intent-prompt`

**Goal:** Improve prompt.md, the instructions a language model follows to label a customer message of a food-delivery
app with exactly one intent. Score = accuracy (%) on the labeled examples in judge/dev.jsonl (48 messages, mixed Chinese and English).
The prompt must work for any new message, so write general rules, not answers for specific examples.

Agent `codex` · judge `command` · branch `rsi/20261023-234624-support-intent-prompt`

| round | status | score | best | change | why |
|---:|---|---:|---:|---|---|
| 0 | BASELINE | 89.6 | 89.6 | baseline |  |
| 1 | REVERT | 89.6 | 89.6 | 明确 cancel_order 包含已下单后的修改请求，减少此类消息被误判为 other，提高分类准确率。 | score 89.6 is not better than 89.6 (required margin: 2 or 0%) |
| 2 | REVERT | 83.3 | 89.6 | 明确错餐、缺餐问题优先于退款诉求归入 wrong_item，减少被误判为 refund 的情况，提高准确率。 | score 83.3 is not better than 89.6 (required margin: 2 or 0%) |
| 3 | REVERT | 89.6 | 89.6 | 将账单与付款凭证请求明确归入 payment，减少误判为 other，提高分类准确率。 | score 89.6 is not better than 89.6 (required margin: 2 or 0%) |

Stopped: reached 3 rounds.

运行状态：finished。已保存 18 条模型调用记录；调用费用：工具未提供。

[任务配置](config/rsi.yaml) · [模型与运行参数](config/execution.json)

## 产物版本

- 初始产物：[out/development.json](artifacts/baseline/files/out/development.json) · [out/development.md](artifacts/baseline/files/out/development.md) · [prompt.md](artifacts/baseline/files/prompt.md)
- 第 1 轮 · REVERT：[out/development.json](rounds/r001/artifacts/files/out/development.json) · [out/development.md](rounds/r001/artifacts/files/out/development.md) · [prompt.md](rounds/r001/artifacts/files/prompt.md)
- 第 2 轮 · REVERT：[out/development.json](rounds/r002/artifacts/files/out/development.json) · [out/development.md](rounds/r002/artifacts/files/out/development.md) · [prompt.md](rounds/r002/artifacts/files/prompt.md)
- 第 3 轮 · REVERT：[out/development.json](rounds/r003/artifacts/files/out/development.json) · [out/development.md](rounds/r003/artifacts/files/out/development.md) · [prompt.md](rounds/r003/artifacts/files/prompt.md)
- 最终产物：[out/development.json](artifacts/final/files/out/development.json) · [out/development.md](artifacts/final/files/out/development.md) · [prompt.md](artifacts/final/files/prompt.md)

Hold-out judge (never shown to the agent): 82.8 → 82.8
