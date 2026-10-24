"""固定业务测试；每个测试对应一项可解释的行为。"""
import copy
import unittest

from expense import amount_to_cents, monthly_totals, split_bill


class ExpenseTests(unittest.TestCase):
    def test_amount_whole(self):
        self.assertEqual(amount_to_cents("12"), 1200)

    def test_amount_exact_cents(self):
        self.assertEqual(amount_to_cents("0.29"), 29)

    def test_amount_signed(self):
        self.assertEqual(amount_to_cents("  -3.45  "), -345)

    def test_amount_reject_extra_precision(self):
        with self.assertRaises(ValueError):
            amount_to_cents("1.999")

    def test_amount_reject_non_finite(self):
        for text in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(ValueError):
                amount_to_cents(text)

    def test_split_even(self):
        self.assertEqual(split_bill(1200, 3), [400, 400, 400])

    def test_split_remainder(self):
        self.assertEqual(split_bill(10000, 3), [3334, 3333, 3333])

    def test_split_small_total(self):
        self.assertEqual(split_bill(2, 4), [1, 1, 0, 0])

    def test_split_reject_invalid(self):
        for cents, people in ((-1, 3), (10, 0), (10, -2), (10.5, 2), (10, 2.5)):
            with self.assertRaises(ValueError):
                split_bill(cents, people)

    def test_month_empty(self):
        self.assertEqual(monthly_totals([], "2026-10"), {})

    def test_month_filter(self):
        rows = [{"date": "2026-10-02", "category": "交通", "amount": "4.20"},
                {"date": "2026-09-30", "category": "交通", "amount": "3"}]
        self.assertEqual(monthly_totals(rows, "2026-10"), {"交通": 420})

    def test_month_refund(self):
        rows = [{"date": "2026-10-01", "category": "餐饮", "amount": "12.50"},
                {"date": "2026-10-02", "category": "餐饮", "amount": "-2.50"}]
        self.assertEqual(monthly_totals(rows, "2026-10"), {"餐饮": 1000})

    def test_month_reject_invalid(self):
        with self.assertRaises(ValueError):
            monthly_totals([], "2026-1")

    def test_date_reject_invalid(self):
        with self.assertRaises(ValueError):
            monthly_totals([{"date": "2026-02-30", "category": "交通", "amount": "3"}], "2026-02")

    def test_does_not_mutate_input(self):
        rows = [{"date": "2026-10-01", "category": "交通", "amount": "3"}]
        before = copy.deepcopy(rows)
        monthly_totals(rows, "2026-10")
        self.assertEqual(rows, before)
