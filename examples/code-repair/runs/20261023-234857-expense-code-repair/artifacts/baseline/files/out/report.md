# 记账项目检查

固定测试通过 6/15。
fixed_expense_tests.ExpenseTests.test_amount_exact_cents: AssertionError: 28 != 29
fixed_expense_tests.ExpenseTests.test_amount_reject_extra_precision: AssertionError: ValueError not raised
fixed_expense_tests.ExpenseTests.test_date_reject_invalid: AssertionError: ValueError not raised
fixed_expense_tests.ExpenseTests.test_month_refund: ?         ^
fixed_expense_tests.ExpenseTests.test_month_reject_invalid: AssertionError: ValueError not raised
fixed_expense_tests.ExpenseTests.test_split_reject_invalid: AssertionError: ValueError not raised
fixed_expense_tests.ExpenseTests.test_split_remainder: + [3334, 3333, 3333]
fixed_expense_tests.ExpenseTests.test_split_small_total: + [1, 1, 0, 0]
fixed_expense_tests.ExpenseTests.test_amount_reject_non_finite: OverflowError: cannot convert float infinity to integer

## 当前示例

```json
{
  "month": "2026-10",
  "totals_cents": {
    "餐饮": 4840,
    "交通": 420
  },
  "dinner_split_cents": [
    3333,
    3333,
    3333
  ]
}
```
