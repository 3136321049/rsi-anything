# 客服分类结果：holdout

模型：`cli:codex:gpt-5.6-sol`

准确率：82.8%（24/29）；调用失败：0

## 错例

- Need a VAT invoice for this order：预期 payment，实际 other
- Can I get a refund on the coupon I couldn't use at checkout?：预期 payment，实际 refund
- I need to change the delivery address, I put my old apartment：预期 cancel_order，实际 other
- 能不能帮我把奶茶改成去冰，订单还没做吧：预期 cancel_order，实际 other
- 骑手冒雨送餐太辛苦了，我想补一个小费：预期 payment，实际 praise
