"""Champion: exact, idempotent, empty-safe O(N) settlement kernel."""

STAGE = 6


def reset_state():
    """The champion deliberately keeps no cross-batch cache."""


def settlement_fee_cents(price_cents, quantity, fee_bps, rebate_bps=0):
    numerator = price_cents * quantity * (fee_bps - rebate_bps)
    sign = 1 if numerator >= 0 else -1
    return sign * ((abs(numerator) + 5_000) // 10_000)

def rolling_vwap(trades):
    positive = [trade for trade in trades if trade["quantity"] > 0]
    volume = sum(trade["quantity"] for trade in positive)
    if volume == 0:
        return 0.0
    return sum(trade["price_cents"] * trade["quantity"] for trade in positive) / volume

def match_and_settle_batch(orders):
    seen_order_ids = set()
    accepted = [None] * len(orders)
    count = total_quantity = fees = weighted_notional = 0
    risk_by_account = {}
    gross_by_account = {}
    for order in orders:
        quantity = int(order["quantity"])
        order_id = order["order_id"]
        if quantity <= 0 or order_id in seen_order_ids:
            continue
        seen_order_ids.add(order_id)
        accepted[count] = dict(order)
        count += 1
        total_quantity += quantity
        weighted_notional += order["price_cents"] * quantity
        fees += settlement_fee_cents(order["price_cents"], quantity,
                                     order.get("fee_bps", 0), order.get("rebate_bps", 0))
        signed = quantity if order["side"] == "buy" else -quantity
        account = order["account"]
        risk_by_account[account] = risk_by_account.get(account, 0) + signed
        gross_by_account[account] = gross_by_account.get(account, 0) + quantity
    return {
        "accepted_count": count,
        "total_quantity": total_quantity,
        "fees_cents": fees,
        "vwap_cents": weighted_notional / total_quantity if total_quantity else 0.0,
        "risk_by_account": risk_by_account,
        "gross_by_account": gross_by_account,
    }
