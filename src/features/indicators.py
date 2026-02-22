from __future__ import annotations

import numpy as np
import pandas as pd
import talib


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema9"] = talib.EMA(out["close"], timeperiod=9)
    out["ema21"] = talib.EMA(out["close"], timeperiod=21)
    out["ema12"] = talib.EMA(out["close"], timeperiod=12)
    out["ema26"] = talib.EMA(out["close"], timeperiod=26)
    out["rsi14"] = talib.RSI(out["close"], timeperiod=14)
    out["atr14"] = talib.ATR(out["high"], out["low"], out["close"], timeperiod=14)
    out["vwap"] = (out["close"] * out["volume"]).cumsum() / out["volume"].replace(0, np.nan).cumsum()
    out["returns_3"] = out["close"].pct_change(3)
    out["returns_5"] = out["close"].pct_change(5)
    out["volume_change"] = out["volume"].pct_change(1)
    out["ema_spread_fast"] = out["ema9"] - out["ema21"]
    out["ema_spread_swing"] = out["ema12"] - out["ema26"]
    out["vwap_dev"] = (out["close"] - out["vwap"]) / out["vwap"]
    out = out.dropna().reset_index(drop=True)
    return out


def create_target(df: pd.DataFrame) -> pd.Series:
    return (df["close"].shift(-1) > df["close"]).astype(int)
