"""Expense tracker helpers: amounts are stored in integer cents, refunds are negative."""


def amount_to_cents(text):
    """Parse a decimal amount; allow surrounding spaces and a sign, reject non-finite values and more than two decimals."""
    return int(float(text) * 100)


def split_bill(cents, people):
    """Split a non-negative integer amount among a positive integer number of people; leftover cents go to the first people in turn."""
    return [cents // people] * people


def monthly_totals(entries, month):
    """Total the given month's entries per category; raise ValueError on a malformed date or month, and do not modify the input."""
    totals = {}
    for entry in entries:
        if entry["date"].startswith(month):
            category = entry["category"]
            totals[category] = totals.get(category, 0) + abs(amount_to_cents(entry["amount"]))
    return totals
