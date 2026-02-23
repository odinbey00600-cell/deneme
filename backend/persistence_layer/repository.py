from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func

from persistence_layer.db import SessionLocal
from persistence_layer.models import EquityHistory, Generation, GenomeParameter, LiquidationEvent, Metric, Trade


class Repository:
    def create_generation(self, generation_number: int, genome: dict[str, Any], starting_balance: float, parent_generation_id: int | None = None) -> Generation:
        with SessionLocal() as session:
            generation = Generation(
                generation_number=generation_number,
                starting_balance=starting_balance,
                equity_peak=starting_balance,
                parent_generation_id=parent_generation_id,
            )
            session.add(generation)
            session.flush()
            session.add(GenomeParameter(generation_id=generation.id, params=genome))
            session.commit()
            session.refresh(generation)
            return generation

    def close_generation(self, generation_id: int, ending_balance: float, survival_seconds: float, equity_peak: float, liquidation_count: int) -> None:
        with SessionLocal() as session:
            generation = session.get(Generation, generation_id)
            if generation:
                generation.ending_balance = ending_balance
                generation.end_time = datetime.utcnow()
                generation.survival_seconds = survival_seconds
                generation.equity_peak = equity_peak
                generation.liquidation_count = liquidation_count
                session.commit()

    def add_trade(self, **kwargs: Any) -> Trade:
        with SessionLocal() as session:
            trade = Trade(**kwargs)
            session.add(trade)
            session.commit()
            session.refresh(trade)
            return trade

    def update_trade(self, trade_id: int, **kwargs: Any) -> None:
        with SessionLocal() as session:
            trade = session.get(Trade, trade_id)
            if trade:
                for k, v in kwargs.items():
                    setattr(trade, k, v)
                session.commit()

    def add_equity_point(self, generation_id: int, balance: float, equity: float, unrealized_pnl: float, drawdown: float) -> None:
        with SessionLocal() as session:
            session.add(EquityHistory(generation_id=generation_id, balance=balance, equity=equity, unrealized_pnl=unrealized_pnl, drawdown=drawdown))
            session.commit()

    def add_metric(self, generation_id: int, key: str, value: float) -> None:
        with SessionLocal() as session:
            session.add(Metric(generation_id=generation_id, key=key, value=value))
            session.commit()

    def add_liquidation(self, generation_id: int, mark_price: float, liquidation_price: float, reason: str) -> None:
        with SessionLocal() as session:
            session.add(LiquidationEvent(generation_id=generation_id, mark_price=mark_price, liquidation_price=liquidation_price, reason=reason))
            session.commit()

    def generation_summary(self) -> list[dict[str, Any]]:
        with SessionLocal() as session:
            rows = (
                session.query(
                    Generation.generation_number,
                    Generation.survival_seconds,
                    Generation.equity_peak,
                    Generation.liquidation_count,
                    Generation.ending_balance,
                )
                .order_by(Generation.generation_number.desc())
                .limit(50)
                .all()
            )
            return [r._asdict() for r in rows]

    def trade_count(self, generation_id: int) -> int:
        with SessionLocal() as session:
            return session.query(func.count(Trade.id)).filter(Trade.generation_id == generation_id).scalar() or 0
