from __future__ import annotations

import copy
import random


class EvolutionEngine:
    def __init__(self, seed: int) -> None:
        self.rng = random.Random(seed)
        self.best_genome: dict | None = None

    def initial_genome(self) -> dict:
        return {
            'ema_short': 9,
            'ema_long': 26,
            'rsi_low': 35,
            'rsi_high': 65,
            'volatility_max': 0.02,
            'risk_aggressiveness': 0.8,
            'exploration_rate': 0.2,
            'reward_weights': {
                'drawdown': 0.5,
                'trade_frequency': 0.1,
                'liquidation_penalty': 10.0,
                'volatility_risk': 0.3,
            },
            'exit_bias': 0.5,
            'stop_tightening': 0.5,
        }

    def mutate(self, genome: dict, score: float) -> dict:
        g = copy.deepcopy(genome)
        for key in ['ema_short', 'ema_long']:
            g[key] = max(3, int(g[key] + self.rng.gauss(0, 2)))
        for key in ['rsi_low', 'rsi_high', 'volatility_max', 'risk_aggressiveness', 'exploration_rate', 'exit_bias', 'stop_tightening']:
            g[key] = max(0.001, float(g[key] + self.rng.gauss(0, 0.05)))
        for wk in g['reward_weights']:
            g['reward_weights'][wk] = max(0.01, g['reward_weights'][wk] + self.rng.gauss(0, 0.1))
        if self.rng.random() < 0.1:
            g['ema_long'] += self.rng.randint(-5, 5)
        if score > 0 and (self.best_genome is None or self.rng.random() < 0.5):
            self.best_genome = copy.deepcopy(genome)
        return g
