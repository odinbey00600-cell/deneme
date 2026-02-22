from src.risk.manager import RiskManager


def test_position_size_positive() -> None:
    qty = RiskManager.calculate_position_size(1000, 0.005, 100, 99)
    assert qty == 5


def test_dynamic_leverage_bounds() -> None:
    lev = RiskManager.dynamic_leverage(0.5, 1, 10)
    assert 1 <= lev <= 10
