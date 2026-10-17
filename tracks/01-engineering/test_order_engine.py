"""Frozen ten-test correctness gate for the settlement kernel."""

import copy
import order_engine as engine


def order(order_id, account="acct-a", side="buy", price=1_000, quantity=2,
          fee_bps=25, rebate_bps=0):
    return {"order_id": order_id, "account": account, "side": side,
            "price_cents": price, "quantity": quantity,
            "fee_bps": fee_bps, "rebate_bps": rebate_bps}


def setup_function():
    engine.reset_state()


def test_single_order_settles():
    result = engine.match_and_settle_batch([order("one")])
    assert result["accepted_count"] == 1
    assert result["total_quantity"] == 2


def test_signed_buy_sell_risk():
    result = engine.match_and_settle_batch([
        order("buy", quantity=8), order("sell", side="sell", quantity=3)
    ])
    assert result["risk_by_account"]["acct-a"] == 5


def test_multiple_accounts_are_isolated_across_batches():
    first = engine.match_and_settle_batch([order("a1", account="acct-a", quantity=9)])
    second = engine.match_and_settle_batch([order("a2", account="acct-a", quantity=1)])
    assert first["risk_by_account"] == {"acct-a": 9}
    assert second["risk_by_account"] == {"acct-a": 1}


def test_regular_fee_settlement():
    result = engine.match_and_settle_batch([order("fee")])
    assert result["fees_cents"] == 5


def test_rebate_nets_against_fee():
    result = engine.match_and_settle_batch([
        order("rebate", price=2_000, quantity=1, fee_bps=20, rebate_bps=5)
    ])
    assert result["fees_cents"] == 3


def test_weighted_vwap():
    result = engine.match_and_settle_batch([
        order("v1", price=100, quantity=2), order("v2", price=110, quantity=1)
    ])
    assert abs(result["vwap_cents"] - (310 / 3)) < 1e-9


def test_input_is_not_mutated():
    orders = [order("immutable")]
    original = copy.deepcopy(orders)
    engine.match_and_settle_batch(orders)
    assert orders == original


def test_adjacent_retry_is_idempotent():
    retry = order("retry-adjacent", quantity=7)
    result = engine.match_and_settle_batch([retry, dict(retry)])
    assert result["accepted_count"] == 1
    assert result["total_quantity"] == 7


def test_separated_retry_is_idempotent():
    retry = order("retry-separated", quantity=4)
    result = engine.match_and_settle_batch([retry, order("middle"), dict(retry)])
    assert result["accepted_count"] == 2
    assert result["total_quantity"] == 6


def test_exact_half_cent_and_empty_window_are_safe():
    assert engine.settlement_fee_cents(100, 1, 50) == 1
    assert engine.settlement_fee_cents(100, 1, 0, 50) == -1
    assert engine.rolling_vwap([]) == 0.0
    assert engine.rolling_vwap([order("zero", quantity=0),
                                order("negative", quantity=-2)]) == 0.0
