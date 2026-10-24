# 客服分类结果：development

模型：`cli:codex:gpt-5.6-sol`

准确率：83.3%（40/48）；调用失败：0

## 错例

- 外卖撒了一半，汤全洒在袋子里了，怎么赔：预期 refund，实际 other
- 能开发票吗？公司报销要用：预期 payment，实际 other
- 奶茶太甜了，完全没按少糖做，喝不了，要求退款：预期 refund，实际 wrong_item
- 能帮我把地址改成公司吗？订单刚下：预期 cancel_order，实际 other
- Can you add a side of fries to the order I just placed?：预期 cancel_order，实际 other
- 麻烦备注一下不要香菜，刚才忘写了：预期 cancel_order，实际 other
- 配送费也太贵了吧，一份面条配送要八块：预期 other，实际 payment
- Your prices went up again, everything is so expensive now：预期 other，实际 payment
