from dataclasses import dataclass


@dataclass
class RuleSignal:
    direction: int
    reason: str


class RuleStrategy:
    def decide(self, f: dict[str, float]) -> RuleSignal:
        if f["regime"] == -1:
            return RuleSignal(0, "chaos regime: stand down")
        if f["ema_fast"] > f["ema_slow"] and f["rsi"] < 70 and f["price"] > f["vwap"]:
            return RuleSignal(1, "trend long setup")
        if f["ema_fast"] < f["ema_slow"] and f["rsi"] > 30 and f["price"] < f["vwap"]:
            return RuleSignal(-1, "trend short setup")
        return RuleSignal(0, "no edge")
