from __future__ import annotations


class MLTradeFilter:
    """Dependency-free confidence gate with sklearn-compatible interface."""

    def __init__(self) -> None:
        self.trained = False
        self.threshold = 0.0

    def train(self, x: list[list[float]], y: list[int]) -> None:
        if not x or not y:
            return
        scores = [sum(v) / max(len(v), 1) for v in x]
        labeled = [(s, label) for s, label in zip(scores, y)]
        pos = [s for s, label in labeled if label > 0]
        neg = [s for s, label in labeled if label <= 0]
        if not pos or not neg:
            return
        self.threshold = (sum(pos) / len(pos) + sum(neg) / len(neg)) / 2
        self.trained = True

    def predict(self, feat_vec: list[float], direction: int) -> tuple[int, float]:
        if direction == 0:
            return 0, 0.0
        score = sum(feat_vec) / max(len(feat_vec), 1)
        if not self.trained:
            confidence = 0.55 if abs(direction) == 1 else 0.0
            return direction, confidence
        predicted = 1 if score >= self.threshold else -1
        confidence = min(0.95, 0.5 + abs(score - self.threshold) / (abs(self.threshold) + 1.0))
        return predicted, confidence
