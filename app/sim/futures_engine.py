from __future__ import annotations

from app.models import Position, Side


class FuturesSimulator:
    @staticmethod
    def unrealized_pnl(position: Position, mark: float) -> float:
        if position.side == Side.LONG:
            return (mark - position.entry_price) * position.qty
        return (position.entry_price - mark) * position.qty

    @staticmethod
    def initial_margin(position: Position) -> float:
        return (position.qty * position.entry_price) / position.leverage

    @staticmethod
    def maintenance_margin(position: Position, mark: float) -> float:
        return position.qty * mark * position.maintenance_margin_rate

    @staticmethod
    def liquidation_price(position: Position, wallet_balance: float) -> float:
        q = position.qty
        mmr = position.maintenance_margin_rate
        e = position.entry_price
        l = position.leverage
        if position.side == Side.LONG:
            denominator = q * (1 - mmr)
            return max((q * e - wallet_balance + (q * e / l)) / max(denominator, 1e-9), 0.0)
        denominator = q * (1 + mmr)
        return max((wallet_balance + q * e + (q * e / l)) / max(denominator, 1e-9), 0.0)

    @classmethod
    def margin_ratio(cls, position: Position, wallet_balance: float, mark: float) -> float:
        upnl = cls.unrealized_pnl(position, mark)
        maint = cls.maintenance_margin(position, mark)
        equity = wallet_balance + upnl
        return maint / max(equity, 1e-9)

    @classmethod
    def is_liquidated(cls, position: Position, wallet_balance: float, mark: float) -> bool:
        upnl = cls.unrealized_pnl(position, mark)
        equity = wallet_balance + upnl
        return equity <= cls.maintenance_margin(position, mark)
