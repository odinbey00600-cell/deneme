from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class HealthState:
    started_at: float = time.time()
    last_error: str = ''
    cpu_pct: float = 0.0
    ram_pct: float = 0.0
