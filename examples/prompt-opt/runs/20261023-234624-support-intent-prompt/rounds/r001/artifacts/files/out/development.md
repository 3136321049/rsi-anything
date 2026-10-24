# 客服分类结果：development

模型：`cli:codex:gpt-5.6-sol`

准确率：89.6%（43/48）；调用失败：0

## 错例

- 等了一个小时还没到，不要了，帮我取消：预期 cancel_order，实际 late_delivery
- 奶茶太甜了，完全没按少糖做，喝不了，要求退款：预期 refund，实际 wrong_item
- Delivery is taking forever, just cancel it and give me my money back：预期 cancel_order，实际 late_delivery
- 骑手特别好，想给他加点小费，在哪里加：预期 payment，实际 praise
- The rider was amazing, how do I add a tip after delivery?：预期 payment，实际 praise
