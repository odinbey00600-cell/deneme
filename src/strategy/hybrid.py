from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class StrategySignal:
    mode: str
    direction: int  # -1,0,1
    reason: str


class HybridStrategy:
    def scalping_signal(self, df_1m: pd.DataFrame) -> StrategySignal:
        row = df_1m.iloc[-1]
        bull = row["ema9"] > row["ema21"] and row["close"] > row["vwap"]
        bear = row["ema9"] < row["ema21"] and row["close"] < row["vwap"]
        rsi_ok_long = row["rsi14"] < 70
        rsi_ok_short = row["rsi14"] > 30

        if bull and rsi_ok_long:
            return StrategySignal("scalp", 1, "ema+vwap long")
        if bear and rsi_ok_short:
            return StrategySignal("scalp", -1, "ema+vwap short")
        return StrategySignal("scalp", 0, "no alignment")

    def swing_signal(self, df_15m: pd.DataFrame) -> StrategySignal:
        row = df_15m.iloc[-1]
        atr_pct = row["atr14"] / row["close"]
        if row["ema12"] > row["ema26"] and row["rsi14"] < 65 and atr_pct < 0.02:
            return StrategySignal("swing", 1, "trend-following long")
        if row["ema12"] < row["ema26"] and row["rsi14"] > 35 and atr_pct < 0.02:
            return StrategySignal("swing", -1, "trend-following short")
        return StrategySignal("swing", 0, "no setup")
