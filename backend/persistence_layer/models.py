from datetime import datetime
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from persistence_layer.db import Base


class Generation(Base):
    __tablename__ = 'generations'

    id = Column(Integer, primary_key=True, index=True)
    generation_number = Column(Integer, unique=True, index=True, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    starting_balance = Column(Float, nullable=False)
    ending_balance = Column(Float, nullable=True)
    survival_seconds = Column(Float, default=0.0)
    equity_peak = Column(Float, default=0.0)
    liquidation_count = Column(Integer, default=0)
    parent_generation_id = Column(Integer, nullable=True)
    genome = relationship('GenomeParameter', back_populates='generation', uselist=False)


class GenomeParameter(Base):
    __tablename__ = 'genome_parameters'

    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey('generations.id'), unique=True)
    params = Column(JSON, nullable=False)
    generation = relationship('Generation', back_populates='genome')


class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    generation_id = Column(Integer, ForeignKey('generations.id'), index=True)
    side = Column(String, nullable=False)
    qty = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)
    fee_paid = Column(Float, default=0.0)
    slippage = Column(Float, default=0.0)
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    liquidation = Column(Boolean, default=False)


class EquityHistory(Base):
    __tablename__ = 'equity_history'

    id = Column(Integer, primary_key=True)
    generation_id = Column(Integer, ForeignKey('generations.id'), index=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)
    balance = Column(Float, nullable=False)
    equity = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, nullable=False)
    drawdown = Column(Float, nullable=False)


class Metric(Base):
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True)
    generation_id = Column(Integer, ForeignKey('generations.id'), index=True)
    ts = Column(DateTime, default=datetime.utcnow)
    key = Column(String, index=True, nullable=False)
    value = Column(Float, nullable=False)


class LiquidationEvent(Base):
    __tablename__ = 'liquidation_events'

    id = Column(Integer, primary_key=True)
    generation_id = Column(Integer, ForeignKey('generations.id'), index=True)
    ts = Column(DateTime, default=datetime.utcnow)
    mark_price = Column(Float, nullable=False)
    liquidation_price = Column(Float, nullable=False)
    reason = Column(String, nullable=False)
