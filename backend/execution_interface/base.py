from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Position:
    side: str = 'FLAT'
    qty: float = 0.0
    entry_price: float = 0.0
    margin: float = 0.0
    opened_ts: float = 0.0


class ExecutionInterface(ABC):
    @abstractmethod
    async def place_order(self, side: str, margin: float, mark_price: float) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def close_position(self, mark_price: float, reason: str = 'signal') -> dict:
        raise NotImplementedError

    @abstractmethod
    def update_mark_price(self, mark_price: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_position(self) -> Position:
        raise NotImplementedError

    @abstractmethod
    def get_balance(self) -> float:
        raise NotImplementedError
