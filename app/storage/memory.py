from __future__ import annotations

import json
from pathlib import Path


class LearningMemory:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = {
            "liquidation_streak": 0,
            "bad_leverages": {},
            "risky_sessions": {},
            "failure_patterns": [],
        }
        self.load()

    def load(self) -> None:
        if self.path.exists():
            self.data.update(json.loads(self.path.read_text()))

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2))

    def record_liquidation(self, context: dict) -> None:
        self.data["liquidation_streak"] += 1
        lev = str(context.get("leverage", "unknown"))
        self.data["bad_leverages"][lev] = self.data["bad_leverages"].get(lev, 0) + 1
        self.data["failure_patterns"].append(context)
        self.save()

    def reset_streak(self) -> None:
        self.data["liquidation_streak"] = 0
        self.save()

    def clear(self) -> None:
        self.data = {
            "liquidation_streak": 0,
            "bad_leverages": {},
            "risky_sessions": {},
            "failure_patterns": [],
        }
        self.save()
