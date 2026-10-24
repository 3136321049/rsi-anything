# 记账项目检查

固定测试通过 12/15。
fixed_expense_tests.ExpenseTests.test_date_reject_invalid: AssertionError: ValueError not raised
fixed_expense_tests.ExpenseTests.test_month_refund: ?         ^
fixed_expense_tests.ExpenseTests.test_month_reject_invalid: AssertionError: ValueError not raised

## 当前示例

```json
{
  "month": "2026-10",
  "totals_cents": {
    "餐饮": 4840,
    "交通": 420
  },
  "dinner_split_cents": [
    3334,
    3333,
    3333
  ]
}
```
