from __future__ import annotations


def _ema(values: list[float], span: int) -> float:
    if not values:
        return 0.0
    alpha = 2.0 / (span + 1.0)
    e = values[0]
    for v in values[1:]:
        e = alpha * v + (1 - alpha) * e
    return e


def _sma(values: list[float], window: int) -> float:
    if not values:
        return 0.0
    chunk = values[-window:]
    return sum(chunk) / len(chunk)


def compute_features(rows) -> dict[str, float]:
    candles = list(rows)
    if not candles:
        candles = [{"open": 0.0, "high": 0.0, "low": 0.0, "close": 0.0, "volume": 1.0}]

    close = [float(r["close"]) for r in candles]
    high = [float(r["high"]) for r in candles]
    low = [float(r["low"]) for r in candles]
    vol = [max(float(r["volume"]), 1e-9) for r in candles]

    ema_fast = _ema(close, 9)
    ema_slow = _ema(close, 21)

    cum_pv = 0.0
    cum_v = 0.0
    for c, v in zip(close, vol):
        cum_pv += c * v
        cum_v += v
    vwap = cum_pv / max(cum_v, 1e-9)

    deltas = [0.0]
    for i in range(1, len(close)):
        deltas.append(close[i] - close[i - 1])
    gains = [d if d > 0 else 0.0 for d in deltas]
    losses = [-d if d < 0 else 0.0 for d in deltas]
    gain = _sma(gains, 14)
    loss = _sma(losses, 14) + 1e-9
    rs = gain / loss
    rsi = 100.0 - (100.0 / (1.0 + rs))

    tr = []
    prev_close = close[0]
    for h, l, c in zip(high, low, close):
        tr.append(max(h - l, abs(h - prev_close), abs(l - prev_close)))
        prev_close = c
    atr = _sma(tr, 14)

    returns = [0.0]
    for i in range(1, len(close)):
        base = close[i - 1] if close[i - 1] != 0 else 1e-9
        returns.append((close[i] - close[i - 1]) / base)
    recent = returns[-20:]
    mean = sum(recent) / max(len(recent), 1)
    var = sum((r - mean) ** 2 for r in recent) / max(len(recent), 1)
    volatility = var ** 0.5

    regime = 0
    if ema_fast > ema_slow and volatility < 0.02:
        regime = 1
    elif volatility > 0.03:
        regime = -1

    return {
        "price": float(close[-1]),
        "ema_fast": float(ema_fast),
        "ema_slow": float(ema_slow),
        "vwap": float(vwap),
        "rsi": float(rsi),
        "atr": float(atr),
        "volatility": float(volatility),
        "regime": float(regime),
    }
