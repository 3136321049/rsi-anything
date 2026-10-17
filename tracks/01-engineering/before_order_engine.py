"""Buggy baseline: correct happy path, but unsafe retries, money, and empty windows."""


def reset_state():
    """The baseline is stateless."""


def settlement_fee_cents(price_cents, quantity, fee_bps, rebate_bps=0):
    # BUG: binary float plus bankers' round loses half-cent batch settlements.
    return round(price_cents * quantity * (fee_bps - rebate_bps) / 10_000)


def rolling_vwap(trades):
    positive = [trade for trade in trades if trade["quantity"] > 0]
    volume = sum(trade["quantity"] for trade in positive)
    # BUG: an empty/zero-volume risk window divides by zero.
    return sum(trade["price_cents"] * trade["quantity"] for trade in positive) / volume


def match_and_settle_batch(orders):
    accepted = []
    risk_by_account = {}
    gross_by_account = {}
    for order in orders:
        quantity = int(order["quantity"])
        if quantity <= 0:
            continue
        # BUG: no order_id idempotency check; retries settle twice.
        accepted.append(dict(order))
        account = order["account"]
        # BOTTLENECK: each fill rescans the full prefix, making the batch O(N²).
        risk_by_account[account] = sum(
            (1 if row["side"] == "buy" else -1) * row["quantity"]
            for row in accepted
            if row["account"] == account
        )
        gross_by_account[account] = sum(
            row["quantity"] for row in accepted if row["account"] == account
        )
    fees = sum(
        settlement_fee_cents(
            row["price_cents"],
            row["quantity"],
            row.get("fee_bps", 0),
            row.get("rebate_bps", 0),
        )
        for row in accepted
    )
    return {
        "accepted_count": len(accepted),
        "total_quantity": sum(row["quantity"] for row in accepted),
        "fees_cents": fees,
        "vwap_cents": rolling_vwap(accepted),
        "risk_by_account": risk_by_account,
        "gross_by_account": gross_by_account,
    }
