from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, BigInteger, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.persistence_layer.db import Base


class Generation(Base):
    __tablename__ = 'generations'
    id = Column(Integer, primary_key=True)
    seed = Column(Integer, nullable=False)
    starting_balance = Column(Float, nullable=False)
    ending_balance = Column(Float, nullable=False, default=0)
    status = Column(String(32), nullable=False, default='running')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))


class GenomeParameter(Base):
    __tablename__ = 'genome_parameters'
    id = Column(Integer, primary_key=True)
    generation_id = Column(Integer, ForeignKey('generations.id', ondelete='CASCADE'), index=True)
    parameters = Column(JSON, nullable=False)


class Trade(Base):
    __tablename__ = 'trades'
    id = Column(BigInteger, primary_key=True)
    generation_id = Column(Integer, ForeignKey('generations.id', ondelete='CASCADE'), index=True)
    side = Column(String(8), nullable=False)
    qty = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, nullable=False)
    realized_pnl = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EquityHistory(Base):
    __tablename__ = 'equity_history'
    id = Column(BigInteger, primary_key=True)
    generation_id = Column(Integer, ForeignKey('generations.id', ondelete='CASCADE'), index=True)
    equity = Column(Float, nullable=False)
    mark_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Metric(Base):
    __tablename__ = 'metrics'
    id = Column(BigInteger, primary_key=True)
    generation_id = Column(Integer, ForeignKey('generations.id', ondelete='CASCADE'), index=True)
    sharpe = Column(Float)
    expectancy = Column(Float)
    max_drawdown = Column(Float)
    liquidation_frequency = Column(Float)


class LiquidationEvent(Base):
    __tablename__ = 'liquidation_events'
    id = Column(BigInteger, primary_key=True)
    generation_id = Column(Integer, ForeignKey('generations.id', ondelete='CASCADE'), index=True)
    mark_price = Column(Float, nullable=False)
    margin_ratio = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

Index('idx_trade_generation_created', Trade.generation_id, Trade.created_at)
Index('idx_equity_generation_created', EquityHistory.generation_id, EquityHistory.created_at)
