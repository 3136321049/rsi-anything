# 客服分类结果：development

模型：`cli:codex:gpt-5.6-sol`

准确率：89.6%（43/48）；调用失败：0

## 错例

- 饭到了但是少了一份米饭，退钱吧：预期 wrong_item，实际 refund
- Thanks for the quick refund last time, but today my burger is missing from the bag：预期 wrong_item，实际 other
- 能帮我把地址改成公司吗？订单刚下：预期 cancel_order，实际 other
- Can you add a side of fries to the order I just placed?：预期 cancel_order，实际 other
- 麻烦备注一下不要香菜，刚才忘写了：预期 cancel_order，实际 other
