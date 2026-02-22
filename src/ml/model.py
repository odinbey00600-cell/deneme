from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "ema_spread_fast",
    "ema_spread_swing",
    "rsi14",
    "atr14",
    "vwap_dev",
    "returns_3",
    "returns_5",
    "volume_change",
]


@dataclass
class MLSignal:
    direction: int
    confidence: float


class SignalFilterModel:
    def __init__(self, algorithm: str = "rf") -> None:
        if algorithm == "logreg":
            classifier = LogisticRegression(max_iter=500)
        else:
            classifier = RandomForestClassifier(n_estimators=300, random_state=42, max_depth=8)
        self.pipeline = Pipeline([("scaler", StandardScaler()), ("clf", classifier)])

    def train(self, df: pd.DataFrame, target: pd.Series) -> str:
        x_train, x_test, y_train, y_test = train_test_split(df[FEATURE_COLUMNS], target, test_size=0.2, shuffle=False)
        self.pipeline.fit(x_train, y_train)
        preds = self.pipeline.predict(x_test)
        return classification_report(y_test, preds)

    def predict_latest(self, features: pd.DataFrame) -> MLSignal:
        latest = features[FEATURE_COLUMNS].tail(1)
        probs = self.pipeline.predict_proba(latest)[0]
        direction = int(probs[1] >= probs[0])
        confidence = float(max(probs))
        return MLSignal(direction=direction, confidence=confidence)

    def save(self, path: str | Path) -> None:
        joblib.dump(self.pipeline, path)

    def load(self, path: str | Path) -> None:
        self.pipeline = joblib.load(path)
